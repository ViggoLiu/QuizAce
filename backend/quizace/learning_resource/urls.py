from django.urls import path
from .views import (
    UploadLearningResourceView,
    ResourceListView,
    ResourceDetailView,
    ResourceViewTrackView,
    MyResourceView,
    ResourceAuditView,
    ResourceFavoriteView,
    ResourceDownloadView,
    ResourceCheckFavoriteView,
    ResourceUsageStatsView,
    ResourceAdminDeleteView,
)



urlpatterns = [
    path('upload/', UploadLearningResourceView.as_view()),
    path('list/', ResourceListView.as_view()),
    path('detail/<int:pk>/', ResourceDetailView.as_view()),
    path('view/<int:pk>/', ResourceViewTrackView.as_view()),
    path('my/', MyResourceView.as_view()),
    path('audit/<int:pk>/', ResourceAuditView.as_view()),
    path('admin/delete/<int:pk>/', ResourceAdminDeleteView.as_view()),
    path('favorite/<int:pk>/', ResourceFavoriteView.as_view()),
    path('download/<int:pk>/', ResourceDownloadView.as_view()),
    path('check_favorite/<int:pk>/', ResourceCheckFavoriteView.as_view()),
    path('usage/stats/', ResourceUsageStatsView.as_view()),
]
