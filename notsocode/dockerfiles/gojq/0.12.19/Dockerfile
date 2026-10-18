ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://github.com/itchyny/gojq/releases/download/v0.12.19/gojq_v0.12.19_linux_amd64.tar.gz" -q -O gojq.tar.gz && tar xzf gojq.tar.gz --strip-components=1
RUN cd ./build && mv ./gojq /usr/bin
RUN rm -rf ./build

ENV COMMAND='gojq -n -r -f $SCRIPT'
