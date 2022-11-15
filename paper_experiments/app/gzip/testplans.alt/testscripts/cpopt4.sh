if [ -f $experiment_root/gzip/inputs/testdir/file17.gz ]
then
  cp $experiment_root/gzip/inputs/testdir/file17.gz $experiment_root/gzip/outputs/test29
else
  cp $experiment_root/gzip/inputs/testdir/file17.z $experiment_root/gzip/outputs/test29
fi

$experiment_root/gzip/testplans.alt/testscripts/cleanup.sh
