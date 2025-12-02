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
