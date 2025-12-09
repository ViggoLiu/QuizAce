# QuizAce Backend

QuizAce平台的后端服务，基于Django框架开发。

## 技术栈

- **框架**: Django 4.2.7
- **语言**: Python 3.x
- **数据库**: MySQL
- **ORM**: Django ORM
- **API**: RESTful API
- **依赖**: 
  - numpy, pandas (数据处理)
  - tensorflow (AI智能批阅)
  - django-rest-framework (API开发)

## 项目结构

```
backend/quizace/
├── quizace/             # 项目配置目录
│   ├── settings.py      # 项目配置
│   ├── urls.py          # 主路由
│   ├── wsgi.py          # WSGI入口
│   ├── asgi.py          # ASGI入口
│   └── views.py         # 项目视图
├── user/                # 用户模块
│   ├── models.py        # 用户模型
│   ├── views.py         # 用户视图
│   ├── serializers.py   # 序列化器
│   ├── urls.py          # 用户路由
│   ├── admin.py         # 后台管理
│   ├── middleware.py    # 中间件
│   └── tests.py         # 测试用例
├── learning_resource/   # 学习资源模块
│   ├── models.py        # 资源模型
│   ├── views.py         # 资源视图
│   ├── serializers.py   # 序列化器
│   ├── urls.py          # 资源路由
│   ├── admin.py         # 后台管理
│   └── tests.py         # 测试用例
├── exam/                # 题库与考试模块
│   ├── models.py        # 考试模型
│   ├── views.py         # 考试视图
│   ├── serializers.py   # 序列化器
│   ├── urls.py          # 考试路由
│   ├── admin.py         # 后台管理
│   └── tests.py         # 测试用例
├── forum/               # 论坛模块
│   ├── models.py        # 论坛模型
│   ├── views.py         # 论坛视图
│   ├── serializers.py   # 序列化器
│   ├── urls.py          # 论坛路由
│   ├── admin.py         # 后台管理
│   └── tests.py         # 测试用例
├── manage.py            # Django管理脚本
├── requirements.txt     # 依赖列表
├── templates/           # HTML模板
├── readme.md            # 后端说明文档
├── BACKEND_STRUCTURE.md # 后端结构说明
└── .gitignore           # Git忽略文件
```

## 核心功能模块

### 1. 用户模块 (user)
- 用户注册、登录、登出
- 用户信息管理
- 角色权限控制（学生、教师、管理员）
- 学生、教师、班级模型扩展

### 2. 学习资源模块 (learning_resource)
- 学习资料上传与下载
- 资源分类与搜索
- 资源权限管理
- 资源收藏、点击记录

### 3. 题库与考试模块 (exam)
- 题目管理（增删改查）
- 试卷创建与管理
- 在线考试功能
- 自动/手动批阅
- 成绩统计与分析
- 练习模式与作答记录
- 错题本功能

### 4. 论坛模块 (forum)
- 课程论坛功能
- 评论管理
- 点赞功能
- 增强师生互动

## API文档

### RESTful规范

- **GET**: 获取资源
- **POST**: 创建资源
- **PUT**: 更新资源
- **DELETE**: 删除资源

### 主要API端点

#### 用户模块
- `POST /api/user/register/` - 用户注册
- `POST /api/user/login/` - 用户登录
- `GET /api/user/profile/` - 获取用户信息
- `PUT /api/user/profile/` - 更新用户信息

#### 学习资源模块
- `GET /api/resource/` - 获取资源列表
- `POST /api/resource/` - 上传资源
- `GET /api/resource/<id>/` - 获取资源详情
- `DELETE /api/resource/<id>/` - 删除资源

#### 题库与考试模块
- `GET /api/questions/` - 获取题目列表
- `POST /api/questions/` - 创建题目
- `GET /api/exams/` - 获取考试列表
- `POST /api/exams/` - 创建考试
- `GET /api/exams/<id>/` - 获取考试详情
- `POST /api/exams/<id>/submit/` - 提交考试

## 安装与运行

### 1. 环境准备
- Python 3.8+
- MySQL 8.0+

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 数据库配置

修改 `quizace/settings.py` 中的数据库配置：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'quizace',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 4. 初始化数据库

```bash
# 创建迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 5. 运行开发服务器

```bash
python manage.py runserver
D:/ANACONDA/envs/SE_ex/python.exe manage.py runserver
```

服务器默认运行在 `http://127.0.0.1:8000/`

## 开发指南

### 创建新应用

```bash
python manage.py startapp <app_name>
```

### 模型设计

在 `models.py` 中定义数据模型：

```python
from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    TYPE_CHOICES = [
        ('single', '单选题'),
        ('multiple', '多选题'),
        ('fill', '填空题'),
        ('essay', '简答题'),
    ]
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    content = models.TextField()
    answer = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 视图开发

使用DRF的视图集：

```python
from rest_framework import viewsets
from .models import Question
from .serializers import QuestionSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
```

### 路由配置

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

## 测试

### 运行单元测试

```bash
python manage.py test
```

### API测试

推荐使用Postman或Insomnia进行API测试。

## 部署

### 生产环境部署

1. 使用Gunicorn或uWSGI作为WSGI服务器
2. 使用Nginx作为反向代理
3. 配置SSL证书
4. 设置环境变量
5. 配置日志系统

## 注意事项

- 开发环境下请勿使用生产数据库
- 定期备份数据库
- 注意API的权限控制
- 敏感数据请使用环境变量配置

## 许可证

MIT License