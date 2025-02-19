ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y build-essential cmake ninja-build libarchive-dev libssl-dev zlib1g-dev

WORKDIR /tmp
RUN mkdir -p build && cd ./build && wget "https://www.swi-prolog.org/download/devel/src/swipl-9.3.20.tar.gz" -q -O swipl.tar.gz && tar xvfz swipl.tar.gz --strip-components=1
RUN cd ./build && \
	cmake -G Ninja \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_INSTALL_PREFIX=/usr/local \
		-DSWIPL_PACKAGES_X=OFF \
		-DSWIPL_PACKAGES_JAVA=OFF \
		-DBUILD_TESTING=OFF \
		.
RUN cd ./build && ninja && ninja install

ENV COMMAND='swipl --quiet -s $SCRIPT'
