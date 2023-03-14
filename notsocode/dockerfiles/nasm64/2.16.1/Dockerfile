ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update && apt install -y libreadline-dev

WORKDIR /tmp
RUN mkdir -p build && cd ./build && wget "https://www.nasm.us/pub/nasm/releasebuilds/2.16.01/nasm-2.16.01.tar.gz" -q -O nasm.tar.gz && tar xvfz nasm.tar.gz --strip-components=1
RUN cd ./build && ./configure && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

ENV COMMAND_COMPILE='nasm -f elf64 -o ./binary.o $SCRIPT && ld -m elf_x86_64 ./binary.o -o ./binary'
ENV COMMAND='./binary'
