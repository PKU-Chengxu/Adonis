# this is a tiny script to generate coverage trace

import json
import subprocess
import os

app = 'abc2mtex'
test_script = 'runall-cov.sh'
test_targets = ['{}-cov.c'.format(app), 'abc-cov.c', 'tex-cov.c', 'index-cov.c']
result_dir = '../cov_trace'.format(app)

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
    script_file = open(test_script, 'r')
    test_cnt = 0
    for line in script_file.readlines():
        if line[0] == '#': continue # comments
        if line == '\n':
            continue
        if line.split()[0] == 'mkdir':
            os.system(line)
            continue
        if line.split()[0] == 'echo':
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
            time.sleep(2)
            os.chdir('../scripts')
    print('all tests done, {} tests performed'.format(test_cnt))

if __name__ == '__main__':
    import time
    st = time.time()
    main()
    ed = time.time()
    print("time used:", ed - st)

