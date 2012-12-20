import os
import sys
from stat import *
import shutil
import sys
sys.path.append('/home/kmm/Plocha/python_code')
import metadata_maker


def walktree(src,trg):
   
    for f in os.listdir(src):
        pathname = os.path.join(src, f)
        mode = os.stat(pathname).st_mode
        print (mode)
        if S_ISDIR(mode):
            # It's a directory
            print "os.mkdir(%s)" % (trg)
            dst = os.path.join(trg,f)
            os.mkdir(dst)
            walktree(pathname,dst)

        elif S_ISREG(mode):
            print (pathname)
            print "shutil.copy(%s,%s)" % (src,trg)
            abc = os.path.join(trg,f)
            shutil.copy(pathname,abc)            
        else:
            # Unknown file type, print a message
            print('Skipping %s' % pathname)

src="/home/kmm/Plocha/source/"
trg="/home/kmm/Plocha/target/zaloha"    
walktree(src,trg)
