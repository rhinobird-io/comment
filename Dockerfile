FROM debian:8.0
MAINTAINER wizawu@gmail.com

RUN apt-get update

# Install Redis
RUN apt-get install -y redis-server

# Install Nginx
RUN apt-get install -y nginx

# Install Gevent
RUN apt-get install -y python3 python-gevent

apt-get clean

EXPOSE 80
