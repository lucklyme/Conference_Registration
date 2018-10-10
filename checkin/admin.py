from django.contrib import admin
from .models import Meeting, CheckinInfo

# Register your models here.


class MeetingAdmin(admin.ModelAdmin):
    list_display = ('name', 'meeting_time', 'state')  # 显示表格的表头
    list_per_page = 50  # 每页显示 50 条记录
    ordering = ('-meeting_time',)  # 用 name 属性排序， '-' 表示倒序排列
    list_filter = ('name', 'meeting_time', 'state')  # 设置过滤器
    search_fields = ('name',)  # 设置搜索框中允许搜索的字段


admin.site.register(Meeting, MeetingAdmin)
admin.site.register(CheckinInfo)
