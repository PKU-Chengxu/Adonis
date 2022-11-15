#!/bin/sh
#*********************************************#
# This is a test to kill a process            #
#*********************************************#

echo
echo "Run break control"
echo

currentdir=`pwd`
user=`whoami`
cd
echo "`ps -u ${user} | grep allfile | awk '{print $1}'`"
pskill=`ps -u ${user} | grep allfile* | awk '{print $1}'`
echo $pskill
sleep 3
kill -9 $pskill

cp $experiment_root/gzip/inputs/testdir/binaryfile1* $experiment_root/gzip/outputs/test52
$experiment_root/gzip/testplans.alt/testscripts/cleanup.sh

cd $currentdir

echo
echo "Exit break control!"
echo

exit 0
