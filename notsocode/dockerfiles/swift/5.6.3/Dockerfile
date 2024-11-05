ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE


#WORKDIR /tmp
#RUN mkdir -p ./build && cd ./build && wget "https://download.swift.org/swift-5.6.3-release/ubuntu2004/swift-5.6.3-RELEASE/swift-5.6.3-RELEASE-ubuntu20.04.tar.gz" -q -O swift.tar.gz && tar xzf swift.tar.gz --strip-components=1
#RUN cd ./build && cp -R ./ / && cd ../ && rm -rf ./build

#RUN apt install -y binutils git gnupg2 libc6-dev libcurl4 libedit2 libgcc-8-dev libncurses-dev libpython3.7 libsqlite3-0 libstdc++-8-dev libxml2 libz3-dev pkg-config python3 tzdata zlib1g-dev libc6
#RUN apt install -y clang clang-13 libicu-dev lld lldb llvm llvm-dev

RUN apt update && apt upgrade -y && apt install -y curl ca-certificates gnupg

#RUN curl -fsSL https://archive.swiftlang.xyz/swiftlang_repo.gpg.key | gpg --dearmor -o /usr/share/keyrings/swiftlang_repo.gpg.key
#RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/swiftlang_repo.gpg.key] https://archive.swiftlang.xyz/debian buster v5_6" | \
#    tee /etc/apt/sources.list.d/swiftlang.list > /dev/null
#RUN apt update && apt install -y swiftlang

RUN curl -s https://archive.swiftlang.xyz/install.sh | bash
RUN apt update && apt install -y swiftlang

ENV COMMAND='swift $SCRIPT'
