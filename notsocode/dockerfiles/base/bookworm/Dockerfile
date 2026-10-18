FROM base-builder as builder

FROM debian:bookworm-20250721

COPY --from=builder /tmp/ffmpeg/ffmpeg /usr/local/bin
COPY --from=builder /tmp/ffmpeg/ffprobe /usr/local/bin


RUN apt update && apt install -y build-essential curl git wget

WORKDIR /tmp

####################
####Latest cmake####
####################

RUN wget https://github.com/Kitware/CMake/releases/download/v4.0.3/cmake-4.0.3-linux-x86_64.sh -O cmake.sh
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
ENV LANG=C.UTF-8
ENV MAX_FILES=$MAX_FILES
ENV USER=$USER
# compile and run both happen as the user, the compiler reads user-controlled source;
# output is pruned even when the script fails, after any leftover user processes are killed so nothing
# writes past it; dotfiles, subdirectories and symlinks count too, keeping the newest $MAX_FILES files
ENTRYPOINT cd $DIRECTORY_HOME && chown -R "$USER":"$USER" $HOME && chmod -R 777 $HOME && \
    export SCRIPT=$(readlink -e $(find . -maxdepth 1 -type f -name "$FILENAME_SCRIPT*" -print -quit)) && \
    su $USER -c 'eval $COMMAND_COMPILE' && \
    (su $USER -c '(if (test -e $FILENAME_STDIN); then cat $FILENAME_STDIN; fi;) | eval $COMMAND'); \
    status=$?; \
    su $USER -c 'kill -9 -1' >/dev/null 2>&1; \
    (if (test -d "$DIRECTORY_OUTPUT"); then cd $DIRECTORY_OUTPUT && \
        find . -mindepth 1 -maxdepth 1 ! -type f -exec rm -rf -- {} + ; \
        find . -mindepth 1 -maxdepth 1 -type f -printf '%T@ %p\0' | sort -z -n | head -z -n -$MAX_FILES | cut -z -d ' ' -f 2- | xargs -0 -r rm -f --; fi;); \
    exit $status
