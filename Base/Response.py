from rest_framework.response import Response


class APIResponse(Response):
    def __init__(self, data=None, code=200, msg='success', **kwargs):
        if 'status' in kwargs:
            code = kwargs.get('status')
            if kwargs.get('status') == 404 and msg == 'success':
                msg = 'Not Found'

        response_data = {
            'code': code,
            'message': msg,
        }
        if data:
            # if isinstance(data, dict):
            #     response_data.update(data)
            # else:
            response_data['data'] = data
        super().__init__(data=response_data, **kwargs)
