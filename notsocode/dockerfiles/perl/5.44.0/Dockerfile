ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://www.cpan.org/src/5.0/perl-5.44.0.tar.gz" -q -O perl.tar.gz && tar xzf perl.tar.gz --strip-components=1
RUN cd ./build && ./Configure -des -Dprefix=/usr/local && make -j$(nproc) && make install && cd ../ && rm -rf ./build

ENV COMMAND='perl $SCRIPT'
