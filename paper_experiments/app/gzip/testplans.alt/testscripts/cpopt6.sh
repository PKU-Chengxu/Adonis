if [ -f $experiment_root/gzip/inputs/testdir/file19.gz ]
then
  cp $experiment_root/gzip/inputs/testdir/file19.gz $experiment_root/gzip/outputs/test31
else
  cp $experiment_root/gzip/inputs/testdir/file19.z $experiment_root/gzip/outputs/test31
fi

$experiment_root/gzip/testplans.alt/testscripts/cleanup.sh
