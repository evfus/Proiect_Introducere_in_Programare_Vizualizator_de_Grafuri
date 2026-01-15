import networkx as nx
class Graph():
    def __init__(self):
        self.node_list={}
        self.edge_list=[]
        self.isDirected = False
        
    def add_node(self, nod, x, y):
        self.node_list[nod]=[int(x), int(y)]
    
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
        self.node_list[node] = [int(x), int(y)]

    def import_graph(self, file_path):
        file = open(file_path, 'r')
        first_line = file.readline().strip()

        self.isDirected = True if first_line == "True" else False

        self.node_list.clear()
        self.edge_list.clear()

        nodes = file.readline().split()
        for i in range(0, len(nodes), 3):
            self.node_list[int(nodes[i])] = [int(nodes[i + 1]), int(nodes[i + 2])]

        edges = file.readline().split()
        for i in range(0, len(edges), 3):
            self.edge_list.append(int(edges[i]))
            self.edge_list.append(int(edges[i + 1]))

            if edges[i + 2] == 'None':
                self.edge_list.append(edges[i + 2])
            else:
                self.edge_list.append(int(edges[i + 2]))

    def export_graph(self, file_path):
        with open(file_path, 'w') as file:
            file.write(f"{self.isDirected}\n")
        
            node_data = []
            for node_id, pos in self.node_list.items():
                node_data.extend([str(node_id), str(int(pos[0])), str(int(pos[1]))])
            file.write(" ".join(node_data) + "\n")
        
            edge_data = []
            for i in range(0, len(self.edge_list), 3):
                u = self.edge_list[i]
                v = self.edge_list[i+1]
                cost = self.edge_list[i+2]
                edge_data.extend([str(u), str(v), str(cost)])
            file.write(" ".join(edge_data) + "\n")
    
    def export_as_dimacs(self, file_path):
        if not file_path:
            return
        
        file = open(file_path, 'w')
        
        problem_type = 'sp' if self.isDirected else 'p'
        node_count = len(self.node_list)
        edge_count = int(len(self.edge_list) / 3)
        
        file.write(f"{problem_type} {node_count} {edge_count}\n")

        edge = 'a' if self.isDirected else 'e'

        for i in range(0, len(self.edge_list), 3):
            cost = "" if self.edge_list[i + 2] == "None" or self.edge_list[i + 2] is None else self.edge_list[i+2]
            file.write(f"{edge} {self.edge_list[i]} {self.edge_list[i + 1]} {cost}\n")

    def export_as_graphml(self, file_path):
        if not file_path:
            return

        file = open(file_path, 'w')

        nxGraph = nx.DiGraph() if self.isDirected else nx.Graph()

        for node, pos in self.node_list.items():
            nxGraph.add_node(node, x = pos[0], y = pos[1])
        
        for i in range(0, len(self.edge_list), 3):
            source = self.edge_list[i]
            target = self.edge_list[i + 1]
            cost = self.edge_list[i + 2]
            nxGraph.add_edge(source, target, weight = cost)

        nx.write_graphml(nxGraph, file_path)