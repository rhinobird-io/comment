#!/bin/bash

if [ -z "$1" ]; then
    echo Usage: $0 IMAGE
    exit 1
fi

docker run -d -t -v $PWD:/var/data $1 bash -c "\
    /usr/local/nginx/sbin/nginx -c /var/data/conf/nginx.conf && \
    /opt/redis-stable/src/redis-server /var/data/conf/redis.conf && \
    sleep $(date +%s)"
