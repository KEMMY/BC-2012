from backuper import *

def backup():
    print "class Target test"
    target = Target('/home/kmm/Plocha/target/new_target')
    print target.get_path()
    print ""
    print "//////////////////////TEST class Backup test NEWBACKUP/////////////////////////"
    print ""
    back = NewBackup('/home/kmm/Plocha/source',target)
    print back.source_path
    print "///////////////////TEST class NEWBACKUP initial_backup//////////////////////////"
    back.backup()


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
    inc_back.backup()

def recovery_backup():
    print "//////////////////////class Target test//////////////////////"
    target = Target('/home/kmm/Plocha/target/new_target')
    print target.get_path()
    print ""
    print "//////////////////////Start Recovery Backup/////////////////////////"
    print ""
    rec_back = ExistingBackup('/home/kmm/Plocha/target/zaloha',target,'2013-04-23T01:22:35') # treba vediet cas
    print rec_back.source_path
    rec_back.recovery_backup()
    
def main():
    print "Hello"
    backup()
    #incremental_backup()
    #recovery_backup()

if  __name__ == "__main__":
    main()
