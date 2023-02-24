# nsb.api.notsocode
 NotSoCode Executor in Docker


Heavily inspired by https://github.com/engineer-man/piston, but we needed to be able to send files to the executor and read files back from it.


# limitations
the docker daemon doesn't like launching containers at the same time rapidly, looks like it can only handle 8 containers being launched at the same time. On an ovh vps it took about 17 seconds to process 200 executions at the same time, on a 7413 cpu it took 10 seconds. I do not think many people use this code execution api so this tradeoff is worth it for the customizability of npm/python packages and passing in/reading files in the executor.
