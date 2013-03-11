from backuper import *

def main():
    b = BackupObject('/home/kmm/Plocha/source/new/')
    print ("------ test stav. premenne ---------")
    print b.mode
    print b.name
    print b.source
    print b.source_dir
    print b.target
    print b.__class__
    print (b.initial_backup())
    '''#b.make_backup_object(b.source,b.target)
    if S_ISDIR(b.mode):
        print ("toto je adresar")
    elif S_ISREG(b.mode):
        print ("toto je subor")
    else :
        pass
    print ("---------- test file_copy ---------")
    print  b.file_copy()
    print ("---------- test make_side_dict ----")
    print (b.make_side_dict())
    print ("---------- teste make_file_dict ----")
    print (b.make_file_dict())
    print ("---")
    print ("---")
    print ("---unpickling file ------")
    print ("---")
    print (b.unpickling('850daf0f033d49bbe2bf936d512445602cefbb2d'))
    directory = BackupObject('/home/kmm/Plocha/source/new/directory1')
    print ("------ test stav. premenne ---------")
    print directory.mode
    print directory.name
    print directory.source
    print directory.source_dir
    print directory.target
    print directory.__class__
    b.make_backup_object(b.source,b.target)
    if S_ISDIR(directory.mode):
        print ("toto je adresar")
    elif S_ISREG(directory.mode):
        print ("toto je subor")
    else :
        pass
    
'''

if  __name__ == "__main__":
    main()
