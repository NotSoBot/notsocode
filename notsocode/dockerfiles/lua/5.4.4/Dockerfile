ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y libreadline-dev

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://www.lua.org/ftp/lua-5.4.4.tar.gz" -q -O lua.tar.gz && tar xzf lua.tar.gz --strip-components=1
RUN cd ./build && make -j$(nproc) && make test && make install -j$(nproc) && cd ../ && rm -rf ./build

RUN mkdir -p /usr/local/share/lua/5.4/ && wget https://raw.githubusercontent.com/LuaDist/dkjson/master/dkjson.lua -P /usr/local/share/lua/5.4

ENV COMMAND='lua $SCRIPT'
