import pickle
import hashlib
import os
import sys
from stat import *
from datetime import datetime as datum
import constants

# do buducna
class Target():
    '''
Refaktorovat kod tak, aby namiesto stringu target_path pouzival objekt target triedy Target.
Jej metody zabezpecia pocitanie spravnych ciest k targetovym suborom
(napr. target.backup_path(nazov_zalohy) posklada cestu k suboru so zalohou,
target.object_path(hash) posklada cestu k suboru s objektom s danym hashom).
Trieda Target by mala vediet aj inicializovat novy target-ovy adresar
(teda vyrobit v nom objects/ a backups/).
    '''
    def __init__(self, pathname):
        self.target_path = pathname
        
    def init_target_dir(self):
        objects_path = os.path.join(self.target_path, "objects")
        if not os.path.exists(objects_path):
            os.mkdir(objects_path)
        backups_path = os.path.join(self.target_path, "backups")
        if not os.path.exists(backups_path):
            os.mkdir(backups_path)
    
    def get_path(self):
        return self.target_path #volania napr. BackupObject.new...(... , target.get_path())
    
    def get_backup_path(self, backup_name):
        backup_path = os.path.join(self.target_path, "backups")
        return os.path.join(backup_path , backup_name)

    def get_object_path(self, hash):
        object_path = os.path.join(self.target_path, "objects")
        return os.path.join(object_path,hash)

    def get_latest_path(self):
        latest_tmp_path = os.path.join(self.target_path,"backups")
        return os.path.join(latest_tmp_path, "latest")
        
    
class Backup():
               
    def __init__(self, source_path, target):
        #self.time = self.get_time() # zbytocne ?!
        self.source_path = source_path
        self.target = target
        #self.backup_time = existing_backup.max_time # napr. 2012-12-12T12:12 / v tedy sa pouzije namiesot self.time
                
                
    def get_time(self):
        return datum.now().strftime('%Y-%m-%dT%H:%M:%S')

    def make_backup(self, time, side_dict):
        pickled_dict = pickle.dumps(side_dict)
        file_name = self.target.get_backup_path(time)
        with open(file_name,"wb") as BF:
            BF.write(pickled_dict)
            BF.close()
                        
    def get_backup(self, time): 
        file_name = self.target.get_backup_path(time)
        with open(file_name, "rb") as BF:
                load_dict=BF.read()
                BF.close()
        side_dict = pickle.loads(load_dict)
        return side_dict

    def update_latest_backup(self,time):# neskor v target
        file_name = self.target.get_latest_path()
        with open(file_name, "wb") as LF:
            LF.write(time)
            LF.close()

    def read_latest_backup(self, target):# neskor v target
        file_name = target.get_latest_path()
        with open(file_name, "rb") as LF:
            time = LF.read()
            LF.close()
        return time

    
    def backup(self):
        # New Backup
        pass
 
    def recover(self):
        pass
        

class NewBackup(Backup):
    #back = NewBackup('/home/kmm/Plocha/source',target.get_path()) + None
    def __init__(self, source_path, target, existing_backup = None):
        print "Initializing NewBackup"
        self.existing_backup = existing_backup
        Backup.__init__(self, source_path, target) 

    def backup(self):
        # vytvori novu zalohu
        self.target.init_target_dir()
        if self.existing_backup == None:    
            trg_object =None
        else :
            trg_object = self.existing_backup.get_root_object()
        src_object = SourceObject.create(self.source_path, self.target, trg_object)
        new_side_dict = src_object.backup()
        backup_time = self.get_time()
        self.make_backup(backup_time, new_side_dict)
        self.update_latest_backup(backup_time)
    

class ExistingBackup(Backup):
    #nacitanie existujucich zaloh
    
    def __init__(self, source_path, target, backup_time):
        print "Initializing ExistingBackup"
        if backup_time == "latest":
            self.backup_time = self.read_latest_backup(target)
        else:
            self.backup_time = backup_time
        Backup.__init__(self, source_path, target)

    def backup(self):
        pass

    def get_root_object(self):
        side_dict = self.get_backup(self.backup_time)
        return TargetObject.create(self.source_path, self.target, side_dict)
        
    #Recovery = ExistingBackup('/home/kmm/Plocha/source',target.get_path(),'2013-03-29T18:57:12')
    #ktoru zalohu chceme obnovit sa bude rieit na urvovni scriptu nie samtotneho backupera
    # self.name obsahuje teraz 2013-29.... zaloha ktoru chcem obnovit
    # self.source - urcuje miesto kam chcem zalohu obnovit
    
    def recovery_backup(self):
        #max_time = self.get_latest_time(self.target)
        side_dict = self.get_backup(self.backup_time)
        print side_dict
        recovery_obj = TargetObject.create(self.source_path, self.target, side_dict)
        recovery_obj.recover()

        
class BackupObject():

    @staticmethod
    # TypeError: readonly attribute
    def make_lstat(lstat):
        print lstat
        lstat.st_dev = None
        lstat.st_nlink = None
        lstat.st_atime = None
        return lstat

    def __init__(self, source_path, target, lstat):
        print "Initializing BackupObject"
        self.source_path = source_path
        self.target = target
        self.lstat = lstat # self.make_lstat(lstat) ... nefunguje vid hore
        self.source_dir = os.path.dirname(source_path)
        self.name = os.path.basename(source_path)

    def make_side_dict(self, hash):
        return { 'lstat': self.lstat,
                 'hash': hash }

    def initial_backup(self):
        #first Backup
        pass
    def incremental_backup(self):
        # Incremental Backup
        pass

    def recover(self):
        # recovery Backup
        pass

    def file_rename(self, old_name, new_name):
        new_file_name = os.path.join(os.path.dirname(old_name), new_name)
        os.rename(old_name,new_file_name)
                
class SourceObject(BackupObject):
    
    @staticmethod
    def create(source_path, target, target_object):
        lstat = os.lstat(source_path)
        mode = lstat.st_mode
        if S_ISDIR(mode):
                return SourceDir(source_path, target, lstat, target_object)
        elif S_ISREG(mode):
                return SourceFile(source_path, target, lstat, target_object)
        elif S_ISLNK(mode):
                return SourceLnk(source_path, target, lstat, target_object)
        else:
                # Unknown file
                return None

    def __init__(self, source_path, target, lstat, target_object):
        print "Initializing SourceFile"
        print source_path
        BackupObject.__init__(self, source_path, target, lstat)
        self.target_object = target_object

        
    def exist_backup(self):
        file_hash = self.make_hash(self.source)
        return os.path.exists(self.target.get_object_path()) ####################################
    
    def compare_stat(self, object_stat, backuped_stat):
        return (object_stat.st_size == backuped_stat.st_size and #nezmenil velkost
                object_stat.st_uid == backuped_stat.st_uid and # nezmenil uziv
                object_stat.st_gid == backuped_stat.st_gid and # nezmenil skupinu
                object_stat.st_mtime == backuped_stat.st_mtime and # posledna modifikacia
                object_stat.st_mode == backuped_stat.st_mode and
                object_stat.st_ctime == backuped_stat.st_ctime) # last metadata change time

class TargetObject(BackupObject):
        
    @staticmethod
    def create(source_path, target, side_dict):
        print side_dict
        lstat = side_dict['lstat']
        mode = lstat.st_mode
        if S_ISDIR(mode):
            return TargetDir(source_path, target, lstat, side_dict)
        elif S_ISREG(mode):
            return TargetFile(source_path, target, lstat, side_dict)
        elif S_ISLNK(mode):
            return TargetLnk(source_path, target, lstat, side_dict)
        else:
            # Unknown file
            return None
        
    def recovery_stat(self, object_path, lstat):
        #os.lchmod(object_path, lstat.st_mode)  AttributeError: 'module' object has no attribute 'lchmod'
        try :
            time = lstat.st_atime, lstat.st_mtime
            os.utime(object_path, time)
        except OSError:
            pass
        try:
            os.chmod(object_path, S_IMODE(lstat.st_mode))
        except OSError:
            pass
        try:
            os.lchown(object_path, lstat.st_uid, lstat.st_gid)
        except OSError:
            pass # dolnit printy / handle exceptetion
        
    def __init__(self, source_path, target, lstat, side_dict ):
        print "Initializing TargetObject"
        print source_path
        BackupObject.__init__(self, source_path, target, lstat)
        self.side_dict = side_dict
        print self.side_dict
        print self.name
        
                
class SourceFile(SourceObject):
    
    def __init__(self, source_path, target, lstat, target_object):
        print "Initializing SourceFile"
        print source_path
        SourceObject.__init__(self, source_path, target, lstat, target_object)
                
    def file_copy(self, block_size = constants.CONST_BLOCK_SIZE):
        file_hash = hashlib.sha1()
        with open(self.source_path, "rb") as SF:
            target_file = self.target.get_object_path(self.name)
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

   
    def backup(self):
        # ak sa zmenil mtime, tak ma zmysel pozerat sa na obsah suboru
        # inak sa mozno zmenili zaujimave metadata
        if self.target_object != None:
            if not self.compare_stat(self.lstat, self.target_object.lstat): # ak sa nerovnaju lstaty
                if (self.lstat.st_mtime == self.target_object.lstat.st_mtime
                    and self.lstat.st_size == self.target_object.lstat.st_size):
                    # rovanky mtime
                    # vyrob side dict stary hash + aktualny lstat
                    return self.make_side_dict(self.target_object.side_dict['hash']) #stary hash
                else:
                    # rozny mtime
                    new_hash = self.make_hash(self.source_path) # spocitaj hash a porovnaj
                    if (new_hash == self.target_object.side_dict['hash']
                        or os.path.exists(self.target.get_object_path(new_hash))):
                        return self.make_side_dict(new_hash)
                    else:
                        hash = self.file_copy()
                        return self.make_side_dict(hash)
            else: return self.target_object.side_dict # ak sa rovnaju staty
        else:
            hash = self.file_copy()
            return self.make_side_dict(hash)
                    
                
class SourceDir(SourceObject):
        
    def __init__(self, source_path, target, lstat, target_object):
        print "Initializing SourceDir"
        print source_path
        SourceObject.__init__(self, source_path, target, lstat, target_object)
        if self.target_object != None: print self.target_object.side_dict

    def pickling(self, input_dict):
        pi = pickle.dumps(input_dict)
        hash_name = hashlib.sha1(pi).hexdigest()
        if (self.target_object == None
            or not os.path.exists(self.target.get_object_path(hash_name))): #or ...hashe sa nerovnaju...:
            tmp = self.target.get_object_path(hash_name)
            #print tmp
            #print pi
            with open(tmp,"wb") as DF:
                    DF.write(pi)
                    DF.close()
        return hash_name

    def backup(self):
        #Metoda SourceDir.incremental_backup() je zmatocna.
        #Ak neexistuje self.target_object (teda stara cielova verzia aktualneho adresara),
        #metodu initial_backup() treba volat na podobjekt v adresari
        #(vytvoreny pomocou SourceObject.create(next_path,self.target,None)),
        #nie na (self teda na aktualny adresar). Takto spraveny incremental_backup()
        #bude potom v pripade neexistujuceho target_object fungovat rovnako
        #ako initial_backup() a teda nemusite mat dve metody
        #(ale podobne treba spravit aj incremental_backup() v SourceFile a SourceLnk).
        main_dict = {}
        for F in os.listdir(self.source_path):
                next_path = os.path.join(self.source_path,F)
                if self.target_object != None:
                    oldF = self.target_object.get_object(F)
                else:
                    oldF = None
                new_object = SourceObject.create(next_path, self.target, oldF)
                side_dict = new_object.backup()
                main_dict[F] = side_dict
        print main_dict
        hash = self.pickling(main_dict)
        return self.make_side_dict(hash)
        
class SourceLnk(SourceObject):
        
    def __init__(self, source_path, target, lstat, target_object):
        print "Initializing SourceLnk"
        print source_path
        SourceObject.__init__(self, source_path, target, lstat, target_object)

    def make_lnk(self):
        link_target = os.readlink(self.source_path)
        hash_name = hashlib.sha1()
        hash_name.update(link_target)
        file_name = self.target.get_object_path(hash_name.hexdigest())
        with open(file_name,"wb") as DF:
                DF.write(link_target)
        return hash_name.hexdigest()
                
    #def initial_backup(self):
    #            return self.make_side_dict(self.make_lnk())

    def backup(self):
        if self.target_object != None:
            if not self.compare_stat(self.lstat, self.target_object.lstat): # ak sa nerovnaju lstaty
                if (self.lstat.st_mtime == self.target_object.lstat.st_mtime
                    and self.lstat.st_size == self.target_object.lstat.st_size):
                    # rovanky mtime
                    # vyrob side dict stary hash + aktualny lstat
                    return self.make_dict(self.target_object.side_dict[self.name]['hash']) #stary hash
                else:
                    # rozny mtime
                    link_target = os.readlink(self.source_path)
                    new_hash = hashlib.sha1(link_target).hexdigest() # spocitaj hash a porovnaj
                    if (new_hash == self.target_object.side_dict[self.name]['hash']
                        or os.path.exists(self.target.get_object_path(new_hash))):
                        return self.make_dict(new_hash)
                    else:
                        return self.make_side_dict(self.make_lnk())
            else: return self.target_object.side_dict # ak sa rovnaju staty
        else:
            return self.make_side_dict(self.make_lnk())

class TargetFile(TargetObject):
    
    def __init__(self, source_path, target, lstat, side_dict):
        print "Initializing TargetFile"
        print source_path
        TargetObject.__init__(self, source_path, target, lstat, side_dict)

    def recover(self, block_size = constants.CONST_BLOCK_SIZE):
        # reverse file_copy()
        file_name = self.target.get_object_path(self.side_dict['hash'])
        with open(file_name, "rb") as TF:
            #recovery_file = os.path.join(self.source_path)#name)
            with open(self.source_path, "wb") as RF:
                while True:
                    block = TF.read(block_size)
                    RF.write(block)
                    if not block:
                        break
                RF.close()
            TF.close()
        self.recovery_stat(self.source_path, self.side_dict['lstat'])


class TargetDir(TargetObject):
    
    #Pomocou tejto metody treba nacitat slovnik objektov v adresari
    #do vhodnej instancnej premennej objektu triedy TargetDir napriklad v konstruktore.
    #Do tohto slovnika (nie do side_dict!) potom pristupuje metoda get_object().
    def __init__(self, source_path, target, lstat , side_dict):
        print "Initializing TargetDir"
        print source_path
        #print target_path
        #print side_dict
        #path = os.path.join(target_path, side_dict['hash'])
        #print path
        self.loaded_dict = self.unpickling(target.get_object_path( side_dict['hash']))
        TargetObject.__init__(self, source_path, target, lstat, side_dict)
        #print self.side_dict
                
    def get_object(self, name):
        # zisti, ci objekt "name" existuje v zalohovanej verzii
        # tohto adresara
        # ak ano, vyrobi prislusny TargetObject
        # ak nie, vrati None
        if name in self.loaded_dict:
            new_target_object = TargetObject.create(os.path.join(self.source_path, name), self.target, self.loaded_dict[name])
            return new_target_object
        else: return None

    def unpickling(self, target_path):
        #unpkl_file = os.path.join(target_path, file_name)
        with open(target_path, "rb") as UPF:
                pi = UPF.read()
                UPF.close()
        return_dict = pickle.loads(pi)
        print return_dict
        return return_dict

    def recover(self):
        #prejst slovnik
        # ak dir tak rekurzia
        #inak .recovery_backup
        #passdef recovery_backup(self):
        #for name , in self.side_dict.iteritems():
        # if IS_REG(self.side_dict[key]['lstat'].st_mode):
        print "///////////////////////////////////////////////////////////////////////////////"
        if not os.path.exists(self.source_path):
            os.mkdir(self.source_path)
        for target_object_name in self.loaded_dict.iterkeys():
            new_target_object = self.get_object(target_object_name)
            new_target_object.recover()#os.path.join(self.source_path, target_object_name))
        # obnovit metadata adresara!!!!!!!!!!!
        self.recovery_stat(self.source_path, self.side_dict['lstat'])
    
class TargetLnk(TargetObject):
    
    def __init__(self, source_path, target, lstat, side_dict):
        print "Initializing TargetLnk"
        print source_path
        TargetObject.__init__(self, source_path, target, lstat, side_dict)

    def read_backuped_lnk(self):
        file_name = self.target.get_object_path(self.side_dict['hash'])
        with open(file_name, "rb") as TF:
            backuped_link_name = TF.read()
        return backuped_link_name

    def recovery_stat(self, object_path, lstat):
        try:
            os.lchown(object_path, lstat.st_uid, lstat.st_gid)
        except OSError:
            pass # dolnit printy / handle exceptetion

    def recover(self):
        os.symlink(self.read_backuped_lnk(), self.source_path )
        self.recovery_stat(self.source_path, self.side_dict['lstat'])
