ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt install -y zlib1g zlib1g-dev libssl-dev libffi-dev

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://www.python.org/ftp/python/3.11.6/Python-3.11.6.tgz" -q -O python.tar.gz && tar xzf python.tar.gz --strip-components=1
RUN cd ./build && ./configure --with-ensurepip=install && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

RUN apt install -y libsqlite3-dev

RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip uninstall -y setuptools && python3.11 -m pip install setuptools
RUN python3.11 -m pip install numpy scipy pandas whoosh bcrypt passlib sympy
ADD requirements.txt ./
RUN python3.11 -m pip install -r requirements.txt

RUN apt update -y

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


################################
### ImageMagick dependencies ###
################################

RUN apt install -y \
	fftw-dev \
	libcairo2-dev libfontconfig1-dev libgtk2.0-dev libpango1.0-dev \
	libjpeg62-turbo libtiff-dev \
	libwebp-dev \
	librsvg2-dev \
	zlib1g


# libdav1d (AV1 decoder)
RUN apt install -y nasm ninja-build
RUN pip install meson
RUN wget https://code.videolan.org/videolan/dav1d/-/archive/1.2.1/dav1d-1.2.1.tar.gz -O dav1d.tar.gz && \
	mkdir -p ./dav1d && tar xvzf dav1d.tar.gz --strip-components=1 -C ./dav1d
RUN cd ./dav1d && mkdir -p ./build && cd ./build && meson setup .. --prefix /usr && ninja && ninja install

# aom install (AV1 encoder)
RUN git clone https://aomedia.googlesource.com/aom.git && cd ./aom && \
	mkdir -p ./build && cd ./build && cmake .. && make -j$(nproc) && make install -j$(nproc)

# libde265 (hevc decoder)
RUN wget https://github.com/strukturag/libde265/releases/download/v1.0.15/libde265-1.0.15.tar.gz -O libde265.tar.gz && \
	mkdir -p ./libde265 && tar xvzf libde265.tar.gz --strip-components=1 -C ./libde265
RUN cd ./libde265 && mkdir -p ./build && cd ./build && cmake .. && make -j$(nproc) && make install -j$(nproc)

# Need a new libheif for ImageMagick now
RUN apt install -y libx264-dev libx265-dev
RUN wget https://github.com/strukturag/libheif/releases/download/v1.18.2/libheif-1.18.2.tar.gz -O libheif.tar.gz && \
	mkdir -p ./libheif && tar xvzf libheif.tar.gz --strip-components=1 -C ./libheif
RUN cd ./libheif && cmake . && make -j$(nproc) && make install -j$(nproc)

# ImageMagick (first one installs deps, second installs shared library)
RUN apt install -y libtool
RUN wget https://github.com/ImageMagick/ImageMagick/archive/refs/tags/7.1.1-36.tar.gz -O ImageMagick.tar.gz && \
	mkdir -p ImageMagick && tar xvzf ImageMagick.tar.gz --strip-components=1 -C ImageMagick
RUN cd ImageMagick && ./configure --with-lqr --enable-shared --with-modules
RUN cd ImageMagick && make -j$(nproc) && make install -j$(nproc)


################################
# GraphicsMagick dependencies ##
################################


# GraphicsMagick
RUN wget https://sourceforge.net/projects/graphicsmagick/files/graphicsmagick/1.3.43/GraphicsMagick-1.3.43.tar.xz -O GraphicsMagick.tar.gz && \
	mkdir -p GraphicsMagick && tar xvfJ GraphicsMagick.tar.gz --strip-components=1 -C GraphicsMagick
RUN cd GraphicsMagick && ./configure --enable-shared --with-modules
RUN cd GraphicsMagick && make -j$(nproc) && make install -j$(nproc)

RUN apt install -y libmagickwand-dev

ENV COMMAND='python3.11 $SCRIPT'
