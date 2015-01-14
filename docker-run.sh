#!/bin/bash

docker -v ./:/var/data comment bash -c \
    "/usr/local/nginx/sbin/nginx -c /var/data/conf/nginx.conf && \
    /opt/redis-stable/src/redis-server /var/data/conf/redis.conf"
