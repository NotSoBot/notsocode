ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y zlib1g zlib1g-dev libssl-dev libffi-dev

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz" -q -O python.tar.gz && tar xzf python.tar.gz --strip-components=1
RUN cd ./build && ./configure --with-ensurepip=install && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

RUN python3.12 -m pip install --upgrade pip
RUN python3.12 -m pip uninstall -y setuptools && python3.12 -m pip install setuptools
RUN python3.12 -m pip install numpy scipy pandas whoosh bcrypt passlib sympy
ADD requirements.txt ./
RUN python3.12 -m pip install -r requirements.txt

ENV COMMAND='python3.12 $SCRIPT'
