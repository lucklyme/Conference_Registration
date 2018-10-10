from django.db import models
import django.utils.timezone as timezone

# Create your models here.


class Meeting(models.Model):
    name = models.CharField(max_length=50, verbose_name="会议名称")
    image = models.ImageField(verbose_name="二维码", max_length=100, null=True, blank=True)
    state = models.BooleanField(default=True, verbose_name='会议状态')
    meeting_time =  models.DateTimeField(verbose_name='开会时间', default=timezone.now)

    class Meta:
        verbose_name = '会议信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CheckinInfo(models.Model):
    meeting_id = models.ForeignKey(Meeting, on_delete=models.CASCADE, verbose_name='会议')
    userid = models.CharField(max_length=20, verbose_name='用户id', default='')
    name = models.CharField(max_length=20, verbose_name='姓名')
    department = models.CharField(max_length=20, verbose_name='部门')
    position = models.CharField(max_length=20, verbose_name='职务')
    company = models.CharField(max_length=20, verbose_name="所属公司", null=True, blank=True)
    checkin_time = models.DateTimeField(auto_now_add=True, verbose_name='签到时间')

    class Meta:
        verbose_name = '签到信息'
        verbose_name_plural = verbose_name
        ordering = ['-checkin_time']

    def __str__(self):
        return self.name
