ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt install -y libncurses5-dev

WORKDIR /tmp
RUN mkdir -p build && cd ./build && wget "https://github.com/erlang/otp/releases/download/OTP-25.3/otp_src_25.3.tar.gz" -q -O erlang.tar.gz && tar xvfz erlang.tar.gz --strip-components=1
RUN cd ./build && ./configure && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

ENV COMMAND='escript $SCRIPT'
