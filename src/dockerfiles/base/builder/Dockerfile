FROM debian:buster-20230208-slim

RUN apt update && apt install -y wget xz-utils

WORKDIR /tmp

RUN mkdir -p ./ffmpeg && cd ./ffmpeg && wget "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz" -q -O ffmpeg.tar.xz && tar xf ffmpeg.tar.xz --strip-components=1
