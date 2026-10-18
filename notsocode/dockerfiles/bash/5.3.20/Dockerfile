ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp

RUN curl -fsSL https://github.com/01mf02/jaq/releases/download/v3.1.1/jaq-$(uname -m)-unknown-linux-musl -o /usr/local/bin/jaq && \
	chmod +x /usr/local/bin/jaq

# 5.3 plus its 20 official patches
RUN mkdir -p build && cd ./build && wget "https://ftp.gnu.org/gnu/bash/bash-5.3.tar.gz" -q -O bash.tar.gz && tar xfz bash.tar.gz --strip-components=1 && \
	for i in $(seq -w 1 20); do wget -q "https://ftp.gnu.org/gnu/bash/bash-5.3-patches/bash53-0$i" -O - | patch -s -p0; done
RUN cd ./build && ./configure && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

ENV COMMAND='bash $SCRIPT'
