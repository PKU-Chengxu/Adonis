from numpy import isin
from requests import get
from octopus.core import edge
from octopus.core.basicblock import BasicBlock
from octopus.core.edge import Edge
from disjoint_set import DisjointSet


class Function(object):

    def __init__(self, start_offset, start_instr=None,
                 name='func_default_name', prefered_name=None):
        # parameters
        self.start_offset = start_offset
        self.start_instr = start_instr
        self.name = name
        self.prefered_name = prefered_name if prefered_name else name
        self.size = 0
        self.end_offset = None
        self.end_instr = None
        self.basicblocks = list()
        self.edges = list()
        self.instructions = list()
        self.simplify_recorder = DisjointSet()
        self.syspath_fields = ["callees", "indirect_callees", "min_api_num", "simplify_recorder"]
        self.min_api_num = -1 # the minimum num of syscall apis a function would call

    def __str__(self):
        line = ('%x' % self.start_offset) + ': ' + str(self.name) + '\n'
        line += 'prefered_name: %s\n' % self.prefered_name
        line += 'start_offset = %x\n' % self.start_offset
        line += 'start_instr = ' + str(self.start_instr.name) + '\n'
        if self.size:
            line += 'size = ' + str(self.size) + '\n'
        if self.end_offset:
            line += 'end_offset = ' + str(self.end_offset) + '\n'
        if self.end_instr:
            line += 'end_instr = ' + str(self.end_instr.name) + '\n'
        line += 'lenght basicblocks: %s\n' % len(self.basicblocks)
        line += 'lenght instructions: %s\n' % len(self.instructions)
        line += '\n\n'
        return line

    
    def copy(self):
        ret = Function(self.start_offset, self.start_instr, self.name, self.prefered_name)
        ret.size = self.size
        ret.end_offset = self.end_offset
        ret.end_instr = self.end_instr
        ret.basicblocks = [ _.copy() for _ in self.basicblocks ]
        ret.edges = self.edges.copy()
        ret.instructions = self.instructions.copy()
        ret.syspath_fields = self.syspath_fields.copy()
        for f in self.syspath_fields:
            setattr(ret, f, getattr(self, f))
        return ret


    def add_entry_and_exit(self):
        entry = BasicBlock(name="entry")
        entry.start_offset = 0
        entry.end_offset = 0
        entry.succ_bbs.append(self.basicblocks[0].name)
        exit = BasicBlock(name="exit")
        exit.start_offset = self.basicblocks[-1].end_offset
        exit.end_offset = self.basicblocks[-1].end_offset
        exit.pred_bbs.append(self.basicblocks[-1].name)
        self.basicblocks = [entry] + self.basicblocks + [exit]
        self.edges = self.edges + [Edge("entry", self.basicblocks[1].name), Edge(self.basicblocks[-2].name, "exit")]
        self.edges = sorted(self.edges, key=lambda e: (get_block_index(e.node_from), get_block_index(e.node_to)))
        self.parse_pred_succ()



    def simplify(self, bb2trace, debug=False, debug_dir = "func/debug"):
        """
        simplify a function, quicker than the previous implementation.
        """
        if debug:
            import os
            print("simplify debug info will be written to", debug_dir)
            os.system("mkdir -p {}".format(debug_dir) )
            from octopus.syspath.util import render, dump_merge_log
        # copy basic blocks and edges
        s_func = self.copy()
        s_func.add_entry_and_exit()
        
        new_basicblocks = s_func.basicblocks.copy()
        new_edges = s_func.edges.copy()
        merge_log = []
        
        from octopus.analysis.dataflow_analysis import DataFlowAnalysis
        front_dfa = DataFlowAnalysis(s_func, dom_init_in_forward, dom_init_out_forward, dom_transfer, dom_merge)
        front_dom = front_dfa.analyze() # this would take 0.033s for a big function.
        back_dfa = DataFlowAnalysis(s_func, dom_init_in_backward, dom_init_out_backward, dom_transfer, dom_merge, True)
        back_dom = back_dfa.analyze()
        i = 0
        cnt = 0
        while i < len(new_edges):
            e = new_edges[i]
            f_node, t_node = e.node_from, e.node_to
            if f_node == "entry" or t_node == "exit":
                i += 1
                continue
            if get_block_index(f_node) > get_block_index(t_node):
                i += 1
                continue
            if not s_func.is_close_neighbor(f_node, t_node):
                i += 1
                continue
            if bb2trace[f_node] != [] or bb2trace[t_node] != []:
                i += 1
                continue

            # in other case, we merge two nodes
            # print("merge {}, {}".format(f_node, t_node))
            cnt += 1
            new_basicblocks, new_edges, removed_bb = merge(f_node, t_node, new_basicblocks, new_edges, front_dom, back_dom)
            if debug:
                s_func.basicblocks = new_basicblocks
                s_func.edges = new_edges
                render(s_func, os.path.join(debug_dir, str(cnt)), bb2trace)
            
            if f_node == removed_bb:
                merge_log.append("{}:{}<-{}".format(cnt, t_node, removed_bb))
            elif t_node == removed_bb:
                merge_log.append("{}:{}<-{}".format(cnt, f_node, removed_bb))

            self.simplify_recorder.union(f_node, t_node)
            # update front_dom and to_dom
            if removed_bb == t_node:
                for k in front_dom:
                    if removed_bb in front_dom[k]:
                        front_dom[k].remove(removed_bb)
                        front_dom[k].add(f_node)
            if removed_bb == f_node:
                for k in back_dom:
                    if removed_bb in back_dom[k]:
                        back_dom[k].remove(removed_bb)
                        back_dom[k].add(t_node)
            new_edges = sorted(new_edges, key=lambda e: (get_block_index(e.node_from), get_block_index(e.node_to)))
            s_func.basicblocks = new_basicblocks
            s_func.edges = new_edges
            # s_func.edges = sorted(s_func.edges, key=lambda e: (get_block_index(e.node_from), get_block_index(e.node_to)))
            s_func.parse_pred_succ()
            i = 0
        s_func.remove_redundant_edges()
        s_func.parse_pred_succ()
        if debug:
            dump_merge_log(os.path.join(debug_dir, "merge_log.txt"), merge_log)
        return s_func, merge_log
        
            
    def remove_unreachable_bb(self):
        self.parse_pred_succ()
        new_bbs = []
        for bb in self.basicblocks:
            if bb.succ_bbs == [] and bb.pred_bbs == [] and get_block_index(bb.name) > 0:
                continue
            new_bbs.append(bb)
        self.basicblocks = new_bbs
        return
    
    def remove_redundant_edges(self):
        # for some reason (related to the implementation of in br_table), there may 
        # be redundant edges in cfg, remove them 
        edges = []
        edges_string = []
        for e in self.edges:
            if e.to_string() not in edges_string:
                edges.append(e)
                edges_string.append(e.to_string())
        self.edges = edges
        return

    def get_bb_by_name(self, name):
        if hasattr(self, "name2bb"):
            return self.name2bb[name]
        else:
            self.name2bb = { bb.name: bb for bb in self.basicblocks }
            return self.name2bb[name]


    def contain_syscall(self, node_a, node_b, bb2api):
        """
        test if all paths from node_a to node_b contain any syscall.
        """
        a_index = get_block_index(node_a)
        b_index = get_block_index(node_b)
        for bb in self.basicblocks:
            bb_index = get_block_index(bb.name)
            if bb_index < a_index:
                continue
            if bb_index > b_index:
                break
            if bb2api[bb.name] != []:
                return True
        return False
    
    def is_close_neighbor(self, node_a, node_b):
        """
        if node a and node b are close neighbor, there is only one path from node a
        to node b, i.e., the edge a->b.
        """
        if node_a == node_b:
            return True
        import queue
        q = queue.Queue()
        q.put(node_a)
        pathNum = 0
        step = 0
        while(not q.empty()):
            step += 1
            if step > 100: # we don't need to search for too long
                break
            cur_node = q.get()
            if cur_node == node_b:
                pathNum += 1
                if pathNum > 1:
                    break
            cur_bb = self.get_bb_by_name(cur_node)
            for succ_node in cur_bb.succ_bbs:
                if get_block_index(succ_node) <= get_block_index(cur_node):
                    continue
                if get_block_index(succ_node) > get_block_index(node_b):
                    continue
                q.put(succ_node)

        # assert pathNum > 0
        return pathNum == 1

    # analyze basic blocks predecessors and successors
    def parse_pred_succ(self):
        for bb in self.basicblocks:
            bb.succ_bbs = []
            bb.pred_bbs = []
        for e in self.edges:
            f_node, t_node = e.node_from, e.node_to
            for bb in self.basicblocks:
                if bb.name == f_node:
                    bb.succ_bbs.append(t_node)
                if bb.name == t_node:
                    bb.pred_bbs.append(f_node)
    

    def get_min_api_num(self, bb2trace, graph):
        if self.min_api_num != -1:
            return self.min_api_num
        else:
            self.cal_min_api_num(bb2trace, graph)
            return self.min_api_num
    

    def cal_min_api_num(self, bb2trace, graph):
        self.min_api_num = 0
        self.parse_pred_succ()
        
        from octopus.analysis.dataflow_analysis import DataFlowAnalysis
        front_dfa = DataFlowAnalysis(self, dom_init_in_forward, dom_init_out_forward, dom_transfer, dom_merge)
        front_dom = front_dfa.analyze() # this would take 0.033s for a big function.

        for bb_name in front_dom["exit"]:
            api_trace = bb2trace[bb_name]
            for api in api_trace:
                if "$" in api.name: # function call
                    callee_func = graph.get_s_func_by_name(api.name[1:])
                    self.min_api_num += callee_func.get_min_api_num(bb2trace, graph)
                elif "^" in api.name: # indirect call
                    possible_callees = api.name[1:].split("&")
                    tmp_min = 100000
                    for possible_callee in possible_callees:
                        callee_func = graph.get_s_func_by_name(possible_callee)
                        if callee_func == None: # no syscall for a function callee
                            tmp_min = 0
                            break
                        if callee_func.get_min_api_num(bb2trace, graph) < tmp_min:
                            tmp_min = callee_func.get_min_api_num(bb2trace, graph)
                    self.min_api_num += tmp_min
                else: # normal system call api
                    self.min_api_num += 1


    def remove_bb(self, bb):
        """
        note that we will not handle the instructions!
        """
        if bb not in self.basicblocks:
            # could be removed before due to the recursive remove
            return
        self.basicblocks.remove(bb)
        to_removed_edge_index = []
        for i in range(len(self.edges)):
            e = self.edges[i]
            if e.node_from == bb.name or e.node_to == bb.name:
                to_removed_edge_index.append(i)
        removed = 0
        for _ in to_removed_edge_index:
            self.edges.pop(_ - removed) # maintain the index using the removed num
            removed += 1
        for pred_bb_name in bb.pred_bbs:
            pred_bb = self.get_bb_by_name(pred_bb_name)
            pred_bb.succ_bbs.remove(bb.name)
            if pred_bb.succ_bbs == []:
                self.remove_bb(pred_bb)
        for succ_bb_name in bb.succ_bbs:
            succ_bb = self.get_bb_by_name(succ_bb_name)
            succ_bb.pred_bbs.remove(bb.name)
            if succ_bb.pred_bbs == []:
                self.remove_bb(succ_bb)


    def cal_full_path(self, edges, symbolic = False):
        """
        Note: May analysis (may contain false positive).
        given the partial path, return the possible executed bbs
        symbolic execution will be used once symbolic is set to True
        """
        ret = []
        if edges == []:
            edges = ["entry->exit"]
        for e in edges:
            from_node, to_node = e.split("->")
            path_between_ft = self.cal_path_between_pair(from_node, to_node, symbolic)
            ret += path_between_ft
        return ret
        
    
    def cal_MPP(self, ckpts, symbolic = False):
        if symbolic:
            return self.cal_MPP_syblolic(ckpts)
        else:
            return self.cal_MPP_naiive(ckpts)
        """
        ret = []
        first_iter_flag = True
        for i in range(len(ckpts)-1):
            from_node, to_node = ckpts[i], ckpts[i+1]
            if from_node == to_node:
                continue
            path_between_ft = self.cal_MPP_between_pair(from_node, to_node, symbolic)
            if first_iter_flag:
                first_iter_flag = False
                ret += path_between_ft
            else:
                ret += path_between_ft[1:]
        return ret
        """


    def cal_MPP_naiive(self, partial_path):
        if partial_path == []:
            partial_path = ["entry", "exit"]
        # recalculate the pred and succ info
        self.parse_pred_succ()

        # calculate the dom info
        from octopus.analysis.dataflow_analysis import DataFlowAnalysis
        front_dfa = DataFlowAnalysis(self, dom_init_in_forward, dom_init_out_forward, dom_transfer, dom_merge)
        front_dom = front_dfa.analyze() # this would take 0.033s for a big function.
        back_dfa = DataFlowAnalysis(self, dom_init_in_backward, dom_init_out_backward, dom_transfer, dom_merge, True)
        back_dom = back_dfa.analyze()
        
        # calculate the must executed bbs
        must_exe_bbs = set()
        for bb in partial_path:
            must_exe_bbs = must_exe_bbs.union(front_dom[bb])
            must_exe_bbs = must_exe_bbs.union(back_dom[bb])
        
        if partial_path == ["entry", "exit"]:
            return list(must_exe_bbs)
        
        # calculate the full path, for the uncertain bbs, random choose a branch
        # using bfs
        from queue import Queue
        import random
        full_paths = []
        start_bb_obj = self.basicblocks[0]
        q = Queue()
        q.put((start_bb_obj, [start_bb_obj.name], 1)) # basic block, recovered full path, mathed num in partial_path
        from octopus.syspath.block_recorder import BlolckRecorder
        br = BlolckRecorder(self)
        # for unknown issue, in very few cases, the search could be unlimited long. 
        # so we limit the searching time by setting a counter.
        cnt = 0

        while (not q.empty()) and cnt < 10000:
            cnt += 1
            cur_bb_obj, cur_path, cur_matched_num = q.get()
            if cur_bb_obj.name == "exit":
                if cur_matched_num == len(partial_path):
                    full_paths.append(cur_path)
                    continue
                else:
                    continue
            if cur_matched_num == len(partial_path) and "exit" not in partial_path:
                # terminated by "exit" function
                full_paths.append(cur_path)
                continue
            succ_must_exe_flag = False
            for succ_bb in cur_bb_obj.succ_bbs:
                if br.check(succ_bb, cur_matched_num):
                    # block recorder has recorded an equal bb with the same matched_num in the queue
                    continue
                if succ_bb in must_exe_bbs:
                    succ_must_exe_flag = True
                    succ_bb_obj = self.get_bb_by_name(succ_bb)
                    new_path = cur_path.copy()
                    new_path.append(succ_bb)
                    if succ_bb == partial_path[cur_matched_num]:
                        # succ_bb is in the partial path
                        q.put((succ_bb_obj, new_path, cur_matched_num+1))
                        br.update(cur_bb_obj.name, cur_matched_num)
                    elif get_block_index(succ_bb) < get_block_index(cur_bb_obj.name) and self.in_the_union(succ_bb, partial_path[cur_matched_num]):
                        # This is a rather corner case, that is we find a back edge, and its t_node (i.e. succ_bb)
                        # succ_bb has been merged by some bb in the partial path. In this case, the succ_bb
                        # may not be in the partial path, but it is indeed matched.
                        q.put((succ_bb_obj, new_path, cur_matched_num+1))
                        br.update(cur_bb_obj.name, cur_matched_num)
                    else:
                        # succ_bb is not in the partial path but must be executed
                        if succ_bb not in partial_path:
                            # bb is must-execute but not in partial path
                            q.put((succ_bb_obj, new_path, cur_matched_num))
                            br.update(cur_bb_obj.name, cur_matched_num)
                        else:
                            # in this case, it is a wrong path
                            continue
            if not succ_must_exe_flag:
                if cur_bb_obj.succ_bbs == []:
                    continue
                # non of the succ is must-executed, and we can not determine which branch to take
                # in this case, we must randomly choose one.
                succ_bb = random.choice(cur_bb_obj.succ_bbs)
                succ_bb_obj = self.get_bb_by_name(succ_bb)
                new_path = cur_path.copy()
                new_path.append(succ_bb)
                q.put((succ_bb_obj, new_path, cur_matched_num))
                br.update(cur_bb_obj.name, cur_matched_num)
        full_paths = sorted(full_paths, key=lambda l: len(l), reverse=True)
        # return the longest full path
        if full_paths == []:
            # print("[INFO] fail to recover the full path for function {}".format(self.name))
            return list(must_exe_bbs)
        else:
            return full_paths[0]



    def cal_MPP_syblolic(self, ckpts):
        return ckpts


    def cal_path_between_pair(self, from_node, to_node, symbolic = False):
        if symbolic:
            return self.symbolic_cal_path_between_pair(from_node, to_node)
        else:
            return self.naiive_cal_path_between_pair(from_node, to_node)

    def cal_MPP_between_pair(self, from_node, to_node, symbolic = False):
        if symbolic:
            return self.symbolic_cal_MPP_between_pair(from_node, to_node)
        else:
            return self.naiive_cal_MPP_between_pair(from_node, to_node)


    def symbolic_cal_MPP_between_pair(self, from_node, to_node):
        raise NotImplementedError


    def naiive_cal_MPP_between_pair(self, from_node, to_node):
        """
        return a path with most possibility
        """
        self.parse_pred_succ()
        
        from queue import Queue
        ret = []
        start_bb_obj = self.get_bb_by_name(from_node)
        end_node_obj = self.get_bb_by_name(to_node)
        q = Queue()
        q.put((start_bb_obj, [start_bb_obj.name])) # (cur_bb, cur_path)
        cnt = 0
        # for some huge function with many branches, it may take too much time
        # for efficiency, we limit the number of search steps
        end_cnt = 10000 
        while not q.empty():
            cnt += 1
            if cnt >= end_cnt:
                ret = self.all_bbs_between_pairs(from_node, to_node)
                break
            cur_bb_obj, cur_path = q.get()
            if cur_bb_obj.name == to_node:
                ret = cur_path
                break
            for succ_bb in cur_bb_obj.succ_bbs:
                succ_bb_obj = self.get_bb_by_name(succ_bb)
                if get_block_index(cur_bb_obj.name) > get_block_index(succ_bb_obj.name):
                    if succ_bb_obj.name != to_node and cur_bb_obj.name != from_node:
                        # back edge, we do not need get in the back edge between two nodes unless any of them contains event
                        continue
                if get_block_index(succ_bb_obj.name) > get_block_index(to_node):
                    continue
                # in other cases, we search deeper
                new_path = cur_path.copy()
                new_path.append(succ_bb)
                q.put((succ_bb_obj, new_path))
        return ret


    def symbolic_cal_path_between_pair(self, from_node, to_node):
        raise NotImplementedError
    

    def naiive_cal_path_between_pair(self, from_node, to_node):
        """
        return all possible bbs
        """
        if from_node == "entry" and to_node == "exit":
            return self.all_bbs_between_pairs(from_node, to_node)

        self.parse_pred_succ()
        
        ret = set()
        from queue import Queue
        start_bb_obj = self.get_bb_by_name(from_node)
        end_node_obj = self.get_bb_by_name(to_node)
        q = Queue()
        q.put((start_bb_obj, [start_bb_obj.name])) # (cur_bb, cur_path)
        cnt = 0
        # for some huge function with many branches, recover may take too much time
        # for efficiency, we limit the number of search steps
        end_cnt = 10000 
        while not q.empty():
            cnt += 1
            if cnt >= end_cnt:
                ret = ret.union(self.all_bbs_between_pairs(from_node, to_node))
                break
            cur_bb_obj, cur_path = q.get()
            if cur_bb_obj.name == to_node:
                ret = ret.union(cur_path)
                continue
            for succ_bb in cur_bb_obj.succ_bbs:
                succ_bb_obj = self.get_bb_by_name(succ_bb)
                if get_block_index(cur_bb_obj.name) > get_block_index(succ_bb_obj.name):
                    if succ_bb_obj.name != to_node and cur_bb_obj.name != from_node:
                        # back edge, we do not need get in the back edge between two nodes unless any of them contains event
                        continue
                if succ_bb_obj.name in ret:
                    # if we have found a path that contains this bb, we do not need to search deeper
                    # because there must exist a path that lead to the to_node passing succ_bb
                    new_path = cur_path.copy()
                    new_path.append(to_node)
                    q.put((end_node_obj, new_path))
                    continue
                if get_block_index(succ_bb_obj.name) > get_block_index(to_node):
                    continue
                # in other cases, we search deeper
                new_path = cur_path.copy()
                new_path.append(succ_bb)
                q.put((succ_bb_obj, new_path))
        ret = list(ret)
        
        ret = sorted(ret, key=lambda bb: get_block_index(bb))
        if get_block_index(from_node) > get_block_index(to_node):
            ret.reverse() 
        return ret


    def all_bbs_between_pairs(self, from_node, to_node):
        ret = []
        if get_block_index(from_node) > get_block_index(to_node):
            from_node, to_node = to_node, from_node
        for bb in self.basicblocks:
            bb_name = bb.name
            if get_block_index(bb_name) >= get_block_index(from_node) and get_block_index(bb_name) <= get_block_index(to_node):
                ret.append(bb_name)
        return ret


    def deprecated_cal_full_path(self, partial_path):
        """
        Note - a deprecated implementation, which is of low efficieny.
        analyze the must-execute bbs given the already executed bbs
        according to the dom info
        node_a in front_dom[node_b] meaning A dom B
        """
        if partial_path == []:
            partial_path = ["entry", "exit"]
        # recalculate the pred and succ info
        self.parse_pred_succ()

        # calculate the dom info
        from octopus.analysis.dataflow_analysis import DataFlowAnalysis
        front_dfa = DataFlowAnalysis(self, dom_init_in_forward, dom_init_out_forward, dom_transfer, dom_merge)
        front_dom = front_dfa.analyze() # this would take 0.033s for a big function.
        back_dfa = DataFlowAnalysis(self, dom_init_in_backward, dom_init_out_backward, dom_transfer, dom_merge, True)
        back_dom = back_dfa.analyze()
        
        # calculate the must executed bbs
        must_exe_bbs = set()
        for bb in partial_path:
            must_exe_bbs = must_exe_bbs.union(front_dom[bb])
            must_exe_bbs = must_exe_bbs.union(back_dom[bb])
        
        # calculate the full path, for the uncertain bbs, random choose a branch
        # using bfs
        from queue import Queue
        import random
        full_paths = []
        start_bb_obj = self.basicblocks[0]
        q = Queue()
        q.put((start_bb_obj, [start_bb_obj.name], 1)) # basic block, recovered full path, mathed num in partial_path
        from octopus.syspath.block_recorder import BlolckRecorder
        br = BlolckRecorder(self)
        # for unknown issue, in very few cases, the search could be unlimited long. 
        # so we limit the searching time by setting a counter.
        cnt = 0

        while (not q.empty()) and cnt < 10000:
            cnt += 1
            cur_bb_obj, cur_path, cur_matched_num = q.get()
            if cur_bb_obj.name == "exit":
                if cur_matched_num == len(partial_path):
                    full_paths.append(cur_path)
                    continue
                else:
                    continue
            succ_must_exe_flag = False
            for succ_bb in cur_bb_obj.succ_bbs:
                if br.check(succ_bb, cur_matched_num):
                    # block recorder has recorded an equal bb with the same matched_num in the queue
                    continue
                if succ_bb in must_exe_bbs:
                    succ_must_exe_flag = True
                    succ_bb_obj = self.get_bb_by_name(succ_bb)
                    new_path = cur_path.copy()
                    new_path.append(succ_bb)
                    if succ_bb == partial_path[cur_matched_num]:
                        # succ_bb is in the partial path
                        q.put((succ_bb_obj, new_path, cur_matched_num+1))
                        br.update(cur_bb_obj.name, cur_matched_num)
                    elif get_block_index(succ_bb) < get_block_index(cur_bb_obj.name) and self.in_the_union(succ_bb, partial_path[cur_matched_num]):
                        # This is a rather corner case, that is we find a back edge, and its t_node (i.e. succ_bb)
                        # succ_bb has been merged by some bb in the partial path. In this case, the succ_bb
                        # may not be in the partial path, but it is indeed matched.
                        q.put((succ_bb_obj, new_path, cur_matched_num+1))
                        br.update(cur_bb_obj.name, cur_matched_num)
                    else:
                        # succ_bb is not in the partial path but must be executed
                        if succ_bb not in partial_path:
                            # bb is must-execute but not in partial path
                            q.put((succ_bb_obj, new_path, cur_matched_num))
                            br.update(cur_bb_obj.name, cur_matched_num)
                        else:
                            # in this case, it is a wrong path
                            continue
            if not succ_must_exe_flag:
                if cur_bb_obj.succ_bbs == []:
                    continue
                # non of the succ is must-executed, and we can not determine which branch to take
                # in this case, we must randomly choose one.
                succ_bb = random.choice(cur_bb_obj.succ_bbs)
                succ_bb_obj = self.get_bb_by_name(succ_bb)
                new_path = cur_path.copy()
                new_path.append(succ_bb)
                q.put((succ_bb_obj, new_path, cur_matched_num))
                br.update(cur_bb_obj.name, cur_matched_num)
        full_paths = sorted(full_paths, key=lambda l: len(l), reverse=True)
        # return the longest full path
        if full_paths == []:
            # print("[INFO] fail to recover the full path for function {}".format(self.name))
            return list(must_exe_bbs)
        else:
            return full_paths[0]


    def in_the_union(self, bb, to_match):
        """
        test if bb is in the union of to_match
        """
        return self.simplify_recorder.connected(to_match, bb)


    def cal_common_dom_node(self, to_doms):
        # recalculate the pred and succ info
        self.parse_pred_succ()

        # calculate the dom info
        from octopus.analysis.dataflow_analysis import DataFlowAnalysis
        front_dfa = DataFlowAnalysis(self, dom_init_in_forward, dom_init_out_forward, dom_transfer, dom_merge)
        front_dom = front_dfa.analyze() # this would take 0.033s for a big function.
        # if node_a in front_dom[node_b] => A dom B
        
        common_dom_node = "entry"
        for bb in self.basicblocks:
            bb_name = bb.name
            dom_all = True
            for _ in to_doms:
                if bb_name not in front_dom[_]:
                    dom_all = False
                    break
            if dom_all and get_block_index(bb_name) > get_block_index(common_dom_node):
                common_dom_node = bb_name
        return common_dom_node

    
    def cal_common_reverse_dom_node(self, to_doms):
        # recalculate the pred and succ info
        self.parse_pred_succ()

        # calculate the dom info
        from octopus.analysis.dataflow_analysis import DataFlowAnalysis
        back_dfa = DataFlowAnalysis(self, dom_init_in_backward, dom_init_out_backward, dom_transfer, dom_merge, True)
        back_dom = back_dfa.analyze()
        
        common_dom_node = "exit"
        for bb in self.basicblocks:
            bb_name = bb.name
            dom_all = True
            for _ in to_doms:
                if bb_name not in back_dom[_]:
                    dom_all = False
                    break
            if dom_all and get_block_index(bb_name) < get_block_index(common_dom_node):
                common_dom_node = bb_name
        return common_dom_node


    def cal_immediate_dom(self, node):
        # recalculate the pred and succ info
        self.parse_pred_succ()

        # calculate the dom info
        from octopus.analysis.dataflow_analysis import DataFlowAnalysis
        front_dfa = DataFlowAnalysis(self, dom_init_in_forward, dom_init_out_forward, dom_transfer, dom_merge)
        front_dom = front_dfa.analyze() # this would take 0.033s for a big function.
        # if node_a in front_dom[node_b] => A dom B

        immediate_dom = "entry"
        for bb in self.basicblocks:
            bb_name = bb.name
            if bb_name == node:
                continue
            if bb_name in front_dom[node] and get_block_index(bb_name) > get_block_index(immediate_dom):
                immediate_dom = bb_name
        return immediate_dom
    

    def cal_immediate_reverse_dom(self, node):
        # recalculate the pred and succ info
        self.parse_pred_succ()

        # calculate the dom info
        from octopus.analysis.dataflow_analysis import DataFlowAnalysis
        back_dfa = DataFlowAnalysis(self, dom_init_in_backward, dom_init_out_backward, dom_transfer, dom_merge, True)
        back_dom = back_dfa.analyze()
        # if node_a in front_dom[node_b] => A dom B

        immediate_reverse_dom = "exit"
        for bb in self.basicblocks:
            bb_name = bb.name
            if bb_name == node:
                continue
            if bb_name in back_dom[node] and get_block_index(bb_name) < get_block_index(immediate_reverse_dom):
                immediate_reverse_dom = bb_name
        return immediate_reverse_dom


def dom_init_in_forward(bb, func):
    return set()


def dom_init_out_forward(bb, func):
    if is_entry(bb, func):
        return set([bb.name])
    else:
        return set([bbb.name for bbb in func.basicblocks])


def dom_merge(Vals):
    if len(Vals) == 0:
        return set()
    if len(Vals) == 1:
        return Vals[0]
    res = Vals[0].copy()
    for Val in Vals:
        res.intersection_update(Val)
    return res


def dom_init_in_backward(bb, func):
    if is_exit(bb, func):
        return set([bb.name])
    else:
        return set([bbb.name for bbb in func.basicblocks])

def dom_init_out_backward(bb, func):
    return set()

def dom_transfer(bb, IN):
    return IN.union(set([bb.name]))


def is_entry(bb, func):
    if isinstance(bb, BasicBlock):
        return bb.name == func.basicblocks[0].name
    else:
        return bb == func.basicblocks[0].name


def is_exit(bb, func):
    if isinstance(bb, BasicBlock):
        return bb.name == func.basicblocks[-1].name
    else:
        return bb == func.basicblocks[-1].name



def get_block_index(block_name):
    """
    get block's index according to its name:
    e.g., for block_42_122, its index is 0x122
    """
    if block_name == "entry":
        return -1 # return a small value
    if block_name == "exit":
        return int("0x3f3f3f", 16)
    return int(block_name.split("_")[-1],16)



def merge(node_a, node_b, bbs, edges, front_dom, back_dom):
    """
    merge node_b and node_a, effects:
    1. node_b or node_a is removed from bbs
    2. edge between node_a and node_b is removed from edges
    3a. if a dom b, b is removed(absorbed), and all edges from b are linked to a (change these edges to point from a)
    3b. else if b reverse dom a, a is removed(absorbed), and all edges to a are linked to b (change these edges to point to b)
    3c. otherwise, b is removed(absorbed).
    """
    if node_a == node_b:
        new_edges = [e for e in edges if not (e.node_from == node_a and e.node_to == node_b)]
        removed_bb = None
        return bbs, new_edges, removed_bb

    from octopus.core.edge import Edge
    if node_a in front_dom[node_b]: # A dom B, b is removed
        removed_bb = node_b
        new_bbs = [bb for bb in bbs if bb.name != node_b]
        new_edges = []
        for e in edges:
            if e.node_from == node_a and e.node_to == node_b:
                continue
            if e.node_from == node_b:
                new_e = Edge(node_a, e.node_to, e.type, e.condition)
                if new_e.node_from != new_e.node_to and not in_edges(new_e, edges):
                    new_edges.append(new_e)
            elif e.node_to == node_b:
                new_e = Edge(e.node_from, node_a, e.type, e.condition)
                if new_e.node_from != new_e.node_to and not in_edges(new_e, edges):
                    new_edges.append(new_e)
            else:
                new_edges.append(e)
    elif node_b in back_dom[node_a]: # B reverse dom A, a is removed
        removed_bb = node_a
        new_bbs = [bb for bb in bbs if bb.name != node_a]
        new_edges = []
        for e in edges:
            if e.node_from == node_a and e.node_to == node_b:
                continue
            if e.node_to == node_a:
                new_e = Edge(e.node_from, node_b, e.type, e.condition)
                if new_e.node_from != new_e.node_to and not in_edges(new_e, edges):
                    new_edges.append(new_e)
            elif e.node_from == node_a:
                new_e = Edge(node_b, e.node_to, e.type, e.condition)
                if new_e.node_from != new_e.node_to and not in_edges(new_e, edges):
                    new_edges.append(new_e)
            else:
                new_edges.append(e)
    else: # B is removed
        removed_bb = node_b
        new_bbs = [bb for bb in bbs if bb.name != node_b]
        new_edges = []
        for e in edges:
            if e.node_from == node_a and e.node_to == node_b:
                continue
            if e.node_from == node_b:
                new_e = Edge(node_a, e.node_to, e.type, e.condition)
                if new_e.node_from != new_e.node_to and not in_edges(new_e, edges):
                    new_edges.append(new_e)
            elif e.node_to == node_b:
                new_e = Edge(e.node_from, node_a, e.type, e.condition)
                if new_e.node_from != new_e.node_to and not in_edges(new_e, edges):
                    new_edges.append(new_e)
            else:
                new_edges.append(e)
        
    return new_bbs, new_edges, removed_bb



def in_edges(edge, edges):
    """
    __eq__ is defined in Edge, which requir all attibutes are equal.
    However, in our case, we regard two edges are equal if only node_from 
    and node_to are equal respectively.
    """
    for e in edges:
        if e.node_from == edge.node_from and\
            e.node_to == edge.node_to:
            return True
    return False


