# this is a tiny script to generate coverage trace

import json
import subprocess
import os

app = 'sqlite'
test_script = 'runall-cov.sh'
test_targets = ['sqlite3-cov.c', 'shell-cov.c', 'os-cov.c', 'vfs-cov.c']
result_dir = '../cov_trace'.format(app)
os.system("rm ../inputs/*.db")

def generate_json(targets, testno):
    objs = []
    for target in targets:
        file = open(target + '.gcov', 'r')
        obj = {'name': target}
        executed = []
        for line in file.readlines():
            row = line.split()
            if '-:' not in row[0] and '#####:' not in row[0]:
                # print(' '.join(row))
                if ":" in row[0]:
                    row_with_execute_info = row[0]
                else:
                    row_with_execute_info = row[1]
                # print(row_with_execute_info)
                # executed.append(int(row_with_execute_info.split(":")[1]))
                executed.append(int(line.split(":")[1]))
                # colon = row_with_execute_info.find(':')
                # executed.append(int(row[1][:colon]))
        obj['executed_lines'] = executed
        objs.append(obj)
        file.close()
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    with open('{}/trace_{:0>3d}.json'.format(result_dir, testno), 'w') as outfile:
        json.dump(objs, outfile)
    # time.sleep(20)
        

def main():
    script_file = open(test_script, 'r')
    test_cnt = 0
    for line in script_file.readlines():
        # print(line)
        # print(os.path.abspath(os.curdir))
        if line[0] == '#': continue # comments
        if line == '\n':
            continue
        if line.split()[0] == 'cd':
            os.chdir('../inputs')
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
            os.chdir('../inputs')
    print('all tests done, {} tests performed'.format(test_cnt))

if __name__ == '__main__':
    import time
    st = time.time()
    main()
    ed = time.time()
    print("time used:", ed - st)

