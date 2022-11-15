if [ -f $experiment_root/gzip/inputs/testdir/file16.gz ]
then
  cp $experiment_root/gzip/inputs/testdir/file16.gz $experiment_root/gzip/outputs/test28
else
  cp $experiment_root/gzip/inputs/testdir/file16.z $experiment_root/gzip/outputs/test28
fi

$experiment_root/gzip/testplans.alt/testscripts/cleanup.sh
