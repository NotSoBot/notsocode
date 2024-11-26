FROM debian:bookworm-20241111-slim

RUN apt update -y && apt install -y wget xz-utils

WORKDIR /tmp


################################
##### FFMPEG dependencies ######
################################


RUN mkdir -p ./ffmpeg && cd ./ffmpeg && \
    wget https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2024-11-25-13-05/ffmpeg-n7.1-36-g20c8a3f5ff-linux64-gpl-7.1.tar.xz -q -O ffmpeg.tar.xz && \
    tar xf ffmpeg.tar.xz --strip-components=1


################################
### ImageMagick dependencies ###
################################


RUN apt-get update -y  && apt-get install -y \
    wget git cmake ninja-build nasm python3 python3-full \
    fftw-dev libcairo2-dev libfontconfig1-dev libgtk2.0-dev libpango1.0-dev \
    libjpeg62-turbo libtiff-dev libwebp-dev librsvg2-dev zlib1g \
    libx264-dev libx265-dev libtool build-essential


# Setup Python venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install meson

# Build dav1d
RUN wget https://code.videolan.org/videolan/dav1d/-/archive/1.2.1/dav1d-1.2.1.tar.gz -O dav1d.tar.gz && \
    mkdir -p dav1d && tar xvzf dav1d.tar.gz --strip-components=1 -C dav1d && \
    cd dav1d && mkdir build && cd build && \
    meson setup .. --prefix /usr && ninja && ninja install

# Build aom
RUN git clone https://aomedia.googlesource.com/aom.git && \
    cd aom && mkdir -p aom_build && cd aom_build && \
    cmake .. && make -j$(nproc) && make install

# Build libde265
RUN wget https://github.com/strukturag/libde265/releases/download/v1.0.15/libde265-1.0.15.tar.gz -O libde265.tar.gz && \
    mkdir -p libde265 && tar xvzf libde265.tar.gz --strip-components=1 -C libde265 && \
    cd libde265 && mkdir build && cd build && \
    cmake .. && make -j$(nproc) && make install

# Build libheif
RUN wget https://github.com/strukturag/libheif/releases/download/v1.18.2/libheif-1.18.2.tar.gz -O libheif.tar.gz && \
    mkdir -p libheif && tar xvzf libheif.tar.gz --strip-components=1 -C libheif && \
    cd libheif && cmake . && make -j$(nproc) && make install

# Build ImageMagick
RUN wget https://github.com/ImageMagick/ImageMagick/archive/refs/tags/7.1.1-36.tar.gz -O ImageMagick.tar.gz && \
    mkdir -p ImageMagick && tar xvzf ImageMagick.tar.gz --strip-components=1 -C ImageMagick && \
    cd ImageMagick && \
    ./configure --with-lqr --enable-shared --with-modules && \
    make -j$(nproc) && make install



###################################
### GraphicsMagick dependencies ###
###################################


RUN apt-get update && apt-get install -y \
    wget build-essential \
    libmagickwand-dev


# Build GraphicsMagick
RUN wget https://sourceforge.net/projects/graphicsmagick/files/graphicsmagick/1.3.43/GraphicsMagick-1.3.43.tar.xz -O GraphicsMagick.tar.gz && \
    mkdir -p GraphicsMagick && tar xvfJ GraphicsMagick.tar.gz --strip-components=1 -C GraphicsMagick && \
    cd GraphicsMagick && \
    ./configure --enable-shared --with-modules && \
    make -j$(nproc) && make install



################################
#### Audio SoX dependencies ####
################################


RUN apt-get update -y && apt-get install -y \
    git autoconf autoconf-archive automake build-essential \
    libtool libao-dev libmad0-dev \
    libid3tag0-dev libsndfile1-dev libflac-dev \
    libvorbis-dev libmp3lame-dev


RUN git clone https://github.com/chirlu/sox.git
RUN cd sox && autoreconf -i && ./configure
RUN cd sox && make -j$(nproc) && make install -j$(nproc)
