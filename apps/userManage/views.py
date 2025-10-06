from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from apps.oauth.models import RoleModel, UserModel
from .models import DepartmentModel
from Base.Response import APIResponse
from Base.Pagination import CustomPagination
from Base.ViewSet import APIViewSet
from .serializers import RoleSerializer, DepartmentSerializer, UserSerializer
from django.db import models


class BaseViewSet(viewsets.ViewSet):
    pass


class RoleViewSet(APIViewSet):
    """
    角色管理
    """
    queryset = RoleModel.objects.all()
    serializer_class = RoleSerializer

    def update(self, request, pk=None, **kwargs):
        """对应 PUT /role/:id - 更新角色信息"""
        try:
            role = RoleModel.objects.get(pk=pk)
            # 非管理员不能修改管理员
            if request.role_id != 1 and role.id == 1:
                return APIResponse(message="无权限修改管理员", status=status.HTTP_403_FORBIDDEN)
        except RoleModel.DoesNotExist as e:
            return APIResponse(message="角色不存在", status=status.HTTP_404_NOT_FOUND)

        return super().update(request, **kwargs)

    def partial_update(self, request, pk=None, **kwargs):
        """对应 PATCH /role/:id - 更新角色状态"""
        if 'status' not in request.data:
            return APIResponse(message='缺少状态字段', status=status.HTTP_400_BAD_REQUEST)
        try:
            role = RoleModel.objects.get(pk=pk)
        except RoleModel.DoesNotExist:
            return APIResponse(message="角色不存在", status=status.HTTP_404_NOT_FOUND)
        # 非管理员不能修改管理员
        if request.role_id != 1 and role.id == 1:
            return APIResponse(message="无权限修改管理员", status=status.HTTP_403_FORBIDDEN)
        if role.id == 1:
            return APIResponse(message="管理员不能禁用", status=status.HTTP_403_FORBIDDEN)
        # 只更新状态字段
        # partial=True 将所有反序列化字段设置为False
        serializer = RoleSerializer(role, data={'status': request.data.get('status')}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)
        return APIResponse(data=serializer.errors, message='修改失败', status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, **kwargs):
        """
        对应 DELETE /role/:id - 删除角色
        """
        try:
            role = RoleModel.objects.get(pk=pk)
        except RoleModel.DoesNotExist:
            return APIResponse(message="角色不存在", status=status.HTTP_404_NOT_FOUND)
        # 判断当前登陆的用户权限，非管理员不能删除超级管理员
        if request.role_id != 1 and role.id == 1:
            return APIResponse(message="非管理员不能删除超级管理员", status=status.HTTP_403_FORBIDDEN)
        if role.id == 1:
            return APIResponse(message="超级管理员不能删除", status=status.HTTP_403_FORBIDDEN)
        # 删除角色
        role.delete()
        return APIResponse(message='删除成功')


class DepartmentViewSet(APIViewSet):
    """
    部门管理
    """
    queryset = DepartmentModel.objects.all()
    serializer_class = DepartmentSerializer

    def partial_update(self, request, pk=None, **kwargs):
        """对应 PATCH /department/:id - 更新部门状态"""
        if 'status' not in request.data:
            return APIResponse(message='缺少状态字段', status=status.HTTP_400_BAD_REQUEST)
        try:
            dept = DepartmentModel.objects.get(pk=pk)
        except DepartmentModel.DoesNotExist:
            return APIResponse(message="部门不存在", status=status.HTTP_404_NOT_FOUND)

        # 只更新状态字段
        # partial=True 将所有反序列化字段设置为False
        serializer = DepartmentSerializer(dept, data={'status': request.data.get('status')}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)
        return APIResponse(data=serializer.errors, message='修改失败', status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(APIViewSet):
    """
    用户管理
    """
    # 文件解析器
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer

    search_fields = ['username', 'phone']
    exact_fields = ['department']

    # def get_custom_query_fields(self):
    #     return ['*username*', '*phone*', 'department']

    def create(self, request, **kwargs):
        """对应 POST /user - 添加新用户"""
        if request.role_id != 1:
            return APIResponse(message='非管理员无权创建用户', status=status.HTTP_401_UNAUTHORIZED)

        return super().create(request, **kwargs)

    def retrieve(self, request, **kwargs):
        """
        获取单个用户详情
        GET /user/:id
        """
        if request.role_id != 1:
            return APIResponse(message='非管理员无权查询用户', status=status.HTTP_401_UNAUTHORIZED)
        return super().retrieve(request, **kwargs)

    def update(self, request, **kwargs):
        """对应 PUT /user/:id - 更新用户信息,包括角色与部门"""
        if request.role_id != 1:
            return APIResponse(message='非管理员无权修改用户', status=status.HTTP_401_UNAUTHORIZED)
        return super().update(request, **kwargs)

    @action(detail=True, methods=['put'])
    # detail为True代表处理单个用户，pk从/user/20/status/获取。如果改为False，代表处理批量操作，pk从/user/status/?ids=1,2,3获取
    def status(self, request, pk=None):
        """对应 PUT /user/:id/status/ - 更新用户状态"""
        if 'status' not in request.data:
            return APIResponse(message='缺少状态字段', status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserModel.objects.get(pk=pk)
        except UserModel.DoesNotExist:
            return APIResponse(message="用户不存在", status=status.HTTP_404_NOT_FOUND)
        # 非管理员不能修改管理员
        if request.role_id != 1:
            return APIResponse(message="无权限修改管理员", status=status.HTTP_403_FORBIDDEN)
        # 只更新状态字段
        # partial=True 将所有反序列化字段设置为False
        serializer = UserSerializer(user, data={'status': request.data.get('status')}, partial=True,
                                    context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)
        return APIResponse(data=serializer.errors, message='修改失败', status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def password(self, request, pk=None):
        """对应 PUT /user/:id/password/ - 更新用户密码"""
        if 'password' not in request.data:
            return APIResponse(message='缺少密码字段', status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserModel.objects.get(pk=pk)
        except UserModel.DoesNotExist:
            return APIResponse(message="用户不存在", status=status.HTTP_404_NOT_FOUND)
        # 只更新状态字段
        # partial=True 将所有反序列化字段设置为False
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)
        return APIResponse(data=serializer.errors, message='修改失败', status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def avatar(self, request, pk=None):
        """头像上传接口"""
        try:
            user = UserModel.objects.get(pk=pk)
        except UserModel.DoesNotExist:
            return APIResponse(message="用户不存在", status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})

        # 检查是否有文件被上传
        if 'avatar' not in request.FILES:
            return APIResponse(
                message='请选择要上传的头像文件',
                status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():
            serializer.save()
            # 返回完整的用户信息（包含新头像URL）
            return APIResponse(
                data=serializer.data,
                message='头像上传成功'
            )

        return APIResponse(
            message='头像上传失败',
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
