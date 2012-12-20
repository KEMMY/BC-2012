import pickle
import os

def pickluj(stat):
    pkl_file = open("/home/kmm/Plocha/nove/piclujem.pkl","wb")
    pickle.dump(stat,pkl_file)
    pkl_file.close()


x = os.stat("/home/kmm/Plocha/nove/stats.txt")
pickluj(x)
