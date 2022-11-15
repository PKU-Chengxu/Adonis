#!/bin/bash

rm -rf $experiment_root/gzip/inputs
cp -r $experiment_root/gzip/inputs.alt $experiment_root/gzip/inputs || { echo "$0: Cannot replenish inputs directory"; exit 1; }
chmod -R u+w $experiment_root/gzip/inputs

chmod 000 $experiment_root/gzip/inputs/testdir/nopermissionfile || { echo "$0: Cannot change permission for nopermissionfile"; exit 1; }
