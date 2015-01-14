FROM debian:8.0
MAINTAINER wizawu@gmail.com

RUN apt-get update
RUN apt-get install -y build-essential wget tar unzip

# Install Redis
WORKDIR /opt
RUN wget http://download.redis.io/redis-stable.tar.gz
RUN tar xf redis-stable.tar.gz

WORKDIR ./redis-stable
RUN make MALLOC=libc

# Install Nginx with Push Stream Module
WORKDIR /opt
RUN wget http://nginx.org/download/nginx-1.6.2.tar.gz
RUN wget https://codeload.github.com/wandenberg/nginx-push-stream-module/zip/0.4.1 -O npsm.zip
RUN tar xf nginx-*.tar.gz
RUN unzip npsm.zip

WORKDIR ./nginx-1.6.2
RUN apt-get install -y libpcre3-dev zlib1g-dev libssl-dev
RUN ./configure --add-module=../nginx-push-stream-module-0.4.1
RUN make && make install

# Install CherryPy
RUN apt-get install -y python3 python3-cherrypy3

# Clean
WORKDIR /opt
RUN rm *.tar.gz *.zip
apt-get clean

EXPOSE 80 6379 9080
