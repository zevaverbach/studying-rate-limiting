# Purpose

This repository contains my implementations and explorations of rate limiting, drawn initially from the book _System Design Interview_.

I'm embarking on this in order to get a great software engineering (probably back-end) job, and at the moment I have Happy Scribe in mind since I have an interview with them on August 24th, directly after our family vacation in Greece.

Over a year ago (early 2022) I did a job search, and some of the interview processes ended right before or after the system design phase, so it's obviously something I need in my portfolio to truly be considered for senior dev roles. While I'd love to get a job as a junior or mid-level, my salary requirements and age (45) push me towards senior. That, and maybe the fact that I'm a decent programmer by now.

# TODO

- [ ] implement token bucket
  - [ ] in-app
    - [x] in-memory, lazy refill
    - [ ] redis, process to refill
- [ ] implement leaky bucket
  - in-app
    - [x] redis
    - [ ] redis cluster
    - [ ] Flask middleware - https://flask.palletsprojects.com/en/2.1.x/quickstart/#hooking-in-wsgi-middleware
  - [ ] NGINX - https://leandromoreira.com/2019/01/25/how-to-build-a-distributed-throttling-system-with-nginx-lua-redis/
              - https://www.nginx.com/blog/rate-limiting-nginx/
  - [ ] AWS API Gateway
  - [ ] HAProxy Stick Tables  - https://www.haproxy.com/blog/introduction-to-haproxy-stick-tables
  - [ ] Cloudflare (Spectrum?)
- [ ] implement expiring tokens
- [ ] implement fixed window counter
- [ ] implement sliding window log
- [ ] implement sliding window counter 
- [ ] use session IDs or API keys instead of IP address
- [ ] set headers appropriately in each case: https://www.ietf.org/archive/id/draft-polli-ratelimit-headers-02.html#name-ratelimit-headers-currently
- [ ] implement different rate limiting for each endpoint, using a `cost` variable for a given task