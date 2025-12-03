from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from .models import LearningResource, ResourceClickRecord, ResourceFavorite
from .serializers import LearningResourceSerializer

import os
from django.conf import settings
from django.http import FileResponse
import mimetypes

class UploadLearningResourceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # 获取上传的文件
            uploaded_file = request.FILES.get("file")
            if not uploaded_file:
                return Response({
                    "code": 400,
                    "info": "未提供文件",
                    "data": None
                })

            # 计算文件大小（转换为MB）
            file_size = round(uploaded_file.size / (1024 * 1024), 2)  # MB
            
            # 获取文件类型
            file_type = os.path.splitext(uploaded_file.name)[1].lstrip('.').lower()

            # 创建资源记录
            resource = LearningResource.objects.create(
                name=request.data.get("name") or uploaded_file.name,
                course=request.data.get("course"),
                college=request.data.get("college"),
                description=request.data.get("description"),
                file=uploaded_file,  # 保存文件
                file_size=f"{file_size} MB",
                file_type=file_type,
                uploader=request.user,
                uploader_role=request.user.role,  # student or teacher
                status=0                           # 审核中
            )

            return Response({
                "code": 200,
                "info": "上传成功，等待审核",
                "data": {"resource_id": resource.id}
            })
        except Exception as e:
            return Response({
                "code": 500,
                "info": f"上传失败：{str(e)}",
                "data": None
            })

class ResourceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 获取all参数，如果为true则返回所有状态的资源
        all_resources = request.GET.get("all", "false").lower() == "true"
        
        if all_resources:
            resources = LearningResource.objects.all()
        else:
            resources = LearningResource.objects.filter(status=1)

        keyword = request.GET.get("keyword")
        course = request.GET.get("course")
        college = request.GET.get("college")

        if keyword:
            resources = resources.filter(name__icontains=keyword)

        if course:
            resources = resources.filter(course=course)

        if college:
            resources = resources.filter(college=college)

        serializer = LearningResourceSerializer(resources, many=True, context={'request': request})
        return Response({
            "code": 200,
            "info": "获取资源列表成功",
            "data": serializer.data
        })


from django.utils import timezone
from datetime import timedelta

class ResourceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        try:
            # 如果是管理员或需要查看所有状态的资源，可以添加权限判断
            resource = LearningResource.objects.get(id=pk)
            
            # 检查用户是否已经点击过该资源，添加时间限制（例如24小时内只能增加一次点击量）
            click_limit_time = 24  # 小时
            time_threshold = timezone.now() - timedelta(hours=click_limit_time)
            
            # 查找指定时间内的点击记录
            existing_record = ResourceClickRecord.objects.filter(
                user=request.user,
                resource=resource,
                clicked_at__gte=time_threshold
            ).first()
            
            if not existing_record:
                # 创建新的点击记录
                ResourceClickRecord.objects.create(user=request.user, resource=resource)
                # 增加点击量
                resource.click_count += 1
                resource.save()

            serializer = LearningResourceSerializer(resource, context={'request': request})
            return Response({
                "code": 200,
                "info": "获取资源详情成功",
                "data": serializer.data
            })

        except LearningResource.DoesNotExist:
            return Response({
                "code": 404,
                "info": "资源不存在",
                "data": None
            })
        except Exception as e:
            return Response({
                "code": 500,
                "info": f"获取资源详情失败：{str(e)}",
                "data": None
            })


class MyResourceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resources = LearningResource.objects.filter(uploader=request.user)
        serializer = LearningResourceSerializer(resources, many=True)
        return Response({
            "code": 200,
            "info": "获取我的资源列表成功",
            "data": serializer.data
        })


class ResourceAuditView(APIView):
    permission_classes = [IsAuthenticated]  # 你可加 admin 判断

    def post(self, request, pk):

        resource = LearningResource.objects.get(id=pk)

        status = int(request.data.get("status"))
        reason = request.data.get("reason", "")

        if status == 0:
            # 将资源撤回到审核中状态
            resource.status = 0
            resource.reject_reason = None
        elif status == 1:
            # 审核通过
            resource.status = 1
            resource.reject_reason = None
        elif status == 2:
            # 审核拒绝
            resource.status = 2
            resource.reject_reason = reason
        else:
            return Response({
                "code": 400,
                "info": "无效的审核状态",
                "data": None
            })

        resource.save()

        return Response({
            "code": 200,
            "info": "审核完成",
            "data": None
        })


class ResourceFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """
        收藏资源
        """
        try:
            resource = LearningResource.objects.get(id=pk, status=1)
            
            # 检查用户是否已经收藏过该资源
            favorite, created = ResourceFavorite.objects.get_or_create(
                user=request.user,
                resource=resource
            )
            
            if created:
                # 增加收藏量
                resource.favorite_count += 1
                resource.save()
                return Response({
                    "code": 200,
                    "info": "收藏成功",
                    "data": None
                })
            else:
                return Response({
                    "code": 400,
                    "info": "您已经收藏过该资源",
                    "data": None
                })
                
        except LearningResource.DoesNotExist:
            return Response({
                "code": 404,
                "info": "资源不存在",
                "data": None
            })
        except Exception as e:
            return Response({
                "code": 500,
                "info": f"收藏失败：{str(e)}",
                "data": None
            })
            
    def delete(self, request, pk):
        """
        取消收藏资源
        """
        try:
            resource = LearningResource.objects.get(id=pk, status=1)
            
            # 检查用户是否已经收藏过该资源
            favorite = ResourceFavorite.objects.filter(
                user=request.user,
                resource=resource
            )
            
            if favorite.exists():
                # 删除收藏记录
                favorite.delete()
                # 减少收藏量
                if resource.favorite_count > 0:
                    resource.favorite_count -= 1
                    resource.save()
                return Response({
                    "code": 200,
                    "info": "取消收藏成功",
                    "data": None
                })
            else:
                return Response({
                    "code": 400,
                    "info": "您还没有收藏该资源",
                    "data": None
                })
                
        except LearningResource.DoesNotExist:
            return Response({
                "code": 404,
                "info": "资源不存在",
                "data": None
            })
        except Exception as e:
            return Response({
                "code": 500,
                "info": f"取消收藏失败：{str(e)}",
                "data": None
            })


class ResourceDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        下载资源文件
        """
        try:
            resource = LearningResource.objects.get(id=pk)
            
            # 检查文件是否存在
            if not resource.file:
                return Response({
                    "code": 404,
                    "info": "文件不存在",
                    "data": None
                })
            
            # 检查文件是否为空
            if resource.file.size == 0:
                return Response({
                    "code": 404,
                    "info": "文件为空",
                    "data": None
                })
            
            # 增加下载量
            resource.download_count += 1
            resource.save()
            
            # 获取文件路径
            file_path = resource.file.path
            
            # 确定文件的MIME类型
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or 'application/octet-stream'
            
            # 提供文件下载
            response = FileResponse(open(file_path, 'rb'), content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            
            return response
            
        except LearningResource.DoesNotExist:
            return Response({
                "code": 404,
                "info": "资源不存在",
                "data": None
            })
        except Exception as e:
            return Response({
                "code": 500,
                "info": f"下载失败：{str(e)}",
                "data": None
            })


class ResourceCheckFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        检查用户是否已收藏资源
        """
        try:
            resource = LearningResource.objects.get(id=pk)
            
            # 检查用户是否已收藏该资源
            is_favorite = ResourceFavorite.objects.filter(
                user=request.user,
                resource=resource
            ).exists()
            
            return Response({
                "code": 200,
                "info": "检查收藏状态成功",
                "data": {
                    "is_favorite": is_favorite
                }
            })
            
        except LearningResource.DoesNotExist:
            return Response({
                "code": 404,
                "info": "资源不存在",
                "data": None
            })
        except Exception as e:
            return Response({
                "code": 500,
                "info": f"检查收藏状态失败：{str(e)}",
                "data": None
            })


class ResourceUsageStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return per-course usage derived from click history."""
        usage_qs = (
            ResourceClickRecord.objects.filter(user=request.user)
            .values("resource__course")
            .annotate(total_time=Count("id"))
            .order_by("-total_time")
        )

        total_time = sum(item["total_time"] for item in usage_qs)
        usage_data = []

        for item in usage_qs:
            course_name = item["resource__course"] or "未分配"
            total = item["total_time"]
            percentage = round(total / total_time * 100, 2) if total_time else 0
            usage_data.append({
                "course": course_name,
                "value": total,
                "percentage": percentage,
            })

        return Response({
            "code": 200,
            "info": "获取学习资源使用统计成功",
            "data": {
                "total": total_time,
                "items": usage_data,
            }
        })
