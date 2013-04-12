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
               
    def __init__(self, source_path, target_path, backup_name = None):
        #self.time = self.get_time() # zbytocne ?!
        self.source_path = source_path
        self.target_path = target_path
        self.name = backup_name # napr. 2012-12-12T12:12 / v tedy sa pouzije namiesot self.time
                
                
    def get_time(self):
        return datum.now().strftime('%Y-%m-%dT%H:%M:%S')

    def make_backup(self, time, side_dict):
        pickled_dict = pickle.dumps(side_dict)
        file_name = self.target_path + "/backups/" + time
        with open(file_name,"wb") as BF:
            BF.write(pickled_dict)
            BF.close()
                        
    def get_backup(self, time):
        file_name = self.target_path + "/backups/" + time
        with open(file_name, "rb") as BF:
                load_dict=BF.read()
                BF.close()
        side_dict = pickle.loads(load_dict)
        return side_dict

    def get_latest_time(self,backups_dir): # backups adresar
        max_time = '0000-00-00T00:00:00'
        for backup in os.listdir(backups_dir):
            if ( backup > max_time):
                max_time = backup
        return max_time

    def initial_backup(self):
        # New Backup
        pass
        
    def incremental_backup(self):
        # New / Existing Backup
        pass

    def recovery_backup(self):
        pass
        

class NewBackup(Backup): 
    #back = NewBackup('/home/kmm/Plocha/source',target.get_path()) + None     
    def __init__(self, source_path, target_path, backup_name = None):
        print "Initializing NewBackup"
        Backup.__init__(self, source_path, target_path, backup_name)

    def initial_backup(self):
        # vytvori novu zalohu
        new_object = SourceObject.create(self.source_path, self.target_path + "/objects/", None) 
        side_dict = new_object.initial_backup()
        self.make_backup(self.get_time(),side_dict) # self.get_time alebo self.time ?

    def incremental_backup(self):
        pass


class ExistingBackup(Backup):
    #nacitanie existujucich zaloh
    
    def __init__(self, source_path, target_path, backup_name):
        print "Initializing LatestBackup"
        Backup.__init__(self, source_path, target_path, backup_name)

    def initial_backup(self):
        pass 
        
    def incremental_backup(self):
        max_time = self.get_latest_time(self.target_path+"/backups")
        side_dict = self.get_backup(max_time)
        trg_object = TargetObject.create(self.source_path, self.target_path + "/backups", side_dict, self.name)
        src_object = SourceObject.create(self.source_path,self.target_path + "/objects", trg_object)
        new_side_dict = src_object.incremental_backup()
        self.make_backup(self.get_time(), new_side_dict)
    
    #Recovery = ExistingBackup('/home/kmm/Plocha/source',target.get_path(),'2013-03-29T18:57:12')
    #ktoru zalohu chceme obnovit sa bude rieit na urvovni scriptu nie samtotneho backupera
    # self.name obsahuje teraz 2013-29.... zaloha ktoru chcem obnovit
    # self.source - urcuje miesto kam chcem zalohu obnovit
    def recovery_backup(self):
        side_dict = self.get_backup(self.name)
        print side_dict
        recovery_obj = TargetObject.create(self.source_path, self.target_path + "/backups", side_dict, self.name)
        recovery_obj.recovery_backup()

        
class BackupObject():

    @staticmethod
    # TypeError: readonly attribute
    def make_lstat(lstat):
        print lstat
        lstat.st_dev = None
        lstat.st_nlink = None 
        lstat.st_atime = None
        return lstat

    def __init__(self, source_path, target_path, lstat):
        print "Initializing BackupObject"
        self.source_path = source_path
        self.target_path = target_path
        self.lstat = lstat # self.make_lstat(lstat) ... negunguje vid hore
        self.source_dir = os.path.dirname(source_path)
        self.name = os.path.basename(source_path)

    def make_side_dict(self, hash):
        return { 'lstat': self.lstat,
                 'hash': hash }

    def initial_backup(self):
        #first Backup
        pass
    def incremental_backup(self):
        pass

    def recovery_backup(self):
        pass

    def file_rename(self, old_name, new_name):
        new_file_name = os.path.join(os.path.dirname(old_name), new_name)
        os.rename(old_name,new_file_name)
                
class SourceObject(BackupObject):
    
    @staticmethod
    def create(source_path, target_path, target_object):
        lstat = os.lstat(source_path)
        mode = lstat.st_mode
        if S_ISDIR(mode):
                return SourceDir(source_path, target_path, lstat, target_object)
        elif S_ISREG(mode):
                return SourceFile(source_path, target_path, lstat, target_object)
        elif S_ISLNK(mode):
                return SourceLnk(source_path, target_path, lstat, target_object)
        else:
                # Unknown file
                return None

    def __init__(self, source_path, target_path, lstat, target_object):
        print "Initializing SourceFile"
        print source_path
        BackupObject.__init__(self, source_path, target_path, lstat)
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
    def create(source_path, target_path, side_dict, name):
        lstat = side_dict['lstat']
        mode = lstat.st_mode
        if S_ISDIR(mode):      
            return TargetDir(source_path, target_path, lstat, side_dict, name)
        elif S_ISREG(mode):
            return TargetFile(source_path, target_path, lstat, side_dict, name)
        elif S_ISLNK(mode):
            return TargetLnk(source_path, target_path, lstat, side_dict, name)
        else:
            # Unknown file
            return None

    def __init__(self, source_path, target_path, lstat, side_dict, name ):
        print "Initializing TargetObject"
        print source_path
        BackupObject.__init__(self, source_path, target_path, lstat)
        self.side_dict = side_dict
        print self.side_dict
        self.name = name # ???? self.name uz existuje v backupObject ako source_path basename
        print self.name
        
                
class SourceFile(SourceObject):
    
    def __init__(self, source_path, target_path, lstat, target_object):
        print "Initializing SourceFile"
        print source_path
        SourceObject.__init__(self, source_path, target_path, lstat, target_object)
                
    def file_copy(self, block_size = constants.CONST_BLOCK_SIZE):
        file_hash = hashlib.sha1()
        with open(self.source_path, "rb") as SF:
            
            target_file = self.target_path  + self.name
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
            if not self.compare_stat(self.lstat, self.target_object.lstat): # ak sa nerovnaju lstaty
                if (self.lstat.st_mtime == self.target_object.lstat.st_mtime
                    and self.lstat.st_size == self.target_object.lstat.st_size):
                    # rovanky mtime
                    # vyrob side dict stary hash + aktualny lstat
                    return self.make_dict(self.target_object.side_dict[self.name]['hash']) #stary hash
                else:
                    # rozny mtime
                    new_hash = make_hash(self.source_path) # spocitaj hash a porovnaj
                    if (new_hash == self.target_object.side_dict[self.name]['hash'] or os.path.exists(os.path.join(self.target,new_hash))):
                        return self.make_dict(new_hash)
                    else:
                        return self.initial_backup()
            else: return self.target_object.side_dict # ak sa rovnaju staty
        else:
            return self.initial_backup()
                    
                
class SourceDir(SourceObject):
        
    def __init__(self, source_path, target_path, lstat, target_object):
        print "Initializing SourceDir"
        print source_path
        SourceObject.__init__(self, source_path, target_path, lstat, target_object)
        if self.target_object != None: print self.target_object.side_dict

    def pickling(self, input_dict):
        hash_name = hashlib.sha1()
        pi = pickle.dumps(input_dict)
        hash_name.update(pi)
        if self.target_object != None and not os.path.exists(os.path.join(self.target, hash_name.hexdigest())): #and ...hashe sa nerovnaju...:
            tmp = os.path.join(self.target_path, hash_name.hexdigest())
            with open(tmp,"wb") as DF:
                    DF.write(pi)
                    DF.close()
        return hash_name.hexdigest()
        
    def initial_backup(self):
        initial_dict = {}
        for F in os.listdir(self.source_path):
                next_path = os.path.join(self.source_path,F)
                new_object = SourceObject.create(next_path, self.target_path, None) 
                side_dict = new_object.initial_backup()
                initial_dict[F] = side_dict
        print initial_dict
        hash = self.pickling(initial_dict)
        return self.make_side_dict(hash)

    def incremental_backup(self):
        #Metoda SourceDir.incremental_backup() je zmatocna.
        #Ak neexistuje self.target_object (teda stara cielova verzia aktualneho adresara),
        #metodu initial_backup() treba volat na podobjekt v adresari
        #(vytvoreny pomocou SourceObject.create(next_path,self.target,None)),
        #nie na (self teda na aktualny adresar). Takto spraveny incremental_backup()
        #bude potom v pripade neexistujuceho target_object fungovat rovnako
        #ako initial_backup() a teda nemusite mat dve metody
        #(ale podobne treba spravit aj incremental_backup() v SourceFile a SourceLnk).
        if self.target_object != None:      
            if not self.compare_stat(self.lstat, self.target_object.lstat): # ak sa nerovnaju lstaty
                if (self.lstat.st_mtime == self.target_object.lstat.st_mtime
                    and self.lstat.st_size == self.target_object.lstat.st_size):
                    # rovanky mtime
                    # vyrob side dict stary hash + aktualny lstat
                    return self.make_dict(self.target_object.side_dict[self.name]['hash']) #stary hash
                else:
                    # rozny mtime
                    new_hash = make_hash(self.source_path) # spocitaj hash a porovnaj
                    if (new_hash == self.target_object.side_dict[self.name]['hash'] or os.path.exists(os.path.join(self.target_path,new_hash))):
                        return self.make_dict(new_hash)
                    else:
                        return self.initial_backup()
            else: return self.target_object.side_dict # ak sa rovnaju staty
        else:
            return self.initial_backup()
        
class SourceLnk(SourceObject):
        
    def __init__(self, source_path, target_path, lstat, target_object):
        print "Initializing SourceLnk"
        print source_path
        SourceObject.__init__(self, source_path, target_path, lstat, target_object)

    def make_lnk(self):
        link_target = os.readlink(self.source_path)
        hash_name = self.make_hash(link_target)
        file_name = os.path.join(self.target_path, hash_name)
        with open(file_name,"wb") as DF:
                DF.write(link_target)
        return hash_name
                
    def initial_backup(self):
                return self.make_side_dict(self.make_lnk())

    def incremental_backup(self):
        if self.target_object != None:      
            if not self.compare_stat(self.lstat, self.target_object.lstat): # ak sa nerovnaju lstaty
                if (self.lstat.st_mtime == self.target_object.lstat.st_mtime
                    and self.lstat.st_size == self.target_object.lstat.st_size):
                    # rovanky mtime
                    # vyrob side dict stary hash + aktualny lstat
                    return self.make_dict(self.target_object.side_dict[self.name]['hash']) #stary hash
                else:
                    # rozny mtime
                    new_hash = make_hash(self.source_path) # spocitaj hash a porovnaj
                    if (new_hash == self.target_object.side_dict[self.name]['hash'] or os.path.exists(os.path.join(self.target_path,new_hash))):
                        return self.make_dict(new_hash)
                    else:
                        return self.initial_backup()
            else: return self.target_object.side_dict # ak sa rovnaju staty
        else:
            return self.initial_backup()

class TargetFile(TargetObject):
    
    def __init__(self, source_path, target_path, lstat, side_dict, name):
        print "Initializing TargetFile"
        print source_path
        TargetObject.__init__(self, source_path, target_path, lstat, side_dict, name)

    def recovery_backup(self,name):
        # reverse file_copy()
        file_name = os.path.join(self.target_path,self.side_dict['hash'])
        with open(file_name, "rb") as TF:
            recovery_file = os.path.join(self.source_path, name)
            with open(recovery_file, "wb") as RF:
                while True:
                    block = TF.read(block_size)
                    RF.write(block)
                    if not block:
                        break
            RF.close()
        TF.close()

        
class TargetDir(TargetObject):
    
    #Pomocou tejto metody treba nacitat slovnik objektov v adresari
    #do vhodnej instancnej premennej objektu triedy TargetDir napriklad v konstruktore.
    #Do tohto slovnika (nie do side_dict!) potom pristupuje metoda get_object().
    def __init__(self, source_path, target_path, lstat , side_dict, name):
        print "Initializing TargetDir"
        print source_path
        self.loaded_dict = self.unpickling(name,target_path)
        TargetObject.__init__(self, source_path, target_path, lstat, self.loaded_dict, name)
        #print self.side_dict
                
    def get_object(self, name):
        # zisti, ci objekt "name" existuje v zalohovanej verzii
        # tohto adresara
        # ak ano, vyrobi prislusny TargetObject
        # ak nie, vrati None
        if name in self.loaded_dict:
            new_target_object = TargetObject.create(self.source_path, self.target_path, loaded_dict[name],name)
            return new_target_object 
        else: return None

    def unpickling(self,file_name,target_path):
        unpkl_file = os.path.join(target_path, file_name)
        with open(unpkl_file, "rb") as UPF:
                pi = UPF.read()
                UPF.close()
        return_dict = pickle.loads(pi)
        print return_dict
        return return_dict

    def recovery_backup(self):
        #prejst slovnik
        # ak dir tak rekurzia
        #inak .recovery_backup
        #passdef recovery_backup(self):
        #for name ,  in self.side_dict.iteritems():
        # if IS_REG(self.side_dict[key]['lstat'].st_mode):    
        pass
    
class TargetLnk(TargetObject):
    
    def __init__(self, source_path, target_path, lstat, side_dict, name):
        print "Initializing TargetLnk"
        print source_path
        TargetObject.__init__(self, source_path, target_path, lstat, side_dict, name)


    def recovery_backup(self):
        link_target = os.readlink(self.target_path)
        file_name = self.target  + self.side_dict['name']
        with open(file_name,"wb") as DF:
                DF.write(link_target)
        return self.file_name

                                                         
        
