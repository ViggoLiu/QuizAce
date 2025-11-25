"""AppConfig 定义题库模块的人类可读名称与配置。"""

from django.apps import AppConfig


class QuestionConfig(AppConfig):
    name = 'question'
    verbose_name = '题库管理'
