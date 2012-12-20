import os
import pickle
import md5
import sys
from stat import *
import shutil
sys.path.append('/home/kmm/Plocha/python_code')



def hash_list(inputlist):
    output_list = []
    for L in inputlist:
        m = md5.new()
        m.update(L)
        output_list.append(m.digest())
    return output_list
    
def change_adress(path):     
    new_path = "/home/kmm/Plocha/target/zaloha" + path[23:]
    return new_path


def compare_file(src,trg):
    trgstat = os.stat(trg)
    srcstat = os.stat(src)
    if srcstat.st_ctime == trgstat.st_ctime and srcstat.st_mtime == trgstat.st_mtime:
        print(src + ":  Súbor bez zmeny")
        return True
    else:
        print(src + ":  Zmenený súbor")
        return False


def pickluj(stat):
    pkl_file = open("/home/kmm/Plocha/nove/piclujem.pkl","wb")
    pickle.dump(stat,pkl_file)
    pkl_file.close()
    

def walktree(src):
    list_zmien = []
    trg = change_adress(src)
    for f in os.listdir(src):
        pathname = os.path.join(src, f)
        mode = os.stat(pathname).st_mode
        if S_ISDIR(mode):
            # It's a directory
            dst = os.path.join(trg,f)
            walktree(pathname)

        elif S_ISREG(mode):
            abc = os.path.join(trg,f)
            x = compare_file(pathname,abc)
            if x == False : list_zmien.append(pathname)
        else:
            # Unknown file type, print a message
            print('Skipping %s' % pathname)
    return hash_list(list_zmien)            



adress = change_adress("/home/kmm/Plocha/source")
print adress
src="/home/kmm/Plocha/source" 
zmeny = walktree(src)
print zmeny

x = os.stat("/home/kmm/Plocha/nove/stats.txt")
pickluj(x)
