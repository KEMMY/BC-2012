import pickle
import hashlib
import os
import sys
from stat import * 
from datetime import datetime as datum
import constants

# do buducna
class Target():
    def __init__(pathname):
        self.target_path = pathname
    def get_path():
        return self.target_path # volania napr. BackupObject.new...(... , target.get_path())



class Backup():
    
    @staticmethod
    def _create_backup(source, target, backup_name):
        if backup_name == None :
            return NewBackup(source, target, backup_name)
        elif backup_name != None : # sem by som este dal kontrolu formatu
            return LatestBackup(source, target, backup_name)
        else:
            # Unknown Backup 
            return None
        
    def __init__(self, source, target, backup_name = None):
        self.time = self.get_time() # zbytocne ?!
        self.source = source
        self.target = target
        self.name = backup_name # napr. 2012-12-12T12:12 / v tedy sa pouzije namiesot self.time
        
        
    def get_time(self):
        return datum.now().strftime('%Y-%m-%dT%H:%M:%S')

    def make_backup(self, time, side_dict):
        pickled_dict = pickle.dumps(self.dict)
        file_name = self.target + "/backups/" + time
        with open(file_name,"wb") as BF:
            BF.write(pickled_dict)
            BF.close()
            
    def get_backup(self, time):
        file_name = self.target + "/backups/" + time
        with open(file_name, "rb") as BF:
            BF.read(load_dict)
            BF.close()
        side_dict = pickle.loads(load_dict)
        return side_dict

    def initial_backup(self):
        # New / Last Backup
        pass
    
    def incremental_backup(self):
        # New / Latest Backup
        pass
    

class NewBackup(Backup):
    
    def __init__(self, source, backup_name):
        print "Initializing NewBackup"
        print source
        Backup.__init__(self, source, backup_name)

    def initial_backup(self):
        # vytvori novu zalohu
        new_object = BackupObject.new_backup_object(self.source, self.target, self.target) # sem com chcel vsunut aj side_dict ako vstupny par. pri inite
        side_dict = new_object.initial_backup()
        self.make_backup(self.get_time(),side_dict) # self.get_time alebo self.time ?

    def incremental_backup(self):
        pass # todo


class LatestBackUp(Backup):

    def __init__(self, source, backup_name):
        print "Initializing LatestBackup"
        print source
        Backup.__init__(self, source, backup_name)

    def initial_backup(self):
        pass #?
    
    def incremental_backup(self):
        pass

    
class BackupObject():
    
    @staticmethod
    def _create_backup_object(pathname, target, stat, side_dict):
        mode = stat.st_mode
        if S_ISDIR(mode):
            return BackupDir(pathname, target, stat, side_dict)
        elif S_ISREG(mode):
            return BackupFile(pathname, target, stat, side_dict)
        elif S_ISLNK(mode):
            return BackupLnk(pathname, target, stat, side_dict)
        else:
            # Unknown file 
            return None

    @staticmethod
    def new_backup_object(pathname, target, side_dict):
        stat = os.stat(pathname)
        '''
        self.pathname = pathname
        self.target = target
        self.side_dict = side_dict ak nieje none ... ak je None ziska ho pri Initial_backup ?
        return BackupObject._create_backup_object(self.pathname, self.target, self.stat, self.side_dict)
        MULTIPLICITA premennych ???

        self. >>> @staticmethod nepouzivaju
        '''
        return BackupObject._create_backup_object( pathname, target,stat, side_dict)

    @staticmethod
    def existing_backup_object(pathname, target, side_dict):
        #stat = os.stat(pathname) >>> current stat netreba
        stat = side_dict['stat'] # ale side_dict musi byt vitiahnuty zo zalohy/slovnika
        return BackupObject._create_backup_object( pathname, target, stat ,side_dict)

    @staticmethod
    # existuje iba v zalohe
    def backup_only_object(pathname,side_dict):
        stat = side_dict['stat']
        # hore ?
        return BackupObject._create_backup_object(pathname, target, stat, side_dict)

    def __init__(self, pathname, stat, side_dict = None):
        print "Initializing BackupObject"
        print pathname
        self.source = pathname
        self.stat = stat
        self.side_dict = side_dict
        self.source_dir = os.path.dirname(pathname)
        self.target = constants.target_dir
        self.name = os.path.basename(pathname)

    def make_side_dict(self, hash):
        return { 'stat': self.stat,
                 'hash': hash }

    def initial_backup(self):
        #first Backup
        pass

    def file_rename(self, old_name, new_name):
        new_file_name = os.path.dirname(old_name) + '/'+ new_name
        os.rename(old_name,new_file_name)


class BackupFile(BackupObject):
    def __init__(self, pathname, target, stat, side_dict):
        print "Initializing BackupFile"
        print pathname
        BackupObject.__init__(self, pathname, target, stat, side_dict)

    
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
                TF.close()
            SF.close()
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
        for F in os.listdir(self.target):
            if F == file_hash:
                break
                return True
        return False

    
    def compare_stat(self, object_stat, backuped_stat):
        # pri zmene aspon jednej z mtime, uid, gid false inak true 
        if object_stat.st_mtime == backuped_stat.st_mtime :
            if object_stat.st_uid == backuped_stat.st_uid :
                 if object_stat.st_gid == backuped_stat.st_gid :
                     return True
                 else : return False
            else : return False
        else : return False
        
    def find_file_name(self, name, dir_dict): # rekurzivny prechod slovnikov hlada meno suboru a potom porovna stat
        file_dict = None
        for file_name in dir_dict.iterkeys():
            if file_name == name :
                if self.compare_stat(self.side_dict , dir_dict[file_name]): # ak nasiel a su rovnake staty
                    return dir_dict[file_name] .... file_copy update side_dict
            else : False
                
    
    def incremental_backup(self):
        pass
        
        
class BackupDir(BackupObject):
    def __init__(self, pathname):
        print "Initializing BackupDir"
        print pathname
        BackupObject.__init__(self, pathname)
    
    def pickling(self, input_dict):
        hash_name = hashlib.sha1()
        pi = pickle.dumps(input_dict)
        hash_name.update(pi)
        tmp  = self.target + "/" + hash_name.hexdigest()
        with open(tmp,"wb") as DF:
            DF.write(pi)
            DF.close()
        return hash_name.hexdigest()

    def unpickling(self,file_name):
        unpkl_file = self.target + "/" + file_name
        with open(unpkl_file, "rb") as UPF:
            UDF.read(pi)
            UDF.close()
        return_dict = pickle.loads(pi)
        return return_dict

    
    def initial_backup(self):
        initial_dict = {}
        for F in os.listdir(self.source):
            next_path = os.path.join(self.source,F)
            new = BackupObject.make_backup_object(next_path)
            side_dict = new.initial_backup()
            initial_dict[F] = side_dict
        print initial_dict
        hash = self.pickling(initial_dict)
        return self.make_side_dict(hash)

    def incremental_backup(self):
        pass
    

class BackupLnk(BackupObject):
    def __init__(self, pathname, target, side_dict):
        print "Initializing BackupLnk"
        print pathname
        BackupObject.__init__(self, pathname, target, side_dict)
    
    def make_hash(self, src_file, block_size = constants.CONST_BLOCK_SIZE):
        file_hash = hashlib.sha1()
        with open(src_file, "rb") as SF :
            while True:
                block = SF.read(block_size)
                file_hash.update(block)
                if not block : break
        return file_hash.hexdigest()


    def read_Lnk(self):
        return os.readlink(self.source)
    
    def make_Lnk(self, real_source):
        hash_name = self.make_hash(self.source)
        file_name = self.target + "/objects/" + hash_name
        with open(file_name,"wb") as DF:
            DF.write(real_source)
        return hash_name
        
    def initial_backup(self):
        # return self.make_side_dict(self.make_Lnk(self.read_Lnk()))
        hash_name = self.make_Lnk(self.read_Lnk())
        return self.make_side_dict(hash_name)
     
        