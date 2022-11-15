app = "sqlite"
print("A simple scripts to generate syscall trace for", app)

# container_hash should be modified accordingly
container_hash = "d4ce37921577ba0a67c80347066ed2fb3e92a8f484ddc01b195c4bc93784add7"

import json
import subprocess
import threading
import os
import time
import argparse
import sys

class NewProcess(threading.Thread):
    def __init__(self, cmd):
        self.cmd = cmd
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)
    
    def killSysdig(self):
        subprocess.call("echo 123 | sudo kill -9 $(ps aux | grep 'sysdig' | awk '{print $2}')", shell=True)
        print("sysdig terminated")

    def run(self):
        p = subprocess.Popen(self.cmd, shell=True)
        try:
            p.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            self.killSysdig()
        p.terminate()
        # os.kill(os.getpgid(p.pid), signal.SIGTERM)
        print("sysdig done")


def main():
    os.system("rm ../inputs/*.db")
    syscall_hook_run(app)
    

def syscall_hook_run(app):
    print("the script needs the root permission to run sysdig:")

    cmd_collection = {}
    app_dir = os.path.abspath("../")
    res_dir = os.path.abspath("../syscall_trace")
    # create trace dir 
    try:
        os.mkdir(res_dir)
    except FileExistsError:
        pass

    print("=========== generating syscall traces for {} ===========".format(app))
    # extract test cmd according to the runall.sh
    test_cmd = []
    fp = open("runall.sh", "r")
    start_flag = False
    cur_cmd = ""
    for l in fp.readlines():
        if "echo" in l:
            start_flag = True
            if cur_cmd != "":
                test_cmd.append(cur_cmd.strip())
            cur_cmd = ""
            continue
        if start_flag:
            cur_cmd += l
    test_cmd.append(cur_cmd.strip())
    
    # save cmd
    print("saving test case commands...")
    cmd_collection[app] = [_ for _ in test_cmd]
    fp = open("./cmd_syscall.json".format(app), "w")
    json.dump(cmd_collection, fp, indent=2)
    fp.close()

    # run these test cases
    os.chdir("../inputs")
    i = 0
    for cmd in test_cmd:
        print("test case", i)
        print("running cmd:", cmd)
        # """
        sysdig_cmd = "echo 123 | sudo docker exec {} sysdig proc.name={} > ".format(container_hash, app) + "{}/trace_{:0>3d}.txt".format(res_dir, i+1)
        sysdig = NewProcess(sysdig_cmd)
        sysdig.start()
        time.sleep(1)
        test = subprocess.call(cmd, shell=True)
        time.sleep(5)
        sysdig.join()
        # """
        i += 1
            
            
if __name__ == "__main__":
    import time
    st = time.time()
    main()
    ed = time.time()
    print("time used:", ed - st)