#!/usr/bin/csh
echo ">>>>>>>>RUNNING TEST FROM SCRIPT"

limit memorysize 1290

${experiment_root}/gzip/versions/allfile.c.inst.exe -d  ${experiment_root}/gzip/inputs/gzfile/binary2.z > ${experiment_root}/gzip/outputs/gzfile/binary2
cp ${experiment_root}/gzip/allfile.c.tr ${experiment_root}/gzip/traces/37.tr

unlimit memorysize

