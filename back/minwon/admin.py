from django.contrib import admin
from .models import Complaint, Comment, Attachment


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'categories')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('id', 'created_at', 'updated_at', 'history')
    fieldsets = (
        ('기본 정보', {
            'fields': ('id', 'author', 'children', 'title', 'content')
        }),
        ('분류', {
            'fields': ('categories',)
        }),
        ('상태 관리', {
            'fields': ('status', 'history', 'closed_by', 'closed_at')
        }),
        ('AI 응답', {
            'fields': ('ai_response',)
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at')
        }),
        ('안티봇', {
            'fields': ('website',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'author_type', 'complaint', 'created_at')
    list_filter = ('author_type', 'created_at')
    search_fields = ('content', 'author__username')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('기본 정보', {
            'fields': ('id', 'complaint', 'author', 'author_type')
        }),
        ('내용', {
            'fields': ('content',)
        }),
        ('타임스탬프', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'complaint', 'size', 'mime_type', 'created_at')
    list_filter = ('mime_type', 'created_at')
    search_fields = ('original_name', 'complaint__title')
    readonly_fields = ('id', 'created_at', 'size')
    fieldsets = (
        ('기본 정보', {
            'fields': ('id', 'complaint', 'file', 'original_name')
        }),
        ('파일 정보', {
            'fields': ('mime_type', 'size')
        }),
        ('타임스탬프', {
            'fields': ('created_at',)
        }),
    )
