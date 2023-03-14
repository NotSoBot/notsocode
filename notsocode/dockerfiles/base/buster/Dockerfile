FROM base-builder as builder

FROM debian:buster-20230208

COPY --from=builder /tmp/ffmpeg/ffmpeg /usr/local/bin
COPY --from=builder /tmp/ffmpeg/ffprobe /usr/local/bin


RUN apt update && apt install -y build-essential curl git wget

WORKDIR /tmp

####################
####Latest cmake####
####################

RUN wget https://github.com/Kitware/CMake/releases/download/v3.25.2/cmake-3.25.2-linux-x86_64.sh -O cmake.sh
RUN mkdir -p /opt/cmake && sh ./cmake.sh --prefix=/opt/cmake --skip-license
RUN ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
RUN rm -rf ./cmake.sh

WORKDIR /

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
ARG SCRIPT_FILE=script
ARG STDIN_FILE=stdin

ENV DIRECTORY_OUTPUT=$DIRECTORY_OUTPUT
ENV COMMAND=bash
ENV COMMAND_COMPILE=''
ENV HOME=$DIRECTORY_HOME
ENV MAX_FILES=$MAX_FILES
ENV SCRIPT_FILE=$SCRIPT_FILE
ENV STDIN_FILE=$STDIN_FILE
ENV USER=$USER
ENTRYPOINT cd $DIRECTORY_HOME && chown -R "$USER":"$USER" $HOME && su - $USER && \
    export SCRIPT_FILE=$(find . -name "$SCRIPT_FILE*" -print -quit) && \
    eval $COMMAND_COMPILE && \
    ((if (test -e "$STDIN_FILE"); then cat "$STDIN_FILE"; fi;) | eval $COMMAND) && \
    (if (test -d "$DIRECTORY_OUTPUT"); then cd $DIRECTORY_OUTPUT && rm -rf -- */ && ls -1tr | head -n -$MAX_FILES | xargs -d "\n" rm -rf --; fi;)
