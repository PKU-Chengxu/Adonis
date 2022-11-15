"""
This file contains the functions that are used to handle the special function 
during the preprocess. For example, for "printf", its handler is to calculate its format string.
"""

from octopus.arch.wasm.helper_c import my_C_extract_string_by_mem_pointer

def printf_handler(graph, func, bb, instruction):
    inst_hash = "{}#{}".format(bb.name, instruction.offset)
    if not hasattr(graph, "inst2fmtstr"):
        graph.inst2fmtstr = {}
    if inst_hash not in graph.inst2fmtstr:
        try:
            format_string = get_printf_format_str(graph, func, bb, instruction)
            # note that the arguements of an event in sysdig are splited by a space
            # this would make it hard to distinguish whether the space is a delimiter or
            # in the arguement. So, to be consistent, we strip the format_string extracted 
            # from the code.
            format_string = format_string.strip()
            format_regex = build_format_regex(format_string)
            graph.inst2fmtstr[inst_hash] = (format_string, format_regex)
        except Exception as e:
            print("failed to analyze the format string in {}. ignore it.".format(inst_hash))
            # raise e
        
    # print("inst2fmtstr:")
    # for k in graph.inst2fmtstr:
    #     print(k, graph.inst2fmtstr[k])
    

def get_printf_format_str(graph, func, bb, target_instruction):
    """
    For performence concerns, we only traverse the exact basic block.
    If the format string is related to a variant value that is defined 
    in previous blocks, we can't get the correct blocks. However, this
    seldom happens according to our experience.
    """
    import copy
    func_name = graph.get_func_readable_name(func)
    param_str, return_str = graph.wasmVM.get_signature(func_name)
    state, has_ret = graph.wasmVM.init_state(
        func.name, param_str, return_str, [])
    halt = False
    states = [state]
    patterns = []
    flag = False
    # we notice that target instruction may at the very end of the basic blocks
    # but analyzing its format string often requests several instructions before
    # the target instruction, so we limit the sysbolic execution space.
    # t_index = bb.instructions.index(target_instruction)
    # left_index_to_search = max(0, t_index - 10)
    for instruction in bb.instructions:
        if instruction.name == "call":
            instruction
        next_states = []
        if flag:
            break
        for state in states:
            if instruction == target_instruction:
                param_list = []
                param_str, return_str = graph.wasmVM.get_signature("printf")
                if param_str:
                    num_arg = len(param_str.split(' '))
                    for _ in range(num_arg):
                        param_list.append(state.symbolic_stack.pop())
                pattern_p = param_list[1].as_long()

                pattern = my_C_extract_string_by_mem_pointer(
                    pattern_p, graph.wasmVM.data_section, state.symbolic_memory)
                patterns.append(pattern)
                flag = True
                continue
            state.instr = instruction
            halt, ret = graph.wasmVM.emulate_one_instruction(
                instruction, state, 0, has_ret, 0, quick=True)
            if ret is not None:
                next_states.extend(ret)
            else:
                next_states.append(copy.deepcopy(state))
        states = next_states
    return patterns[0]


def open_handler(graph, func, bb, instruction):
    open_args = get_open_args(graph, func, bb, instruction)
    inst_hash = "{}#{}".format(bb.name, instruction.offset)
    if not hasattr(graph, "inst2open_args"):
        graph.inst2open_args = {}
    graph.inst2open_args[inst_hash] = open_args


def get_open_args(graph, func, bb, target_instruction):
    """
    Try to get the arguements of open function though static analysis.
    arg: name, mode, flag
    Typically, name is hard to get, so we will not try to infer it.
    For flag, we can infer its value in most cases.
    For mode, its wired that in wasm (mayby for emcc), the third argument 
    passed to open is not mode, it is a memory index pointing the mode. to
    handle this, we dirictly get its value (which is at the 18th instruction
    before call open).
    For performence concerns, we only traverse the exact basic block.
    """
    res = {}
    import copy
    # get flag
    func_name = graph.get_func_readable_name(func)
    param_str, return_str = graph.wasmVM.get_signature(func_name)
    state, has_ret = graph.wasmVM.init_state(
        func.name, param_str, return_str, [])
    states = [state]
    patterns = []
    flag = False
    for instruction in bb.instructions:
        next_states = []
        if flag:
            break
        for state in states:
            if instruction == target_instruction:
                param_list = []
                param_str, return_str = graph.wasmVM.get_signature("open")
                if param_str:
                    num_arg = len(param_str.split(' '))
                    for _ in range(num_arg):
                        param_list.append(state.symbolic_stack.pop())
                try:
                    arg_flag = param_list[1].as_long()
                except Exception as e:
                    arg_flag = None
                res["flags"] = arg_flag
                flag = True
                break
            state.instr = instruction
            halt, ret = graph.wasmVM.emulate_one_instruction(
                instruction, state, 0, has_ret, 0)
            if ret is not None:
                next_states.extend(ret)
            else:
                next_states.append(copy.deepcopy(state))
        states = next_states
    
    # get mode
    try:
        t_index = bb.instructions.index(target_instruction)
        mode_instruction = bb.instructions[t_index-18] # may only works for emcc
        mode_arg = int(mode_instruction.operand_interpretation.split()[-1])
        
    except Exception as e:
        mode_arg = None
    # note that mode is meaningful when (flags & O_CREAT) || (flags & O_TMPFILE) == O_TMPFILE
    # in other case, mode = 0
    # refer to https://man7.org/linux/man-pages/man2/open.2.html
    O_CREAT = int("0100", 8)
    O_TMPFILE = int("020200000", 8)
    if arg_flag == None or not (arg_flag & O_CREAT or (arg_flag&O_TMPFILE) == O_TMPFILE):
        mode_arg = 0
    res["mode"] = mode_arg
    return res


def fprintf_handler(graph, func, bb, instruction):
    inst_hash = "{}#{}".format(bb.name, instruction.offset)
    if not hasattr(graph, "inst2ffmtstr"):
        graph.inst2ffmtstr = {}
    if inst_hash not in graph.inst2ffmtstr:
        try:
            format_string = get_fprintf_format_str(graph, func, bb, instruction)
        except KeyError as e:
            print("failed to analyze the format string in {}. ignore it.".format(inst_hash))
            return
        # note that the arguements of an event in sysdig are splited by a space
        # this would make it hard to distinguish whether the space is a delimiter or
        # in the arguement. So, to be consistent, we strip the format_string extracted 
        # from the code.
        format_string = format_string.strip()
        format_regex = build_format_regex(format_string)
        graph.inst2ffmtstr[inst_hash] = (format_string, format_regex)
    # print("inst2ffmtstr:")
    # for k in graph.inst2ffmtstr:
    #     print(k, graph.inst2ffmtstr[k])


def get_fprintf_format_str(graph, func, bb, target_instruction):
    """
    For performence concerns, we only traverse the exact basic block.
    If the format string is related to a variant value that is defined 
    in previous blocks, we can't get the correct blocks. However, this
    seldom happens according to our experience.
    """
    func_name = graph.get_func_readable_name(func)
    param_str, return_str = graph.wasmVM.get_signature(func_name)
    state, has_ret = graph.wasmVM.init_state(
            func.name, param_str, return_str, [])
    local2value = {}
    target_inst_index = bb.instructions.index(target_instruction)
    inst_store_pattern_val = bb.instructions[target_inst_index - 2] # second instruction from call fprintf
    const_val = None
    for instruction in bb.instructions:
        if instruction == inst_store_pattern_val:
            pattern_val_local_var = get_local_var_from_inst(instruction)
            pattern_val = local2value[pattern_val_local_var]
            pattern = my_C_extract_string_by_mem_pointer(
                    pattern_val, graph.wasmVM.data_section, state.symbolic_memory)
            """
            # we also store other constant strings
            local2value.pop(pattern_val_local_var)
            other_constants = []
            for k in local2value:
                if local2value[k] < 100: # the location wont be too small
                    continue
                try:
                    constant_str = my_C_extract_string_by_mem_pointer(
                        local2value[k], graph.wasmVM.data_section, state.symbolic_memory)
                    if constant_str != "":
                        other_constants.append(constant_str)
                except Exception as e:
                    continue
                """
            return pattern
        if const_val != None and instruction.is_variable:
            target_local = get_local_var_from_inst(instruction)
            local2value[target_local] = const_val
            const_val = None
            continue
        if instruction.is_constant:
            const_val = get_local_var_from_inst(instruction)
            continue

        
    """
    import copy
    func_name = graph.get_func_readable_name(func)
    param_str, return_str = graph.wasmVM.get_signature(func_name)
    state, has_ret = graph.wasmVM.init_state(
        func.name, param_str, return_str, [])
    states = [state]
    patterns = []
    for instruction in bb.instructions:
        next_states = []
        if flag:
            break
        for state in states:
            if instruction == target_instruction:
                param_list = []
                param_str, return_str = graph.wasmVM.get_signature("fprintf")
                if param_str:
                    num_arg = len(param_str.split(' '))
                    for _ in range(num_arg):
                        param_list.append(state.symbolic_stack.pop())
                pattern_p = param_list[1].as_long()

                pattern = C_extract_string_by_mem_pointer(
                    pattern_p, graph.wasmVM.data_section, state.symbolic_memory)
                patterns.append(pattern)
                flag = True
                continue
            state.instr = instruction
            halt, ret = graph.wasmVM.emulate_one_instruction(
                instruction, state, 0, has_ret, 0)
            if ret is not None:
                next_states.extend(ret)
            else:
                next_states.append(copy.deepcopy(state))
        states = next_states
    return patterns[0]
    """

def get_local_var_from_inst(instruction):
    s = instruction.operand_interpretation.split()[-1]
    if "0x" in s:
        return int(s, 16)
    else:
        return int(s, 10)


def build_format_regex(format_str):
    # build the regex according to the format string 
    # this regex will be used in the checker
    regex = replace_spceial_char(format_str)
    regex = regex.replace("\n", r"\.") # in sysdig, \n is represented as .
    regex = regex.replace(r"%s", r".*")
    regex = regex.replace(r"%d", r"(0|[1-9][0-9]*|-[1-9][0-9]*)")
    regex = regex.replace(r"%ld", r"(0|[1-9][0-9]*|-[1-9][0-9]*)")
    regex = regex.replace(r"%2ld", r"[0-9][0-9]")
    regex = regex.replace(r"%%", r"%")
    float_regex = r"(-?([1-9]\d*\.\d*|0\.\d*[1-9]\d*|0?\.0+|0))|([+-]?[\d]+([\.][\d]+)?([Ee][+-]?[\d]+)?)"
    regex = regex.replace(r"%f", float_regex)
    regex = regex.replace(r"%lf", float_regex)
    regex = regex.replace(r"%x", r"(0[xX])?[0-9a-fA-F]+")
    return regex


def replace_spceial_char(s):
    spceial_char = {
        "\\": "\\\\",
        "(" : "\\(",
        ")" : "\\)",
        "[" : "\\[",
        "]" : "\\]",
        "{" : "\\{",
        "}" : "\\}",
        "." : "\\.",
        "*" : "\\*",
        "+" : "\\+",
        "?" : "\\?",
        "^" : "\\^",
        "$" : "\\$",
        "|" : "\\|",
        "#" : "\\#",
    }
    for k in spceial_char:
        s = s.replace(k, spceial_char[k])
    return s


def putc_handler(graph, func, bb, instruction):
    # nothing to do, nothing to save
    pass


def puts_handler(graph, func, bb, instruction):
    # nothing to do, nothing to save
    pass


def fputc_handler(graph, func, bb, instruction):
    # nothing to do, nothing to save
    pass


def fputs_handler(graph, func, bb, instruction):
    # nothing to do, nothing to save
    pass


def fwrite_handler(graph, func, bb, instruction):
    # nothing to do, nothing to save
    pass