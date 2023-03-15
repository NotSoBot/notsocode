ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt install -y libyaml-dev

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://cache.ruby-lang.org/pub/ruby/3.2/ruby-3.2.1.tar.gz" -q -O ruby.tar.gz && tar xzf ruby.tar.gz --strip-components=1
RUN cd ./build && ./configure && make -j$(nproc) && make install -j$(nproc) && cd ../ && rm -rf ./build

RUN wget "https://github.com/darrenks/golfscript/blob/main/golfscript.rb" -q -o golfscript.rb
RUN mv ./golfscript.rb /usr/local/bin && chmod +x /usr/local/bin/golfscript.rb

ENV COMMAND='ruby /usr/local/bin/golfscript.rb $SCRIPT'
