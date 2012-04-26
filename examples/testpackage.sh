#!/bin/sh

PYTHONPATH=$PYTHONPATH:~/src/pwang/pydsl python -c "import pydsl; pydsl.register(debug=True); import testpackage.test1"
echo "\n------ Contents of testpackage/test1.pydsl.out -------"
cat testpackage/test1.pydsl.out

