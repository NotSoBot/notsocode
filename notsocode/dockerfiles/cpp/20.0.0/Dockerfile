ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt install -y gdc

WORKDIR /tmp
RUN mkdir -p build && cd ./build && wget "https://ftp.gnu.org/gnu/gcc/gcc-12.2.0/gcc-12.2.0.tar.gz" -q -O gcc.tar.gz && tar xvfz gcc.tar.gz --strip-components=1
RUN cd ./build && ./contrib/download_prerequisites
RUN cd ./build && ./configure --enable-languages=c,c++,d,fortran --disable-multilib --disable-bootstrap && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build
# build c,c++,d,fortran because this step will be copied to the other files and itll be cached

ENV COMMAND_COMPILE='g++ -std=c++20 $SCRIPT -o ./binary'
ENV COMMAND='./binary'
