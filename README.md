# notsocode
 NotSoCode Executor in Docker


Heavily inspired by https://github.com/engineer-man/piston, but we needed to be able to send files to the executor and read files back from it.


# limitations
the docker daemon doesn't like launching containers at the same time rapidly, looks like it can only handle 8 containers being launched at the same time. On an ovh vps it took about 17 seconds to process 200 executions at the same time, on a 7413 cpu it took 10 seconds. I do not think many people use this code execution api so this tradeoff is worth it for the customizability of npm/python packages and passing in/reading files in the executor.


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

```
export SECRET=somethingsecret
notsocodeserver # will launch an http server at 0.0.0.0:8080, will be customizable in the future if needed
```

# environment variables

NotSoCode
```
NOTSOCODE_USER = 'notsocoder' # the user name for the docker user (including home directory)
NOTSOCODE_USER_UID = '42069' # the user id for the docker user

NOTSOCODE_SCRIPT_FILE = 'script' # the script filename inside the docker
NOTSOCODE_STDIN_FILE = 'stdin' # the stdin filename inside the docker

NOTSOCODE_PROCESS_MAX_FILES = 10 # the max amount of files we will extract from the container's /output
NOTSOCODE_PROCESS_MAX_MEMORY = '256m' # the max amount of memory a container can use before being killed

NOTSOCODE_PROCESS_ULIMIT_FILE_SIZE = (100 * 1024 * 1024) # the max file size a container can make at a time, they can create an infinite amount of these
NOTSOCODE_PROCESS_ULIMIT_FILES = 2048 # the max amount of files a container can make
NOTSOCODE_PROCESS_ULIMIT_PROCESSES = 128 # the max amount of processes a container can make

NOTSOCODE_DOCKER_TAG_PREPEND = 'notsocode'

DOCKER_BASE_URL = '' # incase you're running dind
```

NotSoCode Server
```
SECRET = '' # required, each request must have this secret in the 'authorization' header
```
