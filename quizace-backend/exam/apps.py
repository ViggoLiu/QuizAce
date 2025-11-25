"""AppConfig 声明考试模块的元数据与显示名称。"""

from django.apps import AppConfig


class ExamConfig(AppConfig):
    name = 'exam'
    verbose_name = '考试管理'
