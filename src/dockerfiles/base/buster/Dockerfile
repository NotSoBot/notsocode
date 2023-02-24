FROM debian:buster-20230208

RUN apt update && apt install -y build-essential curl git wget


ARG DIRECTORY_HOME=/home
ENV HOME=$DIRECTORY_HOME


##############
####FFMPEG####
##############

WORKDIR /tmp

# latest cmake
RUN wget https://github.com/Kitware/CMake/releases/download/v3.25.2/cmake-3.25.2-linux-x86_64.sh -O cmake.sh
RUN mkdir -p /opt/cmake && sh ./cmake.sh --prefix=/opt/cmake --skip-license
RUN ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake


RUN mkdir -p ~/ffmpeg-sources ~/bin

# ffmpeg dependencies
RUN apt install -y \
  autoconf automake build-essential cmake git-core \
  libass-dev libfreetype6-dev libgnutls28-dev libmp3lame-dev \
  libtool libvorbis-dev \
  ninja-build pkg-config texinfo wget \
  yasm zlib1g-dev


# optional ffmpeg dependencies
RUN apt install -y nasm libx264-dev libx265-dev libnuma-dev libvpx-dev libopus-dev

# ffmpeg AAC audio encoder
RUN cd ~/ffmpeg-sources && \
    git -C fdk-aac pull 2> /dev/null || git clone --depth 1 https://github.com/mstorsjo/fdk-aac && \
    cd fdk-aac && \
    autoreconf -fiv && \
    ./configure --prefix="$HOME/ffmpeg" --disable-shared && \
    make -j$(nproc) && make install -j$(nproc)

# ffmpeg libsvtav1 (AV1 video encoder)
RUN cd ~/ffmpeg-sources && \
    git -C SVT-AV1 pull 2> /dev/null || git clone https://gitlab.com/AOMediaCodec/SVT-AV1.git && \
    mkdir -p SVT-AV1/build && \
    cd SVT-AV1/build && \
    PATH="$HOME/bin:$PATH" cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg" -DCMAKE_BUILD_TYPE=Release -DBUILD_DEC=OFF -DBUILD_SHARED_LIBS=OFF .. && \
    PATH="$HOME/bin:$PATH" make -j$(nproc) && make install -j$(nproc)

# ffmpeg libdav1d (AV1 video decoder)
RUN apt install -y python3 python3-pip
RUN python3 -m pip install meson
RUN cd ~/ffmpeg-sources && \
    git -C dav1d pull 2> /dev/null || git clone --depth 1 https://github.com/videolan/dav1d.git && \
    mkdir -p dav1d/build && \
    cd dav1d/build && \
    meson setup -Denable_tools=false -Denable_tests=false --default-library=static .. --prefix "$HOME/ffmpeg" --libdir="$HOME/ffmpeg/lib" && \
    ninja && ninja install

RUN apt install -y ffmpeg



##############
####Setup#####
##############

ARG DIRECTORY_HOME=/home
ARG USER=notsocoder
ARG USER_UID=42069

RUN adduser --disabled-password  --gecos "" --home "$DIRECTORY_HOME" --uid "$USER_UID" "$USER"
RUN mkdir -p $DIRECTORY_HOME && chown -R "$USER":"$USER" $DIRECTORY_HOME && chmod g+s $DIRECTORY_HOME

ARG DIRECTORY_OUTPUT=$DIRECTORY_HOME/output
ARG MAX_FILES=10

ENV DIRECTORY_OUTPUT=$DIRECTORY_OUTPUT
ENV COMMAND=bash
ENV COMMAND_COMPILE=''
ENV HOME=$DIRECTORY_HOME
ENV MAX_FILES=$MAX_FILES
ENV USER=$USER
ENTRYPOINT cd $DIRECTORY_HOME && chown -R "$USER":"$USER" $HOME && su - $USER && \
    export SCRIPT=$(find . -name "script*" -print -quit) && \
    eval $COMMAND_COMPILE && \
    ((if (test -e stdin); then cat stdin; fi;) | eval $COMMAND) && \
    (if (test -d "$DIRECTORY_OUTPUT"); then cd $DIRECTORY_OUTPUT && rm -rf -- */ && ls -1tr | head -n -$MAX_FILES | xargs -d "\n" rm -rf --; fi;)
