from rest_framework import viewsets, status
from authSystem.models import RoleModel
from .models import DepartmentModel
from Base.Response import APIResponse
from Base.Pagination import CustomPagination
from .serializers import RoleSerializer, DepartmentSerializer


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
