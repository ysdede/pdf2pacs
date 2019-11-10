# -*- coding: cp1254 -*-

import sys
import os
import colors, colorama

colorama.init()

root = 'Root'

print('Python %s on %s' % (sys.version, sys.platform))
print('sys.executable: %s' % sys.executable)
print('os.getcwd(): %s' % os.getcwd())

print('sys.path: %s' % sys.path)

print('Çözünürlük')

print('{}{}{}'.format(colors.bcolors.HEADER, root, colors.bcolors.ENDC))

print('{}{}{}'.format(colors.OKBLUE, root, colors.ENDC))