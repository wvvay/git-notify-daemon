
from sys import argv
import tarfile
from datetime import datetime
import os

now = datetime.now()
current_date = "{}.{}.{}-{}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute,now.second)
print(argv[1]+'__'+current_date)
tar = tarfile.open(argv[1]+'_'+current_date,mode='w')
dir ='/home/kovalenko/'
for file in os.listdir(dir):
	f = os.path.join(file)
	if os.path.isfile(f) and f.endswith('.txt'):
		tar.add(f)
