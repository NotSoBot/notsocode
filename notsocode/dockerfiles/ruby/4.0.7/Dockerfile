ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y libyaml-dev libssl-dev zlib1g-dev libffi-dev

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://cache.ruby-lang.org/pub/ruby/4.0/ruby-4.0.7.tar.gz" -q -O ruby.tar.gz && tar xzf ruby.tar.gz --strip-components=1
RUN cd ./build && ./configure && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

ENV COMMAND='ruby $SCRIPT'
