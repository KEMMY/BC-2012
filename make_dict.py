import pickle
import hashlib
import os
import sys
from stat import *
import shutil


import copy

def make_hash(o):
  if type(o) == type(object.__dict__):
    o2 = {}
    for k, v in o.items():
      if not k.startswith("__"):
        o2[k] = v
    o = o2 
    return hashlib.sha1(o)
  if isinstance(o, set) or isinstance(o, tuple) or isinstance(o, list):
      return tuple([make_hash(e) for e in o])    
  elif not isinstance(o, dict):
      return hashlib.sha1(o)
    
def pickluj(dictionary,path):
    file_name = make_hash(dictionary)
    path += ".pkl"
    pkl_file = open(path,"wb")
    pickle.dump(dictionary,pkl_file)
    pkl_file.close()
    #os.renames(path,file_name)??? tento posledny krok nefunguje nechapem chybe interpretra

    
def make_dict(src):
    dict = {'':''}
    for F in os.listdir(src):
        nextpath = os.path.join(src,F)
        mode = os.stat(nextpath).st_mode
        if S_ISREG(mode):
            stat = os.stat(nextpath)
            file_name = os.path.basename(nextpath)
            dict = {file_name : stat}    
            
        else:
            # Directory or Unknown file type, print a message
            print('Skipping %s' % nextpath)
    pickluj(dict,src)



make_dict('/home/kmm/Plocha/source')



            
    
