filename = 'runall-cov.sh'
file = open(filename, 'w')
tests = []

for i in range(1, 40):
    tests.append('echo ">>>>>>>>running test {}"\n'.format(i))
    tests.append('cd ../inputs; bundle exec rake test TEST=cov-test{}.rb; cd ../scripts\n'.format(i))

file.writelines(tests)
file.close()