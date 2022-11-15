# a stack checker is to record the searched function
# when a cycle is detected, it will raise a exception,
# so that the searching algorithm can avoid infinite loop.

class StackChecker:
    stack = []
    
    @classmethod
    def init(cls):
        cls.stack.clear()

    @classmethod
    def push_stack(cls, func_name, matched_num):
        cls.stack.append((func_name, matched_num))
    
    @classmethod
    def pop_stack(cls):
        cls.stack.pop()
    
    @classmethod
    def have_loop(cls):
        # a infinite loop happens when there are same items in the stack.
        same_left_to_match = 0
        i = len(cls.stack) - 1
        num_left_to_match = cls.stack[i][1]
        while i >= 0:
            i -= 1
            if cls.stack[i][1] != num_left_to_match:
                break
            else:
                same_left_to_match += 1
            if same_left_to_match >= 5:
                break
        if same_left_to_match >= 5:
            return True
        tmp = set(cls.stack)
        return len(tmp) != len(cls.stack)

# we find the expand operation can also result in an infinite loop
# so, for convenience, we just define a new but same class :)
class ExpandStackChecker:
    stack = []
    
    @classmethod
    def init(cls):
        cls.stack.clear()

    @classmethod
    def push_stack(cls, func_name, matched_num):
        cls.stack.append((func_name, matched_num))
    
    @classmethod
    def pop_stack(cls):
        cls.stack.pop()
    
    @classmethod
    def have_loop(cls):
        # a infinite loop happens when there are same items in the stack.
        tmp = set(cls.stack)
        return len(tmp) != len(cls.stack)
