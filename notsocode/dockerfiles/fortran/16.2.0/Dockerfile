ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y gdc

WORKDIR /tmp
RUN mkdir -p build && cd ./build && wget "https://ftp.gnu.org/gnu/gcc/gcc-16.2.0/gcc-16.2.0.tar.gz" -q -O gcc.tar.gz && tar xfz gcc.tar.gz --strip-components=1
RUN cd ./build && ./contrib/download_prerequisites
# no libatomic: gcc 16 would link a libatomic_asneeded script into everything, but its configure and libatomic's
# disagree on whether to create it here, so every link fails. without it gcc links like 15 did (-latomic by hand)
RUN cd ./build && ./configure --enable-languages=c,c++,d,fortran --disable-multilib --disable-bootstrap --disable-libatomic && \
	make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build
# build c,c++,d,fortran because this step will be copied to the other files and itll be cached
# the new libstdc++/libgphobos/libgfortran live in /usr/local/lib64, put them ahead of debian's older ones;
# libatomic isn't built (above), so `-latomic` links debian's
RUN echo /usr/local/lib64 > /etc/ld.so.conf.d/00-gcc.conf && \
	ln -sf /usr/lib/$(gcc -print-multiarch)/libatomic.so.1 /usr/local/lib64/libatomic.so && ldconfig

ENV COMMAND_COMPILE='gfortran $SCRIPT -o ./binary'
ENV COMMAND='./binary'
