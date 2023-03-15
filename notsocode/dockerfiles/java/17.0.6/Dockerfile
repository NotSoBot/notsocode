ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.tar.gz" -q -O java.tar.gz && tar xzf java.tar.gz --strip-components=1
RUN cd ./build && cp -R ./ /usr && cd ../ && rm -rf ./build

ENV COMMAND='java $SCRIPT'
