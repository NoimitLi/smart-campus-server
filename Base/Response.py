from rest_framework import status as http_status
from rest_framework.response import Response


class APIResponse(Response):
    def __init__(self, data=None, message='success', status=http_status.HTTP_200_OK, **kwargs):
        response = {
            'code': status,
            'message': message,
        }
        if data:
            response['data'] = data
        super().__init__(response, status=status, **kwargs)

    @classmethod
    def success(cls, data=None, message=None, **kwargs):
        return cls(data=data, message=message, **kwargs)

    @classmethod
    def fail(cls, message=None, code=http_status.HTTP_400_BAD_REQUEST, **kwargs):
        return cls(message=message, status=code, **kwargs)
