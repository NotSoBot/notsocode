ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y libedit-dev

WORKDIR /tmp
RUN mkdir -p build && cd ./build && wget "https://github.com/fabianishere/brainfuck/archive/refs/tags/2.7.3.tar.gz" -q -O brainfuck.tar.gz && tar xvfz brainfuck.tar.gz --strip-components=1
RUN cd ./build && cmake . -DCMAKE_INSTALL_PREFIX=/usr/local && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

ENV COMMAND='brainfuck $SCRIPT'
