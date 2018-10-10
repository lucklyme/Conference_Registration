from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
import requests
from .models import Meeting, CheckinInfo
from django.views.decorators.csrf import csrf_exempt
import json
from checkin import models
import qrcode
from urllib.parse import quote
import os
from xlwt import *
from io import BytesIO
import datetime

# Create your views here.
corpid = '**********'
secrect = '******************************'

@csrf_exempt
def checkin(request):
    code = request.GET['code']   # 扫码重定向成功后，企业微信返回code，通过code获取成员信息
    state = request.GET['state']    # 二维码重定向链接中所带的状态值，用来返回会议ID号
   
    api_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + corpid + '&corpsecret=' + secrect
    req = requests.get(api_url)
    token_dict = json.loads(req.text)
    access_token = token_dict['access_token']
    # 以上用于获取access_token

    api_url1 = 'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token=' + access_token + '&code=' + code
    req1 = requests.get(api_url1)
    userid_dict = json.loads(req1.text)
    if 'UserId' in userid_dict.keys():
        userid = userid_dict['UserId']
    else:
        return render(request, 'note1.html')
    # 以上用于获取UserId

    api_url2 = 'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token=' + access_token + '&userid=' + userid
    req2 = requests.get(api_url2)
    userinfo_dict = json.loads(req2.text)
    username = userinfo_dict['name']
    department = userinfo_dict['department']
    position = userinfo_dict['position']

    # 以上用于获取用户姓名及部门ID

    department_name = ''
    if len(department) > 0:
        for i in department:
            api_url3 = 'https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token=' + access_token + '&id=' + str(
                i)
            req3 = requests.get(api_url3)
            department_dict = json.loads(req3.text)
            department_info = department_dict['department']
            department_name = department_name + '    ' + department_info[0]['name']
            department_name = department_name.lstrip()
            company_id = department_info[0]["parentid"]
            company_name = ""
            if company_id == 165:
                company_name = "上海斯耐迪工程咨询有限公司"
            elif company_id == 2 :
                company_name = "上海睦诚工程监理有限公司"

    # 以上用于获取用户所在部门的名称、职务、所属公司
    print(userid)
    confirm = models.CheckinInfo.objects.filter(userid=userid, meeting_id=state)
    if len(confirm) > 0:
        return render(request, 'note.html')
    else:
        meeting = Meeting.objects.get(id=state)
        obj = models.CheckinInfo(userid=userid, name=username, department=department_name, position=position, meeting_id=meeting, company=company_name)
        obj.save()
        return render(request, 'checkin.html')


@csrf_exempt
def index(request):
    AgentId = '1000023'
    meet_id = request.GET.get('meet_id', 0)
    if meet_id == 0:
        try:
            start_date = datetime.datetime.now().date()
            end_date = (datetime.datetime.now()+datetime.timedelta(days=1)).date()
            meet_list = get_list_or_404(Meeting, meeting_time__range=(start_date, end_date))
            return render(request, 'select.html',{'meet_list':meet_list})
        except Http404:
            return HttpResponseRedirect('/admin')
    elif meet_id != 0:
        meet_info = get_object_or_404(Meeting, id=meet_id)
        img_str = meet_info.image
        try:
            checkin_info = get_list_or_404(CheckinInfo, meeting_id=meet_id)
            checkin_count = len(checkin_info)
        except Http404:
            checkin_info = False
            checkin_count = 0
        if not img_str:
            url_urlencode  = quote('http://django.ssecc.com.cn:8000/checkin')
            url_base = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='
            req_url = url_base + corpid + '&redirect_uri=' + url_urlencode + '&response_type=code&scope=snsapi_base&agentid=' + AgentId + '&state=' + str(meet_id) + '#wechat_redirect'
            img = qrcode.make(req_url)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            image_dir = os.path.join(base_dir, 'image')
            img.save(image_dir + '/image/' + str(meet_id) + '.png')
            meet = Meeting.objects.get(id=meet_id)
            meet.image = 'image/' + str(meet_id) + '.png'
            meet.save()
            meet_info.image = 'image/' + str(meet_id) + '.png'
        return render(request, 'index.html',
                      { 'meeting_info': meet_info, 'checkin_info': checkin_info, 'checkin_count': checkin_count})


@csrf_exempt
def refresh(request):
    meet_id = request.POST.get('meet_id')
    try:
        checkin_info = get_list_or_404(CheckinInfo, meeting_id=meet_id)
        checkin_count = len(checkin_info)
    except Http404:
        checkin_info = False
        checkin_count = 0
    return render(request, 'pstable.html', {'checkin_info': checkin_info, 'checkin_count': checkin_count})


def excel_export(request, meet_id):
    meet_id = meet_id
    """
    导出excel表格
    """
    list_obj = CheckinInfo.objects.filter(meeting_id=meet_id).order_by("checkin_time")
    meet_name = Meeting.objects.get(id=meet_id).name
    meet_time = Meeting.objects.get(id=meet_id).meeting_time.strftime("%Y-%m-%d %H:%M")[:16]
    if list_obj:
        # 创建工作薄
        ws = Workbook(encoding='utf-8')
        w = ws.add_sheet(u"数据报表第一页")
        w.write(0, 0, meet_name)
        w.write(0, 2, "开会时间：")
        w.write(0, 3, meet_time)
        w.write(1, 0, "序号")
        w.write(1, 1, u"姓名")
        w.write(1, 2, u"部门")
        w.write(1, 3, u"职务")
        w.write(1, 4, u"所属公司")
        w.write(1, 5, u"签到时间")
        # 写入数据
        excel_row = 2
        for obj in list_obj:
            data_id = obj.id
            data_user = obj.name
            data_department = obj.department
            data_position = obj.position
            checkin_time = obj.checkin_time.strftime("%Y-%m-%d %H:%M:%S")[:19]
            w.write(excel_row, 0, data_id)
            w.write(excel_row, 1, data_user)
            w.write(excel_row, 2, data_department)
            w.write(excel_row, 3, data_position)
            w.write(excel_row, 4, '上海斯耐迪工程咨询有限公司')
            w.write(excel_row, 5, checkin_time)
            excel_row += 1
        # 检测文件是够存在
        # 方框中代码是保存本地文件使用，如不需要请删除该代码
        ###########################
        exist_file = os.path.exists("test.xls")
        if exist_file:
            os.remove(r"test.xls")
        ws.save("test.xls")
        ############################
        sio = BytesIO()
        ws.save(sio)
        sio.seek(0)
        response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=test.xls'
        response.write(sio.getvalue())
        return response
