# Copyright (c) 2025 Stephen G. Pope
# Lambda handler for No-Code Architects Toolkit

import json
import base64
from app import create_app
from werkzeug.serving import WSGIRequestHandler

# Create Flask app instance
flask_app = create_app()

def lambda_handler(event, context):
    """
    AWS Lambda handler for Flask application
    Converts Lambda event to WSGI environ and back
    """
    
    # Handle warmup pings
    if event.get('source') == 'serverless-plugin-warmup':
        return {'statusCode': 200, 'body': 'Lambda is warm'}
    
    # Convert Lambda event to WSGI environ
    environ = convert_event_to_environ(event, context)
    
    # Create a response accumulator
    response = {'statusCode': 200, 'headers': {}, 'body': ''}
    
    def start_response(status, headers, exc_info=None):
        response['statusCode'] = int(status.split(' ', 1)[0])
        for header in headers:
            response['headers'][header[0]] = header[1]
    
    # Call Flask app
    app_iter = flask_app.wsgi_app(environ, start_response)
    response['body'] = ''.join(app_iter)
    
    # Handle binary content
    if response['headers'].get('Content-Type', '').startswith(('image/', 'video/', 'audio/', 'application/octet-stream')):
        response['body'] = base64.b64encode(response['body'].encode() if isinstance(response['body'], str) else response['body']).decode()
        response['isBase64Encoded'] = True
    
    return response

def convert_event_to_environ(event, context):
    """
    Convert AWS Lambda event to WSGI environ dict
    """
    # Extract information from the event
    http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
    path = event.get('path', event.get('rawPath', '/'))
    query_string = event.get('queryStringParameters') or {}
    headers = event.get('headers') or {}
    body = event.get('body', '')
    
    # Handle API Gateway v2 format
    if 'requestContext' in event and 'http' in event['requestContext']:
        http_method = event['requestContext']['http']['method']
        path = event['requestContext']['http']['path']
        query_string = event.get('queryStringParameters') or {}
    
    # Build query string
    query_string_encoded = '&'.join([f"{k}={v}" for k, v in query_string.items()]) if query_string else ''
    
    # Handle base64 encoded body
    if event.get('isBase64Encoded', False):
        body = base64.b64decode(body)
    elif isinstance(body, str):
        body = body.encode('utf-8')
    
    # Build WSGI environ
    environ = {
        'REQUEST_METHOD': http_method,
        'SCRIPT_NAME': '',
        'PATH_INFO': path,
        'QUERY_STRING': query_string_encoded,
        'CONTENT_TYPE': headers.get('content-type', headers.get('Content-Type', '')),
        'CONTENT_LENGTH': str(len(body)) if body else '0',
        'SERVER_NAME': headers.get('host', headers.get('Host', 'localhost')),
        'SERVER_PORT': '443' if headers.get('x-forwarded-proto') == 'https' else '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': headers.get('x-forwarded-proto', 'https'),
        'wsgi.input': BytesIOWrapper(body),
        'wsgi.errors': None,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
        'awslambda.event': event,
        'awslambda.context': context,
    }
    
    # Add headers to environ
    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key}'] = value
    
    return environ

class BytesIOWrapper:
    """Wrapper to make bytes behave like a file object for WSGI"""
    def __init__(self, data):
        self.data = data if isinstance(data, bytes) else data.encode('utf-8')
        self.pos = 0
    
    def read(self, size=-1):
        if size == -1:
            result = self.data[self.pos:]
            self.pos = len(self.data)
        else:
            result = self.data[self.pos:self.pos + size]
            self.pos += len(result)
        return result
    
    def readline(self, size=-1):
        # Find newline
        newline_pos = self.data.find(b'\n', self.pos)
        if newline_pos == -1:
            return self.read(size)
        else:
            end_pos = newline_pos + 1
            if size != -1 and end_pos - self.pos > size:
                end_pos = self.pos + size
            result = self.data[self.pos:end_pos]
            self.pos = end_pos
            return result
    
    def readlines(self):
        lines = []
        while True:
            line = self.readline()
            if not line:
                break
            lines.append(line)
        return lines