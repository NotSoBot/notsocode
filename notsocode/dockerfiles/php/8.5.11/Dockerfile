ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y pkg-config libxml2-dev libsqlite3-dev libssl-dev zlib1g-dev libcurl4-openssl-dev libonig-dev

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://www.php.net/distributions/php-8.5.11.tar.gz" -q -O php.tar.gz && tar xzf php.tar.gz --strip-components=1
RUN cd ./build && ./configure --with-openssl --with-zlib --with-curl --enable-mbstring --enable-bcmath && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

ENV COMMAND='php $SCRIPT'
