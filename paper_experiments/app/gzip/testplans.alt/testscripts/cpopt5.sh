if [ -f $experiment_root/gzip/inputs/testdir/file18.gz ]
then
  cp $experiment_root/gzip/inputs/testdir/file18.gz $experiment_root/gzip/outputs/test30
else
  cp $experiment_root/gzip/inputs/testdir/file18.z $experiment_root/gzip/outputs/test30
fi

$experiment_root/gzip/testplans.alt/testscripts/cleanup.sh
