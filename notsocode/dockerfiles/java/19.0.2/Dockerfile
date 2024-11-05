ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && \
	wget "https://download.oracle.com/java/19/archive/jdk-19.0.2_linux-aarch64_bin.tar.gz" -q -O java.tar.gz && \
	tar xzf java.tar.gz --strip-components=1
RUN cd ./build && cp -R ./ /usr && cd ../ && rm -rf ./build

ENV COMMAND='java $SCRIPT'
