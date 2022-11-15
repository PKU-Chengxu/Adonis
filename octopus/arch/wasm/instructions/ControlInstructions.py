import copy

from z3 import *
import re
import logging
from collections import defaultdict

from octopus.arch.wasm.exceptions import *
from octopus.arch.wasm.internal_functions import CPredefinedFunction, GoPredefinedFunction
from octopus.arch.wasm.graph import Graph
from octopus.arch.wasm.utils import getConcreteBitVec, Configuration

# TODO ensure the correctness of malloc, realloc, and free
C_LIBRARY_FUNCS = {'printf', 'scanf', 'strlen',
                   'swap', 'iprintf', 'strcpy', 'strcat', 'strcmp', 'strstr', 'strchr', 'floor', 'ceil', 'exp', 'sqrt', 'getchar', 'putchar', 'abs', 'memcmp', 'strncpy', 'strncat', 'emscripten_resize_heap', 'puts', '__memcpy', '__small_printf'}
GO_LIBRARY_FUNCS = {'runtime', 'reflect', 'type..', 'sync_atomic', 'fmt', 'strconv', 'sync', 'syscall_js',
                    'internal_poll', 'syscall', '_syscall', 'unicode_utf8', 'os', '_os', 'sort', 'errors', 'internal_cpu', 'wasm_', 'time', 'io', 'unicode', 'mem', 'math_bits', 'internal_bytealg', 'go', 'debug', 'cmpbody', 'callRet', '_rt0_wasm_js', '_*sync', '_*fmt', '_*os'}
TERMINATED_FUNCS = {'__assert_fail', 'exit'}
# below functions are not regarded as library function, need step in
NEED_STEP_IN_GO = {'fmt.Println', '_*fmt.pp_.printArg', '_*fmt.buffer_.writeByte', '_*fmt.pp_.fmtInteger', '_*os.File_.Write',
                   '_*fmt.fmt_.fmtInteger', 'memmove', '_*fmt.pp_.fmtString', '_*fmt.fmt_.truncateString', '_*fmt.fmt_.padString',
                   '_*fmt.buffer_.writeString', '_syscall/js.Value_.Get', '_syscall/js.Value_.Type',
                   '_syscall/js.Value_.isNumber', 'syscall/js.makeValue',
                   '_*sync.Pool_.Get', 'runtime.sliceAppend', '_os.stdioFileHandle_.Write'}
NEED_STEP_IN_C = {}

# we heuristically define that if a func is start with the pre-defined substring, it is a library function


def IS_GO_LIBRARY_FUNCS(x): return x.startswith(tuple(GO_LIBRARY_FUNCS))
def IS_C_LIBRARY_FUNCS(x): return x in C_LIBRARY_FUNCS


class ControlInstructions:
    def __init__(self, instr_name, instr_operand, instr_string):
        self.instr_name = instr_name
        self.instr_operand = instr_operand
        self.instr_string = instr_string
        self.skip_command = {'loop', 'end', 'br', 'else', 'nop', 'block'}
        self.term_command = {'unreachable', 'return'}

    def init_state_before_call(self, param_str, return_str, has_ret, state):
        num_arg = 0
        # this flag indicates whether the caller executes and returns properly
        # if the caller terminates in advance, which results in the imbalance of stack
        # we should use this flag to reallocate the arguments for callee
        need_to_reset = False

        if param_str:
            num_arg = len(param_str.split(' '))
            try:
                arg = [state.symbolic_stack.pop() for _ in range(num_arg)]
            except IndexError:
                need_to_reset = True

        if return_str:
            has_ret.append(True)
        else:
            has_ret.append(False)

        # init state of internal call
        new_state = copy.deepcopy(state)
        new_has_ret = copy.deepcopy(has_ret)

        if need_to_reset:
            for i, local in enumerate(param_str.split(' ')):
                new_state.local_var[i] = getConcreteBitVec(
                    local, state.current_func_name + '_loc_' + str(i) + '_' + local)
        else:
            for x in range(num_arg):
                new_state.local_var[num_arg - 1 - x] = arg[x]

        # set the remaining local vars as None
        for x in range(num_arg, len(new_state.local_var)):
            try:
                new_state.local_var.pop(x)
            except KeyError:
                # if some of the local var is unused during the caller
                # there is no need to pop it, thus continue the loop
                continue

        return new_state, new_has_ret

    def emulate(self, state, has_ret, func_prototypes, func_index2func_name, data_section, analyzer):
        if self.instr_name in self.skip_command:
            return False, None
        if self.instr_name in self.term_command:
            return False, None

        if self.instr_name == 'br_if':
            op = state.symbolic_stack.pop()
            assert is_bv(op) or is_bool(
                op), f"the type of op popped from stack in `br_if` is {type(op)} instead of bv or bool"
            states = {'conditional_true_0': copy.deepcopy(
                state), 'conditional_false_0': copy.deepcopy(state)}
            if is_bv(op):
                op = simplify(op != 0)
            states['conditional_true_0'].constraints.append(op)
            states['conditional_false_0'].constraints.append(simplify(Not(op)))

            return False, [states]
        elif self.instr_name == 'if':
            op = state.symbolic_stack.pop()
            assert is_bv(op) or is_bool(
                op), f"the type of op popped from stack in `if` is {type(op)} instead of bv or bool"
            states = {'conditional_true_0': copy.deepcopy(
                state), 'conditional_false_0': copy.deepcopy(state)}
            if is_bv(op):
                cond = simplify(op != 0)

            states['conditional_true_0'].constraints.append(cond)
            states['conditional_false_0'].constraints.append(
                simplify(Not(cond)))
            return False, [states]
        elif self.instr_name == 'call_indirect':
            # refer to: https://developer.mozilla.org/en-US/docs/WebAssembly/Understanding_the_text_format#webassembly_tables
            # this instruction will pop an element out of the stack, and use this as an index in the table, i.e., elem section in Wasm module, to dynamically determine which fucntion will be invoked
            raise UnsupportInstructionError
        elif self.instr_name == 'br_table':
            # state.instr.xref indicates the destination instruction's offset
            op = state.symbolic_stack.pop()

            # operands of br_table instruction
            ops = [i for i in self.instr_operand]
            n_br, br_lis = ops[0], ops[1:-1]

            # construct a dict to minimize the possible states
            target_branch2index = defaultdict(list)
            for index, target in enumerate(br_lis):
                target_branch2index[target].append(index)
            states = {}
            for target, index_list in target_branch2index.items():
                new_state = copy.deepcopy(state)
                index_list = [simplify(op == i) for i in index_list]
                cond = simplify(Or(index_list))
                new_state.constraints.append(cond)
                states['conditional_true_' + str(target)] = new_state
            false_state = copy.deepcopy(state)
            cond = simplify(op >= n_br)
            false_state.constraints.append(cond)
            states['conditional_false_0'] = false_state
            return False, [states]
        elif self.instr_name == 'call':
            self.instr_operand = self.instr_string.split(' ')[1]

            # get the callee's function signature
            try:
                f_offset = int(self.instr_operand)
            except ValueError:
                # it's possible that the `call` operand is a hex
                f_offset = int(self.instr_operand, 16)
            target_func = func_prototypes[f_offset]
            internal_function_name, param_str, return_str, _ = target_func

            # find a more readable name, need -g3 compiling and --need-mapper
            if func_index2func_name is not None:
                try:
                    readable_name = func_index2func_name[int(
                        re.search('(\d+)', internal_function_name).group())]
                except AttributeError:
                    # if the internal_function_name is the readable name already
                    readable_name = internal_function_name

            new_states = []
            # if the callee is a library function
            if Configuration.get_source_type() == 'c' and IS_C_LIBRARY_FUNCS(readable_name) and readable_name not in NEED_STEP_IN_C:
                logging.warning(
                    f"Invoked a C library function: {readable_name}")
                func = CPredefinedFunction(
                    readable_name, state.current_func_name)
                func.emul(state, param_str, return_str, data_section, analyzer)
            elif Configuration.get_source_type() == 'go' and IS_GO_LIBRARY_FUNCS(readable_name) and readable_name not in NEED_STEP_IN_GO:
                logging.warning(
                    f"Invoked a Go library function: {readable_name}")
                func = GoPredefinedFunction(
                    readable_name, state.current_func_name)
                func.emul(state, param_str, return_str, data_section, analyzer)
            elif readable_name in TERMINATED_FUNCS:
                logging.warning(
                    f"Terminated function invoked: {readable_name} ")
                return False, None
            else:
                # if the callee takes NO symbols as input:
                # 1. the param_str is empty [Doing]
                # 2. the params are all non-symbol [TODO]
                # logging.warning(f'invoke: {readable_name} with {internal_function_name}')
                logging.warning(
                    f"Invoked: {readable_name} ")
                if param_str == "":
                    pass

                new_state, new_has_ret = self.init_state_before_call(
                    param_str, return_str, has_ret, state)
                possible_states = Graph.traverse_one(
                    internal_function_name, new_state, new_has_ret)
                possible_call_results = []
                for pstate in possible_states:
                    to_be_returned = None
                    if has_ret and has_ret[-1]:
                        to_be_returned = pstate.symbolic_stack.pop()
                        if is_bool(to_be_returned):
                            if is_false(to_be_returned):
                                to_be_returned = BitVecVal(0, 32)
                            elif is_true(to_be_returned):
                                to_be_returned = BitVecVal(1, 32)
                            else:
                                raise NotDeterminedRetValError
                    possible_call_results.append(
                        (to_be_returned, copy.deepcopy(pstate)))

                # for stack balance
                outer_need_ret = has_ret.pop()

                for i, return_constraint_tuple in enumerate(possible_call_results):
                    new_state = copy.deepcopy(state)
                    return_value, constraint, state_symbolic_memory, current_globals = \
                        return_constraint_tuple[0], return_constraint_tuple[1].constraints, return_constraint_tuple[
                            1].symbolic_memory, return_constraint_tuple[1].globals

                    # if have outer_need_ret but no return_value, means the callee's this branch is failed
                    if outer_need_ret and return_value is None:
                        continue
                    elif outer_need_ret and return_value is not None:
                        new_state.symbolic_stack.append(return_value)
                        new_state.constraints = constraint
                        new_state.symbolic_memory = state_symbolic_memory
                        new_state.globals = current_globals
                    else:
                        new_state.constraints = constraint
                        new_state.symbolic_memory = state_symbolic_memory
                        new_state.globals = current_globals

                    new_states.append(new_state)
            if len(new_states) == 0:
                new_states.append(state)
            return False, new_states
        else:
            print(self.instr_name)
            raise UnsupportInstructionError


    def emulate_not_step_in(self, state, has_ret, func_prototypes, func_index2func_name, data_section, analyzer, quick = False):
        """
        not step in a function call, except for a internal function.
        used for getting parameters of some internal function, 
        e.g., printf pattern string 
        """
        if self.instr_name in self.skip_command:
            return False, None
        if self.instr_name in self.term_command:
            return False, None

        if self.instr_name == 'br_if':
            op = state.symbolic_stack.pop()
            assert is_bv(op) or is_bool(
                op), f"the type of op popped from stack in `br_if` is {type(op)} instead of bv or bool"
            states = {'conditional_true_0': copy.deepcopy(
                state), 'conditional_false_0': copy.deepcopy(state)}
            if is_bv(op):
                op = simplify(op != 0)
            states['conditional_true_0'].constraints.append(op)
            states['conditional_false_0'].constraints.append(simplify(Not(op)))

            return False, [states]
        elif self.instr_name == 'if':
            op = state.symbolic_stack.pop()
            assert is_bv(op) or is_bool(
                op), f"the type of op popped from stack in `if` is {type(op)} instead of bv or bool"
            states = {'conditional_true_0': copy.deepcopy(
                state), 'conditional_false_0': copy.deepcopy(state)}
            if is_bv(op):
                cond = simplify(op != 0)

            states['conditional_true_0'].constraints.append(cond)
            states['conditional_false_0'].constraints.append(
                simplify(Not(cond)))
            return False, [states]
        elif self.instr_name == 'call_indirect':
            # refer to: https://developer.mozilla.org/en-US/docs/WebAssembly/Understanding_the_text_format#webassembly_tables
            # this instruction will pop an element out of the stack, and use this as an index in the table, i.e., elem section in Wasm module, to dynamically determine which fucntion will be invoked
            raise UnsupportInstructionError
        elif self.instr_name == 'br_table':
            # state.instr.xref indicates the destination instruction's offset
            op = state.symbolic_stack.pop()

            # operands of br_table instruction
            ops = [i for i in self.instr_operand]
            n_br, br_lis = ops[0], ops[1:-1]

            # construct a dict to minimize the possible states
            target_branch2index = defaultdict(list)
            for index, target in enumerate(br_lis):
                target_branch2index[target].append(index)
            states = {}
            for target, index_list in target_branch2index.items():
                new_state = copy.deepcopy(state)
                index_list = [simplify(op == i) for i in index_list]
                cond = simplify(Or(index_list))
                new_state.constraints.append(cond)
                states['conditional_true_' + str(target)] = new_state
            false_state = copy.deepcopy(state)
            cond = simplify(op >= n_br)
            false_state.constraints.append(cond)
            states['conditional_false_0'] = false_state
            return False, [states]
        elif self.instr_name == 'call':
            self.instr_operand = self.instr_string.split(' ')[1]

            # get the callee's function signature
            try:
                f_offset = int(self.instr_operand)
            except ValueError:
                # it's possible that the `call` operand is a hex
                f_offset = int(self.instr_operand, 16)
            target_func = func_prototypes[f_offset]
            internal_function_name, param_str, return_str, _ = target_func

            # find a more readable name, need -g3 compiling and --need-mapper
            if func_index2func_name is not None:
                try:
                    readable_name = func_index2func_name[int(
                        re.search('(\d+)', internal_function_name).group())]
                except AttributeError:
                    # if the internal_function_name is the readable name already
                    readable_name = internal_function_name

            new_states = []
            # if the callee is a library function
            if Configuration.get_source_type() == 'c' and IS_C_LIBRARY_FUNCS(readable_name) and readable_name not in NEED_STEP_IN_C:
                # logging.warning(
                #     f"Invoked a C library function: {readable_name}")
                func = CPredefinedFunction(
                    readable_name, state.current_func_name)
                func.emul(state, param_str, return_str, data_section, analyzer, quick)
            elif Configuration.get_source_type() == 'go' and IS_GO_LIBRARY_FUNCS(readable_name) and readable_name not in NEED_STEP_IN_GO:
                logging.warning(
                    f"Invoked a Go library function: {readable_name}")
                func = GoPredefinedFunction(
                    readable_name, state.current_func_name)
                func.emul(state, param_str, return_str, data_section, analyzer)
            elif readable_name in TERMINATED_FUNCS:
                logging.warning(
                    f"Terminated function invoked: {readable_name} ")
                return False, None
            else:
                # will not step in!
                # if it has a return value, push a fake number (0) into th stack
                # logging.warning(
                #     f"Invoked: {readable_name} (Not step in)")

                new_state, new_has_ret = self.init_state_before_call(
                    param_str, return_str, has_ret, state)
                # possible_states = Graph.traverse_one(
                #     internal_function_name, new_state, new_has_ret)
                # do NOT step in
                possible_state = copy.deepcopy(new_state)
                if return_str == 'i32':
                    possible_state.symbolic_stack.append(BitVecVal(0, 32))
                elif return_str == 'i64':
                    possible_state.symbolic_stack.append(BitVecVal(0, 64))
                elif return_str == 'f32':
                    possible_state.symbolic_stack.append(FPVal(0.0, Float32()))
                elif return_str == 'f64':
                    possible_state.symbolic_stack.append(FPVal(0.0, Float64()))
                possible_states = [possible_state]
                possible_call_results = []
                for pstate in possible_states:
                    to_be_returned = None
                    if has_ret and has_ret[-1]:
                        to_be_returned = pstate.symbolic_stack.pop()
                        if is_bool(to_be_returned):
                            if is_false(to_be_returned):
                                to_be_returned = BitVecVal(0, 32)
                            elif is_true(to_be_returned):
                                to_be_returned = BitVecVal(1, 32)
                            else:
                                raise NotDeterminedRetValError
                    possible_call_results.append(
                        (to_be_returned, copy.deepcopy(pstate)))

                # for stack balance
                outer_need_ret = has_ret.pop()

                for i, return_constraint_tuple in enumerate(possible_call_results):
                    new_state = copy.deepcopy(state)
                    return_value, constraint, state_symbolic_memory, current_globals = \
                        return_constraint_tuple[0], return_constraint_tuple[1].constraints, return_constraint_tuple[
                            1].symbolic_memory, return_constraint_tuple[1].globals

                    # if have outer_need_ret but no return_value, means the callee's this branch is failed
                    if outer_need_ret and return_value is None:
                        continue
                    elif outer_need_ret and return_value is not None:
                        new_state.symbolic_stack.append(return_value)
                        new_state.constraints = constraint
                        new_state.symbolic_memory = state_symbolic_memory
                        new_state.globals = current_globals
                    else:
                        new_state.constraints = constraint
                        new_state.symbolic_memory = state_symbolic_memory
                        new_state.globals = current_globals

                    new_states.append(new_state)
            if len(new_states) == 0:
                new_states.append(state)
            return False, new_states
        else:
            print(self.instr_name)
            raise UnsupportInstructionError