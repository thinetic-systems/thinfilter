

import time


class Expire(str):
    def __init__(self, txt):
        self.printable=self.__printable__()
        self=txt
        
        
    def __printable__(self):
        print "expire => human %s"%self
        if self != '':
            now=int(time.time())
            diff=now-int(self)
            return diff



a=Expire('0')
print a.printable
