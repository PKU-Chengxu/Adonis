from octopus.syspath.path import Path
from octopus.syspath.block_recorder import BlolckRecorder
import json


# used for EPP search
class ExecutionPathNode:
    def __init__(self, func) -> None:
        self.func = func
        self.pathSum_list = []
        self.api_list = []
        self.children = []
        self.children_pos = []
        self.match_start_at = -1
    
    def add_path_tail(self, pathSum):
        self.pathSum_list.append(pathSum)
    
    def add_path_head(self, pathSum):
        self.pathSum_list.insert(0, pathSum)
    
    def add_children(self, pos, child):
        self.children_pos.append(pos)
        self.children.append(child)
    
    def add_api_tail(self, apis):
        self.api_list += apis
    
    def add_api_head(self, apis):
        self.api_list = apis + self.api_list
    
    def merge_tail(self, epn):
        """
        merge two execution path nodes into one.
        """
        self.pathSum_list += epn.pathSum_list
        self.api_list += epn.api_list
        self.children += epn.children
        self.children_pos += epn.children_pos
    
    def merge_head(self, epn):
        self.pathSum_list = epn.pathSum_list + self.pathSum_list
        self.api_list = epn.api_list + self.api_list
        self.children = epn.children + self.children
        self.children_pos = epn.children_pos + self.children_pos
        self.match_start_at = epn.match_start_at
    

    def visualize(self):
        """
        TODO - handle children
        """
        path = []
        g = self.func.g_minus_back_plus_loop
        for pathSum in self.pathSum_list:
            p = Path(pathSum, g)
            path += p.real_path()
        print(path)
    

    def __repr__(self) -> str:
        res = ""
        path = []
        g = self.func.g_minus_back_plus_loop
        for pathSum in self.pathSum_list:
            p = Path(pathSum, g)
            path += p.real_path()
        res += str(path) + "\n"
        if self.children:
            res += "-------- sub path --------\n"
            for i in range(len(self.children)):
                res += "{}th child at {}:\n".format(i, self.children_pos[i])
                res += str(self.children[i])
        return res
    
    def __str__(self) -> str:
        return self.__repr__()
    

    def set_match_start_at(self, match_start_at):
        self.match_start_at = match_start_at


# a more general execution path
class GeneralExecutionPathNode():
    def __init__(self, func, func_readable_name) -> None:
        self.func = func
        self.bbs = []
        self.may_edges = []
        self.api_list = []
        self.children = []
        self.children_pos = []
        self.func_readable_name = func_readable_name
        if func:
            self.br = BlolckRecorder(func)
    
    
    def __hash__(self) -> int:
        return tuple(self.bbs + self.api_list).__hash__()
    
    def add_bb_tail(self, bb):
        self.bbs.append(bb)
    
    def add_bb_head(self, bb):
        self.bbs.insert(0, bb)
    
    def add_bb_list_tail(self, bbs):
        self.bbs += bbs
    
    def add_bb_list_head(self, bbs):
        self.bbs = bbs + self.bbs
    
    def add_api_tail(self, apis):
        self.api_list += apis
    
    def add_api_head(self, apis):
        self.api_list = apis + self.api_list
    
    def copy(self):
        ret = GeneralExecutionPathNode(self.func, self.func_readable_name)
        ret.may_edges = self.may_edges.copy()
        ret.br.records = self.br.records.copy()
        ret.bbs = self.bbs.copy()
        ret.api_list = self.api_list.copy()
        ret.children = self.children.copy()
        ret.children_pos = self.children_pos.copy()
        return ret
    
    def update_by(self, node):
        self.may_edges = node.may_edges.copy()
        if hasattr(node, "br"):
            self.br.records = node.br.records.copy()
        self.bbs = node.bbs.copy()
        self.api_list = node.api_list.copy()
        self.children = node.children.copy()
        self.children_pos = node.children_pos.copy()

    def reverse(self):
        # reverse the path
        new_edges = []
        for e in self.may_edges:
            f, t = e.split("->")
            e = "{}->{}".format(t, f)
            new_edges.append(e)
        self.may_edges = new_edges.copy()
        self.bbs.reverse()
        self.api_list.reverse()
        for _ in self.api_list:
            if _.trace != None:
                _.trace.reverse()
        self.children.reverse()
        self.children_pos.reverse()

    def __add__(self, o):
        assert isinstance(o, GeneralExecutionPathNode) and self.func == o.func
        ret = GeneralExecutionPathNode(self.func, self.func_readable_name)
        ret.bbs = self.bbs + o.bbs
        ret.api_list = self.api_list + o.api_list
        ret.children = self.children + o.children
        ret.children_pos = self.children_pos + o.children_pos
        return ret
    

    def cal_edges(self):
        edges = []
        for i in range(len(self.bbs) - 1):
            f = self.bbs[i]
            t = self.bbs[i+1]
            edges.append("{}->{}".format(f, t))
        return edges


    def update_edges(self, edges):
        for e in edges:
            if e not in self.may_edges:
                self.may_edges.append(e)


    def add_child(self, child_pos, child, update=True):
        if update:
            found = False
            for j in range(len(self.children)):
                if child_pos == self.children_pos[j] and child.func_readable_name == self.children[j].func_readable_name:
                    found = True
                    self.children[j].update_by(child)
            if not found:
                self.children_pos.append(child_pos)
                self.children.append(child)
            # assert found
        else:
            self.children_pos.append(child_pos)
            self.children.append(child)
        
    
    """
    def set_child(self, pos, child):
        find_flag = False
        for i in range(len(self.children)):
            cur_pos = self.children_pos[i]
            if cur_pos == pos:
                self.children[i] = child
                find_flag = True
        if not find_flag:
            raise ValueError("cannot find a pos in the path named ({})".format(pos))
    """


    def to_json_str(self, indent=2):
        res = {}.copy()
        res["func"] = self.func_readable_name
        res["path"] = self.bbs
        res["api_list"] = [str(_) for _ in self.api_list]
        res["children_pos"] = [ str(pos) for pos in self.children_pos]
        res["children"] = [ child.to_json_str(indent=indent) for child in self.children ]
        # for i in range(len(self.children)):
        #     child = self.children[i]
        #     pos = self.children_pos[i]
        #     res["children"][str(pos)] = child.to_json_str(indent=indent)
        return res


    def to_json(self, file_name, indent=2):
        res = {}.copy()
        res["func"] = self.func_readable_name
        res["path"] = self.bbs
        res["api_list"] = [str(_) for _ in self.api_list]
        res["children_pos"] = [ str(pos) for pos in self.children_pos]
        res["children"] = [ child.to_json_str(indent=indent) for child in self.children ]
        # for i in range(len(self.children)):
        #     child = self.children[i]
        #     pos = self.children_pos[i]
        #     res["children"][str(pos)] = child.to_json_str(indent=indent)
        fp = open(file_name, "w")
        json.dump(res, fp, indent=indent)
        fp.close()
    
    
    def cal_coverage(self, graph, file_name, indent=2):
        res = self.cal_coverage_internal(graph)
        fp = open(file_name, "w")
        json.dump(res, fp, indent=indent)
        fp.close()
        return res

    
    def cal_coverage_internal(self, graph):
        intervals = {}.copy() # key: file name, value: line intervals
        for bb in self.bbs:
            if bb == "entry" or bb == "exit":
                continue
            cov_info = graph.block2src(bb)
            filename, from_line, to_line = parse_cov_info(cov_info)
            if filename == None:
                continue
            if filename in intervals:
                intervals[filename] = insert_one_interval(intervals[filename], [from_line, to_line])
            else:
                intervals[filename] = [[from_line, to_line]]
        for child in self.children:
            child_intervals = child.cal_coverage_internal(graph)
            for k in child_intervals:
                if k in intervals:
                    intervals[k] = concat_intervals(intervals[k], child_intervals[k])
                else:
                    intervals[k] = child_intervals[k].copy()
        return intervals
    

    def update_br(self, br: BlolckRecorder):
        self.br.records = br.records.copy()
    

    def check(self):
        for _ in self.children_pos:
            assert isinstance(_, str)
    


    def unfold(self):
        """
        unfold one path (that contain indirect call) to several paths, so that each unfolded path contains only one indirect call at each indirect call site.
        """
        
        # zip:
        # children = [a, b1, b2] ==> to_product_child = [[[a]], [[b1], [b2]]]
        to_product_child = []
        to_product_child_pos = []
        tmp = []
        tmp_pos = []
        # tmp_indirect_api = None
        for i in range(len(self.children)):
            should_add_to_to_product = True
            cur_pos = self.children_pos[i]
            cur_child = self.children[i]
            unfold_cur_child = cur_child.unfold()
            if len(unfold_cur_child) == 3:
                unfold_cur_child
            unfold_cur_pos = [cur_pos]*len(unfold_cur_child)
            cur_child_func_name = cur_child.func_readable_name
            for _ in range(len(unfold_cur_child)):
                tmp.append([unfold_cur_child[_]])
                tmp_pos.append([unfold_cur_pos[_]])
            for api in self.api_list:
                if "^" in api.name:
                    indirect_call_pos = api.position
                    callees = api.name[1:].split("&")
                    if cur_child_func_name in callees:
                        # find a indirect call cover this child
                        should_add_to_to_product = False
                        break
            
            if should_add_to_to_product:
                to_product_child.append(tmp)
                to_product_child_pos.append(tmp_pos)
                tmp = []
                tmp_pos = []
        if tmp != []:
            to_product_child.append(tmp)
            to_product_child_pos.append(tmp_pos)
                    
        if self.func_readable_name == "main":
            self
        new_children_list = perfor_list_product(to_product_child)
        new_children_pos_list = perfor_list_product(to_product_child_pos)
        
        return_list = []
        for i in range(len(new_children_list)):
            tmp_node = self.copy()
            tmp_node.children = new_children_list[i]
            tmp_node.children_pos = new_children_pos_list[i]
            return_list.append(tmp_node)
        
        if new_children_list == []:
            tmp_node = self.copy()
            return_list.append(tmp_node)
        
        return return_list
        
        
            

def list_product(a: list, b: list):
    ret = []
    for i in a:
        for j in b:
            ret.append(i+j)
    return ret


def perfor_list_product(ll: list(list())):
    if len(ll) == 0:
        return []
    elif len(ll) == 1:
        return ll[0]
    else:
        ret = ll[0]
        for i in range(1, len(ll)):
            ret = list_product(ret, ll[i])
        return ret
    
class AmbiguExecutionPathNode():
    """
    Ambiguous Execution Path. This class is built from and updated by several
    General Paths. Compared to the General Path, this class may 
    contain `Ambiguety`, which means it contain the bbs and edges that may have
    executed.
    """
    def __init__(self, func, func_readable_name) -> None:
        self.func = func
        self.edges = []
        self.api_list = []
        self.children = []
        self.children_pos = []
        self.func_readable_name = func_readable_name
        if func:
            self.br = BlolckRecorder(func)
    

    def __hash__(self) -> int:
        return tuple(self.edges + self.api_list + self.children).__hash__()


    def __add__(self, o):
        assert isinstance(o, AmbiguExecutionPathNode) and self.func == o.func
        ret = AmbiguExecutionPathNode(self.func, self.func_readable_name)
        ret.update_by(self)
        ret.update_by(o)
        return ret

    
    def copy(self):
        ret = AmbiguExecutionPathNode(self.func, self.func_readable_name)
        ret.edges = self.edges.copy()
        if hasattr(self, "br"):
            ret.br.records = self.br.records.copy()
        if hasattr(self, "may_bbs"):
            ret.may_bbs = self.may_bbs.copy()
        ret.api_list = self.api_list.copy()
        ret.children = self.children.copy()
        ret.children_pos = self.children_pos.copy()
        
        return ret


    def update_by(self, path_node):
        # print(path_node.func_readable_name)
        try:
            assert path_node.func_readable_name == self.func_readable_name
            assert isinstance(path_node, (GeneralExecutionPathNode, AmbiguExecutionPathNode))
            if isinstance(path_node, GeneralExecutionPathNode):
                for i in range(len(path_node.bbs) - 1):
                    from_bb = path_node.bbs[i]
                    to_bb = path_node.bbs[i + 1]
                    edge = "{}->{}".format(from_bb, to_bb)
                    if edge not in self.edges:
                        self.edges.append(edge)
                for e in path_node.may_edges:
                    if e not in self.edges:
                        self.edges.append(e)
                if hasattr(path_node, "br"):
                    self.br.records = path_node.br.records.copy()
            elif isinstance(path_node, AmbiguExecutionPathNode):
                for e in path_node.edges:
                    if e not in self.edges:
                        self.edges.append(e)
                if hasattr(path_node, "may_bbs"):
                    if not hasattr(self, "may_bbs"):
                        self.may_bbs = []
                    for bb in path_node.may_bbs:
                        if bb not in self.may_bbs:
                            self.may_bbs.append(bb)
            for api in path_node.api_list:
                if api not in self.api_list:
                    self.api_list.append(api)
            for i in range(len(path_node.children)):
                pos = path_node.children_pos[i]
                child = path_node.children[i]
                found = False
                for j in range(len(self.children)):
                    if pos == self.children_pos[j] and child.func_readable_name == self.children[j].func_readable_name:
                        found = True
                        self.children[j].update_by(child)
                if not found:
                    self.add_child(pos, child, update = False) 
        except RecursionError:
            return   
        

    def check(self):
        for _ in self.children_pos:
            assert isinstance(_, str)
    

    def add_edge(self, from_bb, to_bb):
        e = "{}->{}".format(from_bb, to_bb)
        if e not in self.edges:
            self.edges.append(e)
    

    def update_edges(self, edges):
        for e in edges:
            if e not in self.edges:
                self.edges.append(e)


    def add_child(self, child_pos, child, update=True):
        # print(child.func_readable_name)
        if update:
            found = False
            for j in range(len(self.children)):
                if child_pos == self.children_pos[j] and child.func_readable_name == self.children[j].func_readable_name:
                    found = True
                    self.children[j].update_by(child)
            if not found:
                self.children_pos.append(child_pos)
                self.children.append(child)
        else:
            self.children_pos.append(child_pos)
            self.children.append(child)
        
    

    def get_child_by_pos(self, pos):
        for i in range(len(self.children)):
            if pos == self.children_pos[i]:
                return self.children[i]
        assert False


    def cal_bbs(self):
        """
        return bbs in this path
        """
        bbs = []
        for e in self.edges:
            from_bb, to_bb = e.split("->")
            if from_bb not in bbs:
                bbs.append(from_bb)
            if to_bb not in bbs:
                bbs.append(to_bb)
        return bbs


    def cal_bbs_from_api_list(self):
        if self.api_list == []:
            return ["entry", "exit"]
        ret = ["entry"]
        for api in self.api_list:
            pos = api.position
            # remove instruction offset
            if "#" in pos:
                sharp_index = pos.index("#")
                pos = pos[:sharp_index]
            ret.append(pos)
        # we also need to check the last checkpoint to determine if we should add the exit bb in ret
        if not self.terminated_by_exit():
            ret.append("exit")
        return ret


    def terminated_by_exit(self):
        if self.api_list == []:
            return False
        last_api = self.api_list[-1]
        last_api_pos = self.api_list[-1].position
        if last_api.name == "exit":
            return True
        elif "$" in last_api.name:
            child = self.get_child_by_pos(last_api_pos)
            return child.terminated_by_exit()
        else:
            return False

    def reverse(self):
        new_edges = []
        for e in self.edges:
            f, t = e.split("->")
            e = "{}->{}".format(t, f)
            new_edges.append(e)
        self.edges = new_edges.copy()
        # self.bbs.reverse()
        self.api_list.reverse()
        for _ in self.api_list:
            if _.trace != None:
                _.trace.reverse()
        self.children.reverse()
        self.children_pos.reverse()
        
    

    def update_br(self, br: BlolckRecorder):
        self.br.records = br.records.copy()
    

    def to_json_str(self, indent=2):
        res = {}.copy()
        res["func"] = self.func_readable_name
        res["bbs"] = self.cal_bbs()
        if hasattr(self, "may_bbs"):
            res["may_bbs"] = self.may_bbs
        res["edges"] = self.edges
        res["api_list"] = [ str(_) for _ in self.api_list ]
        res["children_pos"] = [ str(pos) for pos in self.children_pos]
        res["children"] = [ child.to_json_str(indent=indent) for child in self.children ]
        # for i in range(len(self.children)):
        #     child = self.children[i]
        #     pos = self.children_pos[i]
        #     res["children"][str(pos)] = child.to_json_str(indent=indent)
        return res
    

    def to_json(self, file_name, indent=2):
        res = {}.copy()
        res["func"] = self.func_readable_name
        res["bbs"] = self.cal_bbs()
        if hasattr(self, "may_bbs"):
            res["may_bbs"] = self.may_bbs
        res["edges"] = self.edges
        res["api_list"] = [ str(_) for _ in self.api_list ]
        res["children_pos"] = [ str(pos) for pos in self.children_pos]
        res["children"] = [ child.to_json_str(indent=indent) for child in self.children ]
        # for i in range(len(self.children)):
        #     child = self.children[i]
        #     pos = self.children_pos[i]
        #     res["children"][str(pos)] = child.to_json_str(indent=indent)
        fp = open(file_name, "w")
        json.dump(res, fp, indent=indent)
        fp.close()


    def cal_coverage(self, graph, file_name, indent=2):
        res = self.cal_coverage_internal(graph)
        fp = open(file_name, "w")
        json.dump(res, fp, indent=indent)
        fp.close()
        return res

    
    def cal_coverage_internal(self, graph):
        if self.func_readable_name == "send_bits":
            self
        intervals = {}.copy() # key: file name, value: line intervals
        if hasattr(self, "may_bbs"):
            bbs = self.may_bbs
        else:
            bbs = self.cal_bbs()
        for bb in bbs:
            if bb == "entry" or bb == "exit":
                continue
            cov_info = graph.block2src(bb)
            filename, from_line, to_line = parse_cov_info(cov_info)
            if filename == None:
                continue
            if filename in intervals:
                intervals[filename] = insert_one_interval(intervals[filename], [from_line, to_line])
            else:
                intervals[filename] = [[from_line, to_line]]
        for child in self.children:
            child_intervals = child.cal_coverage_internal(graph)
            for k in child_intervals:
                if k in intervals:
                    intervals[k] = concat_intervals(intervals[k], child_intervals[k])
                else:
                    intervals[k] = child_intervals[k].copy()
        return intervals


### below is the util functions to handle coverage info
def insert_one_interval(intervals: list, inserted):
    """
    insert an interval to the sorted intervals. concat if necessary.
    """
    intervals.append(inserted)
    intervals.sort(key=lambda x: x[0])
    result = []
    cur_start = intervals[0][0]
    cur_end = intervals[0][1]
    for item in intervals[1:]:
        if item[0] <= cur_end:
            cur_end = max(cur_end, item[1])
        else:
            result.append([cur_start, cur_end])
            cur_start = item[0]
            cur_end = item[1]
    result.append([cur_start, cur_end])
    return result


def concat_intervals(interval_a: list, interval_b: list):
    interval_a += interval_b
    interval_a.sort(key=lambda x: x[0])
    result = []
    cur_start = interval_a[0][0]
    cur_end = interval_a[0][1]
    for item in interval_a[1:]:
        if item[0] <= cur_end:
            cur_end = max(cur_end, item[1])
        else:
            result.append([cur_start, cur_end])
            cur_start = item[0]
            cur_end = item[1]
    result.append([cur_start, cur_end])
    return result


def parse_cov_info(cov_info):
    """
    return filename, from_line, to_line
    """
    try:
        f, t = cov_info.split("->")
        filename = f[1:-1].split(",")[0][1:-1]
        from_line = int(f[1:-1].split(",")[1])
        to_line = int(t[1:-1].split(",")[1])
    except ValueError:
        return None, None, None
    return filename, from_line, to_line