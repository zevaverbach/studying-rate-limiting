import flask as f

from . import algos


application = f.Flask(__name__)


increment_requests_func = algos.token_bucket


@application.before_request
def before_request():
    ip = f.request.remote_addr
    try:
        increment_requests_func(ip)
    except algos.TooManyRequests:
        return f.abort(429)

@application.route('/')
def home():
    return '<!doctype html><title>Hello</title><h1>Hello</h1>'