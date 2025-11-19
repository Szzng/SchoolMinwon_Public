import uuid
from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django_fsm import FSMField, transition
from django.utils import timezone
from accounts.models import User, Child
import re


# Validators
def validate_korean_phone(value):
    """Korean phone number format validator"""
    pattern = r'^(01[016789]|02|\d{3})-?\d{3,4}-?\d{4}$'
    if value and not re.match(pattern, value):
        raise ValidationError("유효한 한국 전화번호 형식이 아닙니다. (예: 010-1234-5678)")


# Choice definitions
class ComplaintCategory(models.TextChoices):
    CURRICULUM = '교육과정', '교육과정'
    MEALS = '급식', '급식'
    FACILITIES = '시설', '시설'
    STUDENT_GUIDANCE = '학생지도', '학생지도'
    ADMINISTRATION = '행정', '행정'
    SAFETY = '안전', '안전'
    SCHOOL_VIOLENCE = '학교폭력', '학교폭력'
    CORPORAL_PUNISHMENT = '체벌/인권', '체벌/인권'
    SCHOOL_SUPPLIES = '학용품비', '학용품비'
    AFTER_SCHOOL = '방과후활동', '방과후활동'
    SPECIAL_EDUCATION = '특수교육', '특수교육'
    PARENT_COMMUNICATION = '학부모소통', '학부모소통'
    DORMITORY = '기숙사', '기숙사'
    TEACHER_ATTITUDE = '교사태도', '교사태도'
    TESTS_EVALUATION = '시험/평가', '시험/평가'
    CAREER = '진로/진학', '진로/진학'
    OTHER = '기타', '기타'


class ComplaintStatus(models.TextChoices):
    AI_RESPONSE_WAIT = 'AI응답대기', 'AI응답대기'
    AI_RESPONSE_COMPLETE = 'AI응답완료', 'AI응답완료'
    FIRST_COMPLETE = '1차완료', '1차완료'
    SECOND_REVIEW_REQUEST = '2차검토요청', '2차검토요청'
    OFFICE_PROCESSING = '교무실처리중', '교무실처리중'
    RESPONSE_COMPLETE = '답변완료', '답변완료'
    CLOSED = '종료됨', '종료됨'


class CommentAuthorType(models.TextChoices):
    USER = 'user', '민원인'
    STAFF = 'staff', '교무실'
    AI = 'ai', 'AI'


class Complaint(models.Model):
    """학교 민원 모델"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # 민원인 정보
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='complaints',
        verbose_name='민원인'
    )

    # 관련 학생들
    children = models.ManyToManyField(
        Child,
        related_name='complaints',
        verbose_name='관련 학생',
        blank=True
    )

    # 기본 정보
    categories = models.JSONField(
        default=list,
        verbose_name='카테고리',
        help_text='선택된 민원 카테고리 목록'
    )
    title = models.CharField(
        max_length=80,
        verbose_name='제목'
    )
    content = models.TextField(
        verbose_name='내용'
    )

    # 상태 관리
    status = FSMField(
        default=ComplaintStatus.AI_RESPONSE_WAIT,
        choices=ComplaintStatus.choices,
        verbose_name='상태',
        protected=True
    )

    # 상태 이력
    history = models.JSONField(
        default=list,
        verbose_name='상태 이력',
        help_text='[{"at": "timestamp", "status": "상태", "note": "설명"}]'
    )

    # AI 응답
    ai_response = models.JSONField(
        null=True,
        blank=True,
        verbose_name='AI 응답',
        help_text='{"content": "...", "generatedAt": "timestamp"}'
    )

    # AI 위험도 감지
    ai_risk_detect = models.JSONField(
        null=True,
        blank=True,
        verbose_name='AI 위험도 감지 결과',
        help_text='{"sentiment": "...", "toxicity_score": 0.0~1.0, "category": "...", "needs_human_review": bool, "notes_for_staff": "...", "generatedAt": "timestamp"}'
    )

    # 종료 관련
    closed_by = models.CharField(
        max_length=10,
        choices=[('user', '민원인'), ('staff', '교무실')],
        null=True,
        blank=True,
        verbose_name='종료 요청자'
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='종료 시간'
    )

    # 타임스탬프
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성 일시'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정 일시'
    )

    # Anti-bot honeypot field
    website = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='웹사이트 (자동입력 금지)',
        help_text='봇 방지용 필드'
    )

    class Meta:
        verbose_name = '민원'
        verbose_name_plural = '민원'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"[{self.status}] {self.title} - {self.author.username}"

    def clean(self):
        """자동 유효성 검사"""
        # 웹사이트 필드가 비어있어야 함 (봇 방지)
        if self.website:
            raise ValidationError({'website': '이 필드는 비어있어야 합니다.'})

        # content 길이 검사
        content_len = len(self.content.strip())
        if content_len < 10:
            raise ValidationError({'content': '내용은 최소 10자 이상이어야 합니다.'})
        if content_len > 2000:
            raise ValidationError({'content': '내용은 최대 2000자 이내여야 합니다.'})

    def add_history_entry(self, status, note=None):
        """상태 이력 추가"""
        if not self.history:
            self.history = []
        self.history.append({
            'at': timezone.now().isoformat(),
            'status': status,
            'note': note
        })

    @transition(
        field=status,
        source=ComplaintStatus.AI_RESPONSE_WAIT,
        target=ComplaintStatus.AI_RESPONSE_COMPLETE
    )
    def ai_response_complete(self):
        """AI가 응답을 완료했을 때"""
        self.add_history_entry(
            ComplaintStatus.AI_RESPONSE_COMPLETE,
            'AI 응답 완료'
        )

    @transition(
        field=status,
        source=ComplaintStatus.AI_RESPONSE_COMPLETE,
        target=ComplaintStatus.FIRST_COMPLETE
    )
    def first_complete(self):
        """사용자가 AI 응답에 만족했을 때"""
        self.add_history_entry(
            ComplaintStatus.FIRST_COMPLETE,
            '민원인 1차 완료'
        )

    @transition(
        field=status,
        source=ComplaintStatus.AI_RESPONSE_COMPLETE,
        target=ComplaintStatus.SECOND_REVIEW_REQUEST
    )
    def request_second_review(self):
        """사용자가 추가 검토를 요청했을 때"""
        self.add_history_entry(
            ComplaintStatus.SECOND_REVIEW_REQUEST,
            '2차 검토 요청'
        )

    @transition(
        field=status,
        source=ComplaintStatus.SECOND_REVIEW_REQUEST,
        target=ComplaintStatus.OFFICE_PROCESSING
    )
    def start_office_processing(self):
        """교무실이 처리를 시작했을 때"""
        self.add_history_entry(
            ComplaintStatus.OFFICE_PROCESSING,
            '교무실 처리 시작'
        )

    @transition(
        field=status,
        source=[
            ComplaintStatus.OFFICE_PROCESSING,
            ComplaintStatus.SECOND_REVIEW_REQUEST
        ],
        target=ComplaintStatus.RESPONSE_COMPLETE
    )
    def response_complete(self):
        """교무실이 최종 답변을 제공했을 때"""
        self.add_history_entry(
            ComplaintStatus.RESPONSE_COMPLETE,
            '교무실 최종 답변'
        )

    @transition(
        field=status,
        source=ComplaintStatus.RESPONSE_COMPLETE,
        target=ComplaintStatus.OFFICE_PROCESSING
    )
    def reopen_by_user(self):
        """민원인이 답변 이후 다시 댓글을 달았을 때"""
        self.add_history_entry(
            ComplaintStatus.OFFICE_PROCESSING,
            '민원인 재개'
        )

    @transition(
        field=status,
        source=ComplaintStatus.RESPONSE_COMPLETE,
        target=ComplaintStatus.CLOSED
    )
    def close_by_user(self):
        """민원인이 종료했을 때"""
        self.closed_by = 'user'
        self.closed_at = timezone.now()
        self.add_history_entry(
            ComplaintStatus.CLOSED,
            '민원인이 종료'
        )

    @transition(
        field=status,
        source=ComplaintStatus.RESPONSE_COMPLETE,
        target=ComplaintStatus.CLOSED
    )
    def close_by_staff(self):
        """교무실이 종료했을 때"""
        self.closed_by = 'staff'
        self.closed_at = timezone.now()
        self.add_history_entry(
            ComplaintStatus.CLOSED,
            '교무실이 종료'
        )


class Comment(models.Model):
    """민원 댓글/응답 모델"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='민원'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='comments',
        verbose_name='작성자'
    )

    author_type = models.CharField(
        max_length=10,
        choices=CommentAuthorType.choices,
        verbose_name='작성자 유형'
    )

    content = models.TextField(verbose_name='내용')

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='작성 일시'
    )

    class Meta:
        verbose_name = '댓글'
        verbose_name_plural = '댓글'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['complaint', 'created_at']),
        ]

    def __str__(self):
        return f"{self.author.username}의 {self.get_author_type_display()}: {self.content[:50]}"

    def save(self, *args, **kwargs):
        """댓글 저장 시 민원 상태 자동 전환"""
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            # 교무실(staff) 댓글이 2차검토요청 상태에 달리면 자동 전환
            if (self.author_type == CommentAuthorType.STAFF and
                self.complaint.status == ComplaintStatus.SECOND_REVIEW_REQUEST):
                self.complaint.start_office_processing()
                self.complaint.save()

            # 민원인(user) 댓글이 답변완료 상태에 달리면 자동 전환
            elif (self.author_type == CommentAuthorType.USER and
                  self.complaint.status == ComplaintStatus.RESPONSE_COMPLETE):
                self.complaint.reopen_by_user()
                self.complaint.save()


class Attachment(models.Model):
    """민원 첨부파일 모델"""

    ALLOWED_MIME_TYPES = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
    ]

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='민원'
    )

    file = models.FileField(
        upload_to='complaints/%Y/%m/%d/',
        verbose_name='파일'
    )

    original_name = models.CharField(
        max_length=255,
        verbose_name='원본 파일명'
    )

    size = models.PositiveIntegerField(
        verbose_name='파일 크기 (bytes)'
    )

    mime_type = models.CharField(
        max_length=100,
        verbose_name='MIME 타입'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='업로드 일시'
    )

    class Meta:
        verbose_name = '첨부파일'
        verbose_name_plural = '첨부파일'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['complaint']),
        ]

    def __str__(self):
        return f"{self.original_name} ({self.complaint.id})"

    def clean(self):
        """파일 유효성 검사"""
        if self.size > self.MAX_FILE_SIZE:
            raise ValidationError({
                'size': f'파일 크기는 {self.MAX_FILE_SIZE / (1024*1024):.0f}MB 이하여야 합니다.'
            })

        if self.mime_type not in self.ALLOWED_MIME_TYPES:
            raise ValidationError({
                'mime_type': f'허용되지 않는 파일 형식입니다. 허용 형식: {", ".join(self.ALLOWED_MIME_TYPES)}'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
