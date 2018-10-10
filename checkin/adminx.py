import xadmin
from .models import Meeting, CheckinInfo


class MeetingAdmin(object):
    model_icon = 'fa fa-group'
    list_display = ('name', 'meeting_time', 'state')  # 显示表格的表头
    list_per_page = 50  # 每页显示 50 条记录
    ordering = ('-meeting_time',)  # 用 name 属性排序， '-' 表示倒序排列
    list_filter = ('name', 'meeting_time', 'state')  # 设置过滤器
    search_fields = ('name',)  # 设置搜索框中允许搜索的字段


class CheckInfoAdmin(object):
    model_icon = 'fa fa-pencil'
    list_display = ('meeting_id', 'name', 'position', 'department', 'checkin_time')  # 显示表格的表头
    list_per_page = 50  # 每页显示 50 条记录
    list_filter = ('meeting_id__name', 'meeting_id__meeting_time', 'name', 'department', 'position', 'checkin_time')  # 设置过滤器
    search_fields = ('name', )  # 设置搜索框中允许搜索的字段


xadmin.site.register(Meeting, MeetingAdmin)
xadmin.site.register(CheckinInfo, CheckInfoAdmin)
