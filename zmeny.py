import os


def change_adress(path): 
    new_path = "/home/kmm/Plocha/target/zaloha" + path[23:]
    return new_path


def compare_file(path):
    target = change_adress(path)
    trg = os.stat(target)
    src = os.stat(path)
    if src.st_size == trg.st_size:
        print("Súbor bez zmeny")
        return True
    else:
        print("Zmenený súbor")
        return False
     

x = change_adress("/home/kmm/Plocha/source/subor1")
print(x)
compare_file("/home/kmm/Plocha/source/subor1")
