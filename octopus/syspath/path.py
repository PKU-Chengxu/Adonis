"""
path class according to EPP algorithm
"""

class Path:
    def __init__(self, pathSum, cfg) -> None:
        self.pathSum = pathSum
        self.cfg = cfg
        self.start_node = None
        self.end_node = None
        self.start_from_entry = None
        self.end_at_exit = None
    
    def real_path(self):
        # generate real path according to the path sum
        # to reduce the memory cost, we will not store the path
        path = []
        path.append(self.cfg.entry)
        pathSum = self.pathSum
        virtual_edge_from_entry = False
        virtual_edge_to_exit = False
        while(True):
            s = path[-1]
            if s == self.cfg.exit:
                break
            
            # here e should be the edge whose val is the biggest and strat from s
            e_with_max_val = None
            max_val = -1
            for e in self.cfg.Val:
                val = self.cfg.Val[e]
                if val <= max_val:
                    continue
                if val <= pathSum:
                    f, t = e.split("->") # from, to
                    if f == s:
                        # find a valid edge
                        if val > max_val:
                            max_val = val
                            e_with_max_val = e
            
            # e_with_max_val is the next edge
            e = e_with_max_val
            virtual_edge = False
            if "#" in e:
                virtual_edge = True
                e = e.split("#")[0]
            f, t = e.split("->") # from, to
            path.append(t)
            val = self.cfg.Val[e_with_max_val]
            pathSum -= val
            if virtual_edge and f == self.cfg.entry:
                virtual_edge_from_entry = True
            if virtual_edge and t == self.cfg.exit:
                virtual_edge_to_exit = True
        if virtual_edge_from_entry:
            path.pop(0)
        if virtual_edge_to_exit:
            path.pop(-1)
        # print("pathSum: {}".format(self.pathSum))
        # print("path: {}".format(path))

        self.start_node = path[0]
        self.end_node = path[-1]
        self.start_from_entry = self.start_node == self.cfg.entry
        self.end_at_exit = self.end_node == self.cfg.exit

        return path
        
                
                