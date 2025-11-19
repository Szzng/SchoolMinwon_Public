from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class UserType(models.TextChoices):
        PARENT = "PARENT", "학부모"
        TEACHER = "TEACHER", "교사"
        ADMIN = "ADMIN", "관리자"

    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.PARENT,
    )

    real_name = models.CharField("실명", max_length=100, blank=True)
    phone = models.CharField("연락처", max_length=20, blank=False)
    school_name = models.CharField("소속 학교", max_length=100, blank=False)

    # AbstractUser의 first_name, last_name 필드 제거
    first_name = None
    last_name = None

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    @property
    def is_parent(self):
        return self.user_type == self.UserType.PARENT

    @property
    def is_teacher(self):
        return self.user_type == self.UserType.TEACHER


class Child(models.Model):
    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="children",
        limit_choices_to={"user_type": User.UserType.PARENT},
    )

    name = models.CharField("자녀 이름", max_length=50)
    grade = models.IntegerField("학년")
    classroom = models.IntegerField("반")

    def __str__(self):
        return f"{self.parent.username}의 자녀: {self.name}({self.grade} {self.classroom})"
