from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from authSystem.models import RoleModel, UserModel
from .models import DepartmentModel
from Base.Response import APIResponse
from Base.Pagination import CustomPagination
from .serializers import RoleSerializer, DepartmentSerializer, UserSerializer
from django.db import models


class BaseViewSet(viewsets.ViewSet):
    pass


class RoleViewSet(viewsets.ViewSet):
    """
    角色管理
    """
    # 分页
    pagination_class = CustomPagination

    def list(self, request):
        """对应 GET /role - 获取所有角色"""
        queryset = RoleModel.objects.all().order_by('id')  # 添加排序以避免分页警告
        # 获取分页实例
        paginator = self.pagination_class()
        # 对查询集进行分页
        page = paginator.paginate_queryset(queryset, request)
        if not page:
            return paginator.get_paginated_response(None)

        # 如果没有分页，返回全部
        serializer = RoleSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        """对应 POST /role - 添加新角色"""
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)
        return APIResponse(data=serializer.errors, msg='创建失败', status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        获取单个角色详情
        GET /role/:id
        """
        try:
            role = RoleModel.objects.get(pk=pk)
        except RoleModel.DoesNotExist:
            return APIResponse(msg='角色不存在', status=status.HTTP_404_NOT_FOUND)

        serializer = RoleSerializer(role)
        return APIResponse(serializer.data)

    def update(self, request, pk=None):
        """对应 PUT /role/:id - 更新角色信息"""
        try:
            role = RoleModel.objects.get(pk=pk)
        except RoleModel.DoesNotExist:
            return APIResponse(msg="角色不存在", status=status.HTTP_404_NOT_FOUND)

        # 非管理员不能修改管理员
        if request.role_id != 1 and role.id == 1:
            return APIResponse(msg="无权限修改管理员", status=status.HTTP_403_FORBIDDEN)

        serializer = RoleSerializer(role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)
        return APIResponse(data=serializer.errors, msg='修改失败', status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """对应 PATCH /role/:id - 更新角色状态"""
        if 'status' not in request.data:
            return APIResponse(msg='缺少状态字段', status=status.HTTP_400_BAD_REQUEST)
        try:
            role = RoleModel.objects.get(pk=pk)
        except RoleModel.DoesNotExist:
            return APIResponse(msg="角色不存在", status=status.HTTP_404_NOT_FOUND)
        # 非管理员不能修改管理员
        if request.role_id != 1 and role.id == 1:
            return APIResponse(msg="无权限修改管理员", status=status.HTTP_403_FORBIDDEN)
        if role.id == 1:
            return APIResponse(msg="管理员不能禁用", status=status.HTTP_403_FORBIDDEN)
        # 只更新状态字段
        # partial=True 将所有反序列化字段设置为False
        serializer = RoleSerializer(role, data={'status': request.data.get('status')}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)
        return APIResponse(data=serializer.errors, msg='修改失败', status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        对应 DELETE /role/:id - 删除角色
        """
        try:
            role = RoleModel.objects.get(pk=pk)
        except RoleModel.DoesNotExist:
            return APIResponse(msg="角色不存在", status=status.HTTP_404_NOT_FOUND)
        # 判断当前登陆的用户权限，非管理员不能删除超级管理员
        if request.role_id != 1 and role.id == 1:
            return APIResponse(msg="非管理员不能删除超级管理员", status=status.HTTP_403_FORBIDDEN)
        if role.id == 1:
            return APIResponse(msg="超级管理员不能删除", status=status.HTTP_403_FORBIDDEN)
        # 删除角色
        role.delete()
        return APIResponse(msg='删除成功')


class DepartmentViewSet(viewsets.ViewSet):
    """
    部门管理
    """
    # 分页
    pagination_class = CustomPagination

    def list(self, request):
        """对应 GET /department - 获取所有部门"""
        # queryset = DepartmentModel.objects.all().order_by('id')  # 添加排序以避免分页警告
        queryset = DepartmentModel.objects.filter(parent__isnull=True).order_by('id')
        # 获取分页实例
        paginator = self.pagination_class()
        # 对查询集进行分页
        page = paginator.paginate_queryset(queryset, request)
        if not page:
            return paginator.get_paginated_response(None)

        # 如果没有分页，返回全部
        serializer = DepartmentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        """对应 POST /department - 添加新部门"""
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)
        return APIResponse(data=serializer.errors, msg='创建失败', status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        获取单个部门详情
        GET /department/:id
        """
        try:
            dept = DepartmentModel.objects.get(pk=pk)
        except DepartmentModel.DoesNotExist:
            return APIResponse(msg='部门不存在', status=status.HTTP_404_NOT_FOUND)

        serializer = DepartmentSerializer(dept)
        return APIResponse(serializer.data)

    def update(self, request, pk=None):
        """对应 PUT /department/:id - 更新部门信息"""
        try:
            dept = DepartmentModel.objects.get(pk=pk)
        except DepartmentModel.DoesNotExist:
            return APIResponse(msg="部门不存在", status=status.HTTP_404_NOT_FOUND)

        serializer = DepartmentSerializer(dept, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)
        return APIResponse(data=serializer.errors, msg='修改失败', status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """对应 PATCH /department/:id - 更新部门状态"""
        if 'status' not in request.data:
            return APIResponse(msg='缺少状态字段', status=status.HTTP_400_BAD_REQUEST)
        try:
            dept = DepartmentModel.objects.get(pk=pk)
        except DepartmentModel.DoesNotExist:
            return APIResponse(msg="部门不存在", status=status.HTTP_404_NOT_FOUND)

        # 只更新状态字段
        # partial=True 将所有反序列化字段设置为False
        serializer = DepartmentSerializer(dept, data={'status': request.data.get('status')}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)
        return APIResponse(data=serializer.errors, msg='修改失败', status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        对应 DELETE /department/:id - 删除部门
        """
        try:
            dept = DepartmentModel.objects.get(pk=pk)
        except DepartmentModel.DoesNotExist:
            return APIResponse(msg="部门不存在", status=status.HTTP_404_NOT_FOUND)

        # 删除部门
        dept.delete()
        return APIResponse(msg='删除成功')


class UserViewSet(viewsets.ViewSet):
    """
    用户管理
    """
    # 分页
    pagination_class = CustomPagination
    # 文件解析器
    parser_classes = [MultiPartParser, FormParser]

    # 认证
    # authentication_classes =
    # 授权
    # permission_classes =
    # 限流
    # throttle_classes =
    def list(self, request):
        """对应 GET /user - 获取所有用户，包含搜索"""
        username = request.query_params.get('username')
        phone = request.query_params.get('phone')
        user_status = request.query_params.get('status')
        department = request.query_params.get('department')

        queryset = UserModel.objects.all().order_by('id')  # 添加排序以避免分页警告
        # 应用过滤条件
        if username:
            queryset = queryset.filter(username__icontains=username)
        if phone:
            queryset = queryset.filter(phone__icontains=phone)
        if user_status:
            try:
                status_bool = user_status.lower() == 'true'
                queryset = queryset.filter(status=status_bool)
            except ValueError:
                pass
        if department:
            queryset = queryset.filter(models.Q(department_relations__department__id=department))

        # 获取分页实例
        paginator = self.pagination_class()
        # 对查询集进行分页
        page = paginator.paginate_queryset(queryset, request)
        if not page:
            return paginator.get_paginated_response(None)

        # 如果没有分页，返回全部
        serializer = UserSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        """对应 POST /user - 添加新用户"""
        if request.role_id != 1:
            return APIResponse(msg='非管理员无权创建用户', status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)

        return APIResponse(data=serializer.errors, msg='创建失败', status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        获取单个用户详情
        GET /user/:id
        """
        if request.role_id != 1:
            return APIResponse(msg='非管理员无权查询用户', status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = UserModel.objects.get(pk=pk)
        except UserModel.DoesNotExist:
            return APIResponse(msg='用户不存在', status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, context={'request': request})
        return APIResponse(serializer.data)

    def update(self, request, pk=None):
        """对应 PUT /user/:id - 更新用户信息,包括角色与部门"""
        if request.role_id != 1:
            return APIResponse(msg='非管理员无权修改用户', status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = UserModel.objects.get(pk=pk)
        except UserModel.DoesNotExist:
            return APIResponse(msg="用户不存在", status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)
        return APIResponse(data=serializer.errors, msg='修改失败', status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    # detail为True代表处理单个用户，pk从/user/20/status/获取。如果改为False，代表处理批量操作，pk从/user/status/?ids=1,2,3获取
    def status(self, request, pk=None):
        """对应 PUT /user/:id/status/ - 更新用户状态"""
        if 'status' not in request.data:
            return APIResponse(msg='缺少状态字段', status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserModel.objects.get(pk=pk)
        except UserModel.DoesNotExist:
            return APIResponse(msg="用户不存在", status=status.HTTP_404_NOT_FOUND)
        # 非管理员不能修改管理员
        if request.role_id != 1:
            return APIResponse(msg="无权限修改管理员", status=status.HTTP_403_FORBIDDEN)
        # 只更新状态字段
        # partial=True 将所有反序列化字段设置为False
        serializer = UserSerializer(user, data={'status': request.data.get('status')}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)
        return APIResponse(data=serializer.errors, msg='修改失败', status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def password(self, request, pk=None):
        """对应 PUT /user/:id/password/ - 更新用户密码"""
        if 'password' not in request.data:
            return APIResponse(msg='缺少密码字段', status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserModel.objects.get(pk=pk)
        except UserModel.DoesNotExist:
            return APIResponse(msg="用户不存在", status=status.HTTP_404_NOT_FOUND)
        # 只更新状态字段
        # partial=True 将所有反序列化字段设置为False
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(serializer.data)
        return APIResponse(data=serializer.errors, msg='修改失败', status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def avatar(self, request, pk=None):
        """头像上传接口"""
        try:
            user = UserModel.objects.get(pk=pk)
        except UserModel.DoesNotExist:
            return APIResponse(msg="用户不存在", status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})

        # 检查是否有文件被上传
        if 'avatar' not in request.FILES:
            return APIResponse(
                msg='请选择要上传的头像文件',
                status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():
            serializer.save()
            # 返回完整的用户信息（包含新头像URL）
            return APIResponse(
                data=serializer.data,
                msg='头像上传成功'
            )

        return APIResponse(
            msg='头像上传失败',
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, pk=None):
        """
        对应 DELETE /user/:id - 删除用户
        """
        try:
            user = UserModel.objects.get(pk=pk)
        except UserModel.DoesNotExist:
            return APIResponse(msg="用户不存在", status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return APIResponse(msg='删除成功')
