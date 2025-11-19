from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

from .models import Child
from .serializers import UserSerializer, ChildSerializer, UserRegisterSerializer, CustomTokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """사용자 정보와 함께 토큰 반환"""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """사용자 ViewSet"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """사용자 자신의 정보만 조회 가능"""
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """현재 로그인한 사용자 정보"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """사용자 등록"""
        serializer = UserRegisterSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 토큰 생성
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """사용자 프로필 업데이트"""
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChildViewSet(viewsets.ModelViewSet):
    """자녀(학생) ViewSet"""

    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """현재 사용자의 자녀만 조회"""
        return Child.objects.filter(parent=self.request.user)

    def create(self, request, *args, **kwargs):
        """자녀 추가 (학부모만)"""
        if request.user.user_type != 'PARENT':
            return Response(
                {'detail': '학부모만 자녀를 등록할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        child = serializer.save(parent=request.user)

        return Response(ChildSerializer(child).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """자녀 정보 수정"""
        child = self.get_object()

        if child.parent != request.user and request.user.user_type != 'ADMIN':
            return Response(
                {'detail': '권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(child, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(ChildSerializer(child).data)

    def destroy(self, request, *args, **kwargs):
        """자녀 삭제"""
        child = self.get_object()

        if child.parent != request.user and request.user.user_type != 'ADMIN':
            return Response(
                {'detail': '권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        child.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def my_children(self, request):
        """현재 사용자의 모든 자녀"""
        children = self.get_queryset()
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)
