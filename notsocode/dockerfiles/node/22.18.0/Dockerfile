ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y python3

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://nodejs.org/dist/v22.18.0/node-v22.18.0-linux-x64.tar.gz" -q -O node.tar.gz && tar xzf node.tar.gz --strip-components=1
RUN cd ./build && cp -R ./ /usr && cd ../ && rm -rf ./build

RUN npm config set prefix '/home/'
RUN npm install -g -y jssoup@0.0.15 mathjs@14.6.0
RUN npm install -g -y imagescript@1.3.1 sharp@0.34.3
RUN npm install -g -y node-fetch@2.7.0 undici@7.13.0
RUN npm install -g -y redis@5.8.0
#RUN npm install -g -y @ffmpeg/ffmpeg@0.11.6 @ffmpeg/core@0.11.0

ENV COMMAND='export NODE_PATH=/home/lib/node_modules && node --no-deprecation $SCRIPT'
