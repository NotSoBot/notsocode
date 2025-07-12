ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && \
	wget "https://download.java.net/java/GA/jdk24.0.1/24a58e0e276943138bf3e963e6291ac2/9/GPL/openjdk-24.0.1_linux-x64_bin.tar.gz" -q -O java.tar.gz && \
	tar xzf java.tar.gz --strip-components=1
RUN cd ./build && cp -R ./ /usr && cd ../ && rm -rf ./build

ENV COMMAND='java $SCRIPT'
