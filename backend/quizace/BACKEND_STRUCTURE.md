# QuizAce 后端结构说明

本文档概述 `quizace-backend` 目录中各模块与 Django 官方脚手架的关系，帮助快速定位哪些部分来自框架默认结构，哪些为 QuizAce 项目定制。

## 1. Django 内置 / 脚手架部分

| 位置 | 说明 |
| --- | --- |
| `manage.py` | Django 自动生成的命令行入口，用于运行服务器、迁移、执行测试等。|
| `ExamOnline/` | Django 工程包，内含 `settings.py`、`urls.py`、`wsgi.py`、`asgi.py` 等全局配置文件，结构与 `django-admin startproject` 输出一致，仅内容根据项目需要调整。|
| `db.sqlite3` | 默认开发数据库，随脚手架一起出现，可替换为其他后端。|
| `__init__.py`（各包） | Python 包初始化文件，Django 用于发现 app；脚手架会为工程包创建，业务 app 后续也会同步添加。|
| `migrations/` + `__init__.py` | Django 在每个 app 下自动维护的迁移记录目录，内含生成的迁移脚本。|
| `templates/`、`static/`（空目录结构） | Django 推荐的全局模板与静态资源位置，框架不会自动填充内容，但目录层级符合惯例。|

## 2. QuizAce 自定义业务模块

| 模块 | 主要文件 | 作用 |
| --- | --- | --- |
| `exam/` | `models.py`、`serializers.py`、`views.py`、`admin.py`、`tests/` | 管理考试、试卷、成绩、练习与主观题批改等核心逻辑，并提供 REST 接口及后台管理配置。|
| `forum/` | `models.py`、`serializers.py`、`views.py`、`admin.py`、`tests/` | 论坛功能模块，支持课程论坛、评论管理、点赞等功能，增强师生互动。|
| `learning_resource/` | `models.py`、`serializers.py`、`views.py`、`admin.py`、`tests/` | 学习资源管理模块，支持资源上传、下载、收藏、点击记录等功能。|
| `user/` | `models.py`、`serializers.py`、`views.py`、`admin.py`、`tests/` | 用户域，扩展学生、教师、班级模型，提供注册、登录、密码修改和基础资料 API。|
| `requirements.txt` | 项目使用的 Python 依赖清单，自定义维护。|
| `README.md`、`BACKEND_STRUCTURE.md` | 项目文档，概述运行方式与架构说明。|

## 3. 第三方扩展集成
| 组件 | 相关文件/目录 | 说明 |
| --- | --- | --- |
| Django REST Framework | 各 app 的 `serializers.py`、`views.py` 中大量使用；`quizace/settings.py` 中配置。|
| Django Admin | 各 app 的 `admin.py` 文件，用于后台管理配置。|
| django-filter | 用于API过滤功能，在相关视图中使用。|

## 4. 结构总结

- **保留 Django 默认约定**：项目沿用了 Django 官方建议的“工程 + 多 app”分层，`manage.py`、`settings.py`、`urls.py`、`migrations/` 等均为框架原生概念。  
- **自定义功能沉淀到 app**：考试、题库、记录、用户四个 app 分别封装业务模型、API、后台与测试，形成清晰的业务边界。  
- **通过第三方增强体验**：在默认架构之上集成 DRF、xadmin、import-export、django-filter 等组件，满足在线出题、批阅与数据管理的需求。  

如需扩展新的业务，只需按 Django 约定创建新的 app，并在 `ExamOnline/settings.py` 与 `urls.py` 中注册即可，与现有结构保持一致。