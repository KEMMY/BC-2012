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
        self.source = pathname
        self.stat = os.stat(pathname)
        self.source_dir = os.path.dirname(pathname)
        self.target = constants.target_dir
        self.name = os.path.basename(pathname)

    def make_side_dict(self, hash):
        return_file_dict = {}
        return_file_dict['stat'] = self.stat
        return_file_dict['hash'] = hash
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
        BackupObject.__init__(self, pathname)

    def initial_backup(self):
	hash = self.file_copy()
	return self.make_side_dict(hash)
    
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

        
class BackupDir(BackupObject):
    def __init__(self, pathname):
	print "Initializing BackupDir"
        BackupObject.__init__(self, pathname)

    def initial_backup(self):
        initial_dict = {}
        for F in os.listdir(self.source):
            next_path = os.path.join(self.source,F)
            new = BackupObject.make_backup_object(next_path)
	    side_dict = new.initial_backup()
	    # pridat novy zaznam do initial_dict
	# zapicklovat slovnik
	return # vratit side_dict pre tento adresar

    def pickling(self, input_dict):
	# pouzit pickle.dumps, najprv zhashovat potom ulozit vysledok
	# do suboru s hashovym menom
	pickled_dict = ""
	hash = ""
        tmp = self.target + "/" + hash
        with open(tmp,"wb") as PF:
            pickle.dump(input_dict,PF)
        return hash

    def unpickling(self,file_name):
        unpkl_file = self.target + "/" + file_name
        with open(unpkl_file, "rb") as UPF:
            return_dict = pickle.load(UPF)
        return return_dict
    

class BackupSymlink(BackupObject):
    def __init__(self, pathname, target):
        pass

    def initial_backup(self):
	pass
        
# pouzitie factory metody makeBackupObject:
#   foo = BackupObject.makeBackupObject("/home/kdslfsl","/fkfjkskf") target je const


