from gc import garbage
import os
import json
import argparse

app = None

ignored_functions = [
    "calloc",
    "malloc",
    "sprintf",
    "free",
    "memcpy",
    # generated *-decompile.c have problem with param name
    "exp",
    "log",
    "sin",
    "acos",
    "asin",
    "atan",
    "cos",
    "pow",
    "sqrt",
    "mmap",
    "realloc",
    "valloc",
    "obstack_free",
    "time",
    # "getpagesize",
    # "lseek",
    # "getopt",
    # "abort",
    # printf -> vfprintf error: too many arguments to function ‘vfprintf’
    # done = vfprintf(stdout, format, arg, 0);
    # vfprintf -> abc2mtex generates: vfprintf(FILE * restrict s, const char * restrict format, _G_va_list arg)
    "vfprintf",
    "getrusage",
    "strcmp",
    "memset",
    "strlen",
    "strncmp",
    # app coap & mqtt-sn-pub network apis generates strange function signature
    # e.g. int bind(int fd, __CONST_SOCKADDR_ARG addr, socklen_t len)
    # "bind",
    # "htonl",
    # "htons",
    # "ntohs",
    # "ntohl",
    # "recvfrom",
    # "sendto",
    # "connect",
    # "getnameinfo",
    # "setsockopt",
    # "inet_ntop",
    "strcpy"
]

function_to_include = {
    "opendir": ["#include <dirent.h>"],
    "readdir": ["#include <dirent.h>"],
    "printf": ['#include <stdarg.h>'],
    "fprintf": ['#include <stdarg.h>'],
    "scanf": ['#include <stdarg.h>'],
    "signal": ['#include <signal.h>'],
    "bind": ['#include <sys/socket.h>'],
    "htonl": ['#include <arpa/inet.h>'],
    "htons": ['#include <arpa/inet.h>'],
    "cfsetospeed": ['#include<termios.h>']
}

libs_to_include = set()

type_to_format_string = {
    "int": "%d",
    "const char *": "%s",
    "const char * restrict": "%s",
    "size_t": "%lu",
    "const void * restrict": "%s"
}


def main():
    parser = argparse.ArgumentParser(
        description='A simple scripts to generate hooking library for the given binary')

    inputs = parser.add_argument_group('Input arguments')
    inputs.add_argument('-f', '--file',
                        type=argparse.FileType('rb'),
                        help='binary file',
                        metavar='BINARY',
                        required=True)
    
    args = parser.parse_args()
    global app
    app = args.file.name[args.file.name.rfind('/') + 1:]
    print('name', app)
    file_to_decompile = args.file.name + "-decompile"
    os.system("cp {} {}".format(args.file.name, file_to_decompile))
    

    basename = os.path.basename(file_to_decompile)
    print("Analyzing {} using retdec...".format(basename))
    os.system("retdec-decompiler.py {}".format(file_to_decompile))

    config_file_name = basename + ".config.json"
    if not os.path.exists(file_to_decompile.replace(basename, config_file_name)):
        print("[ERROR] analyzing failed. please make sure retdec is installed.")
        return
    else:
        # garbage collection
        print("garbage collection...")
        garbage_suffix = [".ll", ".dsm", ".c", ".bc"]
        for suffix in garbage_suffix:
            garbage_file_name = basename + suffix
            if os.path.exists(file_to_decompile.replace(basename, garbage_file_name)):
                os.remove(file_to_decompile.replace(basename, garbage_file_name))
        os.remove(file_to_decompile)

        config_file = open(file_to_decompile.replace(basename, config_file_name), "r")
        bin_info = json.load(config_file)
        config_file.close()

        print("Generating hooking source...")
        hooking_source = generate_hooking_source_code(bin_info)

        hooking_source_name = "{}-hooking.c".format(basename)
        of = file_to_decompile.replace(basename, hooking_source_name)
        ofp = open(of, "w")
        ofp.write(hooking_source)
        ofp.close()
        
        hooking_lib_name = os.path.join(os.path.dirname(file_to_decompile), "{}-hooking.so".format(basename))
        print("Compiling hooking source to {}".format(hooking_lib_name))
        os.system("gcc {} -o {} -fPIC -shared -ldl -D_GNU_SOURCE".format(of, hooking_lib_name))


def generate_hooking_source_code(bin_info):
    ret = init()

    succ_hooked = []
    for function in bin_info["functions"]:
        if function["fncType"] == "dynamicallyLinked":
            if function["name"][0] == "_":
                continue # ignore function start with _
            if function["name"] in ignored_functions:
                continue # ignore functions like malloc
            if "declarationStr" not in function:
                continue # ignore function has no declarationStr field
            declaration_str = function["declarationStr"]
            print("handle", declaration_str)
            old_len = len(ret)
            ret = handle_function(function["name"], declaration_str, ret)
            if len(ret) > old_len:
                succ_hooked.append(function["name"])
    for _ in libs_to_include:
        ret.insert(1, _)
    ret = [_.replace("\n", "") for _ in ret]
    print("successfully hooked functions:", succ_hooked)
    generate_api2trace(succ_hooked)
    return "\n".join(ret)
    
manual_funcs = ["bind", "inet_ntop", "connect"]


def handle_function(func_name, declaration_str, source_code_lines):
    if "..." in declaration_str or func_name in manual_funcs:
        return handle_var_arg_function(func_name, declaration_str, source_code_lines)
    else:
        return handle_normal_function(func_name, declaration_str, source_code_lines)

def handle_normal_function(func_name, declaration_str, source_code_lines):
    global libs_to_include
    if func_name in function_to_include:
        for to_include in function_to_include[func_name]:
            libs_to_include.add(to_include)
    hooked_function_source_code = hook(func_name, declaration_str)
    source_code_lines += ["", ""] # add to blank lines
    source_code_lines += hooked_function_source_code.split("\n")
    return source_code_lines


def handle_var_arg_function(func_name, declaration_str, source_code_lines):
    global libs_to_include
    if func_name in function_to_include:
        for to_include in function_to_include[func_name]:
            libs_to_include.add(to_include)
    try:
        lib_fp = open("libs/{}.c".format(func_name), "r")
        source_code_lines += ["", ""] # add to blank lines
        source_code_lines += lib_fp.readlines()
    except FileNotFoundError:
        print("[WARN] cannot find hooking function for {}, ignore it.".format(func_name))
    return source_code_lines


def init():
    """
    add utility functions
    """
    ret = []
    base_fp = open("libs/base.c", "r")
    ret = base_fp.readlines()
    base_fp.close()
    return ret


def get_return_type(func_name, declaration_str):
    name_index = declaration_str.index(func_name)
    return declaration_str[:name_index].strip()


def get_parameters(func_name, declaration_str):
    lb = declaration_str.index("(")
    rb = declaration_str.index(")")
    paras = declaration_str[lb+1:rb]
    paras = paras.split(",")
    paras = [_.strip() for _ in paras]
    return paras


def get_para_type(parameter_str):
    return " ".join(parameter_str.split(" ")[:-1])


def get_template():
    return \
"""
$signature$
{
    $before_func$
    $in_func$
    $after_func$
}
"""


def get_before_template():
    return \
"""
    char hook_buff[BUFF_SIZE];
    sprintf(hook_buff, "$func_name$(($paras_format_types$))", $paras_values$);
    int sfd = get_sfd();
    hook_log(sfd, hook_buff);
"""


def get_in_template():
    return \
"""
    $return_type$ (*old_$func_name$)($paras$);
    $return_type$ result;
    old_$func_name$ = dlsym(RTLD_NEXT, "$func_name$");
    result = old_$func_name$($paras_variables$);
"""

def get_in_template_void():
    return \
"""
    $return_type$ (*old_$func_name$)($paras$);
    old_$func_name$ = dlsym(RTLD_NEXT, "$func_name$");
    old_$func_name$($paras_variables$);
"""


def get_after_template():
    return \
"""
    sprintf(hook_buff, "==$return_format_type$", $return_value$);
    sprintf(hook_buff + len(hook_buff), "%c", sep);
    hook_log(sfd, hook_buff);

    return result;
"""


def get_after_template_void():
    return \
"""
    sprintf(hook_buff, "%c", sep);
    hook_log(sfd, hook_buff);
"""


def construct_signature(func_name, declaration_str):
    return declaration_str[:-1] # simply remove ';'


def construct_before_func(func_name, declaration_str):
    ret = get_before_template()
    ret = ret.replace("$func_name$", func_name)
    parameters = get_parameters(func_name, declaration_str)
    if len(parameters) == 1 and parameters[0] == "void":
        ret = ret.replace("$paras_format_types$", "%s")
        ret = ret.replace("$paras_values$", '"void"')
    else:
        ret = ret.replace("$paras_format_types$", construct_paras_format_types(parameters))
        ret = ret.replace("$paras_values$", construct_paras_values(parameters))
    return ret

def construct_in_func(func_name, declaration_str):
    return_type = get_return_type(func_name, declaration_str)
    if return_type == "void":
        ret = get_in_template_void()
    else:
        ret = get_in_template()
    ret = ret.replace("$func_name$", func_name)
    ret = ret.replace("$return_type$", get_return_type(func_name, declaration_str))
    parameters = get_parameters(func_name, declaration_str)
    if len(parameters) == 1 and parameters[0] == "void":
        ret = ret.replace("$paras$", "void")
        ret = ret.replace("$paras_values$", '')
        ret = ret.replace("$paras_variables$", construct_paras_variables(parameters))
    else:
        ret = ret.replace("$paras$", ", ".join(parameters))
        ret = ret.replace("$paras_values$", construct_paras_values(parameters))
        ret = ret.replace("$paras_variables$", construct_paras_variables(parameters))
    return ret


def construct_after_func(func_name, declaration_str):
    return_type = get_return_type(func_name, declaration_str)
    if return_type == "void":
        ret = get_after_template_void()
    else:
        ret = get_after_template()
    ret = ret.replace("$return_format_type$", get_format_string_from_type(return_type))
    ret = ret.replace("$return_value$", construct_return_value(return_type))
    return ret
    

def hook(func_name, declaration_str):
    ret = get_template()
    ret = ret.replace("$signature$", construct_signature(func_name, declaration_str))
    ret = ret.replace("$before_func$", construct_before_func(func_name, declaration_str))
    ret = ret.replace("$in_func$", construct_in_func(func_name, declaration_str))
    ret = ret.replace("$after_func$", construct_after_func(func_name, declaration_str))
    return ret


def construct_paras_format_types(parameters):
    # parameters = get_parameters(function_name, declaration_str)
    return ";".join([get_format_string_from_type(get_para_type(_)) for _ in parameters])


def construct_paras_values(parameters):
    ret = []
    for _ in parameters:
        type = get_para_type(_)
        if type in type_to_format_string:
            ret.append(_.split()[-1]) 
        else:
            ret.append("'_'")
    return ", ".join(ret)


def construct_paras_variables(parameters):
    if parameters[0] == "void":
        return ""
    ret = []
    for _ in parameters:
        ret.append(_.split()[-1])
    return ", ".join(ret)


def construct_return_value(return_type):
    if return_type in type_to_format_string:
        return "result"
    else:
        return "'_'"


def get_format_string_from_type(type):
    if type in type_to_format_string:
        return type_to_format_string[type]
    else:
        return "%c"


def generate_api2trace(functions):
    """
    generate api2trace for analyze. api2trace is a dict, whose key is api (function name)
    and value is possible trace. For function hooking. the trace is always determined.
    """
    api2trace = { func : ["{}$".format(func)] for func in functions }
    if "fprintf" in api2trace:
        api2trace["fprintf"] = ["fprintf$","fputc$", "fputs$", "fwrite$"]
    if "printf" in api2trace:
        api2trace["printf"] = ["printf$","putc$", "puts$"]
    print("saving api2trace to {}_api2trace_function.json ...".format(app))
    fp = open("../adonis_res/{}_api2trace_function.json".format(app), "w")
    json.dump(api2trace, fp, indent=2)
    

if __name__ == "__main__":
    main()