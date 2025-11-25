"""AppConfig 定义用户模块的应用元数据。"""

from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'user'
    verbose_name = '用户管理'
