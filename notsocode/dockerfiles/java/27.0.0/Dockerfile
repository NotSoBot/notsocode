ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && \
	wget "https://github.com/adoptium/temurin27-binaries/releases/download/jdk-27%2B35/OpenJDK27U-jdk_x64_linux_hotspot_27_35.tar.gz" -q -O java.tar.gz && \
	tar xzf java.tar.gz --strip-components=1
RUN cd ./build && cp -R ./ /usr && cd ../ && rm -rf ./build

ENV COMMAND='java $SCRIPT'
