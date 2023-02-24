ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://static.rust-lang.org/dist/rust-1.67.1-x86_64-unknown-linux-gnu.tar.gz" -q -O rust.tar.gz && tar xzf rust.tar.gz --strip-components=1
RUN cd ./build && ./install.sh && cd ../ && rm -rf ./build

ENV COMMAND_COMPILE='rustc $SCRIPT -o ./binary'
ENV COMMAND='./binary'
