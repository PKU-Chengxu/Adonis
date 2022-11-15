# A simple scripts to generate hooking library for the given binary
app = "grep"
print("A simple scripts to generate function trace for", app)

from glob import glob
import json
import subprocess
import threading
import os
import time
import argparse
import sys

root_dir = "../"
res_dir = "../function_trace".format(app)

def main():
    global app
    global root_dir
    global res_dir

    try:
        os.mkdir(res_dir)
    except FileExistsError:
        pass

    proxy_lib = os.path.join(root_dir, "source/{}-decompile-hooking.so".format(app))
    if not os.path.exists(proxy_lib):
        generate_hooking_dir = "../../../../hooking/"
        print("cannot find the proxy lib in", proxy_lib)
        print("generate proxy lib using generate_hooking.py in {}".format(os.path.abspath(generate_hooking_dir)))
        saved_cur_dir = os.path.abspath(os.path.curdir)
        os.chdir(generate_hooking_dir)
        cmd = "python generate_hooking.py -f {}/../source/{}".format(saved_cur_dir, app)
        print("generate function hooking for {}/../source/{}".format(saved_cur_dir, app))
        os.system(cmd)

        os.chdir(saved_cur_dir)
        if not os.path.exists(proxy_lib):
            print("generate hooking failed.")
            print("cmd: ", cmd)
            print("please see the documents in {} to manually run the generating hooking script".format(os.path.abspath(generate_hooking_dir)))
            exit()
        else:
            print("generate hooking success.")
            print("continue to generate function trace.")
            os.chdir(saved_cur_dir)
    function_hook_run(app, proxy_lib)


def function_hook_run(app, proxy_lib):
    global root_dir
    global res_dir
    hooking_cmd = "LD_PRELOAD=" + proxy_lib
    cmd_collection = {}
    print("=========== generating function traces for {} ===========".format(app))
    # create trace dir 
    trace_dir = res_dir 
    try:
        os.system("mkdir -p " + trace_dir)
    except FileExistsError:
        pass

    # extract test cmd according to the scriptR0.sh
    test_cmd = []
    fp = open("runall.sh", "r")
    start_flag = False
    cur_cmd = ""
    for l in fp.readlines():
        if l.split()[-1] != '2>&1':
            start_flag = True
            if cur_cmd != "":
                test_cmd.append(cur_cmd.strip().replace("| ", "| "+ hooking_cmd + " "))
            cur_cmd = ""
            continue
        if start_flag:
            cur_cmd += l
    test_cmd.append(cur_cmd.strip().replace("| ", "| "+ hooking_cmd + " "))
    
    # save cmd
    print("saving test case commands...")
    cmd_collection[app] = [_ for _ in test_cmd]
    fp = open("cmd_function.json", "w")
    json.dump(cmd_collection, fp, indent=2)
    fp.close()
    

    # run these test cases
    i = 0
    for cmd in test_cmd:
        print("test case", i)
        for _ in cmd.split("\n"):
            print("running cmd:", _)
            os.system(_)
            time.sleep(0.1)
        os.system("mv hooking.out {}/trace_{:0>3d}.txt".format(trace_dir, i+1))
        time.sleep(0.2)
        i += 1

            
if __name__ == "__main__":
    main()