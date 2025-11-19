from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComplaintViewSet, CommentViewSet, AttachmentViewSet

app_name = 'minwon'

router = DefaultRouter()
router.register(r'complaints', ComplaintViewSet, basename='complaint')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'attachments', AttachmentViewSet, basename='attachment')

urlpatterns = [
    path('', include(router.urls)),
]
