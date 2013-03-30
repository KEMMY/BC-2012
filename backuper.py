import pickle
import hashlib
import os
import sys
from stat import *
from datetime import datetime as datum
import constants

# do buducna
class Target():
    def __init__(self, pathname):
        self.target_path = pathname
    def get_path(self):
        return self.target_path #volania napr. BackupObject.new...(... , target.get_path())

    def get_objects_path(self):
        return self.target_path + "objects/" 
    def get_backup_path(self):
        return self.target_path + "backups/"
    
class Backup():
        
    @staticmethod
    def _create_backup(source, target, backup_name = None):
        if backup_name == None :      
            return NewBackup(source, target)
        elif backup_name != None : #sem by som este dal kontrolu formatu
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
        pickled_dict = pickle.dumps(side_dict)
        file_name = self.target + "/backups/" + time
        with open(file_name,"wb") as BF:
            BF.write(pickled_dict)
            BF.close()
                        
    def get_backup(self, time):
        file_name = self.target + "/backups/" + time
        with open(file_name, "rb") as BF:
                load_dict=BF.read()
                BF.close()
        side_dict = pickle.loads(load_dict)
        return side_dict

    def initial_backup(self):
        # New
        pass
        
    def incremental_backup(self):
        # New / Latest Backup
        pass
        

class NewBackup(Backup):
    
        
    def __init__(self, source, target, backup_name = None):
        print "Initializing NewBackup"
        Backup.__init__(self, source, target, backup_name)

    def initial_backup(self):
        # vytvori novu zalohu
        new_object = SourceObject.create(self.source, self.target + "/objects/", None) 
        side_dict = new_object.initial_backup()
        self.make_backup(self.get_time(),side_dict) # self.get_time alebo self.time ?

    def incremental_backup(self):
        pass


class LatestBackup(Backup):
    
    def __init__(self, source, target, backup_name):
        print "Initializing LatestBackup"
        Backup.__init__(self, source, target, backup_name)

    def initial_backup(self):
        pass #?
        
    def incremental_backup(self):
        side_dict = self.get_backup(self.name)
        trg_object = TargetObject.create(self.source, self.target + "/objects" , side_dict)
        src_object = SourceObject.create(self.source,self.target + "/objects", trg_object)
        new_side_dict = src_object.incremental_backup()
        self.make_backup(self.time, new_side_dict)

        
class BackupObject():

    @staticmethod
    # TypeError: readonly attribute
    def make_lstat(lstat):
        print lstat
        lstat.st_dev = None
        lstat.st_nlink = None 
        lstat.st_atime = None
        return lstat

        
    def __init__(self, source, target, lstat):
        print "Initializing BackupObject"
        self.source = source
        self.target = target
        self.lstat = lstat # self.make_lstat(lstat) ... negunguje vid hore
        self.source_dir = os.path.dirname(source)
        self.name = os.path.basename(source)

    def make_side_dict(self, hash):
        return { 'lstat': self.lstat,
                 'hash': hash }

    def initial_backup(self):
        #first Backup
        pass

    def file_rename(self, old_name, new_name):
        new_file_name = os.path.dirname(old_name) + '/'+ new_name
        os.rename(old_name,new_file_name)
                
class SourceObject(BackupObject):
    
    @staticmethod
    def create(source, target, target_object):
        lstat = os.lstat(source)
        mode = lstat.st_mode
        if S_ISDIR(mode):
                return SourceDir(source, target, lstat, target_object)
        elif S_ISREG(mode):
                return SourceFile(source, target, lstat, target_object)
        elif S_ISLNK(mode):
                return SourceLnk(source, target, lstat, target_object)
        else:
                # Unknown file
                return None

    def __init__(self, source, target, lstat, target_object):
        print "Initializing SourceFile"
        print source
        BackupObject.__init__(self, source, target, lstat)
        self.target_object = target_object

    def make_hash(self, src_file, block_size = constants.CONST_BLOCK_SIZE):             
        file_hash = hashlib.sha1()
        with open(src_file, "rb") as SF :
            while True:
                block = SF.read(block_size)
                file_hash.update(block)
                if not block : break
        return file_hash.hexdigest()
        
    def exist_backup(self):
        file_hash = self.make_hash(self.source)
        return os.path.exists(self.target + file_hash)
    
    def compare_stat(self, object_stat, backuped_stat):
        return (object_stat.st_size == backuped_stat.st_size and #nezmenil velkost
                object_stat.st_uid == backuped_stat.st_uid and # nezmenil uziv
                object_stat.st_gid == backuped_stat.st_gid and # nezmenil skupinu
                object_stat.st_mtime == backuped_stat.st_mtime and # posledna modifikacia
                object_stat.st_mode == backuped_stat.st_mode and
                object_stat.st_ctime == backuped_stat.st_ctime) # last metadata change time 

class TargetObject(BackupObject):
        
    @staticmethod
    def create(source, target, side_dict):
        lstat = side_dict['lstat']
        mode = lstat.st_mode
        if S_ISDIR(mode):      
            return TargetDir(source, target, lstat, side_dict)
        elif S_ISREG(mode):
            return TargetFile(source, target, lstat, side_dict)
        elif S_ISLNK(mode):
            return TargetLnk(source, target, lstat, side_dict)
        else:
            # Unknown file
            return None

    def __init__(self, source, target, lstat, side_dict):
        print "Initializing TargetObject"
        print source
        BackupObject.__init__(self, source, target, lstat)
        self.side_dict = side_dict
        print self.side_dict
                
class SourceFile(SourceObject):
    
    def __init__(self, source, target, lstat, target_object):
        print "Initializing SourceFile"
        print source
        SourceObject.__init__(self, source, target, lstat, target_object)
                
    def file_copy(self, block_size = constants.CONST_BLOCK_SIZE):
        file_hash = hashlib.sha1()
        with open(self.source, "rb") as SF:
            
            target_file = self.target  + self.name
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
    
    def incremental_backup(self):
        # ak sa zmenil mtime, tak ma zmysel pozerat sa na obsah suboru
        # inak sa mozno zmenili zaujimave metadata
        if self.target_object != None:      
            if not self.exist_backup(): # ak ma target_object uz existuje v zalohe
                return self.initial_backup()
            else:
                if not self.compare_stat(self.lstat, self.target_object.lstat): # ak sa nerovnaju lstaty
                    if self.lstat.st_mtime == self.target_object.lstat.st_mtime:
                        # rovanky mtime
                        return self.target_object.side_dict
                    else:
                        # rozny mtime
                        new_hash = make_hash(self.source) # spocitaj hash a porovnaj
                        # uz skontroloval exist asi zbytocna vetva
                        if new_hash == self.target_object.side_dict[self.name]['hash']:
                            return self.target_object.side_dict
                        else: self.initial_backup()
                else: return self.target_object.side_dict # ak sa rovnaju staty
                    
                
class SourceDir(SourceObject):
        
    def __init__(self, source, target, lstat, target_object):
        print "Initializing SourceDir"
        print source
        SourceObject.__init__(self, source, target, lstat, target_object)
        if self.target_object != None: print self.target_object.side_dict

    def pickling(self, input_dict):
        hash_name = hashlib.sha1()
        pi = pickle.dumps(input_dict)
        hash_name.update(pi)
        tmp = self.target + "/" + hash_name.hexdigest()
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
                new_object = SourceObject.create(next_path, self.target, None) 
                side_dict = new_object.initial_backup()
                initial_dict[F] = side_dict
        print initial_dict
        hash = self.pickling(initial_dict)
        return self.make_side_dict(hash)

    def incremental_backup(self):
        incremental_dict = {}
        for F in os.listdir(self.source):
                next_path = os.path.join(self.source,F)
                if self.target_object != None:
                    oldF = self.target_object.get_object(F)
                    new = SourceObject.create(next_path,self.target,oldF)
                    side_dict = new.incremental_backup()
                    incremental_dict[F] = side_dict
                else:
                    side_dict = self.initial_backup()
                    incremental_dict[F] = side_dict
        print incremental_dict
        hash = self.pickling(incremental_dict)
        return self.make_side_dict(hash)
        
class SourceLnk(SourceObject):
        
    def __init__(self, source, target, lstat, target_object):
        print "Initializing SourceLnk"
        print source
        SourceObject.__init__(self, source, target, lstat, target_object)

    def make_lnk(self):
        link_target = os.readlink(self.source)
        hash_name = self.make_hash(link_target)
        file_name = self.target  + hash_name
        with open(file_name,"wb") as DF:
                DF.write(link_target)
        return hash_name
                
    def initial_backup(self):
                return self.make_side_dict(self.make_lnk())

    def incremental_backup(self):
        if self.target_object != None:
            
            if not self.exist_backup(): # ak uz existuje v zalohe
                return self.initial_backup()
            else:
                if not self.compare_stat(self.lstat, self.lstat): # ak sa nerovnaju lstaty
                    if self.lstat.st_mtime == self.target_object.lstat.st_mtime:
                        # rovanky mtime
                        return self.target_object.side_dict
                    else:
                        # rozny mtime
                        new_hash = make_hash(self.source) # spocitaj hash a porovnaj
                        # uz skontroloval exist asi zbytocna vetva
                        if new_hash == self.target_object.side_dict[self.name]['hash']:
                            return self.target_object.side_dict
                        else: self.initial_backup()
                else: return self.target_object.side_dict # ak sa rovnaju staty

class TargetFile(TargetObject):
    
    def __init__(self, source, target, lstat, side_dict):
        print "Initializing TargetFile"
        print source
        TargetObject.__init__(self, source, target, lstat, side_dict)

        
class TargetDir(TargetObject):
    
    def __init__(self, source, target, lstat, side_dict):
        print "Initializing TargetDir"
        print source
        TargetObject.__init__(self, source, target, lstat, side_dict)
        #print self.side_dict
                
    def get_object(self, name):
        # zisti, ci objekt "name" existuje v zalohovanej verzii
        # tohto adresara
        # ak ano, vyrobi prislusny TargetObject
        # ak nie, vrati None
        if name in self.side_dict:
            new_target = TargetObject.create(self.source, self.target, side_dict[name])
            return new_target_object 
        else: return None
        
class TargetLnk(TargetObject):
    
    def __init__(self, source, target, lstat, side_dict):
        print "Initializing TargetLnk"
        print source
        TargetObject.__init__(self, source, target, lstat, side_dict)

                                                         
        
