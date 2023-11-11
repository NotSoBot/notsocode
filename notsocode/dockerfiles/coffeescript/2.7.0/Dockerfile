ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt install -y python3

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://nodejs.org/dist/v21.1.0/node-v21.1.0-linux-x64.tar.gz" -q -O node.tar.gz && tar xzf node.tar.gz --strip-components=1
RUN cd ./build && cp -R ./ /usr && cd ../ && rm -rf ./build

RUN npm install -g -y coffeescript@2.7.0

RUN npm config set prefix '/home/'
RUN npm install -g -y jssoup@0.0.15 mathjs@12.0.0
RUN npm install -g -y imagescript@1.2.16 sharp@0.32.6
RUN npm install -g -y node-fetch@2.7.0 undici@5.27.2
#RUN npm install -g -y @ffmpeg/ffmpeg@0.11.6 @ffmpeg/core@0.11.0

ENV COMMAND='export NODE_PATH=/home/lib/node_modules && coffee $SCRIPT'
