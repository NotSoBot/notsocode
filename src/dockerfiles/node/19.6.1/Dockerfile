FROM node:19.6.1-buster

ARG DIRECTORY_HOME=/home
ARG USER=notsocoder
ARG USER_UID=42069

RUN adduser --disabled-password  --gecos "" --home "$DIRECTORY_HOME" --no-create-home --uid "$USER_UID" "$USER"
RUN mkdir -p $DIRECTORY_HOME && chown -R "$USER":"$USER" $DIRECTORY_HOME && chmod g+s $DIRECTORY_HOME
USER notsocoder

WORKDIR $DIRECTORY_HOME

RUN npm install -y imagescript@1.2.16 sharp@0.31.3

ARG DIRECTORY_OUTPUT=$DIRECTORY_HOME/output
ARG MAX_FILES=10

ENV DIRECTORY_OUTPUT=$DIRECTORY_OUTPUT
ENV HOME=$DIRECTORY_HOME
ENV MAX_FILES=$MAX_FILES
ENV USER=$USER

USER root
ENTRYPOINT chown -R "$USER":"$USER" $HOME && su - $USER && \
    (if (test -e stdin); then cat stdin; fi;) | \
    node $(find . -name "script*" -print -quit) && \
    (if (test -d "$DIRECTORY_OUTPUT"); then cd $DIRECTORY_OUTPUT && rm -rf -- */ && ls -1tr | head -n -$MAX_FILES | xargs -d "\n" rm -rf --; fi;)
