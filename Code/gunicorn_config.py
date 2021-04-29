"""
Gunicorn Config file for Bot Server
"""

import multiprocessing

preload_app = True
bind = '0.0.0.0:5000'
backlog = 2048
daemon = False
capture_output = True

workers = 2
worker_class = 'sync'
worker_connections = 1000
timeout = 400
keepalive = 2

errorlog = 'gunicorn_log.log'
loglevel = 'debug'
accesslog = 'access.log'


def on_starting(server):
    print("Gunicorn on_starting method is executed")
    print("Workers ", multiprocessing.cpu_count() * 2 + 1)
    print("No of CPU ", multiprocessing.cpu_count())


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def pre_fork(server, worker):
    pass


def pre_exec(server):
    server.log.info("Forked child, re-executing.")


def when_ready(server):
    server.log.info("Server is ready. Spawning workers")


def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

    ## get traceback info
    import threading, sys, traceback
    id2name = {th.ident: th.name for th in threading.enumerate()}
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# Thread: %s(%d)" % (id2name.get(threadId, ""),
                                            threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename,
                                                        lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    worker.log.debug("\n".join(code))


def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")
