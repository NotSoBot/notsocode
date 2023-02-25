ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt install -y libncurses5

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://github.com/emojicode/emojicode/releases/download/v1.0-beta.2/Emojicode-1.0-beta.2-Linux-x86_64.tar.gz" -q -O emoji.tar.gz && tar xzf emoji.tar.gz --strip-components=1
RUN cd ./build && cp ./emojicodec /usr/local/bin && cp -R ./packages /usr/local/EmojicodePackages && cp -R ./include /usr/local/include/emojicode && cd ../ && rm -rf ./build

ENV COMMAND_COMPILE='emojicodec $SCRIPT -o ./binary'
ENV COMMAND='./binary'
