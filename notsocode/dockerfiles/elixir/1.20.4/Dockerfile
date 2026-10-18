ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y libncurses-dev libssl-dev

WORKDIR /tmp
RUN mkdir -p build && cd ./build && wget "https://github.com/erlang/otp/releases/download/OTP-29.1.2/otp_src_29.1.2.tar.gz" -q -O erlang.tar.gz && tar xfz erlang.tar.gz --strip-components=1
# no gui/odbc/java apps in a sandbox, wx also crashes the build when its headers aren't there
RUN cd ./build && ./configure --without-wx --without-observer --without-debugger --without-et --without-odbc --without-javac && \
	make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

RUN mkdir -p build && cd ./build && wget "https://github.com/elixir-lang/elixir/archive/refs/tags/v1.20.4.tar.gz" -q -O elixir.tar.gz && tar xfz elixir.tar.gz --strip-components=1
RUN cd ./build && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

RUN apt install -y --no-install-recommends locales && export LANG=en_US.UTF-8 && echo $LANG UTF-8 > /etc/locale.gen && locale-gen && update-locale LANG=$LANG

ENV COMMAND='elixir $SCRIPT'
