import serverless_wsgi
from app import create_app

flask_app = create_app()

def handler(event, context):
    return serverless_wsgi.handle_request(flask_app, event, context)
