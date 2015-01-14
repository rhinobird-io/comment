#!/bin/bash

if [ -n $1 ]; then
    echo Usage: $0 IMAGE
    exit 1
fi

docker -d -t -v .:/var/data $1 bash -c "\
    /usr/local/nginx/sbin/nginx -c /var/data/conf/nginx.conf && \
    /opt/redis-stable/src/redis-server /var/data/conf/redis.conf"
