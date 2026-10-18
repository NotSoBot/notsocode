ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && \
	wget "https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.4.1%2B1/OpenJDK25U-jdk_x64_linux_hotspot_25.0.4.1_1.tar.gz" -q -O java.tar.gz && \
	tar xzf java.tar.gz --strip-components=1
RUN cd ./build && cp -R ./ /usr && cd ../ && rm -rf ./build

ENV COMMAND='java $SCRIPT'
