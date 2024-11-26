ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y zlib1g zlib1g-dev libssl-dev libffi-dev

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz" -q -O python.tar.gz && tar xzf python.tar.gz --strip-components=1
RUN cd ./build && ./configure --with-ensurepip=install && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

RUN apt install -y libsqlite3-dev

RUN python3.9 -m pip install --upgrade pip
RUN python3.9 -m pip uninstall -y setuptools && python3.9 -m pip install setuptools
RUN python3.9 -m pip install numpy scipy pandas pycrypto whoosh bcrypt passlib sympy
ADD requirements.txt ./
RUN python3.9 -m pip install -r requirements.txt


################################
##### Pillow dependencies ######
################################


RUN apt install -y \
	libfribidi-dev libharfbuzz-dev \
	libjpeg62-turbo libtiff-dev \
	liblcms2-dev libwebp-dev \
	libtcl \
	tk-dev zlib1g

# Pillow zlib fix
RUN ln -s /lib/libz.so /usr/lib/


###############
#####Setup#####
###############


ENV COMMAND='python3.9 $SCRIPT'
