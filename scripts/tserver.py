from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from landrecords.app import app

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(5004)
IOLoop.instance().start()
