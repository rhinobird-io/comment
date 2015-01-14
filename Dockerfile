FROM debian:8.0
MAINTAINER wizawu@gmail.com

RUN apt-get update
RUN apt-get install -y build-essential

# Install Redis
RUN apt-get install -y redis-server

# Install Nginx with Push Stream Module
WORKDIR /opt

RUN wget http://nginx.org/download/nginx-1.6.2.tar.gz
RUN wget https://codeload.github.com/wandenberg/nginx-push-stream-module/zip/0.4.1
RUN tar xf nginx-*.tar.gz
RUN unzip nginx-push-stream-module-*.zip

WORKDIR ./nginx-1.6.2
RUN ./configure --add-module=../nginx-push-stream-module-0.4.1
RUN make && make install

COPY ./nginx.conf /usr/local/nginx/conf/nginx.conf
RUN /usr/local/nginx/sbin/nginx

# Install Gevent
RUN apt-get install -y python3 python-gevent

apt-get clean

EXPOSE 80
