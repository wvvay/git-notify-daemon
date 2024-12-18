import time
mytime = time.time()
myhour = mytime.hour
mymin = mytime.min
if myhour == 0 and mymin == 0:
    print('It is midnight')
elif myhour < 12:
    print ('It is AM')
elif myhour == 12 and mymin == 0:
    print('It is noon')
else:
    print ('It is PM')