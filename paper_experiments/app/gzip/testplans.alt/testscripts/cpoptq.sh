if [ -f $experiment_root/gzip/inputs/testdir/file32.gz ]
then
  cp $experiment_root/gzip/inputs/testdir/file32.gz $experiment_root/gzip/outputs/test15 || echo "$0: cp to op dir failed";
else
  cp $experiment_root/gzip/inputs/testdir/file32.z $experiment_root/gzip/outputs/test15 || echo "$0: cp to op dir failed";
fi

$experiment_root/gzip/testplans.alt/testscripts/cleanup.sh
