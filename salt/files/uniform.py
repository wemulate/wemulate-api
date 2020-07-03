#!/bin/env python

# http://www.unixunique.com/2018/07/linux-network-emulator-custom-delay_9.html
# python3 uniform.py | awk 'ORS=NR%8?FS:RS' | tee > uniform.dist

for x in range(-32768, 32767, 4):
    print(x)