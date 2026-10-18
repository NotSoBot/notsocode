ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && \
	wget "https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.4.1%2B1/OpenJDK25U-jdk_x64_linux_hotspot_25.0.4.1_1.tar.gz" -q -O java.tar.gz && \
	tar xzf java.tar.gz --strip-components=1
RUN cd ./build && cp -R ./ /usr && cd ../ && rm -rf ./build

RUN apt update -y && apt install -y unzip
RUN mkdir -p ./build && cd ./build && wget "https://github.com/JetBrains/kotlin/releases/download/v2.4.21/kotlin-compiler-2.4.21.zip" -q -O kotlin.zip && unzip -q kotlin.zip && \
	mv ./kotlinc /opt/kotlinc && cd ../ && rm -rf ./build
RUN ln -s /opt/kotlinc/bin/kotlinc /usr/local/bin/kotlinc

# a lighter jit and gc, kotlinc's startup is most of a run (a cds archive is rejected by kotlinc's own jvm flags)
ENV COMMAND_COMPILE='JAVA_OPTS="-XX:TieredStopAtLevel=1 -XX:+UseSerialGC" kotlinc -nowarn $SCRIPT -include-runtime -d ./binary.jar'
ENV COMMAND='java -jar ./binary.jar'
