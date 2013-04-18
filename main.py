
from backuper import *

def initial_backup():
    print "class Target test"
    target = Target('/home/kmm/Plocha/target/new_target')
    print target.get_path()
    print ""
    print "//////////////////////TEST class Backup test NEWBACKUP/////////////////////////"
    print ""
    back = NewBackup('/home/kmm/Plocha/source',target)
    print back.source_path
    print back.name
    print ""
    print "///////////////////////TEST class Backup LATESTBACKUP////////////////////////"
    print ""
    latest = ExistingBackup('/home/kmm/Plocha/source',target,'2013-03-29T18:57:12')
    print latest.source_path
    print latest.name
    print "///////////////////TEST class NEWBACKUP initial_backup//////////////////////////"
    back.initial_backup()


def incremental_backup():
    print "//////////////////////class Target test//////////////////////"
    target = Target('/home/kmm/Plocha/target/new_target')
    print target.get_path()
    print ""
    print "//////////////////////Start Incremental Backup/////////////////////////"
    print ""
    inc_back = ExistingBackup('/home/kmm/Plocha/source',target,'2013-04-11T23:56:07')
    print inc_back.source_path
    print inc_back.name
    inc_back.incremental_backup()

def recovery_backup():
    print "//////////////////////class Target test//////////////////////"
    target = Target('/home/kmm/Plocha/target/new_target')
    print target.get_path()
    print ""
    print "//////////////////////Start Recovery Backup/////////////////////////"
    print ""
    rec_back = ExistingBackup('/home/kmm/Plocha/target/zaloha',target,'2013-04-11T23:56:07')
    print rec_back.source_path
    print rec_back.name
    rec_back.recovery_backup()
    
def main():
    print "Hello"
    #initial_backup()
    #incremental_backup()
    recovery_backup()

if  __name__ == "__main__":
    main()
