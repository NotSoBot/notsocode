ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y unzip

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://github.com/denoland/deno/releases/download/v2.9.7/deno-x86_64-unknown-linux-gnu.zip" -q -O deno.zip && unzip -q deno.zip
RUN cd ./build && mv deno /usr/local/bin && cd ../ && rm -rf ./build

# the container is the sandbox; without -A deno denies reading ./input, writing ./output and any network
ENV COMMAND='deno run -A $SCRIPT'
