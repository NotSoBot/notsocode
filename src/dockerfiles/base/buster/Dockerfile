FROM debian:buster-20230208

RUN apt update && apt install -y build-essential curl wget

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
