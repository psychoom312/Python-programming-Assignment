import sys
import heapq

sys.setrecursionlimit(250000)

def find_cycle(u, adj, visited, path, in_stack):
    visited.add(u)
    in_stack.add(u)
    path.append(u)
    
    # Sort neighbors to get a consistent cycle trajectory
    for v in sorted(adj.get(u, [])):
        if v not in visited:
            if find_cycle(v, adj, visited, path, in_stack):
                return True
        elif v in in_stack:
            # Cycle found! Extract the path from the first occurrence of v
            cycle_start_idx = path.index(v)
            path[:] = path[cycle_start_idx:]
            return True
            
    path.pop()
    in_stack.remove(u)
    return False

def solve():
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return
        
    first_line = input_data[0].split()
    n = int(first_line[0])
    e = int(first_line[1])
    
    modules = []
    for i in range(1, n + 1):
        modules.append(input_data[i].strip())
        
    # adj represents: module_a -> list of modules that depend on module_a
    adj = {m: set() for m in modules}
    in_degree = {m: 0 for m in modules}
    
    # Track existing duplicate edges
    seen_edges = set()
    
    # Read dependency edges
    for i in range(n + 1, n + 1 + e):
        if i >= len(input_data):
            break
        line = input_data[i].strip()
        if not line:
            continue
        parts = line.split()
        u = parts[0]  # module_a
        v = parts[1]  # imports module_b (v must load before u)
        
        # Edge direction: v -> u (since v must load before u)
        if (v, u) not in seen_edges:
            seen_edges.add((v, u))
            adj[v].add(u)
            in_degree[u] += 1

    # Kahn's Algorithm using a Min-Heap for lexicographical constraint
    heap = []
    for m in modules:
        if in_degree[m] == 0:
            heapq.heappush(heap, m)
            
    order = []
    while heap:
        curr = heapq.heappop(heap)
        order.append(curr)
        
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
                
    # If the order doesn't contain all modules, a cycle exists
    if len(order) == n:
        print(" ".join(order))
    else:
        # Run a localized DFS to isolate the circular path loop
        visited = set()
        in_stack = set()
        path = []
        
        # Find the cycle by scanning modules lexicographically
        for m in sorted(modules):
            if m not in visited:
                if find_cycle(m, adj, visited, path, in_stack):
                    print("CYCLE " + " ".join(path))
                    return

if __name__ == '__main__':
    solve()
