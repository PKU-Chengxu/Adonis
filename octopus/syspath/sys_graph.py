import copy
from queue import Queue
from time import time
from turtle import update
from graphviz import Digraph
import os
import json
from cachetools import cached, LRUCache
from numpy import isin

from octopus.core.edge \
    import (EDGE_UNCONDITIONAL,
            EDGE_CONDITIONAL_TRUE, EDGE_CONDITIONAL_FALSE,
            EDGE_FALLTHROUGH, EDGE_CALL, Edge)

from octopus.analysis.graph import Graph
from octopus.core.function import get_block_index
from octopus.syspath.imcomplete_emulator import ImcompleteWasmSSAEmulatorEngine
from octopus.syspath.util import *
from octopus.syspath.block_recorder import BlolckRecorder
from octopus.arch.wasm.analyzer import WasmModuleAnalyzer

from octopus.core.edge import *
from octopus.syspath.stack_checker import StackChecker, ExpandStackChecker

import random
import importlib
from collections import defaultdict

from octopus.syspath.api import API
from octopus.syspath.execution_path import GeneralExecutionPathNode, AmbiguExecutionPathNode


class SysGraph(Graph):
    specFunc = ["printf", "open", "fprintf", "putc", "puts", "fputc", "fputs", "fwrite"]
    
    def __init__(self, cfg, api2trace, mapper, filename='graph.cfg.gv', design=None, only_func_name=None, simplify=False):
        Graph.__init__(self, cfg.basicblocks, cfg.edges, filename=filename,
                       design=design)
        self.cfg = cfg
        self.analyzer = cfg.analyzer
        self.func2trace = {}
        self.api2trace = api2trace 
        self.mapper = mapper
        self.only_func_name = only_func_name
        self.entry_function_names = []
        
        wasmVM = ImcompleteWasmSSAEmulatorEngine(
            cfg, func_index2func_name=mapper)
        self.wasmVM = wasmVM # used for handling special functions
        self.simplify = simplify

        self.bullshit_wasm_funcs = ["strcat", "printf", "vprintf", "strcmp", "strcpy", "strlen", "dlmalloc", "sbrk"]
        self.recovered_funcs = []

        self.register_handler()
        self.register_checker()
        self.register_queryer()
        self.init()
        # if self.simplify:
        #     self.simplify_cfg()
        # self.preprocess()

####### Below is the functions that we use to prepocess CFG #######      
    def simplify_cfg(self):
        """
        According to our prior experiments. There could be 35 million paths in 1 function.
        Simply tranversing all paths is unacceptable. Also, we notice that most basic blocks
        have no syscall, making many branches have no influence to the syscall trace. So, we
        are motivited to simplify the CFG to reduce the paths num.
        """
        print("=======simplify=======")
        self.s_functions = {}
        sum_p, sum_s = 0, 0
        for f in self.cfg.functions:
            if self.only_func_name:
                if self.get_func_readable_name(f) in self.only_func_name:
                    # print(self.get_func_readable_name(f))
                    # render(f, "cfg-{}".format(self.get_func_readable_name(f)), self.bb2api)
                    s_func, merge_log = f.simplify(self.bb2api)
                    self.s_functions[f.name] = s_func
                    # render(s_func, "s-cfg-{}".format(self.get_func_readable_name(f)), self.bb2api)
                else:
                    continue
            else:
                if self.get_func_readable_name(f) in self.func_need_tr:
                    # print(self.get_func_readable_name(f))
                    # if self.get_func_readable_name(f) == "_getopt_internal":
                    #     s_func, merge_log = f.simplify(self.bb2api, debug=True)
                    s_func, merge_log = f.simplify(self.bb2api)
                    self.s_functions[f.name] = s_func
                    p,s = len(f.basicblocks), len(s_func.basicblocks)
                    sum_p += p
                    sum_s += s
                    print("{}: previous: {}, simplified: {}".format(self.get_func_readable_name(f), p,s))
                    # visualize
                    # render(f, "func/ori-{}".format(self.get_func_readable_name(f)), self.bb2api)
                    # render(s_func, "func/sim-{}".format(self.get_func_readable_name(f)), self.bb2api)
                    # render(s_func, "func/logsim-{}".format(self.get_func_readable_name(f)), self.bb2api)
                    # dump_merge_log("func/ml-{}.txt".format(self.get_func_readable_name(f)), merge_log)
                else:
                    continue
        print("totle: previous: {}, simplified: {}".format(sum_p,sum_s))


    def register_handler(self):
        print("register special function handler...")
        handlers = importlib.import_module("octopus.syspath.handler")
        self.func2handler = {}
        for spec_func in self.specFunc:
            handler = getattr(handlers, spec_func+"_handler")
            self.func2handler[spec_func] = handler

        
    def register_checker(self):
        print("register special function checker...")
        checkers = importlib.import_module("octopus.syspath.checker")
        self.func2checker = {}
        for spec_func in self.specFunc:
            checker = getattr(checkers, spec_func+"_checker")
            self.func2checker[spec_func] = checker
    

    def register_queryer(self):
        print("register special function queryer...")
        queryers = importlib.import_module("octopus.syspath.queryer")
        self.func2queryer = {}
        for spec_func in self.specFunc:
            queryer = getattr(queryers, spec_func+"_queryer")
            self.func2queryer[spec_func] = queryer


    def init(self):
        """
        1. find the finctions that need to build path2api
        2. record the syacall trace(s) held by each basicblock
        """
        print("=======init=======")
        print("extract and record information inside the api calls, which may take a few minutes...")
        self.init_indirect_function()
        # wasm implement some of its own lib functions, 
        # we should ignore the logic in these functions.
        for func in self.cfg.functions:
            func.remove_unreachable_bb()
        func_need_tr = []
        changed = False
        bb2api = defaultdict(list) # record syscall trace in each basic block
        used_api = set()
        handled_func = 0
        for i in range(1000):
            for func in self.cfg.functions:
                if not hasattr(func, "callees"):
                    func.callees = []
                if not hasattr(func, "indirect_callees"):
                    func.indirect_callees = []
                func_name = self.get_func_readable_name(func)
                # if func_name in func_need_tr:
                #     continue
                if func_name in self.bullshit_wasm_funcs:
                    continue
                for bb in func.basicblocks:
                    old_api_trace = bb2api[bb.name]
                    bb2api[bb.name] = []
                    
                    for instruction in bb.instructions:
                        if instruction.name == "call_indirect":
                            callee_type = get_indirect_callee_type(instruction)
                            try:
                                callee_indexs_in_cfg = self.type2func_index_in_cfg[callee_type] # index in cfg
                            except KeyError:
                                continue
                            callee_indexs = \
                                [ int(self.cfg.functions[_].name[5:]) for _ in callee_indexs_in_cfg ] # function index
                            # construc an API obj for this indirect call
                            callee_names = [ self.mapper[_] for _ in callee_indexs ]
                            api = API("^" + "&".join(callee_names))
                            position = "{}#{}".format(bb.name, instruction.offset)
                            api.set_position(position)
                            # test if this indirect call would involve system call
                            contain_syscall = False
                            for callee_name in callee_names:
                                if callee_name in self.api2trace:
                                    continue
                                # we assume that developers would not write a indirect call to call system functions
                                if callee_name in func_need_tr:
                                    contain_syscall = True
                                    break
                            if contain_syscall:
                                # if this indirect call would involve system call, record it
                                if func_name not in func_need_tr:
                                    func_need_tr.append(func_name)
                                if api not in func.indirect_callees:
                                    func.indirect_callees.append(api)
                                bb2api[bb.name].append(api)
                        if instruction.name == "call":
                            callee_index = get_callee_index(instruction)
                            callee_name = self.mapper[callee_index]
                            if callee_name in self.api2trace or callee_name in func_need_tr:
                                # changed = True

                                if func_name not in func_need_tr:
                                    func_need_tr.append(func_name)
                                
                                # record bb2api, record callees of each function
                                if callee_name in self.api2trace:
                                    api = API(callee_name)
                                    position = "{}#{}".format(bb.name, instruction.offset)
                                    api.set_position(position)
                                    used_api.add(callee_name)
                                else:
                                    api = API("$" + callee_name)
                                    position = "{}#{}".format(bb.name, instruction.offset)
                                    api.set_position(position)
                                    if api not in func.callees:
                                        func.callees.append(api)
                                
                                bb2api[bb.name].append(api)
                                
                                # get format string
                                if callee_name in self.specFunc:
                                    self.handle_spec(func, bb, instruction)
                                    handled_func += 1
                                    if handled_func % 10 == 0:
                                        print("# of handled function:", handled_func)
                    new_api_trace = bb2api[bb.name]
                    if new_api_trace != old_api_trace:
                        changed = True
            if not changed:
                break
            else:
                changed = False

        # remove libc api, e.g., printf, read ...
        func_need_tr = [func for func in func_need_tr if func not in self.api2trace]
        self.func_need_tr = func_need_tr
        self.bb2api = bb2api
        self.used_api = used_api
        # print("basic block to api:")
        # print(self.bb2api)

        # print("used api:")
        # print(self.used_api)
    

    def init_indirect_function(self):
        """
        Parse the table, element, and function type section to extract all functions that can be
        called by call_indirect instruction.
        """
        # indirect_functions = {} # key: function's index in cfg; value: function type
        self.type2func_index_in_cfg = {} # key: function type; value: a list of function's index in cfg
        # find function table
        table_index = -1
        for i in range(len(self.analyzer.tables)):
            table = self.analyzer.tables[i]
            if table['element_type'] == 'anyfunc':
                table_index = i
                break
        if table_index == -1:
            return
        table = self.analyzer.tables[table_index]
        element = self.analyzer.elements[table_index]
        assert table["limits_maximum"] == len(element['elems']) + 1 # make sure we find the correct elements
        for func_index in element['elems']:
            index_in_cfg = get_index_in_cfg_by_function_index(self.cfg, func_index)
            func_type = self.analyzer.func_types[index_in_cfg]
            if func_type not in self.type2func_index_in_cfg:
                self.type2func_index_in_cfg[func_type] = []
            self.type2func_index_in_cfg[func_type].append(index_in_cfg)
        return


    def preprocess(self):
        """
        Construct syscall trace for each path in each function.
        Ignore those functions that have no relationship to syscall api.
        Refer to Ball & Larus Path Profiling Algorithm.
        Also refer to https://www.cs.cornell.edu/courses/cs6120/2019fa/blog/efficient-path-prof/ 
        """
        if self.only_func_name:
            func_need_tr = [func for func in self.func_need_tr if func in self.only_func_name]
        else:
            func_need_tr = self.func_need_tr

        print("functions that need to construct path2api:")
        print(func_need_tr)

        if self.simplify:
            functions = list(self.s_functions.values())
        else:
            functions = self.cfg.functions

        for func in functions:
            func_name = self.get_func_readable_name(func)
            if func_name not in func_need_tr:
                continue
            
            print("--------- function <{}> ---------".format(func_name))
            construct_syscall_trace(func, self.bb2api)  


    def get_func_readable_name(self, func):
        if "$" in func.name:
            func_idx = int(func.name[5:])
            func_name = self.mapper[func_idx]
        else:
            func_name = func.name  
        return func_name
    

    def view_functions(self, func_names):
        functions = self.cfg.functions
        func_to_render = []
        for f in functions:
            if self.get_func_readable_name(f) in func_names:
                func_to_render.append(f)
        if func_to_render == []:
            print("No function named as", func_names)
            return
        
        for f in func_to_render:
            render(f, "cfg-{}".format(self.get_func_readable_name(f)), self.bb2api)

        if self.simplify:
            # also render simplified cfg
            functions = self.s_functions
            func_to_render = []
            for f in functions.values():
                if self.get_func_readable_name(f) in func_names:
                    func_to_render.append(f)
                    break
            if func_to_render == []:
                print("No simplified function named as", func_names)
                return
            for f in func_to_render:
                render(f, "s-cfg-{}".format(self.get_func_readable_name(f)), self.bb2api)
    

    def handle_spec(self, func, bb, instruction):
        """
        handle special function, e.g., for printf or fprintf, get its format string
        """
        callee_index = get_callee_index(instruction)
        callee_name = self.mapper[callee_index]
        handler = self.func2handler[callee_name]
        handler(self, func, bb, instruction)


####### Below is the functions that we use to infer paths from syscall trace ####### 
    def solve(self, syscall_trace, cal_coverage = False, output_dir = "default_output_dir"):
        """
        given a syscall_trace monitored by sysdig, return possible paths
        """
        
        # 0. translate syscall trace to possible api trace
        from octopus.syspath.event2api import event_trace2api_trace
        possible_api_traces = event_trace2api_trace(syscall_trace, self.api2trace, self.used_api, self)

        if len(possible_api_traces) == 0:
            return 0 # do not try to analyze an empty trace.

        # 1. preprocess
        # self.preprocess()

        # 2. find possible path using bfs
        final_paths, final_matched_info = [], []
        final_mpps, final_mpps_matched_info = [], []
        for apis, traces in possible_api_traces:
            print("api trace:")
            print(apis)
            apis_with_inferred_locate = self.locate(apis, traces)
            loose_mode = False # though we cannot find a full path, but we can recover some partial path anyway
            self.change_to_amb()
            ExpandStackChecker.init()
            paths, match_infos = self.expand(apis_with_inferred_locate, could_start_from_entry=True)
            if paths != []:
                final_paths += paths
                final_matched_info += match_infos  
            else:
                print("pinpoint failed, try to loose the constraint.")
                loose_mode = True
                paths, match_infos = self.expand_loose(apis_with_inferred_locate, search_type="amb")
                final_paths += paths
                final_matched_info += match_infos
            self.change_to_mpp()
            ExpandStackChecker.init()
            if not loose_mode:
                paths, match_infos = self.expand(apis_with_inferred_locate, could_start_from_entry=True)
                final_mpps += paths
                final_mpps_matched_info += match_infos
            else:
                print("pinpoint failed, try to loose the constraint.")
                paths, match_infos = self.expand_loose(apis_with_inferred_locate, search_type="mpp")
                final_mpps += paths
                final_mpps_matched_info += match_infos
        if final_paths:
            if not os.path.exists("result"):
                os.system("mkdir result")
            abs_output_dir = "{}/result/{}".format(os.getcwd(), output_dir)
            print("writing results to {}".format(abs_output_dir))
            if os.path.exists(abs_output_dir):
                os.system("rm -rf {}".format(abs_output_dir))
            os.system("mkdir -p " + abs_output_dir)
            for i in range(len(final_paths)):
                print("writing {}th amb paths, which matched {} apis".format(i, final_matched_info[i]))
                file_name = "{}/path_{:0>2d}.json".format(abs_output_dir, i)
                final_paths[i].to_json(file_name)
                # full path
                ExpandStackChecker.init()
                self.recovered_funcs = []
                full_path = self.recover(final_paths[i], loose_mode=loose_mode)
                full_path_file_name = "{}/full_path_{:0>2d}.json".format(abs_output_dir, i)
                full_path.to_json(full_path_file_name)
                if cal_coverage:
                    file_name = "{}/coverage_{:0>2d}.json".format(abs_output_dir, i)
                    final_paths[i].cal_coverage(self, file_name)
                    full_path_file_name = "{}/full_path_coverage_{:0>2d}.json".format(abs_output_dir, i)
                    full_path.cal_coverage(self, full_path_file_name)
            MPP_index = 0
            for i in range(len(final_mpps)):
                unfold_final_mpps = final_mpps[i].unfold() # unfold indirect call
                for final_mpp in unfold_final_mpps:
                    print("writing {}th mpp paths, which matched {} apis".format(MPP_index, final_mpps_matched_info[i]))
                    MPP_file_name = "{}/MPP_{:0>2d}.json".format(abs_output_dir, MPP_index)
                    ExpandStackChecker.init()
                    self.recovered_funcs = []
                    MPP = self.recover_MPP(final_mpp, loose_mode=loose_mode)
                    MPP.to_json(MPP_file_name)
                    if cal_coverage:
                        MPP_file_name = "{}/MPP_coverage_{:0>2d}.json".format(abs_output_dir, MPP_index)
                        MPP.cal_coverage(self, MPP_file_name)
                    MPP_index += 1
            return 1
        else:
            print("not found!")
            return 0


    def recover(self, partial_path, should_remove_bb=True, should_recover_full_path=True, should_handle_function_call=True, loose_mode = False):
        """
        recover the full path from the given partial path.
        For each func in partial path, do:
        1. remove will-not-execute blocks in the full cfg
        2. recover the full path according to the domination info
        3. handle the function calls
        """
        # ignore wasm internal function
        if "__" in partial_path.func_readable_name:
            return partial_path
        
        if partial_path.func_readable_name in self.bullshit_wasm_funcs:
            return partial_path
        
        ExpandStackChecker.push_stack(partial_path.func_readable_name, 0)
        if ExpandStackChecker.have_loop():
            ExpandStackChecker.pop_stack()
            return partial_path
        
        if loose_mode:
            self.recovered_funcs.append(partial_path.func_readable_name)

        ret = partial_path.copy()
        ori_func = self.get_func_by_name(ret.func_readable_name)
        # print("recover function: {}; partial path: {}".format(ret.func_readable_name, ret.edges))
        if ori_func == None:
            return ret
        func_remove_non_execute_bbs = ori_func.copy()
        func_remove_non_execute_bbs.add_entry_and_exit()
        if should_remove_bb:
            non_execute_bbs = []
            partial_path_bbs = partial_path.cal_bbs()
            for bb in func_remove_non_execute_bbs.basicblocks:
                if bb.name not in partial_path_bbs and self.min_apis_in_bb(bb.name) > 0 and not loose_mode:
                    non_execute_bbs.append(bb)
            for non_execute_bb in non_execute_bbs:
                func_remove_non_execute_bbs.remove_bb(non_execute_bb)
        
        # recover the full path given the partial path
        if should_recover_full_path:
            full_path = func_remove_non_execute_bbs.cal_full_path(partial_path.edges)
            ret.may_bbs = full_path.copy()
        
        # handle the function calls (which has no syscall) in the full path
        if should_handle_function_call:
            if not should_recover_full_path:
                full_path = partial_path.cal_bbs()
            for bb in full_path:
                api_in_bb = self.bb2api[bb]
                function_contain_event = []
                for api in api_in_bb:
                    if "$" in api.name:
                        function_contain_event.append(api.name[1:])
                    if "^" in api.name:
                        for _ in api.name[1:].split("&"):
                            function_contain_event.append(_)
                if loose_mode and partial_path.edges == ["entry->exit"]:
                    function_contain_event = []
                if bb in ["entry", "exit"]:
                    continue
                bb_obj = self.get_bb_by_name(bb)
                for inst in bb_obj.instructions:
                    if inst.name == "call_indirect":
                        callee_type = get_indirect_callee_type(inst)
                        try:
                            callee_indexs_in_cfg = self.type2func_index_in_cfg[callee_type] # index in cfg
                        except KeyError:
                            continue
                        callee_indexs = \
                            [ int(self.cfg.functions[_].name[5:]) for _ in callee_indexs_in_cfg ] # function index
                        # construc an API obj for this indirect call
                        callee_names = [ self.mapper[_] for _ in callee_indexs ]
                        for callee_name in callee_names:
                            if callee_name in function_contain_event:
                                # this inst may contains syscall, so it should be handled later
                                continue
                        for callee_name in callee_names:
                            callee = self.get_func_by_name(callee_name)
                            tmp_partial_path = GeneralExecutionPathNode(callee, callee_name)
                            tmp_partial_path.add_bb_head("entry")
                            tmp_partial_path.add_bb_tail("exit")
                            a_path = AmbiguExecutionPathNode(callee, callee_name)
                            a_path.update_by(tmp_partial_path)
                            if not loose_mode or callee_name not in self.recovered_funcs:
                                callee_full_path = self.recover(a_path, loose_mode=loose_mode)
                                callee_pos = "{}#{}".format(bb, inst.offset)
                                ret.add_child(callee_pos, callee_full_path, update=False)
                    if inst.name == "call":
                        callee_index = get_callee_index(inst)
                        callee_name = self.mapper[callee_index]
                        if callee_name in function_contain_event:
                            # this inst may contains syscall, so it should be handled later
                            continue
                        callee = self.get_func_by_name(callee_name)
                        tmp_partial_path = GeneralExecutionPathNode(callee, callee_name)
                        tmp_partial_path.add_bb_head("entry")
                        tmp_partial_path.add_bb_tail("exit")
                        a_path = AmbiguExecutionPathNode(callee, callee_name)
                        a_path.update_by(tmp_partial_path)
                        if not loose_mode or callee_name not in self.recovered_funcs:
                            callee_full_path = self.recover(a_path, loose_mode=loose_mode)
                            callee_pos = "{}#{}".format(bb, inst.offset)
                            ret.add_child(callee_pos, callee_full_path, update=False)

        # handle the children in the partial path
        for i in range(len(partial_path.children)):
            child = partial_path.children[i]
            child_pos = partial_path.children_pos[i]
            child_name = child.func_readable_name
            if not loose_mode or child_name not in self.recovered_funcs:
                full_child = self.recover(child, loose_mode=loose_mode)
                ret.add_child(child_pos, full_child)

        ExpandStackChecker.pop_stack()
        return ret
        

    def recover_MPP(self, partial_path, loose_mode = False):
        """
        recover a most possible path from the given partial path.
        in this function, we mainly use the api_list (i.e. checkpoints) in the partial path to recover the MPP
        For each func in partial path, do:
        1. remove will-not-execute blocks in the full cfg
        2. recover the path according to information of each two checkpoints
        3. handle the function calls
        """
        # ignore wasm internal functions
        if "__" in partial_path.func_readable_name:
            return partial_path

        if partial_path.func_readable_name in self.bullshit_wasm_funcs:
            return partial_path
        
        ExpandStackChecker.push_stack(partial_path.func_readable_name, 0)
        if ExpandStackChecker.have_loop():
            ExpandStackChecker.pop_stack()
            return partial_path

        if loose_mode:
            self.recovered_funcs.append(partial_path.func_readable_name)

        ret = GeneralExecutionPathNode(partial_path.func, partial_path.func_readable_name)
        ori_func = self.get_func_by_name(ret.func_readable_name)
        if ori_func == None or ret.func_readable_name in self.api2trace:
            ExpandStackChecker.pop_stack()
            return ret
        func_remove_non_execute_bbs = ori_func.copy()
        func_remove_non_execute_bbs.add_entry_and_exit()
        non_execute_bbs = []
        partial_path_bbs = partial_path.bbs
        # print("recover function: {}; checkpoints: {}".format(ret.func_readable_name, partial_path_bbs))
        for bb in func_remove_non_execute_bbs.basicblocks:
            if bb.name not in partial_path_bbs and self.min_apis_in_bb(bb.name) > 0 and not loose_mode:
                non_execute_bbs.append(bb)
        for non_execute_bb in non_execute_bbs:
            func_remove_non_execute_bbs.remove_bb(non_execute_bb)
        bb_names = [_.name for _ in func_remove_non_execute_bbs.basicblocks]
        if "entry" not in bb_names:
            # in this case, this function would not be executed
            ExpandStackChecker.pop_stack()
            return ret
        
        # recover the  most possible path given the partial path
        checkpoints = partial_path_bbs
        if loose_mode and "entry" not in checkpoints:
            checkpoints.insert(0, "entry")
        if loose_mode and "exit" not in checkpoints:
            checkpoints.append("exit")
        MPP = func_remove_non_execute_bbs.cal_MPP(checkpoints)
        ret.bbs = MPP.copy()
        
        # handle the function calls (which has no syscall) in the full path
        
        for bb in MPP:
            api_in_bb = self.bb2api[bb]
            function_contain_event = []
            for api in api_in_bb:
                if "$" in api.name:
                    function_contain_event.append(api.name[1:])
                if "^" in api.name:
                    for _ in api.name[1:].split("&"):
                        function_contain_event.append(_)
            if bb in ["entry", "exit"]:
                continue
            bb_obj = self.get_bb_by_name(bb)
            for inst in bb_obj.instructions:
                if inst.name == "call":
                    callee_index = get_callee_index(inst)
                    callee_name = self.mapper[callee_index]
                    if callee_name in function_contain_event:
                        # this inst may contains syscall, so it should be handled later
                        continue
                    callee = self.get_func_by_name(callee_name)
                    tmp_partial_path = GeneralExecutionPathNode(callee, callee_name)
                    tmp_partial_path.add_bb_head("entry")
                    tmp_partial_path.add_bb_tail("exit")
                    if not loose_mode or callee_name not in self.recovered_funcs:
                        callee_full_path = self.recover_MPP(tmp_partial_path, loose_mode=loose_mode)
                        callee_pos = "{}#{}".format(bb, inst.offset)
                        ret.add_child(callee_pos, callee_full_path, update=False)
        


        # handle the children in the partial path
        for i in range(len(partial_path.children)):
            child = partial_path.children[i]
            child_pos = partial_path.children_pos[i]
            child_name = child.func_readable_name
            if not loose_mode or child_name not in self.recovered_funcs:
                full_child = self.recover_MPP(child, loose_mode=loose_mode)
                ret.add_child(child_pos, full_child)

        ExpandStackChecker.pop_stack()
        return ret
    


    def expand(self, apis, could_start_from_entry=False):
        """
        expand step: 
        1. find a most possible api in apis
        2. expand it
        """
        # if len(self.basicblocks) > 20000:
        #     return [], []
        apis_to_expand = find_most_possible_api(apis)
        final_paths, final_matched_infos = [], []
        if apis_to_expand == []:
            print("cannot locate a suitable api to expand, search from the entry functions")
            paths, matched_infos = self.match_from_entry(apis)
            final_paths += paths
            final_matched_infos += matched_infos
        else:
            for api_to_expand in apis_to_expand:
                paths, matched_infos = self.expand_one(apis, api_to_expand)
                final_paths += paths
                final_matched_infos += matched_infos
            if final_paths == [] and could_start_from_entry:
                print("expand failed. try to match from the entry")
                paths, matched_infos = self.match_from_entry(apis)
                final_paths += paths
                final_matched_infos += matched_infos
        return final_paths, final_matched_infos


    def expand_loose(self, apis, search_type):
        """
        similar to function expand but with loose constraints
        expand step: 
        1. find a most possible api in apis
        2. expand it
        """
        exclude_apis = []
        final_path = None
        final_matched_num = 0
        chance = 5
        import timeout_decorator
        while chance > 0:
            try:
                apis_to_expand = find_most_possible_lib_api(apis, exclude_apis)
                if apis_to_expand == []:
                    break
                api_to_expand = apis_to_expand[0]
                exclude_apis.append(api_to_expand)
                
                print("expand based on", api_to_expand)

                # search !!
                func_index = get_func_index_by_inst_position(api_to_expand.position)
                func = self.cfg.functions[func_index]
                s_func = self.s_functions[func.name]
                func_name = self.get_func_readable_name(func)
                paths, matched_infos = self.search_path_in_func(s_func, api_to_expand, apis, loose=True)
                assert len(paths) == len(matched_infos)
                if paths == []:
                    chance -= 1
                    continue
                path = paths[0]
                matched_info = matched_infos[0]
                
                # matched num
                match_start, match_end = matched_info
                final_matched_num += match_end - match_start
            
                # add to final path
                callsites = self.get_callsites(self.get_func_readable_name(func))
                if final_path == None:
                    final_path = path.copy()
                    final_matched_num += match_end - match_start
                else:
                    if callsites == []:
                        # add final path to path
                        path.add_child("pos_placeholder", final_path.copy(), update=False)
                        final_path = path.copy()
                    else:
                        # add path to final path
                        final_path.add_child("pos_placeholder", path.copy(), update=False)
                
                if callsites == []:
                    continue
                callsite = callsites[0]
                callsite.set_possibility(api_to_expand.possibility + len(path.api_list))
                to_match_in_caller = tuple(list(apis[:match_start]) + [tuple([callsite])] + list(apis[match_end:]))
                apis = to_match_in_caller
            except timeout_decorator.timeout_decorator.TimeoutError:
                break
        
        if final_path != None:
            root_func_name = final_path.func_readable_name
        if final_path == None or root_func_name != "main":
            main_func = self.get_func_by_name("main")
            if search_type == "amb":
                tmp = AmbiguExecutionPathNode(main_func, "main")
                tmp.add_edge("entry", "exit")
            elif search_type == "mpp":
                tmp = GeneralExecutionPathNode(main_func, "main")
                tmp.add_bb_tail("entry")
                tmp.add_bb_tail("exit")
            if final_path != None:
                tmp.add_child("pos_placeholder", final_path.copy())
            final_path = tmp.copy()

        return [final_path], [final_matched_num]


    def match_from_entry(self, apis):
        final_paths, final_matched_infos = [], []
        for func_name in self.entry_function_names:
            print("entry function: {}".format(func_name))
            func = self.get_s_func_by_name(func_name)
            StackChecker.init()
            StackChecker.push_stack(func_name, len(apis))
            paths, matched_infos = self.bfs_search(self, func, func.basicblocks[0], apis, 0)
            StackChecker.pop_stack()
            final_paths += paths
            final_matched_infos += matched_infos
        return final_paths, final_matched_infos


    def expand_one(self, apis, api_to_expand, loose = False):
        print("expand from", api_to_expand)

        # search !!
        func_index = get_func_index_by_inst_position(api_to_expand.position)
        func = self.cfg.functions[func_index]
        s_func = self.s_functions[func.name]
        func_name = self.get_func_readable_name(func)
        ExpandStackChecker.push_stack(func_name, len(apis))
        if ExpandStackChecker.have_loop():
            ExpandStackChecker.pop_stack()
            return [], []
        paths, matched_info = self.search_path_in_func(s_func, api_to_expand, apis)
        assert len(paths) == len(matched_info)
        
        callsites = self.get_callsites(self.get_func_readable_name(func))
        if callsites == []: # can not find a caller, that's all we could find.
            ExpandStackChecker.pop_stack()
            return paths, matched_info
            
            
        # search in its caller, i.e., bottom up.
        final_paths = []
        final_matched_infos = []
        for i in range(len(paths)):
            path = paths[i]
            match_start, match_end = matched_info[i]
            for callsite in callsites:
                callsite.set_possibility(api_to_expand.possibility + len(path.api_list))
                to_match_in_caller = tuple(list(apis[:match_start]) + [tuple([callsite])] + list(apis[match_end:]))
                try:
                    caller_paths, caller_matched_infos = self.expand(to_match_in_caller)
                except NotImplementedError:
                    continue
                for i in range(len(caller_paths)):
                    caller_path = caller_paths[i]
                    caller_path.children.append(path)
                    caller_path.children_pos.append(callsite.position)
                    final_paths.append(caller_path)
                    caller_matched_start, caller_matched_end = caller_matched_infos[i]
                    final_matched_infos.append((caller_matched_start, caller_matched_end + match_end - match_start + 1))
        ExpandStackChecker.pop_stack()
        return final_paths, final_matched_infos


    def locate(self, apis, trace):
        assert len(apis) == len(trace)
        res = []
        for i in range(len(apis)):
            possible_api = apis[i]
            correspond_trace = trace[i]
            api_position_and_possibility = []
            
            for api in possible_api:
                if api in self.specFunc:
                    poss = self.infer_position(api, correspond_trace)
                    if poss != []:
                        for pos, possiblity in poss:
                            api_position_and_possibility.append((api, pos, possiblity, correspond_trace))
                    else:
                        api_position_and_possibility.append((api, None, -1000, correspond_trace))
                else:
                    api_position_and_possibility.append((api, None, -1000, correspond_trace))
            
            api_position_and_possibility = sorted(
                api_position_and_possibility,
                key=lambda item: item[2],
                reverse=True
            )
            # we only use the results that have top 3 possibility
            top_3_api_position_and_possibility = api_position_and_possibility[0:1]
            k = 0
            for _ in api_position_and_possibility[1:]:
                api, pos, possiblity, correspond_trace = _
                if possiblity < top_3_api_position_and_possibility[-1][2]:
                    top_3_api_position_and_possibility.append(_)
                    k += 1
                else:
                    top_3_api_position_and_possibility.append(_)
                if k >= 2:
                    break
                
            res.append(tuple([API(api_name, position, _, trace) for api_name, position, _, trace in top_3_api_position_and_possibility]))
        res = tuple(res)
        return res


    def search_path_in_func(self, func, api, to_match, loose=False):
        return self.naiive_search(func, api, to_match, loose)


    def naiive_search(self, func, api, to_match, loose = False):
        """
        search paths that contain api and (partially) match the to_match
        trace (i.e., allowing some heading and tailing apis are left unmatched, 
        which might get matched in other function).
        A naive algorithm (test and roll back).
        return path and matched info (match start and match end)
        """
        for api_index in range(len(to_match)):
            if api in to_match[api_index]:
                break
        left_to_match = to_match[:api_index+1] # both will contain api
        right_to_match = to_match[api_index:]
        bb_name = api.position.split("#")[0]
        bb = func.get_bb_by_name(bb_name)
        start_offset = get_inst_offset_in_position(api.position)
        StackChecker.init()
        StackChecker.push_stack(self.get_func_readable_name(func), len(right_to_match))
        right_paths, right_matched = self.bfs_search(self, func, bb, right_to_match, start_offset, tuple([api.name]), loose)
        # this step is necessary due to the use of cache, otherwise any modification to the results would change the value in the cache
        right_paths, right_matched = right_paths.copy(), right_matched.copy() 
        StackChecker.pop_stack()
        
        StackChecker.init()
        StackChecker.push_stack(self.get_func_readable_name(func), len(right_to_match))
        left_paths, left_matched = self.reverse_bfs_search(self, func, bb, left_to_match, start_offset, tuple([api.name]), loose)
        # this step is necessary due to the use of cache, otherwise any modification to the results would change the value in the cache
        left_paths, left_matched = left_paths.copy(), left_matched.copy() 
        StackChecker.pop_stack()
        assert len(right_paths) == len(right_matched) and len(left_paths) == len(left_matched)
        # merge left and right
        paths = []
        matched_info = []
        # both left path and right path contain bb, remove bb from one of them (left path)
        # here we should handle the case that api is in the middle of the bb
        for i in range(len(left_paths)):
            lp = left_paths[i]
            # lm = left_matched[i]
            # lp.bbs = lp.bbs[:-1] # remove last bb
            lp.api_list = lp.api_list[:-1] # remove last api
            left_matched[i] -= 1 # remove last api
        # merge
        for i in range(len(left_paths)):
            for j in range(len(right_paths)):
                lp = left_paths[i]
                lm = left_matched[i]
                rp = right_paths[j]
                rm = right_matched[j]
                paths.append(lp + rp)
                matched_info.append((api_index-lm,api_index+rm))
        return paths, matched_info
    
    def api_match(self, api_from_bb, apis_from_trace, loose = False):
        """
        test if api from basic blocks match the api infer from the trace.
        api_from_bb: the api that extract from the basic blocks, which contains position info
        apis_from_trace: a list of apis, each represent a possible api inferred from a trace
        """
        if loose:
            for _ in apis_from_trace:
                if _.name == api_from_bb.name:
                    return True
        else:
            for _ in apis_from_trace:
                if _.name != api_from_bb.name:
                    continue
                # if _ has position info
                if _.position:
                    if _ == api_from_bb:
                        return True
                    else:
                        continue
                else: # if _ has no position info
                    if api_from_bb.name in self.specFunc: # for special api we could calculate how possible api match the trace
                        possibility = self.query_possibility(api_from_bb, _.trace)
                        if possibility > 0:
                            return True
                        else:
                            continue
                    else:
                        # in this case, we only know they have the same api name, 
                        # and this api is not a special api that we could infer more from its argument
                        # so, for soundness, we consider they are matched.
                        return True
        return False



####### Below is some util functions ####### 
    def get_callsites(self, callee_name):
        callsites = []
        for func in self.s_functions.values():
            for callee in func.callees:
                if ("$"+callee_name) == callee.name:
                    callsites.append(callee) 
        return callsites


    def get_func_by_name(self, func_name):
        for func in self.cfg.functions:
            if func_name == self.get_func_readable_name(func):
                return func


    def get_s_func_by_name(self, func_name):
        for func in self.cfg.functions:
            if func_name == self.get_func_readable_name(func):
                if func.name in self.s_functions:
                    return self.s_functions[func.name]
                else: 
                    return None # in this case, this function has no syscall
        raise ValueError("cannot find a function named as {}".format(func_name))


    def query_possibility(self, api, trace):
        """
        return how possible the trace is generated by the given api.
        """
        queryer = self.func2queryer[api.name]
        return queryer(self, api, trace)
        
        
    def infer_position(self, matched_api, event_trace):
        """
        infer the possible position of an api according to the given event trace
        """
        checker = self.func2checker[matched_api]
        return checker(self, event_trace)
    

    def set_entry_function_names(self, entry_function_names):
        if not isinstance(entry_function_names, list):
            print("please provide a list of string, whose element should be the names of entry functions")
        print("set entry functions: {}".format(entry_function_names))
        self.entry_function_names = entry_function_names
    

    def get_bb_by_name(self, block_name):
        for bb in self.basicblocks:
            if bb.name == block_name:
                return bb
        raise ValueError("cannot find a basic block named as {}".format(block_name))


    def block2src(self, block_name, recompute=False):
        if block_name == "entry" or block_name == "exit":
            # print("ignore", block_name)
            return
        if self.bb2line and not recompute:
            return self.bb2line[block_name]
        import octopus.arch.wasm.dawrf_parser as locator      
        bb = self.get_bb_by_name(block_name)
        func_index = int(block_name.split("_")[1], 16) + len(self.analyzer.imports_func)
        src_start = locator.get_source_location(self.analyzer, func_index, bb.start_offset)
        src_end = locator.get_source_location(self.analyzer, func_index, bb.end_offset)
        # print('{}: {} -> {}'.format(block_name, src_start, src_end))
        return '{}->{}'.format(src_start, src_end)
        
    
    def quick_block2src(self, block_name, dwarf_entries, recompute=False):
        if block_name == "entry" or block_name == "exit":
            # print("ignore", block_name)
            return
        if self.bb2line and not recompute:
            return self.bb2line[block_name]
        import octopus.arch.wasm.dawrf_parser as locator      
        bb = self.get_bb_by_name(block_name)
        func_index = int(block_name.split("_")[1], 16) + len(self.analyzer.imports_func)
        
        src_start, src_end = None, None
        # src_start
        bb_start_address = locator.get_real_addr(self.analyzer, func_index, bb.start_offset)
        # binary search
        n = len(dwarf_entries)
        start = 0
        end = n-1
        while start <= end:
            mid = (start + end) // 2
            if mid == n-1:
                src_start = dwarf_entries[mid][1:]
                break
            if bb_start_address >= dwarf_entries[mid][0] and bb_start_address < dwarf_entries[mid+1][0]:
                src_start = dwarf_entries[mid][1:]
                break
            elif bb_start_address < dwarf_entries[mid][0]:
                end = mid - 1
            else:
                start = mid + 1
        
        # src_end
        bb_end_address = locator.get_real_addr(self.analyzer, func_index, bb.end_offset)
        # binary search
        n = len(dwarf_entries)
        start = 0
        end = n-1
        while start <= end:
            mid = (start + end) // 2
            if mid == n-1:
                src_end = dwarf_entries[mid][1:]
                break
            if bb_end_address >= dwarf_entries[mid][0] and bb_end_address < dwarf_entries[mid+1][0]:
                src_end = dwarf_entries[mid][1:]
                break
            elif bb_end_address < dwarf_entries[mid][0]:
                end = mid-1
            else:
                start = mid + 1

        # print('{}: {} -> {}'.format(block_name, src_start, src_end))
        return '{}->{}'.format(src_start, src_end)


    def init_coverage(self, filename):
        """
        calculate the corresponding code lines of each basic block 
        and store the result in the file
        """
        if os.path.exists(filename):
            print("reading coverage info from {} ...".format(filename))
            fp = open(filename, 'r')
            self.bb2line = json.load(fp)
            fp.close()
        else:
            print("build coverage info from scratch, this may take several hours...")
            self.bb2line = {}.copy()
        try:
            print("tranverse dawrf to extract coverage info ...")
            import octopus.arch.wasm.dawrf_parser as dawrf_parser
            dwarf_entries = dawrf_parser.traverse_dwarf_info(self.analyzer.dwarf_info)
            print("check if all bbs have cov info ...")
            cnt = 0
            for bb in self.basicblocks:
                if bb.name not in self.bb2line:
                    cnt += 1
                    # self.bb2line[bb.name] = self.block2src(bb.name, recompute=True)
                    self.bb2line[bb.name] = self.quick_block2src(bb.name, dwarf_entries, recompute=True)
                if cnt % 10 == 0 and cnt > 0:
                    print(time(), "build {} bbs' cov info".format(cnt))
        except KeyboardInterrupt:
            print("detect keyboard interruption")
            print('writing bb2line into {}...'.format(filename))
            fp = open(filename, 'w')
            json.dump(self.bb2line, fp, indent=2)
            fp.close()
            raise KeyboardInterrupt

        
        print('writing bb2line into {}...'.format(filename))
        fp = open(filename, 'w')
        json.dump(self.bb2line, fp, indent=2)
        fp.close()
    

    def min_apis_in_bb(self, bb_name):
        """
        calculate the minimum number of apis the given bb should contain
        """
        apis = self.bb2api[bb_name]
        min_api_num = 0
        if apis == []:
            return min_api_num
        for api in apis:
            if "$" in api.name:
                func_name = api.name[1:]
                s_func = self.get_s_func_by_name(func_name)
                min_api_num += s_func.get_min_api_num(self.bb2api, self)
            elif "^" in api.name:
                indirect_call_func_names = api.name[1:].split("&")
                tmp_min = 10000
                for func_name in indirect_call_func_names:
                    s_func = self.get_s_func_by_name(func_name)
                    if s_func == None:
                        tmp_min = 0
                        break
                    if s_func.get_min_api_num(self.bb2api, self) < tmp_min:
                        tmp_min = s_func.get_min_api_num(self.bb2api, self)
                min_api_num += tmp_min
            else:
                min_api_num += 1
        return min_api_num


    def change_to_amb(self):
        from octopus.syspath.search_amb import bfs_search, reverse_bfs_search
        self.bfs_search = bfs_search
        self.reverse_bfs_search = reverse_bfs_search
    

    def change_to_mpp(self):
        from octopus.syspath.search_mpp import bfs_search, reverse_bfs_search
        self.bfs_search = bfs_search
        self.reverse_bfs_search = reverse_bfs_search
        