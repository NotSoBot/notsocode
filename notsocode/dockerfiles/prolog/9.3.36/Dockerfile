ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y \
	build-essential cmake ninja-build libarchive-dev libssl-dev zlib1g-dev libpcre2-dev libncurses-dev

WORKDIR /tmp
RUN mkdir -p ./swipl-src && cd ./swipl-src && \
	wget "https://www.swi-prolog.org/download/devel/src/swipl-9.3.36.tar.gz" -q -O swipl.tar.gz && \
	tar xvfz swipl.tar.gz --strip-components=1
RUN mkdir -p ./swipl-build && cd ./swipl-build && \
	cmake -G Ninja \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_INSTALL_PREFIX=/usr/local \
		-DSWIPL_PACKAGES_X=OFF \
		-DSWIPL_PACKAGES_JAVA=OFF \
		-DBUILD_TESTING=OFF \
		../swipl-src
RUN cd ./swipl-build && ninja && ninja install

ENV COMMAND_COMPILE='echo "user:message_hook(_, warning, Lines) :- print_message_lines(user_output, \"Warning: \", Lines)." > $HOME/init.pl'
ENV COMMAND='swipl --quiet -f $HOME/init.pl -s $SCRIPT -t "halt."'
