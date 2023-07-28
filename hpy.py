#!/usr/bin/env python3

import sys
import houseparty

hpmod = houseparty.readFile(sys.argv[1] if len(sys.argv) > 1 else 'test.hpy')
ir = houseparty.genIR(hpmod)

if len(sys.argv) > 2:
  with open(sys.argv[2], 'w') as f:
    f.write(str(ir))
else:
  print(ir)
