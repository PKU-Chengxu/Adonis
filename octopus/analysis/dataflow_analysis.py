MAX_ITER = 1000

class DataFlowAnalysis:
    def __init__(self, func, init_in, init_out, transfer, merge, reverse = False) -> None:
        self.func = func # Function
        self.init_in = init_in # init function I, I(basicblock, func) = Val_IN
        self.init_out = init_out # init function I, I(basicblock, func) = Val_OUT
        self.transfer = transfer # transfer function F,  F(basicblock, IN) = OUT
        self.merge = merge # merge function M, M(Vals) = Val
        self.reverse = reverse
    

    def analyze(self):
        # data flow analysis
        bb_in = { bb.name: self.init_in(bb, self.func) for bb in self.func.basicblocks } # value before basic block
        bb_out = { bb.name: self.init_out(bb, self.func) for bb in self.func.basicblocks } # value after basic block
        if not self.reverse:
            # forward
            is_stable = False
            for i in range(MAX_ITER):
                if is_stable:
                    break
                is_stable = True
                # read from last, write into new
                last_bb_in = bb_in.copy()
                last_bb_out = bb_out.copy()
                for bb in self.func.basicblocks:
                    # merge values of predecessors
                    pred_outs = [last_bb_out[pred] for pred in bb.pred_bbs]
                    new_in = self.merge(pred_outs)
                    if new_in != last_bb_in[bb.name]:
                        is_stable = False
                        bb_in[bb.name] = new_in
                    
                    # transfer function
                    old_bb_out = last_bb_out[bb.name].copy()
                    new_bb_in = bb_in[bb.name].copy() #initialized as new IN of bb, which is bb_in
                    new_bb_out = self.transfer(bb, new_bb_in) # the transfer should handle the instruction reverse or not
                    if new_bb_out != old_bb_out:
                        bb_out[bb.name] = new_bb_out
                        is_stable = False
            return bb_out
        else:
            # backward
            is_stable = False
            for i in range(MAX_ITER):
                if is_stable:
                    break
                is_stable = True
                # read from last, write into new
                last_bb_in = bb_in.copy()
                last_bb_out = bb_out.copy()
                reverse_bbs = self.func.basicblocks.copy()
                reverse_bbs.reverse()
                for bb in reverse_bbs:
                    # merge values of successors
                    succ_ins = [last_bb_in[succ] for succ in bb.succ_bbs]
                    new_out = self.merge(succ_ins)
                    if new_out != last_bb_out[bb.name]:
                        is_stable = False
                        bb_out[bb.name] = new_out
                    
                    # transfer function
                    old_bb_in = last_bb_in[bb.name].copy()
                    new_bb_out = bb_out[bb.name].copy() # the input of transfer function is initialized as new OUT of bb, which is bb_out
                    new_bb_in = self.transfer(bb, new_bb_out) # the transfer function should handle the instruction reverse or not
                    if new_bb_in != old_bb_in:
                        bb_in[bb.name] = new_bb_in
                        is_stable = False
            return bb_in


    
    
