import copy
from queue import PriorityQueue, Queue
from re import I, S
from graphviz import Digraph
import os
import json

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

import random
import importlib
from collections import defaultdict

from octopus.syspath.api import API
from octopus.syspath.execution_path import GeneralExecutionPathNode


class SysGraph(Graph):
    specFunc = ["printf", "open", "fprintf"]
    
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
        
        self.register_handler()
        self.register_checker()
        self.register_queryer()
        self.init()
        if self.simplify:
            self.simplify_cfg()
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
        for f in self.cfg.functions:
            if self.only_func_name:
                if self.get_func_readable_name(f) in self.only_func_name:
                    # print(self.get_func_readable_name(f))
                    # render(f, "cfg-{}".format(self.get_func_readable_name(f)), self.bb2api)
                    s_func = f.simplify(self.bb2api)
                    self.s_functions[f.name] = s_func
                    # render(s_func, "s-cfg-{}".format(self.get_func_readable_name(f)), self.bb2api)
                else:
                    continue
            else:
                if self.get_func_readable_name(f) in self.func_need_tr:
                    s_func = f.simplify(self.bb2api)
                    self.s_functions[f.name] = s_func
                    # visualize
                    # render(f, "func/ori-{}".format(self.get_func_readable_name(f)), self.bb2api)
                    # render(s_func, "func/sim-{}".format(self.get_func_readable_name(f)), self.bb2api)
                else:
                    continue
        
    
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
        self.init_indirect_function()
        for func in self.cfg.functions:
            func.remove_unreachable_bb()
        func_need_tr = []
        changed = False
        bb2api = defaultdict(list) # record syscall trace in each basic block
        used_api = set()
        for i in range(1000):
            for func in self.cfg.functions:
                if not hasattr(func, "callees"):
                    func.callees = []
                if not hasattr(func, "indirect_callees"):
                    func.indirect_callees = []
                func_name = self.get_func_readable_name(func)
                # if func_name in func_need_tr:
                #     continue
                for bb in func.basicblocks:
                    old_api_trace = bb2api[bb.name]
                    bb2api[bb.name] = []
                    
                    for instruction in bb.instructions:
                        if instruction.name == "call_indirect":
                            callee_type = get_indirect_callee_type(instruction)
                            callee_indexs_in_cfg = self.type2func_index_in_cfg[callee_type] # index in cfg
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
                                assert callee_name not in self.api2trace
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

        # 1. preprocess
        # self.preprocess()

        # 2. find possible path using bfs
        final_paths, final_matched_info = [], []
        for apis, traces in possible_api_traces:
            print("api trace:")
            print(apis)
            apis_with_inferred_locate = self.locate(apis, traces)
            paths, match_infos = self.expand(apis_with_inferred_locate, could_start_from_entry=True)
            if paths != []:
                final_paths += paths
                final_matched_info += match_infos
        if final_paths:
            if not os.path.exists("result"):
                os.system("mkdir result")
            abs_output_dir = "{}/result/{}".format(os.getcwd(), output_dir)
            print("writing results to {}".format(abs_output_dir))
            if os.path.exists(abs_output_dir):
                os.system("rm -rf {}".format(abs_output_dir))
            os.mkdir(abs_output_dir)
            for i in range(len(final_paths)):
                print("writing {}th path, which matched {} apis".format(i, final_matched_info[i]))
                file_name = "{}/path_{:0>2d}.json".format(abs_output_dir, i)
                final_paths[i].to_json(file_name)
                full_path = self.recover(final_paths[i], should_remove_bb=True, should_recover_full_path=True, should_handle_function_call=True)
                full_path_file_name = "{}/full_path_{:0>2d}.json".format(abs_output_dir, i)
                full_path.to_json(full_path_file_name)
                if cal_coverage:
                    file_name = "{}/coverage_{:0>2d}.json".format(abs_output_dir, i)
                    final_paths[i].cal_coverage(self, file_name)
                    full_path_file_name = "{}/full_path_coverage_{:0>2d}.json".format(abs_output_dir, i)
                    full_path.cal_coverage(self, full_path_file_name)
            return 1
        else:
            print("not found!")
            return 0


    def recover(self, partial_path, should_remove_bb=False, should_recover_full_path=False, should_handle_function_call=False):
        """
        recover the full path from the given partial path.
        For each func in partial path, do:
        1. remove will-not-execute blocks in the full cfg
        2. recover the full path according to the domination info
        3. handle the function calls
        """
        
        ret = partial_path.copy()
        ori_func = self.get_func_by_name(ret.func_readable_name)
        print("recover function: {}; partial path: {}".format(ret.func_readable_name, ret.bbs))
        if ori_func == None:
            return ret
        func_remove_non_execute_bbs = ori_func.copy()
        func_remove_non_execute_bbs.add_entry_and_exit()
        if should_remove_bb:
            non_execute_bbs = []
            for bb in func_remove_non_execute_bbs.basicblocks:
                if bb.name not in partial_path.bbs and self.min_apis_in_bb(bb.name) > 0:
                    non_execute_bbs.append(bb)
            for non_execute_bb in non_execute_bbs:
                func_remove_non_execute_bbs.remove_bb(non_execute_bb)
        
        # recover the full path given the partial path
        if should_recover_full_path:
            full_path = func_remove_non_execute_bbs.cal_full_path(partial_path.bbs)
            ret.bbs = full_path.copy()
        
        # handle the function calls (which has no syscall) in the full path
        if should_handle_function_call:
            if not should_recover_full_path:
                full_path = partial_path.bbs
            for bb in full_path:
                if bb in ["entry", "exit"]:
                    continue
                if self.bb2api[bb] == []:
                    bb_obj = self.get_bb_by_name(bb)
                    for inst in bb_obj.instructions:
                        if inst.name == "call_indirect":
                            callee_type = get_indirect_callee_type(inst)
                            callee_indexs_in_cfg = self.type2func_index_in_cfg[callee_type] # index in cfg
                            callee_indexs = \
                                [ int(self.cfg.functions[_].name[5:]) for _ in callee_indexs_in_cfg ] # function index
                            # construc an API obj for this indirect call
                            callee_names = [ self.mapper[_] for _ in callee_indexs ]
                            for callee_name in callee_names:
                                callee = self.get_func_by_name(callee_name)
                                tmp_partial_path = GeneralExecutionPathNode(callee, callee_name)
                                tmp_partial_path.add_bb_head("entry")
                                tmp_partial_path.add_bb_tail("exit")
                                callee_full_path = self.recover(tmp_partial_path, should_handle_function_call=True, should_recover_full_path=True)
                                callee_pos = "{}#{}".format(bb, inst.offset)
                                ret.add_children(callee_pos, callee_full_path)
                        if inst.name == "call":
                            callee_index = get_callee_index(inst)
                            callee_name = self.mapper[callee_index]
                            callee = self.get_func_by_name(callee_name)
                            tmp_partial_path = GeneralExecutionPathNode(callee, callee_name)
                            tmp_partial_path.add_bb_head("entry")
                            tmp_partial_path.add_bb_tail("exit")
                            callee_full_path = self.recover(tmp_partial_path, should_handle_function_call=True, should_recover_full_path=True)
                            callee_pos = "{}#{}".format(bb, inst.offset)
                            ret.add_children(callee_pos, callee_full_path)

        # handle the children in the partial path
        for i in range(len(partial_path.children)):
            child = partial_path.children.pop(0)
            child_pos = partial_path.children_pos.pop(0)
            full_child = self.recover(child, should_remove_bb=True, should_handle_function_call=True, should_recover_full_path=True)
            ret.set_child(child_pos, full_child)

        return ret
        

    def expand(self, apis, could_start_from_entry=False):
        """
        expand step: 
        1. find a most possible api in apis
        2. expand it
        """
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


    def match_from_entry(self, apis):
        final_paths, final_matched_infos = [], []
        for func_name in self.entry_function_names:
            print("entry function: {}".format(func_name))
            func = self.get_s_func_by_name(func_name)
            paths, matched_infos = self.bfs_search(func, func.basicblocks[0], apis, 0)
            final_paths += paths
            final_matched_infos += matched_infos
        return final_paths, final_matched_infos


    def expand_one(self, apis, api_to_expand):
        print("expand from", api_to_expand)

        # search !!
        func_index = get_func_index_by_inst_position(api_to_expand.position)
        func = self.cfg.functions[func_index]
        s_func = self.s_functions[func.name]
        paths, matched_info = self.search_path_in_func(s_func, api_to_expand, apis)
        assert len(paths) == len(matched_info)
        
        callsites = self.get_callsites(self.get_func_readable_name(func))
        if callsites == []: # can not find a caller, that's all we could find.
            return paths, matched_info
            
            
        # search in its caller, i.e., bottom up.
        final_paths = []
        final_matched_infos = []
        for i in range(len(paths)):
            path = paths[i]
            match_start, match_end = matched_info[i]
            for callsite in callsites:
                callsite.set_possibility(api_to_expand.possibility + len(path.api_list))
                to_match_in_caller = apis[:match_start] + [[callsite]] + apis[match_end:]
                try:
                    caller_paths, caller_matched_infos = self.expand(to_match_in_caller)
                except NotImplementedError:
                    continue
                for i in range(len(caller_paths)):
                    caller_path = caller_paths[i]
                    caller_matched_start, caller_matched_end = caller_matched_infos[i]
                    caller_path.children.append(path)
                    caller_path.children_pos.append(callsite)
                    final_paths.append(caller_path)
                    final_matched_infos.append((caller_matched_start, caller_matched_end + match_end - match_start + 1))
            
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
                
            res.append([API(api_name, position, _, trace) for api_name, position, _, trace in top_3_api_position_and_possibility])
        return res


    def search_path_in_func(self, func, api, to_match):
        return self.naiive_search(func, api, to_match)


    def naiive_search(self, func, api, to_match):
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
        right_paths, right_matched = self.bfs_search(func, bb, right_to_match, start_offset, [api.name])
        left_paths, left_matched = self.reverse_bfs_search(func, bb, left_to_match, start_offset, [api.name])
        assert len(right_paths) == len(right_matched) and len(left_paths) == len(left_matched)
        # merge left and right
        paths = []
        matched_info = []
        # both left path and right path contain bb, remove bb from one of them (left path)
        # here we should handle the case that api is in the middle of the bb
        for i in range(len(left_paths)):
            lp = left_paths[i]
            # lm = left_matched[i]
            lp.bbs = lp.bbs[:-1] # remove last bb
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


    def bfs_search(self, func, start_bb, to_match, start_offset, exclude_func_calls = []):
        """
        match the 'to_match' api trace in function 'func', starting from start_bb, and starting 
        from the "start_offset" (no less than start_offset). return possible paths (a list of PathNode)
        and matched numbers (a list of numbers, each correspond to a pathNode in paths and means how many 
        apis are successfully matched)
        exclude_func_calls contains the function name that we consider it is not a function, this will be 
        set when we finish matching in a function previously.
        """
        if to_match == [] and start_bb.name == "entry":
            # when there is no syscall to match
            if func.get_min_api_num(self.bb2api, self) > 0:
                return [], []
            else:
                path = GeneralExecutionPathNode(func, self.get_func_readable_name(func))
                return [path], [0]
        
        paths = []
        matched = []
        
        matched_api_num = 0
        path = GeneralExecutionPathNode(func, self.get_func_readable_name(func))
        q = Queue()
        q.put((start_bb, path, matched_api_num, start_offset))
        
        # it records the last matched number when pass a given backedge
        # we use it to avoid endless loop
        back_edge_recorder = defaultdict(int) 

        br = BlolckRecorder(func)

        while(not q.empty()):
            cur_bb, cur_path, cur_matched_num, cur_offset = q.get()
            # if self.mapper[int(func.name[5:])] == "deflate":
            #     print(cur_bb.name)
            if cur_bb.name == "exit":
                cur_path.add_bb_tail(cur_bb.name)
                paths.append(cur_path.copy())
                matched.append(cur_matched_num)
                if br.is_all_equal():
                    break
                else:
                    continue
            
            cur_api = self.bb2api[cur_bb.name].copy()

            index_in_api = -1 # match from i's api in cur_api
            if len(cur_api) == 0:
                index_in_api = 0
            for _ in range(len(cur_api)):
                _offset = get_inst_offset_in_position(cur_api[_].position)
                if _offset >= cur_offset:
                    index_in_api = _
                    break
            # if index_in_api == -1, which means this block has nothing left to match, 
            # this typically happens when we just jump out from a function call. 
            # in this case we should match from its successor.
            if index_in_api == -1:
                cur_path.add_bb_tail(cur_bb.name)
                cur_path.add_api_tail(cur_api[index_in_api:])
                if br.check(cur_bb.name, cur_matched_num):
                    # block recorder has recorded an equal bb with the same matched_num in the queue
                    continue
                for succ_bb_name in cur_bb.succ_bbs:
                    succ_bb = func.get_bb_by_name(succ_bb_name)
                    if get_block_index(succ_bb.name) <= get_block_index(cur_bb.name): # back edge
                        back_edge = "{}->{}".format(cur_bb.name, succ_bb.name)
                        last_mathed_num = back_edge_recorder[back_edge]
                        if cur_matched_num > last_mathed_num:
                            back_edge_recorder[back_edge] = cur_matched_num
                        else:
                            continue
                    q.put((succ_bb, cur_path.copy(), cur_matched_num, succ_bb.start_offset))
                br.update(cur_bb.name, cur_matched_num)
                continue

            func_calls = [_ for _ in cur_api[index_in_api:] if ("$" in _.name or "^" in _.name) and _.name not in exclude_func_calls]
            if func_calls != []:
                # in some case, there would be some syscall apis before function calls
                # we sould handle these apis first.
                apis_before_func_call = []
                for _ in cur_api[index_in_api:]:
                    if "$" in _.name or "^" in _.name:
                        break
                    else:
                        apis_before_func_call.append(_)
                if apis_before_func_call != []:
                    # try to match
                    i, j = 0, 0 # delta in api and to_match
                    while (0 + i)<len(apis_before_func_call) and (j + cur_matched_num) < len(to_match):
                        if self.api_match(apis_before_func_call[0 + i], to_match[j + cur_matched_num]): 
                            i += 1
                            j += 1
                        else: 
                            break
                    if (0 + i) < len(apis_before_func_call): # not match
                        br.update(cur_bb.name, cur_matched_num)
                        continue
                    else: # match
                        cur_matched_num += i

                # after solving the apis before function calls, we should solve the function call
                _ = func_calls[0] # note that we can only solve the function one by one
                if "^" in _.name: # indirect call
                    callee_names = _.name[1:].split("&")
                    indirect_call_result_recorder = defaultdict(list)
                    # we use a dict to save all the results for this indirect call
                    # key: match num, value: list of the paths
                    # we bundle each list since we cannot distinguish them well.
                    for callee_name in callee_names:
                        # try each functions that could be indirectly called
                        callee = self.get_s_func_by_name(callee_name)
                        if callee == None:
                            # no system calls in callee
                            # In this case, we assume that this function is not called
                            continue
                        left_to_match = to_match[cur_matched_num:]
                        callee_paths, callee_match_infos = self.bfs_search(callee, callee.basicblocks[0], left_to_match, 0)
                        for i in range(len(callee_paths)):
                            callee_path = callee_paths[i]
                            callee_match_num = callee_match_infos[i]
                            indirect_call_result_recorder[callee_match_num].append(callee_path)
                    for indirect_call_match_num in indirect_call_result_recorder:
                        indirect_call_paths = indirect_call_result_recorder[indirect_call_match_num]
                        tmp_path = cur_path.copy()
                        # bundle the paths that has same match number
                        for indirect_call_path in indirect_call_paths:
                            tmp_path.add_children(_.position, indirect_call_path)
                        tmp_matched_num = cur_matched_num + indirect_call_match_num
                        q.put( 
                                (cur_bb, \
                                tmp_path, \
                                tmp_matched_num, \
                                get_inst_offset_in_position(_.position) + 1
                                )
                            )
                else: # simple function call
                    callee_name = _.name[1:]
                    callee = self.get_s_func_by_name(callee_name)
                    left_to_match = to_match[cur_matched_num:]
                    callee_paths, callee_match_infos = self.bfs_search(callee, callee.basicblocks[0], left_to_match, 0)
                    for i in range(len(callee_paths)):
                        callee_path = callee_paths[i]
                        callee_match_num =  callee_match_infos[i]
                        tmp_path = cur_path.copy()
                        tmp_path.add_children(_.position, callee_path)
                        tmp_matched_num = cur_matched_num + callee_match_num
                        q.put( 
                                (cur_bb, \
                                tmp_path, \
                                tmp_matched_num, \
                                get_inst_offset_in_position(_.position) + 1
                                )
                            )
                continue

            # try to match
            i, j = 0, 0 # delta in api and to_match
            while (index_in_api + i)<len(cur_api) and (j + cur_matched_num) < len(to_match):
                if self.api_match(cur_api[index_in_api + i], to_match[j + cur_matched_num]): 
                    i += 1
                    j += 1
                else: 
                    break
            if (index_in_api + i) < len(cur_api[index_in_api:]): # not match
                br.update(cur_bb.name, cur_matched_num)
                continue
            else: # match
                cur_path.add_bb_tail(cur_bb.name)
                cur_path.add_api_tail(cur_api[index_in_api:])
                cur_matched_num += i
                if br.check(cur_bb.name, cur_matched_num):
                    # block recorder has recorded an equal bb with the same matched_num in the queue
                    continue
                for succ_bb_name in cur_bb.succ_bbs:
                    succ_bb = func.get_bb_by_name(succ_bb_name)
                    if get_block_index(succ_bb.name) <= get_block_index(cur_bb.name): # back edge
                        back_edge = "{}->{}".format(cur_bb.name, succ_bb.name)
                        last_mathed_num = back_edge_recorder[back_edge]
                        if cur_matched_num > last_mathed_num:
                            back_edge_recorder[back_edge] = cur_matched_num
                        else:
                            continue
                    q.put((succ_bb, cur_path.copy(), cur_matched_num, succ_bb.start_offset))
                br.update(cur_bb.name, cur_matched_num)
        
        # we only use the paths that has the max matched number
        """
        to_sort = [(paths[i], matched[i]) for i in range(len(paths))]
        if to_sort == []:
            return [], []
        sorted_paths_matched = sorted(to_sort, key=lambda _: _[1], reverse=True)
        max_matched_num = sorted_paths_matched[0][1]
        paths = []
        matched = []
        for _, __ in sorted_paths_matched:
            if __ == max_matched_num:
                paths.append(_)
                matched.append(__)
        return paths, matched
        """

        # we only use top k
        to_sort = [(paths[i], matched[i]) for i in range(len(paths))]
        k = 3
        topk = sorted(to_sort, key=lambda _: _[1], reverse=True)[:k]
        paths = [ _[0] for _ in topk]
        matched = [ _[1] for _ in topk]
        
        return paths, matched


    def reverse_bfs_search(self, func, start_bb, to_match, start_offset, exclude_func_calls = []):
        """
        reversely match the 'to_match' api trace in function 'func', starting from start_bb
        return possible paths (a list of PathNode) and matched numbers (a list of 
        numbers, each correspond to a pathNode in paths and means how many apis are 
        successfully matched)
        exclude_func_calls contains the function name that we consider it is not a function, this will be 
        set when we finish matching in a function previously.
        """
        to_match.reverse()

        if to_match == [] and start_bb.name == "exit":
            # when there is no syscall to match
            if func.get_min_api_num(self.bb2api, self) > 0:
                return [], []
            else:
                path = GeneralExecutionPathNode(func, self.get_func_readable_name(func))
                return [path], [0]
        
        paths = []
        matched = []
        
        matched_api_num = 0
        path = GeneralExecutionPathNode(func, self.get_func_readable_name(func))
        q = Queue()
        q.put((start_bb, path, matched_api_num, start_offset))

        # it records the last matched number when pass a given backedge
        # we use it to avoid endless loop
        back_edge_recorder = defaultdict(int) 

        # it records the last matched number when pass a given backedge
        # we use it to avoid endless loop
        br = BlolckRecorder(func)

        while(not q.empty()):
            cur_bb, cur_path, cur_matched_num, cur_offset = q.get()
            if cur_bb.name == "entry":
                cur_path.add_bb_tail(cur_bb.name)
                paths.append(cur_path.copy())
                matched.append(cur_matched_num)
                if br.is_all_equal():
                    break
                else:
                    continue
            
            cur_api = self.bb2api[cur_bb.name].copy()
            cur_api.reverse()
            
            index_in_api = -1 # match from i's api in cur_api
            if len(cur_api) == 0:
                index_in_api = 0
            for _ in range(len(cur_api)):
                _offset = get_inst_offset_in_position(cur_api[_].position)
                if _offset <= cur_offset:
                    index_in_api = _
                    break
            # if index_in_api == -1, which means this block has nothing left to match, 
            # this typically happens when we just jump out from a function call. 
            # in this case we should match from its successor.
            if index_in_api == -1:
                cur_path.add_bb_tail(cur_bb.name)
                cur_path.add_api_tail(cur_api[index_in_api:])
                if br.check(cur_bb.name, cur_matched_num):
                    # block recorder has recorded an equal bb with the same matched_num in the queue
                    continue
                for pred_bb_name in cur_bb.pred_bbs:
                    pred_bb = func.get_bb_by_name(pred_bb_name)
                    if get_block_index(pred_bb.name) >= get_block_index(cur_bb.name): # back edge
                        back_edge = "{}->{}".format(cur_bb.name, pred_bb.name)
                        last_mathed_num = back_edge_recorder[back_edge]
                        if cur_matched_num > last_mathed_num:
                            back_edge_recorder[back_edge] = cur_matched_num
                        else:
                            continue
                    q.put((pred_bb, cur_path.copy(), cur_matched_num, pred_bb.end_offset))
                br.update(cur_bb.name, cur_matched_num)
                continue

            func_calls = [_ for _ in cur_api[index_in_api:] if ("$" in _.name or "^" in _.name) and _.name not in exclude_func_calls]
            if func_calls != []:
                # in some case, there would be some syscall apis before function calls
                # we sould handle these apis first.
                apis_before_func_call = []
                for _ in cur_api[index_in_api:]:
                    if "$" in _.name or "^" in _.name:
                        break
                    else:
                        apis_before_func_call.append(_)
                if apis_before_func_call != []:
                    # try to match
                    i, j = 0, 0 # delta in api and to_match
                    while (0 + i)<len(apis_before_func_call) and (j + cur_matched_num) < len(to_match):
                        if self.api_match(apis_before_func_call[0 + i], to_match[j + cur_matched_num]): 
                            i += 1
                            j += 1
                        else: 
                            break
                    if (0 + i) < len(apis_before_func_call): # not match
                        br.update(cur_bb.name, cur_matched_num)
                        continue
                    else: # match
                        cur_matched_num += i

                # after solving the apis before function calls, we should solve the function call
                _ = func_calls[0] # note that we can only solve the function one by one
                callee_name = _.name[1:]
                if "^" in _.name: # indirect call
                    callee_names = _.name[1:].split("&")
                    indirect_call_result_recorder = defaultdict(list)
                    # we use a dict to save all the results for this indirect call
                    # key: match num, value: list of the paths
                    # we bundle each list since we cannot distinguish them well.
                    for callee_name in callee_names:
                        # try each functions that could be indirectly called
                        callee = self.get_s_func_by_name(callee_name)
                        if callee == None:
                            # no system calls in callee
                            # In this case, we assume that this function is not called
                            continue
                        left_to_match = to_match[cur_matched_num:]
                        left_to_match.reverse()
                        callee_paths, callee_match_infos = self.reverse_bfs_search(callee, callee.basicblocks[0], left_to_match, 0)
                        for i in range(len(callee_paths)):
                            callee_path = callee_paths[i]
                            callee_match_num =  callee_match_infos[i]
                            indirect_call_result_recorder[callee_match_num].append(callee_path)
                    for indirect_call_match_num in indirect_call_result_recorder:
                        indirect_call_paths = indirect_call_result_recorder[indirect_call_match_num]
                        tmp_path = cur_path.copy()
                        # bundle the paths that has same match number
                        for indirect_call_path in indirect_call_paths:
                            tmp_path.add_children(_.position, indirect_call_path)
                        tmp_matched_num = cur_matched_num + indirect_call_match_num
                        q.put( 
                                (cur_bb, \
                                tmp_path, \
                                tmp_matched_num, \
                                get_inst_offset_in_position(_.position) - 1
                                )
                            )
                else:
                    callee = self.get_s_func_by_name(callee_name)
                    left_to_match = to_match[cur_matched_num:]
                    left_to_match.reverse()
                    callee_paths, callee_match_infos = self.reverse_bfs_search(callee, callee.basicblocks[-1], left_to_match, callee.basicblocks[-1].end_offset)
                    for i in range(len(callee_paths)):
                        callee_path = callee_paths[i]
                        callee_match_num =  callee_match_infos[i]
                        tmp_path = cur_path.copy()
                        tmp_path.add_children(_.position, callee_path)
                        tmp_matched_num = cur_matched_num + callee_match_num
                        q.put( 
                                (cur_bb, \
                                tmp_path, \
                                tmp_matched_num, \
                                get_inst_offset_in_position(_.position) - 1
                                )
                            )
                continue

            i, j = 0, 0 # delta in api and to_match
            while (index_in_api + i)<len(cur_api) and (j + cur_matched_num) < len(to_match):
                if self.api_match(cur_api[index_in_api + i], to_match[j + cur_matched_num]):
                    i += 1
                    j += 1
                else: 
                    break
            if i < len(cur_api[index_in_api:]): # not match
                br.update(cur_bb.name, cur_matched_num)
                continue
            else: # match
                cur_path.add_bb_tail(cur_bb.name)
                cur_path.add_api_tail(cur_api[index_in_api:])
                cur_matched_num += i
                if br.check(cur_bb.name, cur_matched_num):
                    # block recorder has recorded an equal bb with the same matched_num in the queue
                    continue
                for pred_bb_name in cur_bb.pred_bbs:
                    pred_bb = func.get_bb_by_name(pred_bb_name)
                    if get_block_index(pred_bb.name) >= get_block_index(cur_bb.name): # back edge
                        back_edge = "{}->{}".format(cur_bb.name, pred_bb.name)
                        last_mathed_num = back_edge_recorder[back_edge]
                        if cur_matched_num > last_mathed_num:
                            back_edge_recorder[back_edge] = cur_matched_num
                        else:
                            continue
                    q.put((pred_bb, cur_path.copy(), cur_matched_num, pred_bb.end_offset))
                    br.update(cur_bb.name, cur_matched_num)
        
        for p in paths:
            p.reverse()
        

        # we only use the paths that has the max matched number
        """
        to_sort = [(paths[i], matched[i]) for i in range(len(paths))]
        if to_sort == []:
            return [], []
        sorted_paths_matched = sorted(to_sort, key=lambda _: _[1], reverse=True)
        max_matched_num = sorted_paths_matched[0][1]
        paths = []
        matched = []
        for _, __ in sorted_paths_matched:
            if __ == max_matched_num:
                paths.append(_)
                matched.append(__)
        return paths, matched
        """

        # we only use top k
        to_sort = [(paths[i], matched[i]) for i in range(len(paths))]
        k = 3
        topk = sorted(to_sort, key=lambda _: _[1], reverse=True)[:k]
        paths = [ _[0] for _ in topk]
        matched = [ _[1] for _ in topk]
        
        return paths, matched
    

    def api_match(self, api_from_bb, apis_from_trace):
        """
        test if api from basic blocks match the api infer from the trace.
        api_from_bb: the api that extract from the basic blocks, which contains position info
        apis_from_trace: a list of apis, each represent a possible api inferred from a trace
        """
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
            print("ignore", block_name)
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
            self.bb2line = {}.copy()
        try:
            for bb in self.basicblocks:
                if bb.name not in self.bb2line:
                    self.bb2line[bb.name] = self.block2src(bb.name)
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
            
        