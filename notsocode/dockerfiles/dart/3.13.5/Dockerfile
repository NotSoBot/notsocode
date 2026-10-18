ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y unzip

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://storage.googleapis.com/dart-archive/channels/stable/release/3.13.5/sdk/dartsdk-linux-x64-release.zip" -q -O dart.zip && unzip -q dart.zip
RUN cd ./build && cp -R ./dart-sdk/* /usr
RUN rm -rf ./build

ENV COMMAND='dart run $SCRIPT'
