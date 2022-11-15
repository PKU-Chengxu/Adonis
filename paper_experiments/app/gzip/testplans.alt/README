8/14/08 - Wayne Motycka SIR
The v0.tsl.universe in this ($experiment_root/gzip/testplans.alt)
directory has 3 tests removed from the original version of this file
(v0.tsl.universe.orig) which caused false positive fault detection
problems when trying to reproduce the fault matrices found in the
$experiment_root/gzip/info directories.  As a result, the file
present in this directory has tests 37, 48 and 54 removed from
the original because each of these tests tries to redirect a bad
or nonexistent filename to gzip resulting in an error from the
shell that cannot be captured using the script created by the mts
MakeTestScript tool of the SIR.  Consequently, these tests are
remove from the universe but not from the v0.tsl file which
created the original v0.tsl.universe file.  This universe file
was used to re-create the fault matrix for v4 of gzip since a
bug was found in v4 with the fault insertion (#ifdef) logic for
fault FAULTY_F_KL_7.  Consequently, the fault matrix delivered
for v4 is delivered in 2 ways, the original fault matrix and
the new recreated one.

8/14/09 - Wayne M. @ SIR
The v0.tsl.universe file specifies in test 19 the --recurse command
line option which changed to --recursive beginning with v4 of the gzip
objects.  Consequently, the original v0.tsl.universe is linked to the
files v[1-3].tsl.universe in this directory and a new v4.tsl.universe
was created reflecting this change.  This new v4 universe file is also
the test universe for v5 and is linked to that universe file name.
This should maintain the ability to script the tests and reproduce the
fault matrix results with the gzip versions.
