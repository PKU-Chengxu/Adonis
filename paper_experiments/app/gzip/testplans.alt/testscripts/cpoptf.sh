if [ -f $experiment_root/gzip/inputs/testdir/file3.gz ]
then
  cp $experiment_root/gzip/inputs/testdir/file3.gz $experiment_root/gzip/outputs/test13 || echo "$0:cp to output dir failed";
else
  cp $experiment_root/gzip/inputs/testdir/file3.z $experiment_root/gzip/outputs/test13 || echo "$0: cp to output dir failed";
fi

$experiment_root/gzip/testplans.alt/testscripts/cleanup.sh
