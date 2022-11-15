if [ -f $experiment_root/gzip/inputs/testdir/file21.gz ]
then
  cp $experiment_root/gzip/inputs/testdir/file21.gz $experiment_root/gzip/outputs/test33
else
  cp $experiment_root/gzip/inputs/testdir/file21.z $experiment_root/gzip/outputs/test33
fi

$experiment_root/gzip/testplans.alt/testscripts/cleanup.sh
