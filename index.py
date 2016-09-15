from bottle import route, run, template
from main import Lemmy

@route ('/ist/<sort_col>/<sort>')
def index_ist (sort_col, sort):
    return Lemmy (sort_col = sort_col, sort = sort).table()

run (host = 'localhost', port = 8080, reloader = True)
