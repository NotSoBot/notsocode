ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y zip

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://github.com/denoland/deno/releases/download/v1.31.0/deno-x86_64-unknown-linux-gnu.zip" -q -O deno.zip && unzip deno.zip
RUN cd ./build && mv deno /usr/local/bin && cd ../ && rm -rf ./build

ENV COMMAND='deno run $SCRIPT'
