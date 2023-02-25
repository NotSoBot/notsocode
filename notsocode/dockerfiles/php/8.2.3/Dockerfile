ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt install -y pkg-config libxml2-dev libsqlite3-dev

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://www.php.net/distributions/php-8.2.3.tar.gz" -q -O php.tar.gz && tar xzf php.tar.gz --strip-components=1
RUN cd ./build && ./configure && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

ENV COMMAND='php $SCRIPT'
