# See https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/views.html#custom-exception-views
from pyramid.view import exception_view_config
from pyramid.response import Response
import json
import os
import ipdb
import requests
import traceback


# Only use this view in production environment
# because in development it is more straighforward
# to see the stacktrace directly in the STDOUT
# from the server
if os.environ.get('POST_TO_SLACK'):

    @exception_view_config(Exception)
    def any_unhandled_exception(exc, request):

        url = 'https://hooks.slack.com/services/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'

        exception_name = exc.__class__.__name__

        frame_summaries = traceback.extract_tb(exc.__traceback__)
        traceback_string = '\n'.join(traceback.format_list(frame_summaries))

        path   = request.environ.get('PATH_INFO')
        method = request.environ.get('REQUEST_METHOD')

        # Asterisks are like <b></b>
        text = f'*{exception_name} @ {method} {path}*\n\n{traceback_string}'

        payload = {'text': text,
                   'username': 'StethoscopeBot',
                   'icon_emoji': ':ghost:'}

        requests.post(url, json=payload, timeout=1)

        return Response(status_int=500, 
                        content_type=request.content_type,
                        json_body=dict(error='Internal Server Error'))
