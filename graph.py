class Graph():
    def __init__(self):
        self.node_list={}
        self.edge_list=[]
        self.isDirected = False
        
    def add_node(self, nod, x, y):
        self.node_list[nod]=[x, y]
    
    def add_edge(self, source, target, cost):
        self.edge_list.append(source)
        self.edge_list.append(target)
        self.edge_list.append(cost)
    
    def remove_node(self, nod):
        del self.node_list[nod]
    
    def remove_edge(self, source, target):
        for i in range(0, len(self.edge_list), 3):
            if self.edge_list[i] == source and self.edge_list[i+1] == target:
                del self.edge_list[i:i+3]
                return

    def change_node(self, old_node, node):
        x, y = self.node_list[old_node]
        self.node_list[node] = [x, y]
        del self.node_list[old_node]

        for i in range(0, len(self.edge_list), 3):
            if self.edge_list[i] == old_node:
                self.edge_list[i] = node

            elif self.edge_list[i+1] == old_node:
                    self.edge_list[i+1] = node
    
    def update_cost(self, source_node, target_node, new_cost):
        for i in range(0, len(self.edge_list), 3):
            if self.edge_list[i] == source_node and self.edge_list[i + 1] == target_node:
                self.edge_list[i + 2] = new_cost

    def update_node_position(self, node, x, y):
        self.node_list[node] = [x, y]

    def import_graph(self):
        file = open('graph', 'r')
        self.isDirected = bool(int(file.readline()))

        self.node_list.clear()
        self.edge_list.clear()

        nodes = file.readline().split()
        for i in range(0, len(nodes), 3):
            self.node_list[int(nodes[i])] = [float(nodes[i + 1]), float(nodes[i + 2])]

        edges = file.readline().split()
        for i in range(0, len(edges), 3):
            self.edge_list.append(int(edges[i]))
            self.edge_list.append(int(edges[i + 1]))

            if edges[i + 2] == 'None':
                self.edge_list.append(edges[i + 2])
            else:
                self.edge_list.append(int(edges[i + 2]))