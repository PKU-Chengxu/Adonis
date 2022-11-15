# calculate LOC

import os


LOC = 0

for root, dirs, files in os.walk(".", topdown=False):
    for name in files:
        if name[-3:] == ".py":
            fp = open(os.path.join(root, name), "r")
            LOC += len(fp.readlines())

print(LOC)