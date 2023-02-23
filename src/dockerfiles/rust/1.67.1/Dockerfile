FROM rust:1.67.1-buster

ARG DIRECTORY_HOME=/home
ARG USER=notsocoder
ARG USER_UID=42069

RUN adduser --disabled-password  --gecos "" --home "$DIRECTORY_HOME" --no-create-home --uid "$USER_UID" "$USER"
RUN mkdir -p $DIRECTORY_HOME && chown -R "$USER":"$USER" $DIRECTORY_HOME && chmod g+s $DIRECTORY_HOME
USER notsocoder

WORKDIR $HOME

ARG DIRECTORY_OUTPUT=$DIRECTORY_HOME/output
ARG MAX_FILES=10

ENV DIRECTORY_OUTPUT=$DIRECTORY_OUTPUT
ENV HOME=$DIRECTORY_HOME
ENV MAX_FILES=$MAX_FILES
ENV USER=$USER

USER root

#ENTRYPOINT cargo install --path . && $(find . -name "script*" -print -quit)
ENTRYPOINT chown -R "$USER":"$USER" $HOME && su - $USER && \
    rustc $(find . -name "script*" -print -quit) -o binary && \
    (if (test -e stdin); then cat stdin; fi;) | \
    ./binary && \
    (if (test -d "$DIRECTORY_OUTPUT"); then cd $DIRECTORY_OUTPUT && rm -rf -- */ && ls -1tr | head -n -$MAX_FILES | xargs -d "\n" rm -rf --; fi;)
