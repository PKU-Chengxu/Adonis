echo ">>>>>>>>running test 1"
echo 'abc' | ../source/grep -E -e 'abc' > /dev/null 2>&1
echo ">>>>>>>>running test 2"
echo 'xbc' | ../source/grep -E -e 'abc' > /dev/null 2>&1
echo ">>>>>>>>running test 3"
echo 'axc' | ../source/grep -E -e 'abc' > /dev/null 2>&1
echo ">>>>>>>>running test 4"
echo 'abx' | ../source/grep -E -e 'abc' > /dev/null 2>&1
echo ">>>>>>>>running test 5"
echo 'xabcy' | ../source/grep -E -e 'abc' > /dev/null 2>&1
echo ">>>>>>>>running test 6"
echo 'ababc' | ../source/grep -E -e 'abc' > /dev/null 2>&1
echo ">>>>>>>>running test 7"
echo 'abc' | ../source/grep -E -e 'ab*c' > /dev/null 2>&1
echo ">>>>>>>>running test 8"
echo 'abc' | ../source/grep -E -e 'ab*bc' > /dev/null 2>&1
echo ">>>>>>>>running test 9"
echo 'abbc' | ../source/grep -E -e 'ab*bc' > /dev/null 2>&1
echo ">>>>>>>>running test 10"
echo 'abbbbc' | ../source/grep -E -e 'ab*bc' > /dev/null 2>&1
echo ">>>>>>>>running test 11"
echo 'abbc' | ../source/grep -E -e 'ab+bc' > /dev/null 2>&1
echo ">>>>>>>>running test 12"
echo 'abc' | ../source/grep -E -e 'ab+bc' > /dev/null 2>&1
echo ">>>>>>>>running test 13"
echo 'abq' | ../source/grep -E -e 'ab+bc' > /dev/null 2>&1
echo ">>>>>>>>running test 14"
echo 'abbbbc' | ../source/grep -E -e 'ab+bc' > /dev/null 2>&1
echo ">>>>>>>>running test 15"
echo 'abbc' | ../source/grep -E -e 'ab?bc' > /dev/null 2>&1
echo ">>>>>>>>running test 16"
echo 'abc' | ../source/grep -E -e 'ab?bc' > /dev/null 2>&1
echo ">>>>>>>>running test 17"
echo 'abbbbc' | ../source/grep -E -e 'ab?bc' > /dev/null 2>&1
echo ">>>>>>>>running test 18"
echo 'abc' | ../source/grep -E -e 'ab?c' > /dev/null 2>&1
echo ">>>>>>>>running test 19"
echo 'abc' | ../source/grep -E -e '^abc$' > /dev/null 2>&1
echo ">>>>>>>>running test 20"
echo 'abcc' | ../source/grep -E -e '^abc$' > /dev/null 2>&1
echo ">>>>>>>>running test 21"
echo 'abcc' | ../source/grep -E -e '^abc' > /dev/null 2>&1
echo ">>>>>>>>running test 22"
echo 'aabc' | ../source/grep -E -e '^abc$' > /dev/null 2>&1
echo ">>>>>>>>running test 23"
echo 'aabc' | ../source/grep -E -e 'abc$' > /dev/null 2>&1
echo ">>>>>>>>running test 24"
echo 'acc' | ../source/grep -E -e 'ac*c' > /dev/null 2>&1
echo ">>>>>>>>running test 25"
echo 'adc' | ../source/grep -E -e 'ad*c' > /dev/null 2>&1
echo ">>>>>>>>running test 26"
echo 'abc' | ../source/grep -E -e 'a.c' > /dev/null 2>&1
echo ">>>>>>>>running test 27"
echo 'axc' | ../source/grep -E -e 'a.c' > /dev/null 2>&1
echo ">>>>>>>>running test 28"
echo 'axyzc' | ../source/grep -E -e 'a.*c' > /dev/null 2>&1
echo ">>>>>>>>running test 29"
echo 'axyzd' | ../source/grep -E -e 'a.*c' > /dev/null 2>&1
echo ">>>>>>>>running test 30"
echo 'aabcc' | ../source/grep -E -e 'abc$' > /dev/null 2>&1
echo ">>>>>>>>running test 31"
echo 'abcabc' | ../source/grep -E -e 'abc$' > /dev/null 2>&1
echo ">>>>>>>>running test 32"
echo 'cabc' | ../source/grep -E -e 'abc$' > /dev/null 2>&1
echo ">>>>>>>>running test 33"
echo 'abcd' | ../source/grep -E -e 'abc$' > /dev/null 2>&1
echo ">>>>>>>>running test 34"
echo 'acc' | ../source/grep -E -e 'ac*c' > /dev/null 2>&1
echo ">>>>>>>>running test 35"
echo 'abc' | ../source/grep -E -e 'ab?c' > /dev/null 2>&1
echo ">>>>>>>>running test 36"
echo 'abccc' | ../source/grep -E -e '^abc$' > /dev/null 2>&1
echo ">>>>>>>>running test 37"
echo 'abbbbc' | ../source/grep -E -e 'ab?bc' > /dev/null 2>&1
echo ">>>>>>>>running test 38"
echo '-' | ../source/grep -E -e 'ab?bc' > /dev/null 2>&1
echo ">>>>>>>>running test 39"
echo '-' | ../source/grep -E -e 'a[' > /dev/null 2>&1
echo ">>>>>>>>running test 40"
echo 'a]' | ../source/grep -E -e 'a]' > /dev/null 2>&1
echo ">>>>>>>>running test 41"
echo 'a]b' | ../source/grep -E -e 'a]b' > /dev/null 2>&1
echo ">>>>>>>>running test 42"
echo 'abbbbc' | ../source/grep -E -e 'ab*bc' > /dev/null 2>&1
echo ">>>>>>>>running test 43"
echo 'abd' | ../source/grep -E -e 'abcd' > /dev/null 2>&1
echo ">>>>>>>>running test 44"
echo 'adc' | ../source/grep -E -e 'a^-bc' > /dev/null 2>&1
echo ">>>>>>>>running test 45"
echo 'a-c' | ../source/grep -E -e 'a^-bc' > /dev/null 2>&1
echo ">>>>>>>>running test 46"
echo 'a]c' | ../source/grep -E -e 'a^b]c' > /dev/null 2>&1
echo ">>>>>>>>running test 47"
echo 'adc' | ../source/grep -E -e 'a^b]c' > /dev/null 2>&1
echo ">>>>>>>>running test 48"
echo 'abc' | ../source/grep -E -e 'ab|cd' > /dev/null 2>&1
echo ">>>>>>>>running test 49"
echo 'abcd' | ../source/grep -E -e 'ab|cd' > /dev/null 2>&1
echo ">>>>>>>>running test 50"
echo 'def' | ../source/grep -E -e '()ef' > /dev/null 2>&1