ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y libreadline-dev

WORKDIR /tmp
RUN mkdir -p build && cd ./build && wget "https://github.com/justinmeza/lci/archive/refs/tags/v1.3.tar.gz" -q -O lolcode.tar.gz && tar xfz lolcode.tar.gz --strip-components=1
RUN cd ./build && cmake -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_INSTALL_PREFIX=/usr/local . && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

ENV COMMAND='lci $SCRIPT'
