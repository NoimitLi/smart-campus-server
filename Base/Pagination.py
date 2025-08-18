from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from Base.Response import APIResponse


class CustomPagination(PageNumberPagination):
    page_query_param = 'page'  # 允许客户端通过参数指定第几页
    page_size = 10  # 默认每页数量
    page_size_query_param = 'page_size'  # 允许客户端通过参数指定每页数量
    max_page_size = 20  # 每页最大数量限制

    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view)
        except Exception as e:
            # 捕获所有分页错误,阻止自带的返回NOTFOUND错误
            return None

    def get_paginated_response(self, data):
        """重写响应格式"""
        if data is None:
            return APIResponse(data=None, code=404, msg='数据不存在', status=status.HTTP_404_NOT_FOUND)
            # return APIResponse(data=None, code=400, msg="请求的页码不存在或无效", status=status.HTTP_400_BAD_REQUEST)
        return APIResponse({
            'total': self.page.paginator.count,
            'page_num': self.page.number,
            'page_size': self.page_size,
            'list': data
        })
