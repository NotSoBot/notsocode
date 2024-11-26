ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y zlib1g zlib1g-dev libssl-dev

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz" -q -O python.tar.gz && tar xzf python.tar.gz --strip-components=1
RUN cd ./build && ./configure --with-ensurepip=install && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

RUN python2.7 -m pip install --upgrade pip
RUN python2.7 -m pip install numpy scipy pycrypto whoosh bcrypt passlib
RUN python2.7 -m pip install requests urllib3

ENV COMMAND='python2.7 $SCRIPT'
