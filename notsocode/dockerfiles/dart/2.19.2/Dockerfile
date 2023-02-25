ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt install -y zip

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://storage.googleapis.com/dart-archive/channels/stable/release/2.19.2/sdk/dartsdk-linux-x64-release.zip" -q -O dart.zip && unzip dart.zip
RUN cd ./build && cp -R ./dart-sdk/* /usr
RUN rm -rf ./build

ENV COMMAND='dart run $SCRIPT'
