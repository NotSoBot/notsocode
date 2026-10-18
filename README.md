# notsocode
 NotSoCode Executor in Docker


Heavily inspired by https://github.com/engineer-man/piston, but we needed to be able to send files to the executor and read files back from it.


# limitations
the docker daemon doesn't like launching containers at the same time rapidly, looks like it can only handle 8 containers being launched at the same time. On an ovh vps it took about 17 seconds to process 200 executions at the same time, on a 7413 cpu it took 10 seconds. I do not think many people use this code execution api so this tradeoff is worth it for the customizability of npm/python packages and passing in/reading files in the executor.


# running the server
the server has to run on a linux x86_64 host with docker, as root: every job with network access gets its own docker network plus iptables (`DOCKER-USER` and `INPUT`) and `tc` rules. it refuses to start if docker's `DOCKER-USER` chain is missing. python 3.10+

1. install it editable from a checkout, the images are built from `notsocode/dockerfiles` next to the code and a normal `pip install` doesn't ship that folder
```
git clone https://github.com/notsobot/notsocode.git && cd notsocode
python3 -m venv .venv && .venv/bin/pip install -e '.[server]'
```

2. make a secret and put it in `.env` at the root of the checkout
```
echo "SECRET=$(openssl rand -hex 32)" > .env
```

3. start it, it listens on `0.0.0.0:8080`. the secret is the only thing guarding it, so firewall the port to whatever calls it
```
sudo .venv/bin/python -m notsocode_server
```

4. build the images ahead of time, otherwise each one builds on its first run (the gcc ones take a long while)
```
set -a && . ./.env && set +a  # loads SECRET into the shell
curl -X POST -H "authorization: $SECRET" http://localhost:8080/build/all  # starts the build
curl -H "authorization: $SECRET" http://localhost:8080/build/all  # waits for it, then gives per-language results
```

5. point notsobot.api at it with `NOTSOCODE_URL=http://<host>:8080` and `NOTSOCODE_TOKEN=<the same secret>`

endpoints (all need the `authorization` header): `GET /languages`, `GET /languages/example?language=`, `POST /execute` (form: `language`, `code`, optional `version`, `stdin`, `timeout`, `allow_network` and files), `POST /build`, `POST|GET /build/all`. a run that goes over its timeout comes back as a 408


# examples

by default, `execute` and `create_job` will try to build the images if the image isnt built already, will change in the future probably to error out if the image isn't built already (using `NotSoCode.build(Languages, version=)`)
```py
from notsocode import Languages, NotSoCode



async def test():
  job = await NotSoCode.create_job(Languages.PYTHON, 'print("OK")')
  response = await job.execute(timeout=10)
  # output is {language: {language-object}, result: {error, files, output}, version}
  print(response['result'])



async def test_with_files():
  job = await NotSoCode.create_job(
    Languages.NODE,
    'console.log(require("fs").readFileSync("./input/file.txt"))',
    version=Languages.NODE.default_version,
    files=[{'filename': 'file.txt', 'buffer': 'something'.encode()}],
  )
  response = await job.execute(timeout=10)
  print(response['result']['output'])



async def test_with_files_2():
  response = await NotSoCode.execute(
    Languages.BASH,
    'touch ./output/file{0001..0020}.txt',
  )
  # output will be [{'buffer', 'filename'}]
  print(response['result']['files']) # it will only save however much `NOTSOCODE_PROCESS_MAX_FILES` is set to, which is 10



async def test_with_stdin():
  response = await NotSoCode.execute(
    Languages.NODE,
    'console.log(require("fs").readFileSync(0))',
    stdin='Some stdin here',
  )
  print(response['result']['output']) # outputs 'Some stdin here'
```


# environment variables

NotSoCode
```
NOTSOCODE_USER = 'notsocoder' # the user name for the docker user (including home directory)
NOTSOCODE_USER_UID = '42069' # the user id for the docker user

NOTSOCODE_SCRIPT_FILE = 'script' # the script filename inside the docker
NOTSOCODE_STDIN_FILE = 'stdin' # the stdin filename inside the docker

NOTSOCODE_PROCESS_MAX_FILES = 10 # the max amount of files we will extract from the container's /output
NOTSOCODE_PROCESS_MAX_MEMORY = '2048m' # the max amount of memory a container can use before being killed
NOTSOCODE_PROCESS_MAX_STORAGE = '' # writable layer quota per container (e.g. '512m'), off by default since docker needs overlay2 on xfs with pquota for it
NOTSOCODE_PROCESS_MAX_TIMEOUT = 30 # the highest timeout (in seconds) the server accepts

NOTSOCODE_PROCESS_ULIMIT_FILE_SIZE = (100 * 1024 * 1024) # the max file size a container can make at a time
NOTSOCODE_PROCESS_ULIMIT_FILES = 2048 # the max amount of open files a container can have
NOTSOCODE_PROCESS_ULIMIT_PROCESSES = 512 # the max amount of processes a container can make (a per-container pids limit)

NOTSOCODE_PROCESS_MAX_CONNECTION_RATE = '3/sec' # new outbound connections a job can open
NOTSOCODE_PROCESS_MAX_CONNECTION_BURST = 5
NOTSOCODE_PROCESS_MAX_CONNECTION_SPEED = '160mbit' # bandwidth limit on the job's network

NOTSOCODE_NETWORK_MAINTENANCE_INTERVAL = 60 # how often (in seconds) stale job networks are pruned and their leftover firewall rules swept

NOTSOCODE_DOCKER_TAG_PREPEND = 'notsocode'

DOCKER_BASE_URL = '' # incase you're running dind
```

NotSoCode Server
```
SECRET = '' # required, each request must have this secret in the 'authorization' header
```
