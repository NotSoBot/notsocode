FROM base-builder as builder

FROM debian:bookworm-slim

COPY --from=builder /tmp/ffmpeg/bin/ffmpeg /usr/local/bin
COPY --from=builder /tmp/ffmpeg/bin/ffprobe /usr/local/bin


RUN apt update -y && apt install -y build-essential curl git wget

WORKDIR /tmp


####################
### Latest cmake ###
####################

RUN wget https://github.com/Kitware/CMake/releases/download/v4.0.3/cmake-4.0.3-linux-x86_64.sh -O cmake.sh && \
    mkdir -p /opt/cmake && sh ./cmake.sh --prefix=/opt/cmake --skip-license
RUN ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake && rm -rf ./cmake.sh


################################
##### ImageMagick Install ######
################################


COPY --from=builder /usr/local/lib /usr/local/lib/
COPY --from=builder /usr/local/bin /usr/local/bin/
COPY --from=builder /usr/local/etc/ImageMagick-7 /usr/local/etc/ImageMagick-7/
COPY --from=builder /usr/local/share/ImageMagick-7 /usr/local/share/ImageMagick-7/
COPY --from=builder /usr/local/lib/ImageMagick-7.1.2 /usr/local/lib/ImageMagick-7.1.2/

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
COPY --from=builder /usr/local/lib/GraphicsMagick-1.3.46 /usr/local/lib/GraphicsMagick-1.3.46/
COPY --from=builder /usr/local/share/GraphicsMagick-1.3.46 /usr/local/share/GraphicsMagick-1.3.46/

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


################################
####### frei0r Install #########
################################

COPY --from=builder /usr/local/lib/frei0r-1/ /usr/local/lib/frei0r-1/
COPY --from=builder /usr/local/lib/pkgconfig/frei0r.pc /usr/local/lib/pkgconfig/

RUN apt-get update -y && apt-get install -y \
    libcairo2 && \
    rm -rf /var/lib/apt/lists/* && \
    ldconfig


################################
#### BC Calculator Install #####
################################

RUN apt-get update -y && apt-get install -y bc


################################
######## Wine Install ##########
################################

RUN dpkg --add-architecture i386 && apt-get update && \
    apt-get install -y --no-install-recommends \
    wine wine32:i386 wine64 && apt-get clean && rm -rf /var/lib/apt/lists/*


################################
##### libqrencode Install ######
################################

RUN apt-get update -y && apt-get install -y \
    autoconf automake autotools-dev libtool pkg-config libpng-dev && \
    rm -rf /var/lib/apt/lists/* && \
    ldconfig

RUN wget https://github.com/fukuchi/libqrencode/archive/715e29fd4cd71b6e452ae0f4e36d917b43122ce8.tar.gz -O /tmp/libqrencode.tar.gz && \
    mkdir -p /tmp/libqrencode && tar xvzf /tmp/libqrencode.tar.gz --strip-components=1 -C /tmp/libqrencode
RUN cd /tmp/libqrencode && ./autogen.sh && ./configure && make -j$(nproc) && make install -j$(nproc) && ldconfig
RUN rm -rf /tmp/libqrencode



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

ENV WINEDEBUG=-all
ENV WINEPREFIX=$DIRECTORY_HOME/.wine
# wine refuses a prefix it doesn't own, so init it as the user (root's init always failed);
# mscoree/mshtml off so it doesn't try to fetch mono/gecko
RUN mkdir -p $WINEPREFIX && chown -R "$USER":"$USER" $WINEPREFIX && \
    (su "$USER" -c 'WINEDLLOVERRIDES="mscoree,mshtml=" wineboot --init && wineserver -w' || true)

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
ENV LANG=C.UTF-8
ENV MAX_FILES=$MAX_FILES
ENV USER=$USER
# .wine is skipped: it's already the user's, and touching it would copy the whole prefix up on every run
# compile and run both happen as the user, the compiler reads user-controlled source;
# output is pruned even when the script fails, after any leftover user processes are killed so nothing
# writes past it; dotfiles, subdirectories and symlinks count too, keeping the newest $MAX_FILES files
ENTRYPOINT cd $DIRECTORY_HOME && chown "$USER":"$USER" . && chmod 777 . && \
    find . -mindepth 1 -maxdepth 1 ! -name .wine -exec chown -R "$USER":"$USER" {} + -exec chmod -R 777 {} + && \
    export SCRIPT=$(readlink -e $(find . -maxdepth 1 -type f -name "$FILENAME_SCRIPT*" -print -quit)) && \
    su $USER -c 'eval $COMMAND_COMPILE' && \
    (su $USER -c '(if (test -e $FILENAME_STDIN); then cat $FILENAME_STDIN; fi;) | eval $COMMAND'); \
    status=$?; \
    su $USER -c 'kill -9 -1' >/dev/null 2>&1; \
    (if (test -d "$DIRECTORY_OUTPUT"); then cd $DIRECTORY_OUTPUT && \
        find . -mindepth 1 -maxdepth 1 ! -type f -exec rm -rf -- {} + ; \
        find . -mindepth 1 -maxdepth 1 -type f -printf '%T@ %p\0' | sort -z -n | head -z -n -$MAX_FILES | cut -z -d ' ' -f 2- | xargs -0 -r rm -f --; fi;); \
    exit $status
