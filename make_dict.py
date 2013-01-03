import pickle
import hashlib
import os
import sys
from stat import *
import shutil


    
ef pickluj(src_dict,path):
    path += ".pkl"
    pkl_file = open(path,"wb")
    str_dict = str(src_dict)
    # x = hashlib.sha1(str_dict) can't pickle HASH objects
    pickle.dump(str_dict,pkl_file)
    pkl_file.close()
    #os.renames(path,file_name)??? tento posledny krok nefunguje nechapem chybe interpretra


    # Skuska dict to string pomocov pikle

    
def make_dict(src):
    src_dict = {}
    for F in os.listdir(src):
        nextpath = os.path.join(src,F)
        mode = os.stat(nextpath).st_mode
        if S_ISREG(mode):
            stat = os.stat(nextpath)
            typ = "Blob"
            file_name = os.path.basename(nextpath)
            hash_file_name = hashlib.sha1(file_name) #iba skuska hashovania nazvu  
            value = str(mode) +" "+ typ + " " + str(hash_file_name) + " " + file_name
            src_dict[file_name] = value    
            
        else:
            # Directory or Unknown file type, print a message
            print('Skipping %s' % nextpath)
    pickluj(src_dict,src)
    print (src_dict)



make_dict('/home/kmm/Plocha/source')



            
    
