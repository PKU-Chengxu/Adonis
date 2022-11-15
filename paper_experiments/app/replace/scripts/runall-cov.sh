mkdir -p ../outputs

echo ">>>>>>>>running test 1"
../source/replace-cov '-?' 'a&'  < ../inputs/temp-test/1.inp.1.1 > ../outputs/t1
echo ">>>>>>>>running test 2"
../source/replace-cov ' ' '@%@&'  < ../inputs/temp-test/777.inp.334.1 > ../outputs/t2
echo ">>>>>>>>running test 3"
../source/replace-cov ' ' 'NEW'  < ../inputs/temp-test/550.inp.238.1 > ../outputs/t3
echo ">>>>>>>>running test 4"
../source/replace-cov ' ' 'NEW'  < ../inputs/temp-test/551.inp.238.3 > ../outputs/t4
echo ">>>>>>>>running test 5"
../source/replace-cov ' ' 'rY NCDt+32Ilu>dr~s^1Q{0*{RLN>Muz'  < ../inputs/input/ruin.1224 > ../outputs/t5
echo ">>>>>>>>running test 6"
../source/replace-cov ' '  < ../inputs/input/ruin.1160 > ../outputs/t6
echo ">>>>>>>>running test 7"
../source/replace-cov ' *' '@%&a'  < ../inputs/temp-test/2298.inp.975.1 > ../outputs/t7
echo ">>>>>>>>running test 8"
../source/replace-cov ' *' 'a&'  < ../inputs/temp-test/1839.inp.782.1 > ../outputs/t8
echo ">>>>>>>>running test 9"
../source/replace-cov ' *' 'a&'  < ../inputs/temp-test/1840.inp.782.2 > ../outputs/t9
echo ">>>>>>>>running test 10"
../source/replace-cov ' *' 'a&'  < ../inputs/temp-test/1841.inp.782.3 > ../outputs/t10
echo ">>>>>>>>running test 11"
../source/replace-cov ' *-' '@t'  < ../inputs/temp-test/1828.inp.778.1 > ../outputs/t11
echo ">>>>>>>>running test 12"
../source/replace-cov ' *-' '@t'  < ../inputs/temp-test/1829.inp.778.2 > ../outputs/t12
echo ">>>>>>>>running test 13"
../source/replace-cov ' *-' '@t'  < ../inputs/temp-test/1830.inp.778.3 > ../outputs/t13
echo ">>>>>>>>running test 14"
../source/replace-cov ' *?' ''  < ../inputs/temp-test/1964.inp.834.1 > ../outputs/t14
echo ">>>>>>>>running test 15"
../source/replace-cov ' *?' ''  < ../inputs/temp-test/1965.inp.834.2 > ../outputs/t15
echo ">>>>>>>>running test 16"
../source/replace-cov ' *[0-9]-? [^a-c]@[*-^a-c]' ''  < ../inputs/temp-test/758.inp.325.1 > ../outputs/t16
echo ">>>>>>>>running test 17"
../source/replace-cov ' *[0-9]-? [^a-c]@[*-^a-c]' ''  < ../inputs/temp-test/759.inp.325.3 > ../outputs/t17
echo ">>>>>>>>running test 18"
../source/replace-cov ' *[0-9]@[[9-B]??[0-9]-[^-[^0-9]-[a-c][^a-c]' 'NEW'  < ../inputs/temp-test/1133.inp.487.1 > ../outputs/t18
echo ">>>>>>>>running test 19"
../source/replace-cov ' *[0-9]@[[9-B]??[0-9]-[^-[^0-9]-[a-c][^a-c]' 'NEW'  < ../inputs/temp-test/1134.inp.487.2 > ../outputs/t19
echo ">>>>>>>>running test 20"
../source/replace-cov ' *[9-B]' 'a&'  < ../inputs/temp-test/1274.inp.547.1 > ../outputs/t20
echo ">>>>>>>>running test 21"
../source/replace-cov ' *[9-B]' 'a&'  < ../inputs/temp-test/1275.inp.547.3 > ../outputs/t21
echo ">>>>>>>>running test 22"
../source/replace-cov ' *^-]-' '@n'  < ../inputs/temp-test/956.inp.412.1 > ../outputs/t22
echo ">>>>>>>>running test 23"
../source/replace-cov ' *^-]-' '@n'  < ../inputs/temp-test/957.inp.412.2 > ../outputs/t23
echo ">>>>>>>>running test 24"
../source/replace-cov ' *a-c]' '&a@%'  < ../inputs/temp-test/74.inp.32.1 > ../outputs/t24
echo ">>>>>>>>running test 25"
../source/replace-cov ' *a-c]' '&a@%'  < ../inputs/temp-test/75.inp.32.3 > ../outputs/t25
echo ">>>>>>>>running test 26"
../source/replace-cov ' -[][^9-B][a-c][9-B]' '@%&a'  < ../inputs/temp-test/529.inp.229.2 > ../outputs/t26
echo ">>>>>>>>running test 27"
../source/replace-cov ' -[^9-B]*$' '@%&a'  < ../inputs/temp-test/528.inp.229.1 > ../outputs/t27
echo ">>>>>>>>running test 28"
../source/replace-cov ' -[^9-B]*' '@%&a'  < ../inputs/temp-test/528.inp.229.1 > ../outputs/t28
echo ">>>>>>>>running test 29"
../source/replace-cov ' -[^9-B]?*'  < ../inputs/temp-test/528.inp.229.1 > ../outputs/t29
echo ">>>>>>>>running test 30"
../source/replace-cov ' -[^9-B][][a-c][9-B]' '@%&a'  < ../inputs/temp-test/528.inp.229.1 > ../outputs/t30
echo ">>>>>>>>running test 31"
../source/replace-cov ' -[^9-B][^][a-c][9-B]' '@%&a'  < ../inputs/temp-test/528.inp.229.1 > ../outputs/t31
echo ">>>>>>>>running test 32"
../source/replace-cov ' -[^9-B][a-c]*$' '@%&a'  < ../inputs/temp-test/529.inp.229.2 > ../outputs/t32
echo ">>>>>>>>running test 33"
../source/replace-cov ' -[^9-B][a-c]*' '@%&a'  < ../inputs/temp-test/529.inp.229.2 > ../outputs/t33
echo ">>>>>>>>running test 34"
../source/replace-cov ' -[^9-B][a-c]?*' '@%&a'  < ../inputs/temp-test/529.inp.229.2 > ../outputs/t34
echo ">>>>>>>>running test 35"
../source/replace-cov ' -[^9-B][a-c][9-B]'   < ../inputs/temp-test/529.inp.229.2 > ../outputs/t35
echo ">>>>>>>>running test 36"
../source/replace-cov ' -[^9-B][a-c][9-B]' '@%&a'  < ../inputs/temp-test/528.inp.229.1 > ../outputs/t36
echo ">>>>>>>>running test 37"
../source/replace-cov ' -[^9-B][a-c][9-B]' '@%&a'  < ../inputs/temp-test/529.inp.229.2 > ../outputs/t37
echo ">>>>>>>>running test 38"
../source/replace-cov ' -[^9-B][a-c][9-B]'  < ../inputs/temp-test/528.inp.229.1 > ../outputs/t38
echo ">>>>>>>>running test 39"
../source/replace-cov ' -[^][^9-B][a-c][9-B]' '@%&a'  < ../inputs/temp-test/529.inp.229.2 > ../outputs/t39
echo ">>>>>>>>running test 40"
../source/replace-cov ' -]' 'a@nb@tc'  < ../inputs/temp-test/1638.inp.698.1 > ../outputs/t40
echo ">>>>>>>>running test 41"
../source/replace-cov ' -c*[^a-c]' 'NEW'  < ../inputs/temp-test/477.inp.209.1 > ../outputs/t41
echo ">>>>>>>>running test 42"
../source/replace-cov ' -c*[^a-c]' 'NEW'  < ../inputs/temp-test/478.inp.209.2 > ../outputs/t42
echo ">>>>>>>>running test 43"
../source/replace-cov ' -c*[^a-c]' 'NEW'  < ../inputs/temp-test/479.inp.209.3 > ../outputs/t43
echo ">>>>>>>>running test 44"
../source/replace-cov ' ?' '&'  < ../inputs/temp-test/54.inp.23.1 > ../outputs/t44
echo ">>>>>>>>running test 45"
../source/replace-cov ' [a-c]' '&'  < ../inputs/temp-test/634.inp.274.1 > ../outputs/t45
echo ">>>>>>>>running test 46"
../source/replace-cov ' [a-c]' '&'  < ../inputs/temp-test/635.inp.274.2 > ../outputs/t46
echo ">>>>>>>>running test 47"
../source/replace-cov ' [a-c]' '&'  < ../inputs/temp-test/636.inp.274.3 > ../outputs/t47
echo ">>>>>>>>running test 48"
../source/replace-cov ' [a-c]' '&@n'  < ../inputs/temp-test/634.inp.274.1 > ../outputs/t48
echo ">>>>>>>>running test 49"
../source/replace-cov ' [a-c]' '&@n'  < ../inputs/temp-test/635.inp.274.2 > ../outputs/t49
echo ">>>>>>>>running test 50"
../source/replace-cov ' [a-c]' '&@n'  < ../inputs/temp-test/636.inp.274.3 > ../outputs/t50
echo ">>>>>>>>running test 51"
../source/replace-cov ' [a-c]' '&@nfoo'  < ../inputs/temp-test/635.inp.274.2 > ../outputs/t51
echo ">>>>>>>>running test 52"
../source/replace-cov ' ^a-]' 'NEW'  < ../inputs/temp-test/2186.inp.925.1 > ../outputs/t52
echo ">>>>>>>>running test 53"
../source/replace-cov ' ^a-]' 'NEW'  < ../inputs/temp-test/2187.inp.925.2 > ../outputs/t53
echo ">>>>>>>>running test 54"
../source/replace-cov '!$' '^'  < ../inputs/input/ruin.1470 > ../outputs/t54
echo ">>>>>>>>running test 55"
../source/replace-cov '!' 'JeQwMtQsX"@?#Q1)jO;[#@Y^SE,&N$~<>FK'  < ../inputs/input/ruin.677 > ../outputs/t55
echo ">>>>>>>>running test 56"
../source/replace-cov '!' '\-'  < ../inputs/input/ruin.1946 > ../outputs/t56
echo ">>>>>>>>running test 57"
../source/replace-cov '!' 'f)n'\'':Ig"_@4},'  < ../inputs/input/ruin.1784 > ../outputs/t57
echo ">>>>>>>>running test 58"
../source/replace-cov '!2' 4  < ../inputs/moni/f7.inp > ../outputs/t58
echo ">>>>>>>>running test 59"
../source/replace-cov '"' '6'  < ../inputs/input/ruin.197 > ../outputs/t59
echo ">>>>>>>>running test 60"
../source/replace-cov '"@@' 'm'  < ../inputs/input/ruin.1890 > ../outputs/t60
echo ">>>>>>>>running test 61"
../source/replace-cov '##[0-9]?[a-b]**' 'a'  < ../inputs/moni/f7.inp > ../outputs/t61
echo ">>>>>>>>running test 62"
../source/replace-cov '#' '&'  < ../inputs/input/ruin.1044 > ../outputs/t62
echo ">>>>>>>>running test 63"
../source/replace-cov '#' '&G:]y;Zm{7<\33O~h_JG:]y;Zm{7<\33O~h_JG:]y;Zm{7<\33O~h_JG:]y;Zm{7<\33O~h_JG:]y;Zm{7<\33O~h_JG:]y;Zm{7<\33O~h_JG:]y;Zm{7<\33O~h_JG:]y;Zm{7<\33O~h_JG:]y;Zm{7<\33O~h_J'  < ../inputs/input/ruin.1044 > ../outputs/t63
echo ">>>>>>>>running test 64"
../source/replace-cov '#' '_W$'  < ../inputs/input/ruin.1198 > ../outputs/t64
echo ">>>>>>>>running test 65"
../source/replace-cov '#8|G=x$)8Bi3&]|}0Ei%$sGmY={x{8WXO#8|G=x$)8Bi3&]|}0Ei%$sGmY={x{8WXO#8|G=x$)8Bi3&]|}0Ei%$sGmY={x{8WXO#8|G=x$)8Bi3&]|}0Ei%$sGmY={x{8WXO#8|G=x$)8Bi3&]|}0Ei%$sGmY={x{8WXO#8|G=x$)8Bi3&]|}0Ei%$sGmY={x{8WXO#8|G=x$)8Bi3&]|}0Ei%$sGmY={x{8WXO#8|G=x$)8Bi3&]|}0Ei%$sGmY={x{8WXO-[^--z]-[^a--b][^0-9]@* *?-c' '@n'  < ../inputs/temp-test/902.inp.388.1 > ../outputs/t65
echo ">>>>>>>>running test 66"
../source/replace-cov '$ -[^9-B][a-c][9-B]' '@%&a'  < ../inputs/temp-test/528.inp.229.1 > ../outputs/t66
echo ">>>>>>>>running test 67"
../source/replace-cov '$ -[^9-B][a-c][9-B]' '@%&a'  < ../inputs/temp-test/529.inp.229.2 > ../outputs/t67
echo ">>>>>>>>running test 68"
../source/replace-cov '$$**' 'a'  < ../inputs/moni/f7.inp > ../outputs/t68
echo ">>>>>>>>running test 69"
../source/replace-cov '$%**' 'a'  < ../inputs/moni/f7.inp > ../outputs/t69
echo ">>>>>>>>running test 70"
../source/replace-cov '$%-[@n][^a--b]$' 'NEW'  < ../inputs/temp-test/216.inp.96.11 > ../outputs/t70
echo ">>>>>>>>running test 71"
../source/replace-cov '$%? ' 'a@nb@tc'  < ../inputs/temp-test/218.inp.97.5 > ../outputs/t71
echo ">>>>>>>>running test 72"
../source/replace-cov '$%?@*' 'NEW'  < ../inputs/temp-test/523.inp.226.5 > ../outputs/t72
echo ">>>>>>>>running test 73"
../source/replace-cov '$%?^$' '@%&a'  < ../inputs/temp-test/513.inp.223.10 > ../outputs/t73
echo ">>>>>>>>running test 74"
../source/replace-cov '$%@*?' '@%&a'  < ../inputs/temp-test/199.inp.89.5 > ../outputs/t74
echo ">>>>>>>>running test 75"
../source/replace-cov '$%[^0-9]-?[9-B]?-[9-B]?' '@t'  < ../inputs/temp-test/527.inp.228.5 > ../outputs/t75
echo ">>>>>>>>running test 76"
../source/replace-cov '$'   < ../inputs/moni/f7.inp > ../outputs/t76
echo ">>>>>>>>running test 77"
../source/replace-cov '$' '%'  < ../inputs/input/ruin.1122 > ../outputs/t77
echo ">>>>>>>>running test 78"
../source/replace-cov '$' ''\''Z y<j$`3-b6{hC,KW4dJZ\tWkm'  < ../inputs/input/ruin.1104 > ../outputs/t78
echo ">>>>>>>>running test 79"
../source/replace-cov '$' 'F]"8mW1FGw`iK4QO;MuiQ4{%mW1FGw`iK4QO;MuiQ4{%mW1FGw`iK4QO;MuiQ4{%mW1FGw`iK4QO;MuiQ4{%`#tLmW1FGw`iK4QO;MuiQ4{%mW1FGw`iK4QO;MuiQ4{%mW1FGw`iK4QO;MuiQ4{%mW1FGw`iK4QO;MuiQ4{%mW1FGw`iK4QO;MuiQ4{%R:h2`^Ndy W4p?5Yd9N%7tp~'  < ../inputs/input/ruin.154 > ../outputs/t79
echo ">>>>>>>>running test 80"
../source/replace-cov '$' 'K'  < ../inputs/input/ruin.1121 > ../outputs/t80
echo ">>>>>>>>running test 81"
../source/replace-cov '$' 'Pb'  < ../inputs/input/ruin.1111 > ../outputs/t81
echo ">>>>>>>>running test 82"
../source/replace-cov '$' 'X'\'',id`ucU?Bhj!aeGJ~qW=F*9LTRouw#I-quWg}}wkR8Cwfff{{JGSTC2v7(*^3wSqSn{{\Jx9r8a'  < ../inputs/input/ruin.130 > ../outputs/t82
echo ">>>>>>>>running test 83"
../source/replace-cov '$' 'xv'\''%;99C.L6GYG|5'\''B4JA{:,!;i0:/n+[q}2g+Q+T[#; `w&%3:]~,5M]m.'  < ../inputs/input/ruin.1118 > ../outputs/t83
echo ">>>>>>>>running test 84"
../source/replace-cov '$- ' '&'  < ../inputs/temp-test/524.inp.227.1 > ../outputs/t84
echo ">>>>>>>>running test 85"
../source/replace-cov '$-'   < ../inputs/temp-test/215.inp.96.8 > ../outputs/t85
echo ">>>>>>>>running test 86"
../source/replace-cov '$-' '&@n'   < ../inputs/temp-test/215.inp.96.8 > ../outputs/t86
echo ">>>>>>>>running test 87"
../source/replace-cov '$-*[][^0-9]' '&'  < ../inputs/temp-test/201.inp.90.3 > ../outputs/t87
echo ">>>>>>>>running test 88"
../source/replace-cov '$-*[^0-9]$' '&'  < ../inputs/temp-test/202.inp.90.6 > ../outputs/t88
echo ">>>>>>>>running test 89"
../source/replace-cov '$-*[^0-9]' '&'  < ../inputs/temp-test/200.inp.90.1 > ../outputs/t89
echo ">>>>>>>>running test 90"
../source/replace-cov '$-*[^0-9]' '&'  < ../inputs/temp-test/201.inp.90.3 > ../outputs/t90
echo ">>>>>>>>running test 91"
../source/replace-cov '$-*[^0-9]' '&@n' < ../inputs/temp-test/201.inp.90.3 > ../outputs/t91
echo ">>>>>>>>running test 92"
../source/replace-cov '$-*[^0-9]'  < ../inputs/temp-test/201.inp.90.3 > ../outputs/t92
echo ">>>>>>>>running test 93"
../source/replace-cov '$-*[^][^0-9]' '&'  < ../inputs/temp-test/201.inp.90.3 > ../outputs/t93
echo ">>>>>>>>running test 94"
../source/replace-cov '$-[@n][^a--b]$' 'NEW'  < ../inputs/temp-test/215.inp.96.8 > ../outputs/t94
echo ">>>>>>>>running test 95"
../source/replace-cov '$-[@n][^a--b]' 'NEW'  < ../inputs/temp-test/213.inp.96.1 > ../outputs/t95
echo ">>>>>>>>running test 96"
../source/replace-cov '$-[@n][^a--b]' 'NEW'  < ../inputs/temp-test/214.inp.96.3 > ../outputs/t96
echo ">>>>>>>>running test 97"
../source/replace-cov '$-[][@n][^a--b]$' 'NEW'  < ../inputs/temp-test/215.inp.96.8 > ../outputs/t97
echo ">>>>>>>>running test 98"
../source/replace-cov '$-[^][@n][^a--b]$' 'NEW'  < ../inputs/temp-test/215.inp.96.8 > ../outputs/t98
echo ">>>>>>>>running test 99"
../source/replace-cov '$? ' 'a@nb@tc'  < ../inputs/temp-test/217.inp.97.1 > ../outputs/t99
echo ">>>>>>>>running test 100"
../source/replace-cov '$?-[^-z][0-9]' '&a@%'  < ../inputs/temp-test/224.inp.100.1 > ../outputs/t100