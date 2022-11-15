import os
app = "tot_info"

print("a tiny script to run adonis to analyze the {} application.".format(app))

if not os.path.exists("../cov_trace"):
    print("please make sure you have run generate_cov_trace.py before using this script")
    exit()

if not os.path.exists("../function_trace"):
    print("please make sure you have run generate_function_trace.py before using this script")
    exit()

if not os.path.exists("../syscall_trace"):
    print("please make sure you have run generate_syscall_trace.py before using this script")
    exit()

trace_type = input("select the trace to use: [function|syscall] \n")
if trace_type not in ["function", "syscall"]:
    print("please select from [function|syscall]")
    exit()
print("selected trace to use: {} trace".format(trace_type))

os.chdir("../../../../")
if trace_type == "function":
    cmd = "python adonis.py -f paper_experiments/app/{}/source/{}.wasm -s \
        -b paper_experiments/app/{}/function_trace \
        --func_hooking adonis_res/{}_api2trace_function.json \
        -c adonis_res/{}_bb2line.json \
        -o {}_function".format(app, app, app, app, app, app)
else:
    cmd = "python adonis.py -f paper_experiments/app/{}/source/{}.wasm -s \
        -b paper_experiments/app/{}/syscall_trace \
        -c adonis_res/{}_bb2line.json \
        -o {}_syscall".format(app, app, app, app, app)

print(cmd)

os.system(cmd)