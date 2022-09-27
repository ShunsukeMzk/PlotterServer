import os
from datetime import datetime
from pathlib import Path

f = Path("_sample.txt")
print(f.stat())



def d(t):
    return datetime.fromtimestamp(t)

stat = os.stat("_sample.txt")

print(d(stat.st_ctime))
print(d(stat.st_atime))
print(d(stat.st_mtime))