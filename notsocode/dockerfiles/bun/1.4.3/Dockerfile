ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y unzip

WORKDIR /tmp
RUN mkdir -p ./build && cd ./build && wget "https://github.com/oven-sh/bun/releases/download/bun-v1.4.3/bun-linux-x64.zip" -q -O bun.zip && unzip -q bun.zip && \
	mv ./bun-linux-x64/bun /usr/local/bin/bun && cd ../ && rm -rf ./build

# same packages as the node images, in /home/node_modules: resolution walks up from the script in $HOME and
# finds them without NODE_PATH, and having a node_modules keeps bun from auto-installing from npm
RUN cd /home && echo '{}' > package.json && \
	BUN_INSTALL_CACHE_DIR=/tmp/bun-cache bun add --trust \
		jssoup@0.0.15 mathjs@15.2.0 imagescript@3.3.0 sharp@0.35.5 node-fetch@2.7.0 undici@8.12.2 redis@6.3.0 canvas@3.2.3 && \
	rm -rf /tmp/bun-cache

# runs .js and .ts alike
ENV COMMAND='bun run $SCRIPT'
