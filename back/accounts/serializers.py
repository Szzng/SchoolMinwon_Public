from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Child

User = get_user_model()


class ChildSerializer(serializers.ModelSerializer):
    """자녀(학생) 시리얼라이저"""

    class Meta:
        model = Child
        fields = ('id', 'name', 'grade', 'classroom')
        read_only_fields = ('id',)

    def validate_grade(self, value):
        """학년 유효성 검사"""
        if not (1 <= value <= 6):
            raise serializers.ValidationError("학년은 1~6 사이여야 합니다.")
        return value

    def validate_classroom(self, value):
        """반 유효성 검사"""
        if not (1 <= value <= 10):
            raise serializers.ValidationError("반은 1~10 사이여야 합니다.")
        return value


class UserSerializer(serializers.ModelSerializer):
    """사용자 시리얼라이저"""

    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    children = ChildSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'real_name',
            'user_type',
            'user_type_display',
            'phone',
            'school_name',
            'children'
        )
        read_only_fields = ('id', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    """사용자 등록 시리얼라이저"""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    user_type = serializers.ChoiceField(choices=['PARENT', 'TEACHER', 'ADMIN'])
    children = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        required=False,
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'password_confirm',
            'real_name',
            'user_type',
            'phone',
            'school_name',
            'children'
        )

    def validate(self, data):
        """비밀번호 확인 및 필수 필드 검증"""
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({'password': '비밀번호가 일치하지 않습니다.'})

        # 전체 사용자는 phone과 school_name이 필수
        if not data.get('phone'):
            raise serializers.ValidationError({'phone': '연락처는 필수입니다.'})
        if not data.get('school_name'):
            raise serializers.ValidationError({'school_name': '학교명은 필수입니다.'})

        # 학부모는 자녀 정보 필수
        user_type = data.get('user_type')
        children = self.context.get('request').data.get('children', []) if self.context.get('request') else data.get('children', [])

        if user_type == 'PARENT' and not children:
            raise serializers.ValidationError({'children': '학부모는 최소 1명 이상의 자녀 정보를 등록해야 합니다.'})

        return data

    def create(self, validated_data):
        """사용자 생성"""
        password = validated_data.pop('password')
        children = self.context.get('request').data.get('children', []) if self.context.get('request') else []
        validated_data.pop('children', None)

        user = User.objects.create_user(password=password, **validated_data)

        # 학부모인 경우 자녀 정보 추가
        if user.user_type == 'PARENT' and children:
            for child_data in children:
                Child.objects.create(
                    parent=user,
                    name=child_data.get('name'),
                    grade=int(child_data.get('grade', 1)),
                    classroom=int(child_data.get('classroom', 1))
                )

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """사용자 정보와 함께 토큰 반환"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # 커스텀 클레임 추가
        token['username'] = user.username
        token['user_type'] = user.user_type
        token['email'] = user.email
        token['real_name'] = user.real_name

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # 사용자 정보 추가
        data['user'] = UserSerializer(self.user).data

        return data
