# -*- coding:utf-8 -*-

from heapq import heappush, heappop

class LogDump(object):
    def __init__(self,taskid):
        self.taskid = taskid

    def open(self):
        file=open('/tmp/deplog/%s.log'%self.taskid,'a')
        return file

    def dump(self,file,logstr):
        file.write(logstr)

    def close(self,file):
        file.close()

if __name__ == '__main__':
    logdunmp = LogDump('test_123')
    # file = logdunmp.open()
    # logdunmp.dump(file,'test')
    # file.close()
    #
    # file = logdunmp.open()
    # logdunmp.dump(file,'test')
    # file.close()
    #
    # file = logdunmp.open()
    # logdunmp.dump(file,'test')
    # file.close()

