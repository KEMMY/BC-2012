import pickle
import hashlib
import os
import sys
from stat import * 
import constants 

class BackupObject():
    
    @staticmethod
    def make_backup_object(pathname):
        mode = os.stat(pathname).st_mode
        if S_ISDIR(mode):
            # It's a directory
            return BackupDir(pathname)
        elif S_ISREG(mode):
            return BackupFile(pathname)
        else:
            # Unknown file 
            return None

    def __init__(self, pathname):
        print "Initializing BackupObject"
        print pathname
        self.source = pathname
        self.stat = os.stat(pathname)
        self.source_dir = os.path.dirname(pathname)
        self.target = constants.target_dir
        self.name = os.path.basename(pathname)

    def make_side_dict(self, hash_i):
        return_file_dict = {}
        return_file_dict['stat'] = self.stat
        return_file_dict['hash'] = hash_i
        return return_file_dict

    def initial_backup(self):
        #first Backup
        pass

    def file_rename(self, old_name, new_name):
        new_file_name = os.path.dirname(old_name) + '/'+ new_name
        os.rename(old_name,new_file_name)


class BackupFile(BackupObject):
    def __init__(self, pathname):
        print "Initializing BackupFile"
        print pathname
        BackupObject.__init__(self, pathname)

    
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

    def initial_backup(self):
        hash = self.file_copy()
        return self.make_side_dict(hash)

    def exist_backup(self):
        file_hash = self.make_hash(self.source)
        #print file_hash
        for F in os.listdir(self.target): # co s sprazdnym dir prebehne cyklus ?
            if F == file_hash:
                break
                return True
        return False
    
    def inc_backup(self):
        #print self.exist_backup()
        if self.exist_backup():
            print ('existuje')
            self.initial_backup()
            #dopln do slovnik :
            #self.source ziskaj base name
            #hladaj base name v slovnikoch
            #ak nasiel ak rodicov. adresar existuje a doplni
            
        else:
            print ('nexistuje')
        
        
class BackupDir(BackupObject):
    def __init__(self, pathname):
        print "Initializing BackupDir"
        print pathname
        BackupObject.__init__(self, pathname)

    def initial_backup(self):
        initial_dict = {}
        for F in os.listdir(self.source):
            next_path = os.path.join(self.source,F)
            new = BackupObject.make_backup_object(next_path)
            side_dict = new.initial_backup()
            initial_dict[F] = side_dict
        initial_dict[self.name] = self.pickling(initial_dict)
        print initial_dict
        return initial_dict
    
    def pickling(self, input_dict):
        hash_name = hashlib.sha1()
        pi = pickle.dumps(input_dict)
        hash_name.update(pi)
        tmp  = self.target + "/" + hash_name.hexdigest()
        with open(tmp,"wb") as DF:
            pickle.dump(input_dict,DF)
        return hash_name.hexdigest()

    def unpickling(self,file_name):
        unpkl_file = self.target + "/" + file_name
        with open(unpkl_file, "rb") as UPF:
            return_dict = pickle.loads(UPF)
        return return_dict
    

class BackupSymlink(BackupObject):
    def __init__(self, pathname, target):
        pass

    def initial_backup(self):
        pass
        

