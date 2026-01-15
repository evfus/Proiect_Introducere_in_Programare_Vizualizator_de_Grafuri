from collections import deque
import heapq

#prezenta visited este doar pt eficenta mergand pe baza de hash-uri, aceasta poate fi scoasa si inlocuita doar de order daca nu cont eficenta

def dfs(graph_obj, start_node, visited=None, order=None):
    if start_node%2 == 0:
        return
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
        if u == start_node and u%2!=0:
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

def dijkstra(graph_obj, start_node, target_node):
    for i in range(2, len(graph_obj.edge_list), 3):
        cost = graph_obj.edge_list[i]
        if cost is None or cost == "None" or cost == "":
            return "ERROR_COST"

    distances = {node: float('inf') for node in graph_obj.node_list.keys()}
    distances[start_node] = 0
    predecessors = {node: None for node in graph_obj.node_list.keys()}
    priority_queue = [(0, start_node)]
    visited = set()

    while priority_queue:
        current_dist, u = heapq.heappop(priority_queue)  #heapq pt efficenta, radacina(index 0) mereu are cea mai mica val.

        if u in visited:
            continue
        visited.add(u)

        if u == target_node:
            break

        for i in range(0, len(graph_obj.edge_list), 3):
            src = graph_obj.edge_list[i]
            dest = graph_obj.edge_list[i+1]
            weight = int(graph_obj.edge_list[i+2])

            neighbor = None
            if src == u: neighbor = dest
            elif not graph_obj.isDirected and dest == u: neighbor = src

            if neighbor is not None:
                new_dist = current_dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = u
                    heapq.heappush(priority_queue, (new_dist, neighbor))
    path = []
    curr = target_node
    while curr is not None:
        path.append(curr)
        curr = predecessors[curr]
    path.reverse() 

    if path[0] != start_node:
        return []
        
    return path
