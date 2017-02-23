from subprocess import Popen, PIPE, STDOUT
from threading import Thread
import time
import sys
import os
import select
import sublime

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty


def find_executable():
    prefixs = os.getenv("PATH").split(':')
    for prefix in prefixs:
        try:
            os.stat(prefix + "/coqtop")
        except OSError:
            continue
        return prefix + "/coqtop"


class Coqtop:

    def __init__(self, manager, path):
        try:
            os.stat(path)
        except IOError:
            path = find_executable()
        if path is not None:
            if sys.platform.startswith('darwin'):
                self.proc = Popen([path], stdin=PIPE, stderr=STDOUT, stdout=PIPE, universal_newlines=True)
            elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
                self.proc = Popen([path], stdin=PIPE, stderr=STDOUT, stdout=PIPE, universal_newlines=True)
            else:
                self.proc = Popen([path], stdin=PIPE, stderr=STDOUT, stdout=PIPE, universal_newlines=True)
            self.manager = manager
            self.out_thread = Thread(target=self.receive)
            self.out_thread.daemon = True
            self.out_thread.start()
        else:
            sublime.error_message("Coqtop not found")

    def kill(self):
        self.proc.kill()

    def receive(self):
        while True:
            buf = ""
            while not buf.endswith(' < '):
                select.select([self.proc.stdout], [], [self.proc.stdout])
                try:
                    data = os.read(self.proc.stdout.fileno(), 256)
                    buf += data.decode(encoding='UTF-8')
                except OSError as e:
                    sublime.error_message(str(e))
                    pass
            if buf == "":
                continue
            if buf.find("\n") == -1:
                output = ""
                prompt = buf
            else:
                (output, prompt) = buf.rsplit("\n", 1)
            self.manager.receive(output, prompt)

    def send(self, statement):
        os.write(self.proc.stdin.fileno(), (statement + '\n').encode('utf-8'))
        self.proc.stdin.flush()
