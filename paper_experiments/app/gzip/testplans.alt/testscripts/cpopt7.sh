if [ -f $experiment_root/gzip/inputs/testdir/file20.gz ]
then
  cp $experiment_root/gzip/inputs/testdir/file20.gz $experiment_root/gzip/outputs/test32
else
  cp $experiment_root/gzip/inputs/testdir/file20.z $experiment_root/gzip/outputs/test32
fi

$experiment_root/gzip/testplans.alt/testscripts/cleanup.sh
