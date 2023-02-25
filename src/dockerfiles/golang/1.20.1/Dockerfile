ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://go.dev/dl/go1.20.1.linux-amd64.tar.gz" -q -O go.tar.gz && tar xzf go.tar.gz
RUN cd ./build && mv ./go /usr/local && cd ../ && rm -rf ./build
RUN ln -s /usr/local/go/bin/go /usr/local/bin/go && ln -s /usr/local/go/bin/gofmt /usr/local/bin/gofmt

ENV COMMAND='go run $SCRIPT'
