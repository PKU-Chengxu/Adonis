SUBJECT GZIP
============
The test suites are based on the functionalities of gzip. The base version
of gzip is 1.0.7

IMPORTANT NOTES
===============
* Before attempting to run this subject, set the environment variable
  'experiment_root' to point to the directory containing the gzip
  infrastructure directory (e.g. the directory containing the 'gzip'
  directory).
* There is a test case that exercises the functionality of gzip on a file
  that is 2GB in size. It is impractical to distribute such a file with the
  subject infrastructure, and we wish to avoid surprising the user by
  automatically generating such a file during the course of script
  execution by default. If you wish to use this test case, use one of the
  scripts '2gbfile.pl' or '2gbfile.py' found in the 'testplans.alt/testscripts'
  directory to generate the necessary file, and place it in 'inputs/testdir'.
  (Thanks to Ben Liblit, University of Wisconsin for the contribution of
  these scripts.)

GZIP DIRECTORY SETUP
====================

info - contains fault-matrices
inputs - contains input files
outputs - empty directory, holds temporary output files for current version
outputs.alt - directory for storing the output files for all versions of gzip
traces - empty directory, holds temporary trace files for current version
traces.alt - directory for storing the trace files for all versions of gzip
scripts - directory for scripts to run gzip experiment
testplans.alt - contains the universe file and testscripts 
versions.alt - contains versions.orig and versions.seeded

