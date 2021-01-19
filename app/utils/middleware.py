from werkzeug.wrappers import Request, Response, ResponseStream
import jwt
from app.utils.db import mongoClient

class middleware():
    '''
    Simple WSGI middleware
    '''

    def __init__(self, app):
        self.app = app
        self.authClient = mongoClient.users["authStore"]

    def __call__(self, environ, start_response):
        request = Request(environ)
        authHeader = request.headers.get('Authorization')
        if authHeader == None:
            res = Response(u'Authorization failed', mimetype= 'text/plain', status=401)
            return res(environ, start_response)     

        token = authHeader.split("Bearer ")[1]
        tokenDecoded = jwt.decode(token, "secret", algorithms=["HS256"])

        authRecord = self.authClient.find_one({'token': token})
        if authRecord == None:
            res = Response(u'Authorization failed', mimetype= 'text/plain', status=401)
            return res(environ, start_response)     


        # these are hardcoded for demonstration
        # verify the username and password from some database or env config variable
        return self.app(environ, start_response)