class API:
    def __init__(self, name, position = None, possibility = -1000, trace = None):
        self.name = name
        self.position = position
        self.possibility = possibility
        self.trace = trace
    
    def set_position(self, position):
        self.position = position
    
    def set_possibility(self, possibility):
        self.possibility = possibility
    
    def __str__(self) -> str:
        if self.position:
            return "<{}@{}:{}>".format(self.name, self.position, self.trace)
        else:
            return "<{}:{}>".format(self.name, self.trace)
    
    def __repr__(self) -> str:
        return str(self)
    
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, API):
            return False
        return self.name == __o.name and self.position == __o.position # exactly match
    

    def __hash__(self) -> int:
        # print("api.py: hash: ", (self.name, self.position).__hash__())
        return (self.name, self.position).__hash__()

    def loose_equal(self, __o: object) -> bool:
        """
        test if api A equals to api B under a loose constraint:
        if A, B both have position info, then we compare the position info
        if not, we only compare the api name.
        """
        if not isinstance(__o, API):
            return False
        if self.position and __o.position:
            return self == __o
        else:
            return self.name ==__o.name

