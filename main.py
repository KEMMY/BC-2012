from backuper import *

def initial_backup():
    print "class Target test"
    target = Target('/home/kmm/Plocha/target/new_target')
    print target.get_path()
    print ""
    print "//////////////////////TEST class Backup test NEWBACKUP/////////////////////////"
    print ""
    back = Backup._create_backup('/home/kmm/Plocha/source',target.get_path())
    print back.time
    print back.source
    print back.target
    print back.name
    print ""
    print "///////////////////////TEST class Backup LATESTBACKUP////////////////////////"
    print ""
    latest = Backup._create_backup('/home/kmm/Plocha/source',target.get_path(),'2013-03-29T18:57:12')
    print latest.time
    print latest.source
    print latest.target
    print latest.name
    print "///////////////////TEST class NEWBACKUP initial_backup//////////////////////////"
    os.mkdir (back.target + "/objects" )
    os.mkdir (back.target + "/backups" )
    back.initial_backup()


def incremental_backup():
    print "//////////////////////class Target test//////////////////////"
    target = Target('/home/kmm/Plocha/target/new_target')
    print target.get_path()
    print ""
    print "//////////////////////Start Incremental Backup/////////////////////////"
    print ""
    inc_back = Backup._create_backup('/home/kmm/Plocha/source',target.get_path(),'2013-03-30T23:02:42')
    print inc_back.time
    print inc_back.source
    print inc_back.target
    print inc_back.name
    inc_back.incremental_backup()
    
def main():
    print "Hello"
    #initial_backup()
    incremental_backup()

if  __name__ == "__main__":
    main()
