echo ">>>>>>>>running test 1"
../source/mb-server-cov > ../outputs/server-bad.log 2>&1 & sleep 1; ../source/test-bad > ../outputs/client-bad.log 2>&1
echo ">>>>>>>>running test 2"
../source/mb-server-cov > ../outputs/server-exception.log 2>&1 & sleep 1; ../source/test-exception > ../outputs/client-exception.log 2>&1
echo ">>>>>>>>running test 3"
../source/mb-server-cov > ../outputs/server-floats.log 2>&1 & sleep 1; ../source/test-floats > ../outputs/client-floats.log 2>&1
echo ">>>>>>>>running test 4"
../source/mb-server-cov > ../outputs/server-illegal.log 2>&1 & sleep 1; ../source/test-illegal > ../outputs/client-illegal.log 2>&1
echo ">>>>>>>>running test 5"
../source/mb-server-cov > ../outputs/server-init.log 2>&1 & sleep 1; ../source/test-init > ../outputs/client-init.log 2>&1
echo ">>>>>>>>running test 6"
../source/mb-server-cov > ../outputs/server-many.log 2>&1 & sleep 1; ../source/test-many > ../outputs/client-many.log 2>&1
echo ">>>>>>>>running test 7"
../source/mb-server-cov > ../outputs/server-rw.log 2>&1 & sleep 1; ../source/test-rw > ../outputs/client-rw.log 2>&1
echo ">>>>>>>>running test 8"
../source/mb-server-cov > ../outputs/server-slave.log 2>&1 & sleep 1; ../source/test-slave > ../outputs/client-slave.log 2>&1
