ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p build && cd ./build && wget "https://www.nasm.us/pub/nasm/releasebuilds/3.02/nasm-3.02.tar.gz" -q -O nasm.tar.gz && tar xfz nasm.tar.gz --strip-components=1
RUN cd ./build && ./configure && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

ENV COMMAND_COMPILE='nasm -f elf64 -o ./binary.o $SCRIPT && ld -m elf_x86_64 ./binary.o -o ./binary'
ENV COMMAND='./binary'
