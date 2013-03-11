import pickle
import hashlib
import os
import sys
from stat import * 
import constants 

class BackupObject():

    def __init__(self, pathname):
        self.source = pathname
        self.mode = os.stat(pathname).st_mode
        self.source_dir = os.path.dirname(pathname)
        self.target = constants.target_dir
        self.name = os.path.basename(pathname)
    
    def file_rename(self, old_name, new_name):
        new_file_name = os.path.dirname(old_name) + '/'+ new_name
        os.rename(old_name,new_file_name)

    def file_copy(self, block_size = constants.CONST_BLOCK_SIZE):
        file_hash = hashlib.sha1()
        with open(self.source, "rb") as SF:
            target_file = self.target + "/" + self.name
            with open(target_file, "wb") as TF:
                while True:
                    block = SF.read(block_size)
                    file_hash.update(block)
                    TF.write(block)
                    if not block:
                        self.file_rename(target_file,file_hash.hexdigest())
                        break
        return file_hash.hexdigest()

    def make_hash(self, src_file, block_size = constants.CONST_BLOCK_SIZE):
        file_hash = hashlib.sha1()
        with open(src_file, "rb") as SF :
            while True:
                block = SF.read(block_size)
                file_hash.update(block)
                if not block : break
        return file_hash.hexdigest()

    def pickling(self, input_dict):
        tmp = self.target + "/"+"tmp.pkl"
        with open(tmp,"wb") as PF:
            pickle.dump(input_dict,PF)
        new_name = self.make_hash(tmp)
        self.file_rename(tmp,new_name)
        return new_name

    def unpickling(self,file_name):
        unpkl_file = self.target + "/" + file_name
        with open(unpkl_file, "rb") as UPF:
            return_dict = pickle.load(UPF)
        return return_dict

    def make_side_dict(self):
        return_file_dict = {}
        file_stat = os.stat(self.source)
        return_file_dict['stat'] = file_stat
        return_file_dict['hash'] = self.file_copy()
        # ??? alebo make_hash() prob. existencie target
        return return_file_dict

    def make_file_dict(self):
        main_file_dict = {}
        main_file_dict[self.name] = self.make_side_dict()
        #self.pickling(main_file_dict)
        return main_file_dict
    
    def initial_backup(self):
        #first Backup
        initial_dict = {}
        for F in os.listdir(self.source):
            next_path = os.path.join(self.source,F)
            new = BackupObject(next_path)
            if S_ISREG(new.mode):
                initial_dict[new.name] = new.make_file_dict
            elif S_ISDIR(new.mode):
                new.initial_backup()
            else:
                break
            return initial_dict
        
        

    def make_backup_object(self,pathname, target):
        mode = os.stat(pathname).st_mode
        pass
        #if S_ISDIR(mode):
            # It's a directory
            #return BackupDir(pathname, target)
        #elif S_ISREG(self.mode):
            #return BackupFile(pathname, target)
        #else:
            # Unknown file 
           # return None

class BackupFile(BackupObject):
    def __init__(self, path):
        BackupObject.__init__(self, pathname, target)

    #def initial_backup(self):

        
class BackupDir(BackupObject):
    def __init__(self, pathname, target):
        BackupObject.__init__(self, pathname, target)

    #def initial_backup(self):

class BackupSymlink(BackupObject):
    def __init__(self, pathname, target):
        pass
        
# pouzitie factory metody makeBackupObject:
#   foo = BackupObject.makeBackupObject("/home/kdslfsl","/fkfjkskf") target je const



