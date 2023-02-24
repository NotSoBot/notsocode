ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://nodejs.org/dist/v19.7.0/node-v19.7.0.tar.gz" -O node.tar.gz && tar xzf node.tar.gz --strip-components=1
RUN cd ./build && make -j$(nproc) && make test && make install -j$(nproc) && cd ../ && rm -rf ./build

ENV COMMAND='node $SCRIPT'
