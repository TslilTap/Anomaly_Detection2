import copy


class LZ_tree:
    def __init__(self, seq,tree=None):
        if not all(isinstance(symbol, int) for symbol in seq):
            raise ValueError("Input 'seq' must be a vector of integers.")

        if tree is None:
            # start tree from scratch
            self.nodes = []
            self.libsize = max(seq)+1  # size of library, how many different symbols are there
            self.root = self.Node(tree=self) # create the root
        else:
            # build from an existing tree
            self.libsize = tree.libsize
            self.nodes = tree.nodes.copy()
        self.build_tree(seq)
        self.prob_model_flag = False



    def build_tree(self, seq):
        node_address = 0  # start at the root
        for symbol in seq:
            node = self.nodes[node_address]
            child_address = node.children_address[symbol] # go to current node's child
            if child_address == 0:
                ##no child, update
                node.add_child(symbol)
            node_address = child_address # look at the next node (either the previous node's child or the root)

    def compress(self):
        seq = []
        for node in self.nodes:
            if node.symbol is not None:
                seq.append(node.get_sequence())
        return seq

    def seq2node(self,seq):
        '''
        :param seq: a sequence of symbols
        :return: if such node exists in the tree, return its address. If not, return '-1'.
        :Note: if you wish for a sequence of nodes, use 'seq2nodes'
        '''

        if len(seq) == 0:
            return 0

        node = self.root
        for symbol in seq:
            child = node.children[symbol]
            if child is None:
                return None
            node = child
        return node

    def seq2nodes(self,seq):
        if len(seq) == 0:
            return [0]

        nodes = []
        node = self.root
        for symbol in seq:
            child = node.children[symbol]
            if child is None:
                nodes.append(node)
                child = self.root
            node = child

        if node is not None:
            nodes.append(node)
        return nodes

    def prob_init(self):
        self.prob_model_flag = True
        self.root.prob_init()


    def get_prob_model(self):
        prob_model = copy.copy(self)
        prob_model.root.prob_init()
        return prob_model

    def update(self,seq):
        if self.prob_model_flag:
            self.prob_model_flag = False
            for node in self.nodes:
                node.prob_reset()
            self.build_tree(seq)

    def get_updated_tree(self,seq):
        updated_tree = copy.copy(tree)
        updated_tree.update(seq)
        return updated_tree

    def seq_prob(self, seq):
        if not self.prob_model_flag:
            print("the tree was not yet updated to be a probability model. updating it now")
            self.prob_init()
        p = 1
        node = self.root  # start at the root
        for symbol in seq:
            p *= node.children_prob[symbol]
            child_address = node.children_address[symbol]
            node = self.nodes[child_address]
        return p


    class Node:
        def __init__(self,
                     tree,
                     symbol=None,
                     parent=None):

            self.tree = tree # the tree of which this node belongs to
            self.symbol = symbol  # which symbol exists within this node
            self.address = len(self.tree.nodes)  # this node's address in the tree
            tree.nodes.append(self)  # add the node to the tree's list of nodes

            self.parent = parent # the node's parent


            if parent is not None:
                self.parent_address = parent.address  # this node's parent's address
            else:
                self.parent_address = None

            self.children = [None] * self.tree.libsize # a list of the node's children. upon creation it has None.
            self.children_address = [0] * self.tree.libsize # the children addresses in the tree. upon creation, put in '0'. the address of the root

            # variables for probability model
            self.children_weights = None
            self.weight = None
            self.children_prob = None


        def add_child(self,symbol):
            if self.children[symbol] is not None:
                raise ValueError("trying to add a child where a child already exists")
            child = self.tree.Node(tree=self.tree,
                                   symbol=symbol,
                                   parent=self)
            self.children[symbol] = child
            self.children_address[symbol] = child.address

        def get_sequence(self):
            if self.parent is None:
                seq = []
            else:
                seq = self.parent.get_sequence()
            seq.append(self.symbol)
            return seq

        def prob_init(self):
            self.children_weights = [1] * self.tree.libsize
            for symbol in range(self.tree.libsize):
                child = self.children[symbol]
                if child is not None:
                    child.prob_init()
                    self.children_weights[symbol] = child.weight
            self.weight = sum(self.children_weights)
            self.children_prob = [weight / self.weight for weight in self.children_weights]

        def prob_reset(self):
            self.children_weights = None
            self.weight = None
            self.children_prob = None

seq = [0,0,1,3,1,1,0,2,1,1,3,0]
tree = LZ_tree(seq=seq)


seq2 = [0,0,1,3,1,1,0,2,1,1,3,0,3,1,2,3]
tree2 = LZ_tree(seq=seq)

example_seq = [1,3,2,0]
x = tree.seq_prob1(example_seq)
print(x)
x = tree.seq_prob2(example_seq)
print(x)