ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp

RUN curl -fsSL https://github.com/01mf02/jaq/releases/latest/download/jaq-$(uname -m)-unknown-linux-musl -o /usr/local/bin/jaq && \
	chmod +x /usr/local/bin/jaq

RUN mkdir -p build && cd ./build && wget "https://ftp.gnu.org/gnu/bash/bash-5.2.15.tar.gz" -q -O bash.tar.gz && tar xvfz bash.tar.gz --strip-components=1
RUN cd ./build && ./configure && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

ENV COMMAND='bash $SCRIPT'
