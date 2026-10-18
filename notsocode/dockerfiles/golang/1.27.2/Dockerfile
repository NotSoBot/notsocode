ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://go.dev/dl/go1.27.2.linux-amd64.tar.gz" -q -O go.tar.gz && tar xzf go.tar.gz
RUN cd ./build && mv ./go /usr/local && cd ../ && rm -rf ./build
RUN ln -s /usr/local/go/bin/go /usr/local/bin/go && ln -s /usr/local/go/bin/gofmt /usr/local/bin/gofmt

# go doesn't ship a prebuilt std anymore, so a cold cache compiles it on every `go run`;
# warm a shared cache at build time (outside $HOME, the entrypoint's chmod would copy it up every run)
ENV GOCACHE=/opt/gocache
ENV GOTOOLCHAIN=local
RUN go build std && chmod -R a+rwX $GOCACHE

ENV COMMAND='go run $SCRIPT'
