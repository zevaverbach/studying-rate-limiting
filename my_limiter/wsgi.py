"""
TODO: implement token bucket
  - [ ] in-app
    - [x] in-memory
    - [ ] redis
TODO: implement leaky bucket
  - in-app
    - [ ] redis
    - [ ] redis cluster
    - [ ] Flask middleware - https://flask.palletsprojects.com/en/2.1.x/quickstart/#hooking-in-wsgi-middleware
  - [ ] NGINX - https://leandromoreira.com/2019/01/25/how-to-build-a-distributed-throttling-system-with-nginx-lua-redis/
              - https://www.nginx.com/blog/rate-limiting-nginx/
  - [ ] AWS API Gateway
  - [ ] HAProxy Stick Tables  - https://www.haproxy.com/blog/introduction-to-haproxy-stick-tables
  - [ ] Cloudflare (Spectrum?)
TODO: implement expiring tokens
TODO: implement fixed window counter
TODO: implement sliding window log
TODO: implement sliding window counter 
TODO: use session IDs or API keys instead of IP address
TODO: set headers appropriately in each case: https://www.ietf.org/archive/id/draft-polli-ratelimit-headers-02.html#name-ratelimit-headers-currently
TODO: implement different rate limiting for each endpoint, using a `cost` variable for a given task
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