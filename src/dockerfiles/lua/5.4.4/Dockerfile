FROM debian:buster

RUN apt update && apt install -y build-essential curl make libreadline-dev

WORKDIR /tmp

RUN curl -R -L https://www.lua.org/ftp/lua-5.4.4.tar.gz -o lua.tar.gz && mkdir lua && tar xvzf lua.tar.gz --strip-components=1 -C lua
RUN cd lua && make && make test && make install
RUN rm ./lua.tar.gz && rm -rf ./lua

ARG DIRECTORY_HOME=/home
ARG USER=notsocoder
ARG USER_UID=42069

RUN adduser --disabled-password  --gecos "" --home "$DIRECTORY_HOME" --no-create-home --uid "$USER_UID" "$USER"
RUN mkdir -p $DIRECTORY_HOME && chown -R "$USER":"$USER" $DIRECTORY_HOME && chmod g+s $DIRECTORY_HOME
USER notsocoder

WORKDIR $DIRECTORY_HOME

ARG DIRECTORY_OUTPUT=$DIRECTORY_HOME/output
ARG MAX_FILES=10

ENV DIRECTORY_OUTPUT=$DIRECTORY_OUTPUT
ENV HOME=$DIRECTORY_HOME
ENV MAX_FILES=$MAX_FILES
ENV USER=$USER

USER root
ENTRYPOINT chown -R "$USER":"$USER" $HOME && su $USER && \
    (if (test -e stdin); then cat stdin; fi;) | \
    lua $(find . -name "script*" -print -quit) && \
    (if (test -d "$DIRECTORY_OUTPUT"); then cd $DIRECTORY_OUTPUT && rm -rf -- */ && ls -1tr | head -n -$MAX_FILES | xargs -d "\n" rm -rf --; fi;)
