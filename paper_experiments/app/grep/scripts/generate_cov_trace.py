# this is a tiny script to generate coverage trace

import json
import subprocess
import os

app = 'grep'
test_script = 'runall-cov.sh'
test_targets = ['{}-cov.c'.format(app), 'dfa-cov.c', 'kwset-cov.c', 'regex-cov.c', 'search-cov.c']
result_dir = '../cov_trace'

def generate_json(targets, testno):
    objs = []
    for target in targets:
        file = open(target + '.gcov', 'r')
        obj = {'name': target}
        executed = []
        for line in file.readlines():
            row = line.split()
            if row[0] != '-:' and row[0] != '#####:':
                colon = row[1].find(':')
                executed.append(int(row[1][:colon]))
        obj['executed_lines'] = executed
        objs.append(obj)
        file.close()
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    with open('{}/trace_{:0>3d}.json'.format(result_dir, testno), 'w') as outfile:
        json.dump(objs, outfile)
        

def main():
    print("create output dir")
    os.system("mkdir -p ../outputs")
    script_file = open(test_script, 'r')
    test_cnt = 0
    for line in script_file.readlines():
        if line[0] == '#': continue # comments
        if line == '\n':
            continue
        if line.split()[0] == 'export':
            # set experiment root
            os.system(line)
            continue
        if line.split()[-1] != '2>&1':
            # new test case
            print(line, end='')
        else:
            # execute command
            subprocess.call(line, shell=True)
            test_cnt += 1
            os.chdir('../source')
            subprocess.call('gcov {}'.format(' '.join(test_targets)), shell=True)
            generate_json(test_targets, test_cnt)
            subprocess.call('rm *.gcda *.gcov', shell=True)
            os.chdir('../scripts')
    print('all tests done, {} tests performed'.format(test_cnt))

if __name__ == '__main__':
    main()

