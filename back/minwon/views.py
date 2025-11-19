from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from minwon.ai.review import review_staff_response
from .models import Complaint, Comment, Attachment, CommentAuthorType
from .tasks import process_complaint_with_ai
from .serializers import (
    ComplaintListSerializer,
    ComplaintDetailSerializer,
    ComplaintCreateSerializer,
    ComplaintUpdateSerializer,
    ComplaintStatusChangeSerializer,
    CommentSerializer,
    AttachmentSerializer,
    AIResponseSerializer,
)


class ComplaintViewSet(viewsets.ModelViewSet):
    """민원 ViewSet"""

    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        """사용자의 민원만 조회"""
        user = self.request.user

        # 교사/관리자는 모든 민원 조회 가능
        if user.user_type in ['TEACHER', 'ADMIN']:
            return Complaint.objects.prefetch_related('comments', 'attachments', 'children').all()

        # 일반 사용자는 자신의 민원만 조회
        return Complaint.objects.filter(author=user).prefetch_related('comments', 'attachments', 'children')

    def get_serializer_class(self):
        """요청 유형에 따른 시리얼라이저 선택"""
        if self.action == 'list':
            return ComplaintListSerializer
        elif self.action == 'retrieve':
            return ComplaintDetailSerializer
        elif self.action == 'create':
            return ComplaintCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ComplaintUpdateSerializer
        elif self.action == 'change_status':
            return ComplaintStatusChangeSerializer
        elif self.action == 'set_ai_response':
            return AIResponseSerializer
        return ComplaintDetailSerializer

    def create(self, request, *args, **kwargs):
        """민원 생성 및 AI 응답 자동 생성"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        complaint = serializer.save()

        process_complaint_with_ai.delay(complaint.id)

        # 생성된 민원 상세 정보 반환
        detail_serializer = ComplaintDetailSerializer(complaint)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """민원 수정 (제목, 내용, 카테고리만 가능)"""
        complaint = self.get_object()

        # 권한 확인: 본인이거나 교직원
        if complaint.author != request.user and request.user.user_type not in ['TEACHER', 'ADMIN']:
            return Response(
                {'detail': '권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(complaint, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        complaint = serializer.save()

        detail_serializer = ComplaintDetailSerializer(complaint)
        return Response(detail_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """민원 삭제"""
        complaint = self.get_object()

        # 권한 확인: 본인 또는 관리자만 삭제 가능
        if complaint.author != request.user and request.user.user_type != 'ADMIN':
            return Response(
                {'detail': '권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        complaint.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def change_status(self, request, id=None):
        """민원 상태 변경"""
        complaint = self.get_object()

        # 권한 확인: 민원 작성자 또는 교직원만 상태 변경 가능
        is_owner = complaint.author == request.user
        is_staff = request.user.user_type in ['TEACHER', 'ADMIN']

        if not (is_owner or is_staff):
            return Response(
                {'detail': '권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ComplaintStatusChangeSerializer(
            data=request.data,
            context={'complaint': complaint}
        )
        serializer.is_valid(raise_exception=True)

        action_name = serializer.validated_data['action']
        transition_method = getattr(complaint, action_name)

        try:
            transition_method()
            complaint.save()

            detail_serializer = ComplaintDetailSerializer(complaint)
            return Response(detail_serializer.data)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def my_complaints(self, request):
        """현재 사용자의 민원 목록"""
        complaints = self.get_queryset().filter(author=request.user)
        serializer = ComplaintListSerializer(complaints, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_complaints(self, request):
        """대기 중인 민원 (교직원용)"""
        if request.user.user_type not in ['TEACHER', 'ADMIN']:
            return Response(
                {'detail': '교직원만 조회할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        complaints = self.get_queryset().filter(
            status__in=['2차검토요청', '교무실처리중']
        )
        serializer = ComplaintListSerializer(complaints, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def review_complaint_reply(self, request, id=None):
        """작성 중인 댓글에 대한 AI 리뷰 요청 (동기 처리)"""
        complaint = self.get_object()

        # 권한 확인: 교직원만 리뷰 요청 가능
        if request.user.user_type not in ['TEACHER', 'ADMIN']:
            return Response(
                {'detail': '교직원만 리뷰를 요청할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # 요청 데이터에서 draft_content 추출
        draft_content = request.data.get('draft_content')

        if not draft_content or not draft_content.strip():
            return Response(
                {'detail': '검토할 댓글 내용이 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Mock Comment 객체 생성 (실제로는 DB에 저장하지 않음)
            class DraftComment:
                def __init__(self, content):
                    self.content = content

            draft_comment = DraftComment(draft_content)

            # AI 리뷰 생성 (동기 처리)
            import traceback
            try:
                review_content = review_staff_response(complaint, draft_comment)
            except Exception as ai_error:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"AI review error: {str(ai_error)}")
                logger.error(traceback.format_exc())
                return Response(
                    {'detail': f'AI 리뷰 생성 실패: {str(ai_error)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 임시 AI 리뷰 댓글 객체 생성 (DB 미저장)
            temporary_ai_comment = {
                'id': '',  # 임시 ID
                'complaint': str(complaint.id),
                'author': complaint.author.id,
                'author_name': complaint.author.real_name,
                'author_type': CommentAuthorType.AI,
                'author_type_display': 'AI',
                'content': review_content,
                'created_at': str(__import__('django.utils.timezone', fromlist=['now']).now()),
                'original_content': draft_content  # 리뷰 대상이었던 원문 포함
            }

            # 기존 complaint 정보와 함께 임시 AI 리뷰만 반환
            detail_serializer = ComplaintDetailSerializer(complaint)
            return Response({
                **detail_serializer.data,
                'ai_review': temporary_ai_comment,
                'message': 'AI 리뷰가 완료되었습니다. (임시 표시, DB 미저장)'
            })

        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Review complaint reply error: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {'detail': f'AI 리뷰 중 오류가 발생했습니다: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CommentViewSet(viewsets.ModelViewSet):
    """댓글 ViewSet"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """댓글 조회"""
        return Comment.objects.select_related('author', 'complaint').all()

    def create(self, request, *args, **kwargs):
        """댓글 생성"""
        data = request.data.copy()
        data['author'] = request.user.id

        # author_type 결정
        if request.user.user_type in ['TEACHER', 'ADMIN']:
            data['author_type'] = CommentAuthorType.STAFF
        else:
            data['author_type'] = CommentAuthorType.USER

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        # 댓글 생성 시 자동 상태 전환은 Comment.save()에서 처리됨

        response_serializer = CommentSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """댓글 삭제"""
        comment = self.get_object()

        # 권한 확인: 작성자 또는 관리자만 삭제 가능
        if comment.author != request.user and request.user.user_type != 'ADMIN':
            return Response(
                {'detail': '권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def add_to_complaint(self, request):
        """특정 민원에 댓글 추가"""
        complaint_id = request.data.get('complaint_id')
        content = request.data.get('content')

        if not complaint_id or not content:
            return Response(
                {'detail': 'complaint_id와 content는 필수입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        complaint = get_object_or_404(Complaint, id=complaint_id)

        # 권한 확인: 민원 작성자 또는 교직원
        is_owner = complaint.author == request.user
        is_staff = request.user.user_type in ['TEACHER', 'ADMIN']

        if not (is_owner or is_staff):
            return Response(
                {'detail': '권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # 댓글 작성자 타입 결정
        author_type = CommentAuthorType.STAFF if is_staff else CommentAuthorType.USER

        comment = Comment.objects.create(
            complaint=complaint,
            author=request.user,
            author_type=author_type,
            content=content
        )

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AttachmentViewSet(viewsets.ModelViewSet):
    """첨부파일 ViewSet"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AttachmentSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """첨부파일 조회"""
        return Attachment.objects.select_related('complaint').all()

    def create(self, request, *args, **kwargs):
        """첨부파일 생성"""
        complaint_id = request.data.get('complaint_id')

        if not complaint_id:
            return Response(
                {'detail': 'complaint_id는 필수입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        complaint = get_object_or_404(Complaint, id=complaint_id)

        # 권한 확인: 민원 작성자 또는 교직원
        if complaint.author != request.user and request.user.user_type not in ['TEACHER', 'ADMIN']:
            return Response(
                {'detail': '권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attachment = serializer.save(complaint=complaint)

        return Response(
            AttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        """첨부파일 삭제"""
        attachment = self.get_object()

        # 권한 확인
        if (attachment.complaint.author != request.user and
                request.user.user_type not in ['TEACHER', 'ADMIN']):
            return Response(
                {'detail': '권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        attachment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
