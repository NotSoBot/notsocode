ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y gdc

WORKDIR /tmp
RUN mkdir -p build && cd ./build && wget "https://ftp.gnu.org/gnu/gcc/gcc-16.2.0/gcc-16.2.0.tar.gz" -q -O gcc.tar.gz && tar xfz gcc.tar.gz --strip-components=1
RUN cd ./build && ./contrib/download_prerequisites
RUN cd ./build && ./configure --enable-languages=c,c++,d,fortran --disable-multilib --disable-bootstrap && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build
# build c,c++,d,fortran because this step will be copied to the other files and itll be cached
# the new libstdc++/libgphobos/libgfortran live in /usr/local/lib64, put them ahead of debian's older ones
RUN echo /usr/local/lib64 > /etc/ld.so.conf.d/00-gcc.conf && ldconfig

ENV COMMAND_COMPILE='gcc -std=c17 $SCRIPT -lm -o ./binary'
ENV COMMAND='./binary'
