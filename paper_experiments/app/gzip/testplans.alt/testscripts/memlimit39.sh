#!/usr/bin/csh
echo ">>>>>>>>RUNNING TEST FROM SCRIPT"

limit memorysize 1300

${ARISTOTLE_DB_DIR}/versions/allfile.c.inst.exe -d  ${ARISTOTLE_DB_DIR}/inputs/gzfile/binary2.gz > ${ARISTOTLE_DB_DIR}/outputs/gzfile/binary2
cp ${ARISTOTLE_DB_DIR}/allfile13.c.tr ${ARISTOTLE_DB_DIR}/traces/39.tr

unlimit memorysize

