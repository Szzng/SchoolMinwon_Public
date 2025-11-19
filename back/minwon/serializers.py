from rest_framework import serializers
from .models import Complaint, Comment, Attachment, CommentAuthorType
from accounts.models import User, Child
import uuid


class AttachmentSerializer(serializers.ModelSerializer):
    """첨부파일 시리얼라이저"""

    class Meta:
        model = Attachment
        fields = ('id', 'original_name', 'size', 'mime_type', 'file', 'created_at')
        read_only_fields = ('id', 'created_at', 'size')


class CommentSerializer(serializers.ModelSerializer):
    """댓글 시리얼라이저"""

    author_name = serializers.CharField(source='author.real_name', read_only=True)
    author_type_display = serializers.CharField(source='get_author_type_display', read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'complaint',
            'author',
            'author_name',
            'author_type',
            'author_type_display',
            'content',
            'created_at'
        )
        read_only_fields = ('id', 'created_at', 'author_name')

    def create(self, validated_data):
        """댓글 생성 (자동 상태 전환 포함)"""
        return Comment.objects.create(**validated_data)


class ChildSerializer(serializers.ModelSerializer):
    """학생(자녀) 시리얼라이저"""

    class Meta:
        model = Child
        fields = ('id', 'name', 'grade', 'classroom')
        read_only_fields = ('id',)


class ComplaintListSerializer(serializers.ModelSerializer):
    """민원 목록 조회용 시리얼라이저"""

    author_name = serializers.CharField(source='author.real_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    comment_count = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = (
            'id',
            'title',
            'content',
            'author',
            'author_name',
            'status',
            'status_display',
            'ai_risk_detect',
            'created_at',
            'updated_at',
            'comment_count',
            'attachment_count'
        )
        read_only_fields = fields

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_attachment_count(self, obj):
        return obj.attachments.count()


class ComplaintDetailSerializer(serializers.ModelSerializer):
    """민원 상세 조회용 시리얼라이저"""

    author_name = serializers.CharField(source='author.real_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    children = ChildSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Complaint
        fields = (
            'id',
            'title',
            'content',
            'author',
            'author_name',
            'children',
            'categories',
            'status',
            'status_display',
            'history',
            'ai_response',
            'ai_risk_detect',
            'comments',
            'attachments',
            'closed_by',
            'closed_at',
            'created_at',
            'updated_at'
        )
        read_only_fields = (
            'id',
            'author',
            'author_name',
            'status',
            'status_display',
            'history',
            'ai_response',
            'ai_risk_detect',
            'comments',
            'attachments',
            'closed_by',
            'closed_at',
            'created_at',
            'updated_at'
        )

    def to_representation(self, instance):
        """응답 데이터 형식 조정"""
        data = super().to_representation(instance)
        # comments를 created_at으로 정렬
        data['comments'] = sorted(data['comments'], key=lambda x: x['created_at'])
        return data


class ComplaintCreateSerializer(serializers.ModelSerializer):
    """민원 생성용 시리얼라이저"""

    children_ids = serializers.PrimaryKeyRelatedField(
        queryset=Child.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='children'
    )

    class Meta:
        model = Complaint
        fields = (
            'title',
            'content',
            'categories',
            'children_ids',
            'website'
        )

    def validate_title(self, value):
        """제목 유효성 검사"""
        if not value or not value.strip():
            raise serializers.ValidationError("제목은 비워둘 수 없습니다.")
        if len(value) > 80:
            raise serializers.ValidationError("제목은 최대 80자입니다.")
        return value

    def validate_content(self, value):
        """내용 유효성 검사"""
        content_len = len(value.strip())
        if content_len < 10:
            raise serializers.ValidationError("내용은 최소 10자 이상이어야 합니다.")
        if content_len > 2000:
            raise serializers.ValidationError("내용은 최대 2000자입니다.")
        return value

    def validate_website(self, value):
        """honeypot 필드 검사"""
        if value:
            raise serializers.ValidationError("이 필드는 비어있어야 합니다.")
        return value

    def create(self, validated_data):
        """민원 생성"""
        children_data = validated_data.pop('children', [])
        validated_data.pop('website', None)  # website 제거

        # 요청자를 author로 설정
        user = self.context['request'].user
        complaint = Complaint.objects.create(author=user, **validated_data)

        # 학생 추가
        if children_data:
            complaint.children.set(children_data)

        # 초기 이력 기록
        complaint.add_history_entry(
            complaint.status,
            '민원 접수'
        )
        complaint.save()

        return complaint


class ComplaintUpdateSerializer(serializers.ModelSerializer):
    """민원 수정용 시리얼라이저 (상태 변경 제외)"""

    class Meta:
        model = Complaint
        fields = (
            'title',
            'content',
            'categories'
        )


class ComplaintStatusChangeSerializer(serializers.Serializer):
    """민원 상태 변경 시리얼라이저"""

    action = serializers.ChoiceField(
        choices=[
            'ai_response_complete',
            'first_complete',
            'request_second_review',
            'start_office_processing',
            'response_complete',
            'reopen_by_user',
            'close_by_user',
            'close_by_staff'
        ]
    )

    def validate_action(self, value):
        """상태 변경 가능성 검사"""
        complaint = self.context['complaint']

        # FSM transition 가능 여부 확인
        transition_method = getattr(complaint, value, None)
        if not transition_method:
            raise serializers.ValidationError(f"'{value}' 상태 변경이 불가능합니다.")

        # 메서드가 callable인지 확인
        if not callable(transition_method):
            raise serializers.ValidationError(f"'{value}' 상태 변경이 불가능합니다.")

        return value


class AIResponseSerializer(serializers.Serializer):
    """AI 응답 생성 시리얼라이저"""

    content = serializers.CharField()

    def validate_content(self, value):
        """AI 응답 내용 유효성 검사"""
        if not value or not value.strip():
            raise serializers.ValidationError("AI 응답 내용은 비워둘 수 없습니다.")
        return value


class UserSerializer(serializers.ModelSerializer):
    """사용자 시리얼라이저"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_type', 'phone', 'school_name')
        read_only_fields = ('id', 'username')
