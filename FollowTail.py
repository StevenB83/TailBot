from twisted.internet.task import LoopingCall
from os import stat, fstat, path, listdir
import codecs

class FollowTail:
    fileObj = None

    def __init__(self, directory, base, callback, *a, **kw):
        self.encoding = 'utf-16'
        self.special_delim = ' ] '

        self.directory = directory
        self.base = base
        self.filename = self.find_file()
        print "Found file %s for %s" % (self.filename, base)
        assert path.exists(self.file_path())
        self.lc = LoopingCall(self.check)
        self.callback = callback
        self.a, self.kw = a, kw

    def start(self, checkFreq = 0.5):
        self.fileObj = codecs.open(self.file_path(), 'rb',
                                   encoding=self.encoding)
        self.fileObj.seek(0, 2)
        self.lc.start(checkFreq)

    def file_path(self):
        return path.join(self.directory, self.filename)

    def find_file(self):
        return max(f for f in listdir(self.directory) if self.base in f)

    def check(self):
        obj, callback, a, kw = self.fileObj, self.callback, self.a, self.kw
        obj.seek(obj.tell())
        for line in obj:
            line = line.strip()
            if self.special_delim not in line: continue
            line = line.split(self.special_delim, 1)[1]

            line = line.encode('utf-8')
            callback(line, self.base, *a, **kw)

        newfile = self.find_file()
        if newfile != self.filename:
            self.filename = newfile
            print "Switching to %s for %s" % (newfile, self.base)
            self.fileObj.close()
            self.fileObj = codecs.open(self.file_path(), 'rb',
                                       encoding=self.encoding)


    def stop(self):
        if self.lc.running:
            self.lc.stop()
        if self.fileObj:
            self.fileObj.close()
            self.fileObj = None

class ChainCallback:
    def __init__(self, *callbacks):
        self.callbacks = list(callbacks)

    def __call__(self, *a, **kw):
        for callback in self.callbacks:
            callback(*a, **kw)

    def addCallback(self, callback):
        self.callbacks.append(callback)

    def removeCallback(self, callback):
        if callback in self.callbacks:
            self.callbacks.remove(callback)
