ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

# official swift.org build for debian 12 and its listed dependencies
RUN apt update -y && apt install -y \
	binutils-gold gcc git libcurl4-openssl-dev libedit-dev libicu-dev libncurses-dev libpython3-dev \
	libsqlite3-dev libstdc++-12-dev libxml2-dev pkg-config tzdata uuid-dev

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://download.swift.org/swift-6.4.1-release/debian12/swift-6.4.1-RELEASE/swift-6.4.1-RELEASE-debian12.tar.gz" -q -O swift.tar.gz && tar xzf swift.tar.gz --strip-components=1
RUN cd ./build && cp -R ./usr / && cd ../ && rm -rf ./build

ENV COMMAND='swift $SCRIPT'
