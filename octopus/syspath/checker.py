"""
This file contains the checkers of special functions.
A checker recieves an event trace as the input and return 
a list of positions (could be empty if not found). Note that
a position is a tuple, which includes the possition in the 
cfg and the corresponding possibility that this event trace 
matches this possition.
"""

import re
import Levenshtein

def printf_checker(graph, event_trace):
    """
    for printf, we check the format string
    """
    if is_function_trace(event_trace):
        event_trace = event_trace[0]
        arg_fmt_str = event_trace.fields[0].strip()
        poss = []
        for inst_hash in graph.inst2fmtstr:
            fmtstr, regex = graph.inst2fmtstr[inst_hash]
            if fmtstr == "\n" or fmtstr == "": # we will not try to match \n
                continue
            if arg_fmt_str == fmtstr:
                poss.append((inst_hash, 200+len(arg_fmt_str)))
        return poss
    else:
        output_str = extract_output(event_trace)
        if output_str == None or simple_output(output_str):
            return []
        poss = []
        for inst_hash in graph.inst2fmtstr:
            fmtstr, regex = graph.inst2fmtstr[inst_hash]
            if fmtstr == "\n" or fmtstr == "": # we will not try to match \n
                continue
            if fmt_match(regex, output_str):
                possibility = 200
                possibility -= distance(fmtstr, output_str)
                if simple_format(fmtstr):
                    possibility -= 100
                if possibility > 50:
                    poss.append((inst_hash, possibility))
        # poss = sorted(poss, key=lambda item: item[1], reverse=True)
        return poss

def extract_output(event_trace):
    for e in event_trace:
        if e.event_type == "write":
            return e.fields["data"]

def fmt_match(regex: str, to_match: str):
    result = re.match(regex, to_match)
    if result:
        # print("True")
        return True
    # print("False")
    return False

def open_checker(graph, event_trace):
    """
    for open, we check the mode and flag
    We note that the flag monitored by sysdig does not
    equal to the definition of linux system (open/fcntl).
    So we need to do some translation.
    """
    if is_function_trace(event_trace):
        event_trace = event_trace[0]
        mode = extract_mode_from_function(event_trace)
        flags = extract_flags_from_function(event_trace)
        poss = []
        for inst_hash in graph.inst2open_args:
            args = graph.inst2open_args[inst_hash]
            t_mode = args["mode"]
            t_flags = args["flags"]
            if t_mode == mode and t_flags == flags:
                poss.append((inst_hash,100))
        return poss
    else:
        mode = extract_mode_from_syscall(event_trace)
        flags = extract_flags_from_syscall(event_trace)
        poss = []
        for inst_hash in graph.inst2open_args:
            args = graph.inst2open_args[inst_hash]
            t_mode = args["mode"]
            t_flags = args["flags"]
            if t_mode == mode and t_flags == flags:
                poss.append((inst_hash,100))
        return poss

def extract_mode_from_syscall(event_trace):
    for e in event_trace:
        if e.event_type == "openat":
            break
    mode = int(e.fields["mode"], 8)
    return mode

def extract_mode_from_function(event_trace):
    mode = int(event_trace.fields[1])
    return mode


# mapper from define string to value
# refer to fcntl-linux.h
define2value = {
        "O_ACCMODE": int("0003", 8),
        "O_RDONLY": int("00", 8),
        "O_WRONLY": int("01", 8),
        "O_RDWR": int("02", 8),
        "O_CREAT": int("0100", 8),
        "O_EXCL": int("0200", 8),
        "O_NOCTTY": int("0400", 8),
        "O_TRUNC": int("01000", 8),
        "O_APPEND": int("02000", 8),
        "O_NONBLOCK": int("04000", 8),
        "O_NDELAY": int("04000", 8),
        "O_SYNC": int("04010000", 8),
        "O_FSYNC": int("04010000", 8),
        "O_ASYNC": int("020000", 8),
        "__O_LARGEFILE": int("0100000", 8),
        "__O_DIRECTORY": int("0200000", 8),
        "__O_NOFOLLOW": int("0400000", 8),
        "__O_CLOEXEC": int("02000000", 8),
        "__O_DIRECT": int("040000", 8),
        "__O_NOATIME": int("01000000", 8),
        "__O_PATH": int("010000000", 8),
        "__O_DSYNC": int("010000", 8),
        "__O_TMPFILE": int("020200000", 8),
        "O_LARGEFILE": int("0100000", 8),
        "O_DIRECTORY": int("0200000", 8),
        "O_NOFOLLOW": int("0400000", 8),
        "O_CLOEXEC": int("02000000", 8),
        "O_DIRECT": int("040000", 8),
        "O_NOATIME": int("01000000", 8),
        "O_PATH": int("010000000", 8),
        "O_DSYNC": int("010000", 8),
        "O_TMPFILE": int("020200000", 8)
    }

def extract_flags_from_syscall(event_trace):
    for e in event_trace:
        if e.event_type == "openat":
            break
    flag_str = e.fields["flags"]
    l = flag_str.index("(")
    r = flag_str.index(")")
    define_str = flag_str[l+1:r]
    defines = define_str.split("|")
    flag_value = 0
    for define in defines:
        flag_value |= define2value[define]
    return flag_value


def extract_flags_from_function(event_trace):
    flags = int(event_trace.fields[2])
    return flags

def fprintf_checker(graph, event_trace):
    """
    for fprintf, we check the format string
    """
    if is_function_trace(event_trace):
        event_trace = event_trace[0]
        arg_fmt_str = event_trace.fields[1].strip()
        poss = []
        for inst_hash in graph.inst2ffmtstr:
            fmtstr, regex = graph.inst2ffmtstr[inst_hash]
            if fmtstr == "\n" or fmtstr == "": # we will not try to match \n
                continue
            if arg_fmt_str == fmtstr:
                poss.append((inst_hash, 200+len(arg_fmt_str)))
        return poss
    else:
        output_str = extract_output(event_trace)
        if output_str == None or simple_output(output_str):
            return []
        poss = []
        for inst_hash in graph.inst2ffmtstr:
            fmtstr, regex = graph.inst2ffmtstr[inst_hash]
            if fmtstr == "\n" or fmtstr == "": # we will not try to match \n
                continue
            if fmt_match(regex, output_str):
                possibility = 200
                possibility -= distance(fmtstr, output_str)
                if simple_format(fmtstr):
                    possibility -= 100
                if possibility > 50:
                    poss.append((inst_hash, possibility))
        # poss = sorted(poss, key=lambda item: item[1], reverse=True)
        return poss


def putc_checker(graph, event_trace):
    poss = []
    return poss
    if is_function_trace(event_trace):
        event_trace = event_trace[0]
        arg_fmt_str = chr(int(event_trace.fields[0])).strip() # putc(int), so translate int to string
        for inst_hash in graph.inst2fmtstr:
            fmtstr, regex = graph.inst2fmtstr[inst_hash]
            if fmtstr == "\n" or fmtstr == "": # we will not try to match \n
                continue
            if arg_fmt_str == fmtstr:
                poss.append((inst_hash, 200+len(arg_fmt_str)))
    return poss


def puts_checker(graph, event_trace):
    poss = []
    return poss
    if is_function_trace(event_trace):
        event_trace = event_trace[0]
        arg_fmt_str = event_trace.fields[0].strip()
        for inst_hash in graph.inst2fmtstr:
            fmtstr, regex = graph.inst2fmtstr[inst_hash]
            if fmtstr == "\n" or fmtstr == "": # we will not try to match \n
                continue
            if arg_fmt_str == fmtstr:
                poss.append((inst_hash, 200+len(arg_fmt_str)))
    return poss


def fputc_checker(graph, event_trace):
    poss = []
    return poss
    if is_function_trace(event_trace):
        event_trace = event_trace[0]
        arg_fmt_str = chr(int(event_trace.fields[0])).strip() # fputc(int), so translate int to string
        for inst_hash in graph.inst2ffmtstr:
            fmtstr, regex = graph.inst2ffmtstr[inst_hash]
            if fmtstr == "\n" or fmtstr == "": # we will not try to match \n
                continue
            if arg_fmt_str == fmtstr:
                poss.append((inst_hash, 200+len(arg_fmt_str)))
    return poss


def fputs_checker(graph, event_trace):
    poss = []
    return poss
    if is_function_trace(event_trace):
        event_trace = event_trace[0]
        arg_fmt_str = event_trace.fields[0].strip()
        for inst_hash in graph.inst2ffmtstr:
            fmtstr, regex = graph.inst2ffmtstr[inst_hash]
            if fmtstr == "\n" or fmtstr == "": # we will not try to match \n
                continue
            if arg_fmt_str == fmtstr:
                poss.append((inst_hash, 200+len(arg_fmt_str)))
    return poss


def fwrite_checker(graph, event_trace):
    poss = []
    return poss
    if is_function_trace(event_trace):
        event_trace = event_trace[0]
        arg_fmt_str = event_trace.fields[0].strip()
        for inst_hash in graph.inst2ffmtstr:
            fmtstr, regex = graph.inst2ffmtstr[inst_hash]
            if fmtstr == "\n" or fmtstr == "": # we will not try to match \n
                continue
            if "%" in fmtstr and "%%" not in fmtstr:
                continue
            if "%%" in fmtstr:
                fmtstr = fmtstr.replace("%%", "%")
            if arg_fmt_str == fmtstr:
                poss.append((inst_hash, 200+len(arg_fmt_str)))
    return poss


def simple_format(format_str: str):
    """
    given a format string, if the string contains only 2 %s and the other chars' length
    is less than three, we consider it a simple format, which means it is too easy to
    match it with a given string.
    """
    num_of_s = len(re.findall(r"%s", format_str))
    return num_of_s in [1, 2] and len(format_str.replace(r"%s", "").replace("\n", "")) <= 3


def simple_output(s: str):
    # test if the string s is too simple
    if len(s) == 0:
        return True
    num_of_dot = len(re.findall(r"\.", s))
    return num_of_dot/len(s) > 0.8


def distance(str_1, str_2):
    # calculate edit distance between str_1 and str_2
    return Levenshtein.distance(str_1, str_2)


def is_function_trace(trace):
    if len(trace) == 1:
        for k in trace[0].fields.keys():
            if isinstance(k, int) or "ret" == k:
                return True
    return False