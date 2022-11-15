from queue import Queue
from octopus.syspath.execution_path import GeneralExecutionPathNode
from octopus.syspath.util import *
from octopus.syspath.block_recorder import BlolckRecorder
from octopus.core.function import get_block_index
from cachetools import cached, LRUCache, LFUCache
from octopus.syspath.stack_checker import StackChecker
from threading import RLock


# when the search queue is too long, we will take some options to limit it.
limited_queue_size = 100
lock = RLock()

#### function for searching most possible path
@cached(cache=LRUCache(maxsize=1000))
def bfs_search(self, func, start_bb, to_match, start_offset, exclude_func_calls = [], loose = False):
    """
    match the 'to_match' api trace in function 'func', starting from start_bb, and starting 
    from the "start_offset" (no less than start_offset). return possible paths (a list of PathNode)
    and matched numbers (a list of numbers, each correspond to a pathNode in paths and means how many 
    apis are successfully matched)
    exclude_func_calls contains the function name that we consider it is not a function, this will be 
    set when we finish matching in a function previously.
    """
    to_match = list(to_match)
    
    if StackChecker.have_loop():
        return [], [] # have infinite loop, no need to search deep

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
        if loose and cur_matched_num > 0:
            if matched == [] or cur_matched_num > max(matched):
                paths.append(cur_path.copy())
                matched.append(cur_matched_num)
                if cur_matched_num > 1000:
                    # avoid too long search
                    break
        # special case for exit api
        if cur_matched_num > 0:
            last_api = to_match[cur_matched_num-1]
            if last_api[0].name == "exit":
                # in this cae, the program should have exited
                cur_path.add_bb_tail(cur_bb.name)
                # this is a very corner case, when we just match from a function call, 
                # we should add this function to api_list
                cur_api = self.bb2api[cur_bb.name].copy()
                index_in_api = -1 # match from i's api in cur_api
                if len(cur_api) == 0:
                    index_in_api = 0
                for _ in range(len(cur_api)):
                    _offset = get_inst_offset_in_position(cur_api[_].position)
                    if _offset >= cur_offset:
                        index_in_api = _
                        break
                if index_in_api == -1:
                    cur_path.add_api_tail(cur_api[index_in_api:])
                if cur_matched_num not in matched:
                    paths.append(cur_path.copy())
                    matched.append(cur_matched_num)
                continue
        if cur_bb.name == "exit":
            cur_path.add_bb_tail(cur_bb.name)
            paths.append(cur_path.copy())
            matched.append(cur_matched_num)
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
                if self.get_func_readable_name(func) == "flush_block":
                    func
                continue
                # nodes_have_same_matched_num = br.query(cur_matched_num)
                # common_dom = func.cal_common_dom_node(nodes_have_same_matched_num)
                # if not cur_matched_num > br.records[common_dom]:
                #     # block recorder has recorded an equal bb with the same matched_num in the queue
                #     # and this path provide not increase to matched_num
                #     if len(q.queue) > limited_queue_size:
                #         continue
            br.update(cur_bb.name, cur_matched_num)
            cur_path.update_br(br)
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
            continue

        func_calls = [_ for _ in cur_api[index_in_api:] if ("$" in _.name or "^" in _.name) and _.name not in exclude_func_calls]
        if func_calls != []:
            # in some case, there would be some syscall apis before function calls
            # we sould handle these apis first.
            apis_before_func_call = []
            for _ in cur_api[index_in_api:]:
                if _.name not in exclude_func_calls and ("$" in _.name or "^" in _.name):
                    break
                else:
                    apis_before_func_call.append(_)
            if apis_before_func_call != []:
                # try to match
                i, j = 0, 0 # delta in api and to_match
                while (0 + i)<len(apis_before_func_call) and (j + cur_matched_num) < len(to_match):
                    if self.api_match(apis_before_func_call[0 + i], to_match[j + cur_matched_num], loose): 
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
                    StackChecker.push_stack(callee_name, len(left_to_match))
                    callee_paths, callee_match_infos = self.bfs_search(self, callee, callee.basicblocks[0], tuple(left_to_match), 0)
                    StackChecker.pop_stack()
                    for i in range(len(callee_paths)):
                        callee_path = callee_paths[i]
                        callee_match_num = callee_match_infos[i]
                        indirect_call_result_recorder[callee_match_num].append(callee_path)
                for indirect_call_match_num in indirect_call_result_recorder:
                    indirect_call_paths = indirect_call_result_recorder[indirect_call_match_num]
                    tmp_path = cur_path.copy()
                    # bundle the paths that has same match number
                    for indirect_call_path in indirect_call_paths:
                        tmp_path.add_child(_.position, indirect_call_path)
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
                StackChecker.push_stack(callee_name, len(left_to_match))
                callee_paths, callee_match_infos = self.bfs_search(self, callee, callee.basicblocks[0], tuple(left_to_match), 0)
                StackChecker.pop_stack()
                for i in range(len(callee_paths)):
                    callee_path = callee_paths[i]
                    callee_match_num =  callee_match_infos[i]
                    tmp_path = cur_path.copy()
                    tmp_path.add_child(_.position, callee_path)
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
            if self.api_match(cur_api[index_in_api + i], to_match[j + cur_matched_num], loose): 
                i += 1
                j += 1
            else: 
                break
        if (index_in_api + i) < len(cur_api): # not match
            br.update(cur_bb.name, cur_matched_num)
            continue
        else: # match
            cur_path.add_bb_tail(cur_bb.name)
            cur_path.add_api_tail(cur_api[index_in_api:])
            cur_matched_num += i
            if br.check(cur_bb.name, cur_matched_num):
                if self.get_func_readable_name(func) == "flush_block":
                    func
                continue
                # nodes_have_same_matched_num = br.query(cur_matched_num)
                # common_dom = func.cal_common_dom_node(nodes_have_same_matched_num)
                # if not cur_matched_num > br.records[common_dom]:
                #     # block recorder has recorded an equal bb with the same matched_num in the queue
                #     # and this path provide not increase to matched_num
                #     if len(q.queue) > limited_queue_size:
                #         continue
            br.update(cur_bb.name, cur_matched_num)
            cur_path.update_br(br)
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
            

    # we only use top k
    # to_sort = [(paths[i], matched[i]) for i in range(len(paths))]
    # k = 3
    # topk = sorted(to_sort, key=lambda _: _[1], reverse=True)[:k]
    # paths = [ _[0] for _ in topk]
    # matched = [ _[1] for _ in topk]

    # we only use the paths that has the top k matched number
    if self.get_func_readable_name(func) == "flush_block":
        func

    # we only use top k
    k = 5
    if loose:
        k = 1
    to_sort = [(paths[i], matched[i]) for i in range(len(paths))]
    if to_sort == []:
        return [], []
    sorted_paths_matched = sorted(to_sort, key=lambda _: _[1], reverse=True)
    topk = sorted_paths_matched[:k]
    paths = [ _[0] for _ in topk]
    matched = [ _[1] for _ in topk]


    """
    max_index = 0
    cur_max_matched_num = sorted_paths_matched[0][1]
    while max_index < len(sorted_paths_matched) and k > 1:
        paths.append(sorted_paths_matched[max_index][0])
        matched.append(sorted_paths_matched[max_index][1])
        if sorted_paths_matched[max_index][1] < cur_max_matched_num:
            cur_max_matched_num = sorted_paths_matched[max_index][1]
            k -= 1
        max_index += 1
    """
    return paths, matched

@cached(cache=LFUCache(maxsize=1000))
def reverse_bfs_search(self, func, start_bb, to_match, start_offset, exclude_func_calls = [], loose = False):
    """
    reversely match the 'to_match' api trace in function 'func', starting from start_bb
    return possible paths (a list of PathNode) and matched numbers (a list of 
    numbers, each correspond to a pathNode in paths and means how many apis are 
    successfully matched)
    exclude_func_calls contains the function name that we consider it is not a function, this will be 
    set when we finish matching in a function previously.
    """
    if StackChecker.have_loop():
        return [], [] # have infinite loop, no need to search deep

    to_match = list(to_match)
    # exclude_func_calls = list(exclude_func_calls)
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
        if loose and cur_matched_num > 0:
            if matched == [] or cur_matched_num > max(matched):
                paths.append(cur_path.copy())
                matched.append(cur_matched_num)
                if cur_matched_num > 1000:
                    # avoid too long search
                    break
        if cur_bb.name == "entry":
            cur_path.add_bb_tail(cur_bb.name)
            paths.append(cur_path.copy())
            matched.append(cur_matched_num)
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
                continue
                # nodes_have_same_matched_num = br.query(cur_matched_num)
                # common_dom = func.cal_common_reverse_dom_node(nodes_have_same_matched_num)
                # if not cur_matched_num > br.records[common_dom]:
                #     # block recorder has recorded an equal bb with the same matched_num in the queue
                #     # and this path provide not increase to matched_num
                #     if len(q.queue) > limited_queue_size:
                #         continue
            br.update(cur_bb.name, cur_matched_num)
            cur_path.update_br(br)
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
            continue

        func_calls = [_ for _ in cur_api[index_in_api:] if ("$" in _.name or "^" in _.name) and _.name not in exclude_func_calls]
        if func_calls != []:
            # in some case, there would be some syscall apis before function calls
            # we sould handle these apis first.
            apis_before_func_call = []
            for _ in cur_api[index_in_api:]:
                if _.name not in exclude_func_calls and ("$" in _.name or "^" in _.name):
                    break
                else:
                    apis_before_func_call.append(_)
            if apis_before_func_call != []:
                # try to match
                i, j = 0, 0 # delta in api and to_match
                while (0 + i)<len(apis_before_func_call) and (j + cur_matched_num) < len(to_match):
                    if self.api_match(apis_before_func_call[0 + i], to_match[j + cur_matched_num], loose): 
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
                    StackChecker.push_stack(callee_name, len(left_to_match))
                    callee_paths, callee_match_infos = self.reverse_bfs_search(self, callee, callee.basicblocks[0], tuple(left_to_match), 0)
                    StackChecker.pop_stack()
                    for i in range(len(callee_paths)):
                        callee_path = callee_paths[i]
                        callee_match_num =  callee_match_infos[i]
                        indirect_call_result_recorder[callee_match_num].append(callee_path)
                for indirect_call_match_num in indirect_call_result_recorder:
                    indirect_call_paths = indirect_call_result_recorder[indirect_call_match_num]
                    tmp_path = cur_path.copy()
                    # bundle the paths that has same match number
                    for indirect_call_path in indirect_call_paths:
                        tmp_path.add_child(_.position, indirect_call_path)
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
                StackChecker.push_stack(callee_name, len(left_to_match))
                callee_paths, callee_match_infos = self.reverse_bfs_search(self, callee, callee.basicblocks[-1], tuple(left_to_match), callee.basicblocks[-1].end_offset)
                StackChecker.pop_stack()
                for i in range(len(callee_paths)):
                    callee_path = callee_paths[i]
                    callee_match_num =  callee_match_infos[i]
                    tmp_path = cur_path.copy()
                    tmp_path.add_child(_.position, callee_path)
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
            if self.api_match(cur_api[index_in_api + i], to_match[j + cur_matched_num], loose):
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
                continue
                # nodes_have_same_matched_num = br.query(cur_matched_num)
                # common_dom = func.cal_common_reverse_dom_node(nodes_have_same_matched_num)
                # if not cur_matched_num > br.records[common_dom]:
                #     # block recorder has recorded an equal bb with the same matched_num in the queue
                #     # and this path provide not increase to matched_num
                #     if len(q.queue) > limited_queue_size:
                #         continue
            br.update(cur_bb.name, cur_matched_num)
            cur_path.update_br(br)
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
    # to_sort = [(paths[i], matched[i]) for i in range(len(paths))]
    # k = 3
    # topk = sorted(to_sort, key=lambda _: _[1], reverse=True)[:k]
    # paths = [ _[0] for _ in topk]
    # matched = [ _[1] for _ in topk]

    # we only use the paths that has the top k matched number
    k = 5
    if loose:
        k = 1
    to_sort = [(paths[i], matched[i]) for i in range(len(paths))]
    if to_sort == []:
        return [], []
    sorted_paths_matched = sorted(to_sort, key=lambda _: _[1], reverse=True)
    topk = sorted_paths_matched[:k]
    paths = [ _[0] for _ in topk]
    matched = [ _[1] for _ in topk]
    
    """
    paths = []
    matched = []

    max_index = 0
    cur_max_matched_num = sorted_paths_matched[0][1]
    while max_index < len(sorted_paths_matched) and k > 1:
        paths.append(sorted_paths_matched[max_index][0])
        matched.append(sorted_paths_matched[max_index][1])
        if sorted_paths_matched[max_index][1] < cur_max_matched_num:
            cur_max_matched_num = sorted_paths_matched[max_index][1]
            k -= 1
        max_index += 1
    """
    return paths, matched
    

