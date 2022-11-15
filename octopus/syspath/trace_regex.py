import random
import sys

# three types of TR
SEQ = "sequance"
SEL = "select"
LOOP = "loop"

MAX_LOOP = 4

class TR:
    valid_type = [SEQ, SEL, LOOP]

    def __init__(self, type):
        if type not in TR.valid_type:
            assert False
        self.type = type
        self.value = []
        self.min_len = -1
        self.max_len = -1
        if self.type == SEL:
            self.edges = []
    
    def __repr__(self) -> str:
        res = ""
        if self.type == SEQ:
            res += "("
            flag = False
            for ele in self.value:
                if flag:
                    res += ", "
                res += str(ele)
                flag = True
            res += ")"
            return res
        elif self.type == SEL:
            res += "{"
            flag = False
            for ele in self.value:
                if flag:
                    res += ", "
                res += str(ele)
                flag = True
            res += "}"
            return res
        else:
            res += "["
            flag = False
            for ele in self.value:
                if flag:
                    res += ", "
                res += str(ele)
                flag = True
            res += "]"
            return res
        
    def __str__(self) -> str:
        res = ""
        if self.type == SEQ:
            res += "("
            flag = False
            for ele in self.value:
                if flag:
                    res += ", "
                res += str(ele)
                flag = True
            res += ")"
        elif self.type == SEL:
            res += "{"
            flag = False
            for ele in self.value:
                if flag:
                    res += ", "
                res += str(ele)
                flag = True
            res += "}"
        else:
            res += "["
            flag = False
            for ele in self.value:
                if flag:
                    res += ", "
                res += str(ele)
                flag = True
            res += "]"
        self.string = res
        return res
    
    def __getitem__(self, item):
        if self.type in [SEL, LOOP]:
            # wrap self with SEQ
            t = TR(SEQ)
            t.value.append(self)
            self = t.copy()
        ret = TR(SEQ)
        if isinstance(item, slice):
            ret.value = self.value.__getitem__(item)
        else:
            ret.value = [self.value.__getitem__(item)]
        if len(ret.value) == 1 and \
            isinstance(ret.value[0], TR) and \
                ret.value[0].type in [SEL, LOOP]:
            ret = ret.value[0]
        return ret
    
    # only support SEQ + SEQ
    def __add__(self, tr1):
        assert isinstance(tr1, TR) and self.type == SEQ
        res = self.copy()
        if tr1.type == SEQ:
            res.value.extend(tr1.value)
        else:
            res.value.append(tr1)
        if res.min_len != -1:
            res.min_len += tr1.get_min_len()
        if res.max_len != -1:
            res.max_len += tr1.get_max_len()
        return res
    
    def __eq__(self, o):
        if o == None:
            return False
        if not isinstance(o, TR):
            return False
        if self.type != o.type:
            return False
        if len(self.value) != len(o.value):
            return False
        for i in range(len(self.value)):
            if self.value[i] != o.value[i]:
                return False
        return True
            
    def copy(self):
        ret = TR(self.type)
        ret.value = self.value.copy()
        if self.type == SEL:
            ret.edges = self.edges
        ret.min_len = self.min_len
        ret.max_len = self.max_len
        return ret

    # LOOP to SEQ, used when expand LOOP
    def to_seq(self):
        ret = TR(SEQ)
        ret.value = self.value.copy()
        ret.min_len = self.min_len
        ret.max_len = self.max_len
        return ret
    
    # SEQ to LOOP, used when construct LOOP (merge function)
    def to_loop(self):
        ret = TR(LOOP)
        if self.type == SEQ:
            ret.value = self.value.copy()
        else:
            ret.value.append(self)
        return ret
    
    def add_seq(self, ele):
        assert isinstance(ele, TR) or isinstance(ele, str)
        if self.type in [SEL, LOOP]:
            # wrap it with a SEQ
            res = TR(SEQ)
            res.value.append(self)
        else:
            res = self
        if isinstance(ele, str):
            res.value.append(ele)
            if res.min_len != -1:
                res.min_len += 1
            if res.max_len != -1:
                res.max_len += 1
        elif ele.type == SEQ:
            res += ele
            if res.min_len != -1:
                res.min_len += ele.get_min_len()
            if res.max_len != -1:
                res.max_len += ele.get_max_len()
        else:
            res.value.append(ele)
            if res.min_len != -1:
                res.min_len += ele.get_min_len()
            if res.max_len != -1:
                res.max_len += ele.get_max_len()
        return res
    
    def add_sel(self, ele, edge):
        assert self.type == SEL
        assert isinstance(ele, TR)
        self.value.append(ele)
        self.edges.append(edge)
        if ele.get_min_len() < self.get_min_len():
            self.min_len = ele.min_len
        if ele.get_max_len() > self.get_max_len():
            self.max_len = ele.max_len

    def can_be_empty(self):
        return self.get_min_len() == 0
        """
        if hasattr(self, "emptyable"):
            return self.emptyable
        self.emptyable = False
        if self.type == SEQ:
            for ele in self.value:
                if isinstance(ele, str):
                    return False
                if not ele.can_be_empty():
                    return False
            self.emptyable= True
            return True
        elif self.type == SEL:
            for ele in self.value:
                if isinstance(ele, str):
                    continue
                if ele.can_be_empty():
                    self.emptyable = True
                    break
            return self.emptyable
        else:
            self.emptyable = True # loop can always be empty
            return self.emptyable
            """

    def get_min_len(self):
        if self.min_len >= 0:
            return self.min_len
        self.min_len = 0
        if self.type == SEQ:
            for ele in self.value:
                if isinstance(ele, str):
                    self.min_len += 1
                else:
                    self.min_len += ele.get_min_len()
        elif self.type == SEL:
            tmp_min = sys.maxsize
            for ele in self.value:
                if ele.get_min_len() < tmp_min:
                    tmp_min = ele.get_min_len()
            self.min_len = tmp_min
        else:
            # here we suppose loop has one depth at least, 
            # because the 0-depth loop is covered by SEL according to the merge function.
            self.min_len = 0
            for ele in self.value:
                if isinstance(ele, str):
                    self.min_len += 1
                else:
                    self.min_len += ele.get_min_len()

        return self.min_len

    def get_max_len(self):
        if self.max_len >= 0:
            return self.max_len
        self.max_len = 0
        if self.type == SEQ:
            for ele in self.value:
                if isinstance(ele, str):
                    self.max_len += 1
                else:
                    self.max_len += ele.get_max_len()
        elif self.type == SEL:
            tmp_max = 0
            for ele in self.value:
                if ele.get_max_len() > tmp_max:
                    tmp_max = ele.get_max_len()
            self.max_len = tmp_max
        else:
            # here we suppose loop has one depth at least, 
            # because the 0-depth loop is covered by SEL according to the merge function.
            self.max_len = 0
            for ele in self.value:
                if isinstance(ele, str):
                    self.max_len += 1
                else:
                    self.max_len += ele.get_max_len()
            self.max_len = self.max_len * MAX_LOOP

        return self.max_len



    def random_generate(self, seed=0):
        trace = []
        if len(self.value) == 0:
            return trace
        if self.type == SEQ:
            for ele in self.value:
                if isinstance(ele, str):
                    trace.append(ele)
                else:
                    trace.extend(ele.random_generate(seed))
        elif self.type == SEL:
            choice = random.randint(0, len(self.value)-1)
            ele = self.value[choice]
            if isinstance(ele, str):
                trace.append(ele)
            else:
                trace.extend(ele.random_generate(seed))
        else: # loop
            loop_num = 2
            ele_seq = TR(SEQ)
            ele_seq.value = self.value.copy()
            for i in range(loop_num):
                subtrace = ele_seq.random_generate(seed)
                trace.extend(subtrace)
        return trace
    

    # test if TR matches the trace
    def match(self, trace, depth = 0):
        # pre = ""
        # for i in range(depth):
        #     pre += "|--"
        # print("{}match {} with {}".format(pre, self, trace))
        if self.get_min_len() > len(trace):
            return False
        if self.get_max_len() < len(trace):
            return False
        
        trace_len = len(trace)
        if trace_len == 0:
            return self.can_be_empty()
        
        if self.type in [SEL, LOOP]:
            # wrap it with SEQ
            tr = TR(SEQ)
            tr.value.append(self)
        else:
            tr = self
        
        try:
            ele = tr.value[0]
        except IndexError:
            return False
        if isinstance(ele, str):
            to_match = trace[0]
            if ele == to_match:
                return tr[1:].match(trace[1:], depth+1)
            else:
                return False
        elif ele.type == SEQ:
            print("HOW???")
            assert False
        elif ele.type == SEL:
            for i in range(len(ele.value)):
                selected_TR = TR(SEQ) # change SEL to SEQ and put it at the head of tr
                selected_TR = selected_TR.add_seq(ele.value[i])
                selected_TR += tr[1:]
                if selected_TR.match(trace, depth+1):
                    return True
            return False
        elif ele.type == LOOP:
            selected_TR = TR(SEQ) # expand the LOOP i times (i= 0 ~ max_loop-1)
            first_in = True
            if ele.get_min_len() == 0:
                max_try = MAX_LOOP
            else:
                max_try = min(MAX_LOOP, trace_len//ele.get_min_len())
            for i in range(max_try):
                if first_in:
                    first_in = False
                    continue
                else:
                    selected_TR += ele.to_seq()
                TR_to_test = selected_TR + tr[1:]
                if TR_to_test.match(trace, depth+1):
                    return True
            return False

# test if TR_a covers TR_b
# we test this by generating complex traces from TR_b
def cover(tra, trb):
    if trb == None:
        return True
    if tra == None:
        return False
    # print("{} covers {}?".format(tra, trb))
    max_try = 10 # test i times
    for i in range(max_try):
        tmp_trace = trb.random_generate()
        # print("!!! {} matches {}?".format(tra, tmp_trace))
        if not tra.match(tmp_trace):
            # print("No")
            return False
    # print("Yes")
    return True


# merge function in dataflow analysis
# which can be optimized
def merge(outs, edges): 
    # print("merge:")
    # for out in outs:
    #     print(out)
    # print("edges:")
    # for edge in edges:
    #     print(edge)

    res = TR(SEQ)
    LCP = longest_common_prefix(outs)
    if len(LCP.value) > 0:
        res += LCP

    branches = TR(SEL)
    start_at = element_num(LCP)
    max_len = -1
    max_tr = None
    left_trs = [] # left TRs after cut LCP off
    for i in range(len(outs)):
        left_tr = outs[i][start_at:]
        left_trs.append(left_tr)
        l = len(str(left_tr))
        if l > max_len:
            max_tr = left_tr
            max_len = l
    
    # all left TR is empty
    if len(max_tr.value) == 0:
        # print("merge result:")
        # print(res)
        return res

    # merge left TRs
    # optimization: remove TRs covered by max_tr
    for i in range(len(left_trs)):
        if left_trs[i] == max_tr or not cover(max_tr, left_trs[i]):
            if is_back_edge(edges[i]):
                branches.add_sel(left_trs[i].to_loop(), edges[i]) 
            else:
                branches.add_sel(left_trs[i], edges[i])
    if len(branches.value) < 1:
        print("how???")
        assert False
    elif len(branches.value) == 1 and len(LCP.value) == 0:
        res = branches.value[0]
    elif len(branches.value) == 1:
        branches = branches.value[0]
        res = res.add_seq(branches)
    else:
        if len(LCP.value) == 0:
            res = branches
        else:
            res = res.add_seq(branches)
    # print("merge result:")
    # print(res)
    return res
        


# a,b is a list
def longest_common_prefix(outs):
    min_len = sys.maxsize
    for out in outs:
        len_out = element_num(out)
        if len_out < min_len:
            min_len = len_out
    for i in range(min_len):
        v = outs[0][i]
        for out in outs[1:]:
            if out[i] != v:
                return outs[0][:i]
    return outs[0][:min_len]


def element_num(tr):
    if tr.type == SEQ:
        return len(tr.value)
    else: # regard LOOP or SEL as ONE element in TR
        return 1


def is_back_edge(edge):
    f, t = edge.split("->")
    f_num_str = f.split("_")[-1]
    t_num_str = t.split("_")[-1]
    f_num = int(f_num_str, 16)
    t_num = int(t_num_str, 16)
    return f_num > t_num


def get_inst_index(func_name, bbname, offset):
    return func_name + "_" + bbname + "_" + str(offset)


# construct a TR from a string
def from_string(s):
    stack = [] # stack used to store constructed TR
    current_value = ""
    for e in s:
        if e == " ":
            continue
        elif e == ",":
            if len(current_value) > 0:
                stack.append(current_value)
                current_value = ""
        elif e in ["(", "{", "["]:
            tr_type = TR.valid_type[["(", "{", "["].index(e)]
            tr = TR(tr_type)
            stack.append(tr)
        elif e in [")", "}", "]"]:
            if len(current_value) > 0:
                stack.append(current_value)
                current_value = ""
            tr_type = TR.valid_type[[")", "}", "]"].index(e)]
            ele_num = 0 # ele num is the num of elements in this TR
            # pop until get a matched type
            while(not (isinstance(stack[-1-ele_num], TR) and\
                        stack[-1-ele_num].type == tr_type and\
                         stack[-1-ele_num].value == [])):
                ele_num += 1
            tr = TR(tr_type)
            if ele_num > 0:
                tr.value = stack[-ele_num:]
            # pop ele_num+1 elements and push a new TR
            for i in range(ele_num+1):
                stack.pop()
            stack.append(tr)
        else:
            current_value += e
    return stack[0]            


if __name__ == "__main__":
    # test build from string
    sa = "[{[{(A), ()}], {(B), ()}}]"
    # sb = "[{{(), (B)}, [{(A), ()}]}, {(A), ()}]"
    
    trace = ['B', 'A', 'B', 'A', 'B', 'A']
    
    tra = from_string(sa)
    # trb = from_string(sb)

    # print(cover(tra, trb))
    # print(tra)
    # print(trb)
    # print(merge([tra, trb], ["1->2", "2->3"]))
    print(tra.match(trace, 0))



# previous implementation, which has some problems
"""
# construct a TR from a string
def from_string(s):
    bracket_stack = [] # stack used to store brackets and comma
    value_stack = [] # stack used to store value in TR

    current_value = ""
    "({(@A), [{(@A), [@B]}, @B]})"
    for e in s:
        if e == " ":
            continue
        elif e in ["(", "[", "{", ","]:
            bracket_stack.append(e)
            if len(current_value) > 0:
                assert e == ","
                value_stack.append(current_value)
                current_value = ""
        elif e in [")", "]", "}"]:
            if len(current_value) > 0:
                value_stack.append(current_value)
                current_value = ""
            num_to_pop = 0
            while(bracket_stack[-1-num_to_pop] == ','):
                num_to_pop += 1
            try:
                if isinstance(value_stack[-1], str) or num_to_pop > 0:
                    num_to_pop += 1
            except IndexError:
                pass
            if num_to_pop == 0:
                value = []
            else:
                value = value_stack[-num_to_pop:]
            # get tr_type according to e is ), } or ]
            tr_type = TR.valid_type[[")", "}", "]"].index(e)]
            tr = TR(tr_type)
            tr.value = value
            # pop value and push tr into the value stack
            for i in range(num_to_pop):
                value_stack.pop()
                bracket_stack.pop()
            value_stack.append(tr)
        else:
            current_value += e
    return value_stack[0]
"""