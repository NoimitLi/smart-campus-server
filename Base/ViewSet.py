from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from django.db.models import Q, Model
from django.http.response import Http404
from Base.Pagination import CustomPagination
from Base.Response import APIResponse


class APIViewSet(ModelViewSet):
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'delete', 'put', 'head', 'options', 'patch']

    # throttle_classes = None # 限流
    # authentication_classes = None # 认证
    # permission_classes = None # 权限

    # 新增配置项，让子类可以更灵活地配置
    filter_fields = []  # 可过滤的字段列表
    search_fields = []  # 支持模糊搜索的字段列表
    exact_fields = []  # 需要精确匹配的字段列表

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params

        # 状态过滤
        status = query_params.get('status')
        if status and hasattr(queryset.model, 'status'):
            status_list = status.split(',')
            queryset = queryset.filter(status__in=status_list)

        # 构建查询条件
        query_conditions = Q()

        for field in self.get_custom_query_fields():
            # 模糊查询（支持通配符）
            if field.startswith('*') and field.endswith('*'):
                field_name = field[1:-1]
                search_value = query_params.get(field_name)
                if search_value:
                    query_conditions &= Q(**{f"{field_name}__icontains": search_value})
            # 精确查询
            else:
                value = query_params.get(field)
                if value:
                    query_conditions &= Q(**{field: value})

        # 处理配置的过滤字段
        for field in self.filter_fields:
            value = query_params.get(field)
            if value:
                query_conditions &= Q(**{field: value})

        # 处理模糊搜索字段
        for field in self.search_fields:
            value = query_params.get(field)
            if value:
                query_conditions &= Q(**{f"{field}__icontains": value})

        # 处理精确匹配字段
        for field in self.exact_fields:
            value = query_params.get(field)
            if value:
                query_conditions &= Q(**{field: value})

        if query_conditions:
            queryset = queryset.filter(query_conditions)

        return queryset

    def get_custom_query_fields(self):
        """
        获取自定义查询字段列表
        子类可以重写此方法来定义支持的查询字段
        """
        return []

    def list(self, request, *args, **kwargs):
        """对应 GET / - 获取所有数据"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return APIResponse.success(serializer.data)

        except Exception as e:
            # 可以根据异常类型返回不同的错误信息
            return APIResponse.fail(
                message=str(e),
                code=status.HTTP_400_BAD_REQUEST
            )

    def create(self, request, *args, **kwargs):
        """对应 POST / - 添加新数据"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                headers = self.get_success_headers(serializer.data)
                return APIResponse.success(
                    data=serializer.data,
                    message="创建成功",
                    code=status.HTTP_201_CREATED,
                    headers=headers
                )
            return APIResponse.fail(
                message="数据验证失败",
                errors=serializer.errors,
                code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return APIResponse.fail(
                message=f"创建失败: {str(e)}",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """对应 GET /{id} - 获取单个数据"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return APIResponse.success(serializer.data)
        except Http404:
            return APIResponse.fail(
                message="数据不存在",
                code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return APIResponse.fail(
                message=f"获取数据失败: {str(e)}",
                code=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, *args, **kwargs):
        """对应 PUT /{id} - 更新单个数据"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=partial
            )

            if serializer.is_valid():
                serializer.save()
                return APIResponse.success(
                    data=serializer.data,
                    message="更新成功"
                )

            return APIResponse.fail(
                message=serializer.errors,
                code=status.HTTP_400_BAD_REQUEST
            )
        except Http404:
            return APIResponse.fail(
                message="数据不存在",
                code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return APIResponse.fail(
                message=f"更新失败: {str(e)}",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def partial_update(self, request, *args, **kwargs):
        """对应 PATCH /{id} - 部分更新"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """对应 DELETE /{id} - 删除单个数据"""
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return APIResponse.success(message="删除成功")
        except Http404:
            return APIResponse.fail(
                message="数据不存在",
                code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return APIResponse.fail(
                message=f"删除失败: {str(e)}",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_destroy(self, instance):
        """重写删除方法，支持软删除"""
        if hasattr(instance, 'is_deleted'):
            # 软删除
            instance.is_deleted = True
            instance.save()
        elif hasattr(instance, 'status'):
            # 状态删除
            instance.status = 0
            instance.save()
        else:
            # 物理删除
            instance.delete()
