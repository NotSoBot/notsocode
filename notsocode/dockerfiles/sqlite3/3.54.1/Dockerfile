ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y libreadline-dev zlib1g-dev

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://sqlite.org/2026/sqlite-autoconf-3540100.tar.gz" -q -O sqlite.tar.gz && tar xzf sqlite.tar.gz --strip-components=1
RUN cd ./build && ./configure --prefix=/usr/local && make -j$(nproc) && make install && ldconfig && cd ../ && rm -rf ./build

# in-memory database by default, `.open ./output/name.db` to get one back as a file
ENV COMMAND='sqlite3 -bail < $SCRIPT'
