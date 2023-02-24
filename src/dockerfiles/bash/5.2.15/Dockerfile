ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p build && cd ./build && wget "https://ftp.gnu.org/gnu/bash/bash-5.2.15.tar.gz" -q -O bash.tar.gz && tar xvfz bash.tar.gz --strip-components=1
RUN cd ./build && ./configure && make -j$(nproc) && make install -j$(nproc)

ENV COMMAND='bash $SCRIPT'
