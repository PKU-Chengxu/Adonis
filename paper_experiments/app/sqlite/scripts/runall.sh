mkdir -p ../outputs

cd ../inputs

echo ">>>>>>>>running test 1"
../source/sqlite cse.db < cse.sql > ../outputs/cse
echo ">>>>>>>>running test 2"
../source/sqlite fkey.db < fkey.sql > ../outputs/fkey
echo ">>>>>>>>running test 3"
../source/sqlite autoinc.db < autoinc.sql > ../outputs/autoinc
echo ">>>>>>>>running test 4"
../source/sqlite autoindex7.db < autoindex7.sql > ../outputs/autoindex7
echo ">>>>>>>>running test 5"
../source/sqlite analyze_G.db < analyze_G.sql > ../outputs/analyze_G
echo ">>>>>>>>running test 6"
../source/sqlite autoindex5.db < autoindex5.sql > ../outputs/autoindex5
echo ">>>>>>>>running test 7"
../source/sqlite analyze.db < analyze.sql > ../outputs/analyze
echo ">>>>>>>>running test 8"
../source/sqlite cost.db < cost.sql > ../outputs/cost
echo ">>>>>>>>running test 9"
../source/sqlite autoindex3.db < autoindex3.sql > ../outputs/autoindex3
echo ">>>>>>>>running test 10"
../source/sqlite close.db < close.sql > ../outputs/close
echo ">>>>>>>>running test 11"
../source/sqlite cffault.db < cffault.sql > ../outputs/cffault
echo ">>>>>>>>running test 12"
../source/sqlite autoindex6.db < autoindex6.sql > ../outputs/autoindex6
echo ">>>>>>>>running test 13"
../source/sqlite avfs.db < avfs.sql > ../outputs/avfs
echo ">>>>>>>>running test 14"
../source/sqlite date.db < date.sql > ../outputs/date
echo ">>>>>>>>running test 15"
../source/sqlite analyze_D.db < analyze_D.sql > ../outputs/analyze_D
echo ">>>>>>>>running test 16"
../source/sqlite cachespill.db < cachespill.sql > ../outputs/cachespill
echo ">>>>>>>>running test 17"
../source/sqlite atomic.db < atomic.sql > ../outputs/atomic
echo ">>>>>>>>running test 18"
../source/sqlite cast.db < cast.sql > ../outputs/cast
echo ">>>>>>>>running test 19"
../source/sqlite countofview.db < countofview.sql > ../outputs/countofview
echo ">>>>>>>>running test 20"
../source/sqlite descidx1.db < descidx1.sql > ../outputs/descidx1
echo ">>>>>>>>running test 21"
../source/sqlite analyze_E.db < analyze_E.sql > ../outputs/analyze_E
echo ">>>>>>>>running test 22"
../source/sqlite analyze_C.db < analyze_C.sql > ../outputs/analyze_C
echo ">>>>>>>>running test 23"
../source/sqlite descidx3.db < descidx3.sql > ../outputs/descidx3
echo ">>>>>>>>running test 24"
../source/sqlite checksize.db < checksize.sql > ../outputs/checksize
echo ">>>>>>>>running test 25"
../source/sqlite count.db < count.sql > ../outputs/count
echo ">>>>>>>>running test 26"
../source/sqlite coveridxscan.db < coveridxscan.sql > ../outputs/coveridxscan
echo ">>>>>>>>running test 27"
../source/sqlite descidx2.db < descidx2.sql > ../outputs/descidx2
echo ">>>>>>>>running test 28"
../source/sqlite boundary.db < boundary.sql > ../outputs/boundary
echo ">>>>>>>>running test 29"
../source/sqlite affinity2.db < affinity2.sql > ../outputs/affinity2
echo ">>>>>>>>running test 30"
../source/sqlite aggerror.db < aggerror.sql > ../outputs/aggerror
echo ">>>>>>>>running test 31"
../source/sqlite cacheflush.db < cacheflush.sql > ../outputs/cacheflush
echo ">>>>>>>>running test 32"
../source/sqlite columncount.db < columncount.sql > ../outputs/columncount
echo ">>>>>>>>running test 33"
../source/sqlite fallocate.db < fallocate.sql > ../outputs/fallocate
echo ">>>>>>>>running test 34"
../source/sqlite exists.db < exists.sql > ../outputs/exists
echo ">>>>>>>>running test 35"
../source/sqlite colmeta.db < colmeta.sql > ../outputs/colmeta
echo ">>>>>>>>running test 36"
../source/sqlite backcompat.db < backcompat.sql > ../outputs/backcompat
echo ">>>>>>>>running test 37"
../source/sqlite cast2.db < cast2.sql > ../outputs/cast2
echo ">>>>>>>>running test 38"
../source/sqlite cursorhint.db < cursorhint.sql > ../outputs/cursorhint
echo ">>>>>>>>running test 39"
../source/sqlite analyze1.db < analyze1.sql > ../outputs/analyze1
echo ">>>>>>>>running test 40"
../source/sqlite avtrans.db < avtrans.sql > ../outputs/avtrans
echo ">>>>>>>>running test 41"
../source/sqlite contrib01.db < contrib01.sql > ../outputs/contrib01
echo ">>>>>>>>running test 42"
../source/sqlite autoindex1.db < autoindex1.sql > ../outputs/autoindex1
echo ">>>>>>>>running test 43"
../source/sqlite cache.db < cache.sql > ../outputs/cache
echo ">>>>>>>>running test 44"
../source/sqlite btree1.db < btree1.sql > ../outputs/btree1
echo ">>>>>>>>running test 45"
../source/sqlite checkfault.db < checkfault.sql > ../outputs/checkfault
echo ">>>>>>>>running test 46"
../source/sqlite autoindex4.db < autoindex4.sql > ../outputs/autoindex4
echo ">>>>>>>>running test 47"
../source/sqlite check.db < check.sql > ../outputs/check
echo ">>>>>>>>running test 48"
../source/sqlite date2.db < date2.sql > ../outputs/date2
echo ">>>>>>>>running test 49"
../source/sqlite autoindex2.db < autoindex2.sql > ../outputs/autoindex2
echo ">>>>>>>>running test 50"
../source/sqlite cursorhint2.db < cursorhint2.sql > ../outputs/cursorhint2
echo ">>>>>>>>running test 51"
../source/sqlite atomic2.db < atomic2.sql > ../outputs/atomic2