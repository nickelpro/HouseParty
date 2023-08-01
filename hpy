#!/usr/bin/env python3

import sys
import houseparty

use_int = '--no-int' not in sys.argv
hpmod = houseparty.readFile(sys.argv[1 if use_int else 2])
ir = houseparty.genIR(hpmod, use_int)

if (use_int and len(sys.argv) > 2):
  with open(sys.argv[2], 'w') as f:
    f.write(str(ir))
elif (not use_int and len(sys.argv) > 3):
  with open(sys.argv[3], 'w') as f:
    f.write(str(ir))
else:
  print(ir)
