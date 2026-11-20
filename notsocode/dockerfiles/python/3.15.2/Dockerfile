ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

# every optional stdlib module's headers, a missing one silently drops that module (bz2 broke networkx)
RUN apt update -y && apt install -y \
	zlib1g zlib1g-dev \
	libssl-dev \
	libffi-dev \
	liblzma-dev \
	libsqlite3-dev \
	libbz2-dev \
	libreadline-dev \
	libncurses-dev \
	libgdbm-dev libgdbm-compat-dev \
	uuid-dev \
	libzstd-dev \
	tk-dev \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://www.python.org/ftp/python/3.15.2/Python-3.15.2.tgz" -q -O python.tar.gz && tar xzf python.tar.gz --strip-components=1
RUN cd ./build && ./configure --with-ensurepip=install && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

RUN python3.15 -m pip install --upgrade pip
RUN python3.15 -m pip uninstall -y setuptools && python3.15 -m pip install setuptools
RUN python3.15 -m pip install numpy scipy pandas whoosh bcrypt passlib sympy

################################
##### Pillow dependencies ######
################################

# before the requirements: Pillow 11.3.0 (moviepy caps it below 12) and PyYAML 6.0.3 have no cp315 wheels,
# so both build from source here. jpeg, freetype and raqm match what the wheels ship
RUN apt update -y && apt install -y \
	libfribidi-dev libharfbuzz-dev libfreetype-dev libraqm-dev \
	libjpeg62-turbo libjpeg62-turbo-dev libtiff-dev \
	liblcms2-dev libwebp-dev libopenjp2-7-dev \
	libtcl tk-dev libyaml-dev \
	&& rm -rf /var/lib/apt/lists/*

# Pillow zlib fix
RUN ln -s /lib/libz.so /usr/lib/

ADD requirements.txt ./
RUN python3.15 -m pip install -r requirements.txt

ENV COMMAND='python3.15 $SCRIPT'
