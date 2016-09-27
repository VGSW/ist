from bottle import route, run, template, response
from main import Lemmy

@route ('/ist/<sort_col>/<sort>')
def index_ist (sort_col, sort):
    return Lemmy (sort_col = sort_col, sort = sort).table()

@route ('/')
def index ():
    response.status = 303
    response.set_header('Location', '/ist/id/asc')

run (host = 'localhost', port = 8080, reloader = True)
