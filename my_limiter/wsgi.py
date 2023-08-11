"""
TODO: implement leaky bucket
  - in-app
    - [x] in-memory
    - [ ] redis
    - [ ] redis cluster
    - [ ] Flask middleware - https://flask.palletsprojects.com/en/2.1.x/quickstart/#hooking-in-wsgi-middleware
  - [ ] NGINX - https://leandromoreira.com/2019/01/25/how-to-build-a-distributed-throttling-system-with-nginx-lua-redis/
              - https://www.nginx.com/blog/rate-limiting-nginx/
  - [ ] AWS API Gateway
  - [ ] HAProxy Stick Tables  - https://www.haproxy.com/blog/introduction-to-haproxy-stick-tables
  - [ ] Cloudflare (Spectrum?)
TODO: implement fixed window counter
TODO: implement sliding window log
TODO: implement sliding window counter 
TODO: use session IDs instead of IP address
"""
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