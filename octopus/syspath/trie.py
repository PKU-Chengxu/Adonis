# We use Trie (Prefix Tree) to build the API model
# The edge in Trie is event, leaf node is API (note 
# that one leaf node may correspond to more than one APIs).
# Here a node is a leaf node means the node can determine APIs.

from octopus.syspath.api import API

class TrieNode:
    """A node in the trie structure"""

    def __init__(self):
        # the event stored in this node
        self.event = None
        
        # the API stored in this node
        self.API = []

        # whether this can be the end of a API
        self.is_end = False

        # a dictionary of child nodes
        # keys are event, values are nodes
        self.children = {}

class Trie(object):
    """The trie object"""

    def __init__(self):
        """
        The trie has at least the root node.
        The root node does not store any event
        """
        self.root = TrieNode()
        self.used_api = None
    
    def insert(self, event_trace, api):
        """Insert a word into the trie"""
        if self.used_api and api not in self.used_api:
            return
        
        node = self.root
        
        # Loop through each event in the api
        # Check if there is no child containing the event, create a new child for the current node
        for event in event_trace:
            if event in node.children:
                node = node.children[event]
            else:
                # If a event is not found,
                # create a new node in the trie
                new_node = TrieNode()
                new_node.event = event
                node.children[event] = new_node
                node = new_node
        
        if api not in node.API:
            node.API.append(api)
        
        # Mark the end of a word
        node.is_end = True
    
    def match_from_head(self, event_trace):
        if event_trace == []:
            self.res = [([], 0)]
            return self.res
        node = self.root
        self.res = []
        self.dfs(node, event_trace, 0)
        if self.res == []:
            print("[WARN] cannot find a suitable api trace for: {}".format(event_trace))
            # if event_trace[0].event_type == "brk":
            print("try to ignore", event_trace[0].event_type)
            self.match_from_head(event_trace[1:])
            self.res = [( _[0], _[1]+1 ) for _ in self.res] # ignored brk also count for the matched number
            return self.res
        return self.res

    def dfs(self, node, event_trace, matched_num):
        """
        Depth-first traversal of the trie
        Args:
            - node: the node to start with
            - event_trace: the current event trace to search
            - matched_num: the number of matchend events in event trace
        """
        if node.is_end:
            self.res.append((node.API, matched_num))
        
        if event_trace == []:
            return
        
        to_match = event_trace[0].event_type
        if to_match not in node.children:
            return
        
        next_node = node.children[to_match]
        self.dfs(next_node, event_trace[1:], matched_num+1)

    def set_used_api(self, used_api):
        self.used_api = used_api