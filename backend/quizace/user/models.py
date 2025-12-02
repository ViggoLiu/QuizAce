from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from rest_framework import serializers


class SysUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('必须提供用户名')
        # 补充 email 校验（因为 REQUIRED_FIELDS 包含 email）
        if 'email' not in extra_fields or not extra_fields['email']:
            raise ValueError('必须提供邮箱')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)  # 依赖 AbstractBaseUser 的 set_password 加密方法
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('status', 0)
        return self.create_user(username, password, **extra_fields)


class SysUser(AbstractBaseUser):
    objects = SysUserManager()
    USERNAME_FIELD = 'username'  # 登录用户名（必须唯一）
    REQUIRED_FIELDS = ['email']  # 创建用户时必须传入的字段

    ROLE_CHOICES = [
        ('student', '学生'),
        ('teacher', '教师'),
        ('admin', '管理员')
    ]

    STATUS_CHOICES = [
        (0, '正常'),
        (1, '禁用')
    ]

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, verbose_name="用户名")
    # 删：重复的 password 字段（AbstractBaseUser 已包含）
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student', verbose_name="用户角色")

    avatar = models.CharField(max_length=255, blank=True, null=True, verbose_name="头像")  # 加 null=True 匹配数据库 DEFAULT NULL
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="手机号")

    status = models.IntegerField(default=0, choices=STATUS_CHOICES, verbose_name="状态")
    # 删：重复的 last_login 字段（AbstractBaseUser 已包含）
    # 改：保留 auto_now_add=True 并添加 null=True 以兼容现有数据
    create_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    remark = models.CharField(max_length=255, blank=True, null=True, verbose_name="备注")  # 加 null=True 匹配数据库 DEFAULT NULL

    class Meta:
        db_table = "sys_user"
        verbose_name = "系统用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

# 以下 StudentProfile、TeacherProfile、Serializer 无需修改，保持原样即可
class StudentProfile(models.Model):
    user = models.OneToOneField(SysUser, on_delete=models.CASCADE, related_name="student_profile")
    student_no = models.CharField(max_length=50, null=True, blank=True, verbose_name="学号")
    college = models.CharField(max_length=100, null=True, blank=True, verbose_name="学院")
    major = models.CharField(max_length=100, null=True, blank=True, verbose_name="专业")
    grade = models.CharField(max_length=20, null=True, blank=True, verbose_name="年级")

    class Meta:
        db_table = "student_profile"
        verbose_name = "学生信息"

class TeacherProfile(models.Model):
    user = models.OneToOneField(SysUser, on_delete=models.CASCADE, related_name="teacher_profile")
    teacher_no = models.CharField(max_length=50, null=True, blank=True, verbose_name="工号")
    college = models.CharField(max_length=100, null=True, blank=True, verbose_name="学院")
    title = models.CharField(max_length=50, null=True, blank=True, verbose_name="职称")
    research_area = models.CharField(max_length=200, null=True, blank=True, verbose_name="研究方向")

    class Meta:
        db_table = "teacher_profile"
        verbose_name = "教师信息"

class SysUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}  # 密码只写不读，避免返回哈希值

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = '__all__'

class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = '__all__'