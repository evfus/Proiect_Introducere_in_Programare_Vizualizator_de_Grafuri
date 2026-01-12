from collections import deque

#prezenta visited este doar pt eficenta mergand pe baza de hash-uri, aceasta poate fi scoasa si inlocuita doar de order daca nu cont eficenta

def dfs(graph_obj, start_node, visited=None, order=None):
    if visited is None:
        visited = set()
    if order is None:
        order = []
    
    visited.add(start_node)
    order.append(start_node)

    neighbors = []
    for i in range(0, len(graph_obj.edge_list), 3):
        u = graph_obj.edge_list[i]
        v = graph_obj.edge_list[i+1]
        if u == start_node:
            neighbors.append(v)
        elif not graph_obj.isDirected and v == start_node:
            neighbors.append(u)
    for neighbor in neighbors:
        if neighbor not in visited:
            dfs(graph_obj, neighbor, visited, order)
            
    return order

def bfs(graph_obj, start_node):
    visited = {start_node}
    order = []
    queue = deque([start_node]) # deque pt eficenta

    while queue:
        current_node = queue.popleft()
        order.append(current_node)
        neighbors = []
        for i in range(0, len(graph_obj.edge_list), 3):
            u = graph_obj.edge_list[i]
            v = graph_obj.edge_list[i+1]
            
            if u == current_node:
                neighbors.append(v)
            elif not graph_obj.isDirected and v == current_node:
                neighbors.append(u)

        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order
