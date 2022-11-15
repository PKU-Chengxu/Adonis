from octopus.core.function import Function


class BlolckRecorder:
    """
    This class will be used to record each basic block's match number 
    when performing bfs search. If all basic blocks' match number is 
    equal when meeting the 'exit' block, then the search process for 
    this function could be stopped. Because in this case, all basic
    blocks can not match with the first API in the to-match trace.
    """
    def __init__(self, func: Function):
        self.records = { _.name: -1 for _ in func.basicblocks if _.name != "exit" or _.name != "entry"}
    

    def update(self, bb_name, match_num):
        """
        update the records, make sure bb_name is in the records.
        """
        assert bb_name in self.records
        self.records[bb_name] = match_num
    

    def check(self, bb_name, match_num):
        """
        check if (bb_name, match_num) is in the records. If so, we can ignore
        the successors of bb_name, because they have already been put into the 
        search queue.
        """
        assert bb_name in self.records
        return self.records[bb_name] == match_num
    

    def is_all_equal(self):
        """
        Check if all match num in the records are eqaul. This function would be
        called when meeting an 'exit' node in the search queue.
        """
        return len(set(self.records.values())) == 1
    

    def query(self, value):
        """
        return the bbs whose value is equal to the arguement
        """
        ret = []
        for _ in self.records:
            if self.records[_] == value:
                ret.append(_)
        return ret

