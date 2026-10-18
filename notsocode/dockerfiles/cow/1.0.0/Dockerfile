ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && git clone -q https://github.com/Hydrazer/COW.git cow && cd cow && git checkout -q 6bab491612ec013f4775ce42332e3adcafded35f
RUN cd ./build && sed -i '1i#define NO_GREETINGS' ./cow/source/cow.cpp && g++ ./cow/source/cow.cpp -o /usr/bin/cow
RUN rm -rf ./build

ENV COMMAND='cow $SCRIPT'
