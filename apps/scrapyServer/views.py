from django.shortcuts import render
from rest_framework import viewsets
from Base.Response import APIResponse
from django.views import View
from django.http.response import JsonResponse


# Create your views here.
class TestView(View):
    def get(self, request, id=None, *args, **kwargs):
        print(f'爬虫访问测试 ==> {id}')
        return JsonResponse({
            'code': 200,
            'msg': 'success',
        })
