ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update && apt install -y libreadline-dev

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz" -O python.tar.gz && tar xzf python.tar.gz --strip-components=1
RUN cd ./build && ./configure --with-ensurepip=install && make -j$(nproc) && make test && make install -j$(nproc) && cd ../ && rm -rf ./build
RUN python2.7 -m pip install -U pip==20.3.*

RUN python2.7 -m pip install install numpy scipy pycrypto whoosh bcrypt passlib

ENV COMMAND='python2.7 $SCRIPT'
