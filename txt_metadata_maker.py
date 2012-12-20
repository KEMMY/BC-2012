import os



def file_maker(statinfo):
    log_file = open("/home/kmm/Plocha/nove/stats.txt",'w')
    txt = ""

    txt += 'Protection bits : '+ str(statinfo.st_mode) + "\n" #portection bits
    txt += "Inode number : "+ str(statinfo.st_ino) + "\n" # Inode number 
    txt += "Device :" + str(statinfo.st_dev) + "\n" # Zariadenie
    txt += "Number of hard links : " + str(statinfo.st_nlink) + "\n" # pocet hardlinkov  
    txt += "User ID of owner : " + str(statinfo.st_uid) + "\n" # userID
    txt += "Group ID of owner : " + str(statinfo.st_gid) + "\n" # Group ID
    txt += "Size of file : "+ str(statinfo.st_size) + "\n" # File size
    txt += "Time of most recent acces : "+ str(statinfo.st_atime) + "\n"# cas posledneho pristupu
    txt += "Time of most recent content modification : "+ str(statinfo.st_mtime) + "\n" # cas poseldnej zmeny
    txt += "Platform : " + str(statinfo.st_ctime) + "\n" # Linux or Win

    log_file.write(txt)
    log_file.close()


x = os.stat("/home/kmm/Plocha/nove")
print x
file_maker(x)    
