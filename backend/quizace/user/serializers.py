from rest_framework import serializers
from user.models import SysUser, StudentProfile, TeacherProfile


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = '__all__'
        read_only_fields = ['user']


class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = '__all__'
        read_only_fields = ['user']


class UserSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(read_only=False, required=False)
    teacher_profile = TeacherProfileSerializer(read_only=False, required=False)
    
    class Meta:
        model = SysUser
        fields = ['id', 'username', 'role', 'avatar', 'email', 'phone', 'remark', 'student_profile', 'teacher_profile']
        read_only_fields = ['id', 'username', 'role']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # 根据用户角色决定返回哪个角色的profile
        if instance.role == 'student':
            # 移除teacher_profile字段
            representation.pop('teacher_profile', None)
        elif instance.role == 'teacher':
            # 移除student_profile字段
            representation.pop('student_profile', None)
        return representation
    
    def update(self, instance, validated_data):
        # 更新基础用户信息
        student_profile_data = validated_data.pop('student_profile', None)
        teacher_profile_data = validated_data.pop('teacher_profile', None)
        
        instance = super().update(instance, validated_data)
        
        # 更新学生信息
        if instance.role == 'student' and student_profile_data:
            student_profile, created = StudentProfile.objects.get_or_create(user=instance)
            for attr, value in student_profile_data.items():
                setattr(student_profile, attr, value)
            student_profile.save()
        # 更新教师信息
        elif instance.role == 'teacher' and teacher_profile_data:
            teacher_profile, created = TeacherProfile.objects.get_or_create(user=instance)
            for attr, value in teacher_profile_data.items():
                setattr(teacher_profile, attr, value)
            teacher_profile.save()
        
        return instance


class AdminUserManageSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(required=False, allow_null=True)
    teacher_profile = TeacherProfileSerializer(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)

    class Meta:
        model = SysUser
        fields = [
            'id', 'username', 'password', 'role', 'email', 'phone', 'status',
            'remark', 'student_profile', 'teacher_profile', 'create_time', 'update_time'
        ]
        read_only_fields = ['id', 'create_time', 'update_time']

    def validate(self, attrs):
        role = attrs.get('role')
        if not role and self.instance:
            role = self.instance.role
        if role not in ('student', 'teacher', 'admin'):
            raise serializers.ValidationError({'role': '只能管理学生、教师或管理员账号'})
        return attrs

    def create(self, validated_data):
        student_profile_data = validated_data.pop('student_profile', None)
        teacher_profile_data = validated_data.pop('teacher_profile', None)
        password = validated_data.pop('password', None)
        role = validated_data.get('role')

        if not password:
            raise serializers.ValidationError({'password': '创建账号时必须设置密码'})

        try:
            user = SysUser.objects.create_user(password=password, **validated_data)
        except ValueError as exc:
            raise serializers.ValidationError({'detail': str(exc)})

        self._upsert_profiles(user, role, student_profile_data, teacher_profile_data)
        return user

    def update(self, instance, validated_data):
        student_profile_data = validated_data.pop('student_profile', None)
        teacher_profile_data = validated_data.pop('teacher_profile', None)
        password = validated_data.pop('password', None)
        role = validated_data.get('role', instance.role)

        instance = super().update(instance, validated_data)

        if password:
            instance.set_password(password)
            instance.save()

        self._upsert_profiles(instance, role, student_profile_data, teacher_profile_data)
        return instance

    def _upsert_profiles(self, user, role, student_profile_data, teacher_profile_data):
        if role == 'student':
            defaults = student_profile_data or {}
            StudentProfile.objects.update_or_create(user=user, defaults=defaults)
            TeacherProfile.objects.filter(user=user).delete()
        elif role == 'teacher':
            defaults = teacher_profile_data or {}
            TeacherProfile.objects.update_or_create(user=user, defaults=defaults)
            StudentProfile.objects.filter(user=user).delete()
        elif role == 'admin':
            StudentProfile.objects.filter(user=user).delete()
            TeacherProfile.objects.filter(user=user).delete()

    def to_representation(self, instance):
        """Ensure related profile exists so serialization never raises."""
        if instance.role == 'student':
            StudentProfile.objects.get_or_create(user=instance)
        elif instance.role == 'teacher':
            TeacherProfile.objects.get_or_create(user=instance)
        return super().to_representation(instance)
