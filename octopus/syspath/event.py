# events that we should record their fields, including args and return values.
event2field = {
    "openat": ["name", "flags", "mode"], 
    "write": ["fd", "data"]
}

class Event:
    def __init__(self):
        self.event_type = None
        self.fields = None
    
    def __str__(self) -> str:
        if self.fields:
            return "<{}:{}>".format(self.event_type, 
                    ",".join(["{}={}".format(k, self.fields[k]) for k in self.fields]))
        else:
            return "<{}>".format(self.event_type)
    
    def __repr__(self) -> str:
        return str(self)


def build_from_log(log_line, log_next_line):
    from octopus.syspath.trace_parser import get_event_type, get_event_args_str
    e = Event()
    e.event_type = get_event_type(log_line)
    if e.event_type in event2field:
        arg1 = get_event_args_str(log_line)
        arg2 = get_event_args_str(log_next_line)
        field_str = arg1 + " " + arg2
        e.fields = construct_fields(field_str, e.event_type)
    return e
        

def build_from_function_hooking_log(hooking_log):
    if hooking_log == "":
        # in this case, the program stops unexpectedly. so no exit is logged in the hooking log
        return None
    e = Event()
    left_break_index = hooking_log.index("((")
    right_break_index = hooking_log.index("))")
    
    e.event_type = hooking_log[:left_break_index]
    paras = hooking_log[left_break_index+2:right_break_index]
    paras = paras.split(";")
    e.fields = {}.copy()
    for i in range(len(paras)):
        e.fields[i] = paras[i]
    if "==" in hooking_log:
        equal_index = hooking_log.index("==")
        ret = hooking_log[equal_index+2:]
        e.fields["ret"] = ret
    return e


def construct_fields(field_str, event_type):
    fields = {}.copy()
    k = None
    v = None
    ss = field_str.split("=") 
    for i in range(len(ss)):
        s = ss[i]
        if i == 0:    # head
            k = s
            continue
        if i == len(ss) - 1: # tail
            v = s
            if k in event2field[event_type]:
                fields[k] = v
        else:           # normal
            v = " ".join(s.split(" ")[:-1])
            if k in event2field[event_type]:
                fields[k] = v
            k = s.split(" ")[-1]
    return fields
