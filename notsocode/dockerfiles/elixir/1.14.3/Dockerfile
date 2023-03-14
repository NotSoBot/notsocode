ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt install -y libncurses5-dev

WORKDIR /tmp
RUN mkdir -p build && cd ./build && wget "https://github.com/erlang/otp/releases/download/OTP-25.3/otp_src_25.3.tar.gz" -q -O erlang.tar.gz && tar xvfz erlang.tar.gz --strip-components=1
RUN cd ./build && ./configure && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

RUN mkdir -p build && cd ./build && wget "https://github.com/elixir-lang/elixir/archive/refs/tags/v1.14.3.tar.gz" -q -O bash.tar.gz && tar xvfz bash.tar.gz --strip-components=1
RUN cd ./build && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

RUN apt install -y --no-install-recommends locales && export LANG=en_US.UTF-8 && echo $LANG UTF-8 > /etc/locale.gen && locale-gen && update-locale LANG=$LANG

ENV COMMAND='elixir $SCRIPT'
