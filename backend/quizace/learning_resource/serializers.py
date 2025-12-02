from rest_framework import serializers
from .models import LearningResource


class LearningResourceSerializer(serializers.ModelSerializer):
    # 添加文件URL字段
    file_url = serializers.SerializerMethodField()
    # 添加上传者名称字段
    uploader_name = serializers.CharField(source="uploader.username", read_only=True)
    
    def get_file_url(self, obj):
        """生成文件的完整URL"""
        if obj.file:
            return self.context['request'].build_absolute_uri(obj.file.url)
        return None
    
    class Meta:
        model = LearningResource
        fields = "__all__"
