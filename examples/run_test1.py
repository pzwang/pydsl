import sys
if len(sys.argv) < 3:
    print "Usage: run_test1.py min_age max_age"
    sys.exit()

import pydsl
pydsl.register(debug=True)

import test1
test1.sqlfunc(int(sys.argv[1]), int(sys.argv[2]))


