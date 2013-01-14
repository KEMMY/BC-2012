import pickle
import hashlib
import os
import sys
from stat import *



def MakeHashFromFile( FileName, BlockSize = 1024 ):
    FileHash = hashlib.sha1()
    with open(FileName, "r") as F:
        while True:
            Block = F.read(BlockSize)
            FileHash.update(Block)
            if not Block: break
    return FileHash.hexdigest()

#x = MakeHashFromFile('/home/kmm/Plocha/source/skuska_01/Python.png')
#y = MakeHashFromFile('/home/kmm/Plocha/source/skuska_01/subor_test')
#z = MakeHashFromFile('/home/kmm/Plocha/source/skuska_01/prednaska.pdf')
#print z
#print x
#print y

def FileCopy(source,target, BlockSize = 1024):
    SFile = open(source, "r") 
    TFile = open(target, "w") 
    with SFile as SF:
        while True:
            Block = SF.read(BlockSize)
            print Block
            TFile.write(Block)
            if not Block: break
    TFile.close()
    SFile.close()


#FileCopy('/home/kmm/Plocha/source/skuska_01/subor_test','/home/kmm/Plocha/target/skuska_01/Tsubor_test')
#FileCopy('/home/kmm/Plocha/source/skuska_01/Python.png','/home/kmm/Plocha/target/skuska_01/TPython.png')

def FileCopyWithHashRename(source,target, BlockSize = 1024):
    FileHash = hashlib.sha1()
    SFile = open(source, "r") 
    TFile = open(target, "w")
    with SFile as SF:
        while True:
            Block = SF.read(BlockSize)
            FileHash.update(Block)
            print Block
            TFile.write(Block)
            if not Block:
                break
    TFile.close()
    SFile.close()
    BaseName = FileHash.hexdigest()
    #print basename
    Path = os.path.dirname(target)
    #print path
    NewFileName = Path + '/'+ BaseName
    #print NewFileName
    os.rename(target,NewFileName)
    return FileHash.hexdigest()

#x = FileCopyWithHashRename('/home/kmm/Plocha/source/skuska_01/subor_test','/home/kmm/Plocha/target/skuska_01/Tsubor_test')
#y = FileCopyWithHashRename('/home/kmm/Plocha/source/skuska_01/Python.png','/home/kmm/Plocha/target/skuska_01/TPython.png')
#z = FileCopyWithHashRename('/home/kmm/Plocha/source/skuska_01/prednaska.pdf','/home/kmm/Plocha/target/skuska_01/Tprednaska.pdf')
#print x
#print y
#print z
    
