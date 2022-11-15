if [ -f $experiment_root/gzip/inputs/testdir/file13.gz ]
then
  cp $experiment_root/gzip/inputs/testdir/file13.gz $experiment_root/gzip/outputs/test25 || { echo "$0: cp to output dir failed"; }
else
  cp $experiment_root/gzip/inputs/testdir/file13.z $experiment_root/gzip/outputs/test25 || echo "$0: cp to output dir failed";
fi

$experiment_root/gzip/testplans.alt/testscripts/cleanup.sh
