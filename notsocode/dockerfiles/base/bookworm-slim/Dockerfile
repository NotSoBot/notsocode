FROM base-builder as builder

FROM debian:bookworm-20241111-slim

COPY --from=builder /tmp/ffmpeg/bin/ffmpeg /usr/local/bin
COPY --from=builder /tmp/ffmpeg/bin/ffprobe /usr/local/bin


RUN apt update -y && apt install -y build-essential curl git wget

WORKDIR /tmp


####################
####Latest cmake####
####################

RUN wget https://github.com/Kitware/CMake/releases/download/v3.27.7/cmake-3.27.7-linux-x86_64.sh -O cmake.sh
RUN mkdir -p /opt/cmake && sh ./cmake.sh --prefix=/opt/cmake --skip-license
RUN ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
RUN rm -rf ./cmake.sh


################################
##### ImageMagick Install ######
################################


COPY --from=builder /usr/local/lib /usr/local/lib/
COPY --from=builder /usr/local/bin /usr/local/bin/
COPY --from=builder /usr/local/etc/ImageMagick-7 /usr/local/etc/ImageMagick-7/
COPY --from=builder /usr/local/share/ImageMagick-7 /usr/local/share/ImageMagick-7/
COPY --from=builder /usr/local/lib/ImageMagick-7.1.1 /usr/local/lib/ImageMagick-7.1.1/

RUN apt-get update -y && apt-get install -y \
    libcairo2 libfontconfig1 libpango1.0-0 \
    libjpeg62-turbo libtiff6 libwebp7 librsvg2-2 \
    libx264-dev libx265-dev && \
    rm -rf /var/lib/apt/lists/* && \
    ldconfig


################################
#### GraphicsMagick Install ####
################################


COPY --from=builder /usr/local/lib /usr/local/lib/
COPY --from=builder /usr/local/bin /usr/local/bin/
COPY --from=builder /usr/local/lib/GraphicsMagick-1.3.43 /usr/local/lib/GraphicsMagick-1.3.43/
COPY --from=builder /usr/local/share/GraphicsMagick-1.3.43 /usr/local/share/GraphicsMagick-1.3.43/

RUN apt-get update && apt-get install -y \
    libmagickwand-6.q16-6 && \
    rm -rf /var/lib/apt/lists/* && \
    ldconfig


################################
###### Audio SoX Install #######
################################

COPY --from=builder /usr/local/bin/sox /usr/local/bin/
COPY --from=builder /usr/local/lib/libsox.* /usr/local/lib/

RUN apt-get update -y && apt-get install -y \
    libao4 libmad0 libid3tag0 libsndfile1 libflac12 \
    libvorbis0a libmp3lame0 libvorbisfile3 && \
    rm -rf /var/lib/apt/lists/* && \
    ldconfig


###############
#####Setup#####
###############

WORKDIR /

ARG DIRECTORY_HOME=/home
ARG USER=notsocoder
ARG USER_UID=42069

RUN adduser --disabled-password  --gecos "" --home "$DIRECTORY_HOME" --uid "$USER_UID" "$USER"
RUN mkdir -p $DIRECTORY_HOME && chown -R "$USER":"$USER" $DIRECTORY_HOME && chmod g+s $DIRECTORY_HOME
RUN chmod -R 555 /bin

ARG DIRECTORY_OUTPUT=$DIRECTORY_HOME/output
ARG FILENAME_SCRIPT=script
ARG FILENAME_STDIN=stdin
ARG MAX_FILES=10

ENV DIRECTORY_OUTPUT=$DIRECTORY_OUTPUT
ENV COMMAND=bash
ENV COMMAND_COMPILE=''
ENV FILENAME_SCRIPT=$FILENAME_SCRIPT
ENV FILENAME_STDIN=$FILENAME_STDIN
ENV HOME=$DIRECTORY_HOME
ENV MAX_FILES=$MAX_FILES
ENV USER=$USER
ENTRYPOINT cd $DIRECTORY_HOME && chown -R "$USER":"$USER" $HOME && chmod -R 777 $HOME && \
    export SCRIPT=$(readlink -e $(find . -type f -name "$FILENAME_SCRIPT*" -print -quit)) && \
    eval $COMMAND_COMPILE && \
    (su $USER -c '(if (test -e $FILENAME_STDIN); then cat $FILENAME_STDIN; fi;) | eval $COMMAND') && \
    (if (test -d "$DIRECTORY_OUTPUT"); then cd $DIRECTORY_OUTPUT && rm -rf -- */ && ls -1tr | head -n -$MAX_FILES | xargs -d "\n" rm -rf --; fi;)
