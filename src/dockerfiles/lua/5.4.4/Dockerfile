ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update && apt install -y libreadline-dev

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://www.lua.org/ftp/lua-5.4.4.tar.gz" -O lua.tar.gz && tar xzf lua.tar.gz --strip-components=1
RUN cd ./build && make -j$(nproc) && make test && make install -j$(nproc) && cd ../ && rm -rf ./build

ENV COMMAND='lua $SCRIPT'
