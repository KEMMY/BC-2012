from backuper import *
import sys

def initial_backup(source_path, target_path):
    target = Target(target_path)#'/home/kmm/Plocha/target/new_target')
    back = NewBackup(source_path,target) # '/home/kmm/Plocha/source'
    back.backup()


def incremental_backup(source_path, target_path, time):
    target = Target(target_path)#'/home/kmm/Plocha/target/new_target')
    old_back = ExistingBackup(source_path, target, time)
    #'/home/kmm/Plocha/target/zaloha',target,'2013-04-29T21:00:42')
    inc_back = NewBackup(source_path,target,old_back)
    inc_back.backup()

def recovery_backup(source_path, target_path, time):
    target = Target(target_path)#'/home/kmm/Plocha/target/new_target')
    rec_back = ExistingBackup(source_path, target, time)
    #'/home/kmm/Plocha/target/zaloha',target,'2013-04-29T21:00:42') # treba vediet cas
    rec_back.recovery_backup()
    
def main(argv):
    print "Hello"
    if len(argv) > 3 and len(argv) < 6: # 4 - 6 argumentov
        if argv[1] == "init":
            if os.path.exists(argv[2]) :
                if os.path.exists(argv[3]):
                    initial_backup(argv[2],argv[3])
                else :
                    print "Neexistujuca cesta: " + argv[3]
            else :
                print "Neexistujuca cesta: " + argv[2]
            # argv[4] ak je ignorujem
                
        elif argv[1] == "inc":
            if os.path.exists(argv[2]) :
                if os.path.exists(argv[3]):
                    time_path = os.path.join(os.path.join(argv[3],"backups"), argv[4])
                    if os.path.exists(time_path):
                        incremental_backup(argv[2],argv[3], argv[4])
                    else :
                        print time_path
                        print "Neexistujuci cas zalohy:" + argv[4]
                else :
                    print "Neexistujuca cesta: " + argv[3]
            else :
                print "Neexistujuca cesta: " + argv[2]
            
            
        elif argv[1] == "rec":
            if os.path.exists(argv[3]) :
                time_path = os.path.join(os.path.join(argv[3],"backups"), argv[4])
                if os.path.exists(time_path):
                    recovery_backup(argv[2],argv[3], argv[4])
                else :
                    print "Neexistujuci cas zalohy: " + argv[4]
            else :
                print "Neexistujuca cesta: " + argv[3]

        else :
            print "'" + argv[1] +"' Neexistuje moznost -> vyber jednu z moznosti : 'init' - 'inc' - 'rec'"
            
    elif len(argv) > 5 :
        print "Privela argumentov"
    elif len(argv) < 4 :
        print "Malo argumentov"
    else :
        print "Nesprane argumenty" # sem sa ani nikdy nedostane
        
    #backup()
    #incremental_backup()
    #recovery_backup()

if  __name__ == "__main__":
    main(sys.argv) #od 1 po nevidim

#python main.py init /home/kmm/Plocha/source  /home/kmm/Plocha/target/new_target time
# pozor pri rec je 3 argument cesta kam obnovit zalohu
#python main.py rec /home/kmm/Plocha/target/zaloha  /home/kmm/Plocha/target/new_target latest
#python main.py init /home/kmm/Plocha/source  /home/kmm/Plocha/target/new_target time
# python main.py inc /home/kmm/Plocha/source  /home/kmm/Plocha/target/new_target latest

