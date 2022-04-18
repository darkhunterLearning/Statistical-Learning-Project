from collections import defaultdict
 
# this class represents a directed graph using adjacency list representation
 
 
class Graph:
    # Constructor
    def __init__(self):
        # default dictionary to store graph
        self.graph = defaultdict(list)
 
    # Function to add an edge to graph
    def addEdge(self, u, v):
        self.graph[u].append(v)
    # A function used by DFS
 
    def DFSUtil(self, v, visited):
        # Mark the current node as visited and print it
        visited.add(v)
        print(v,end=" ")
 
        # recur for all the vertices adjacent to this vertex
        for neighbour in self.graph[v]:
            if neighbour not in visited:
                self.DFSUtil(neighbour, visited)
        # The function to do DFS traversal. It uses recursive DFSUtil
 
    def DFS(self):
        # create a set to store all visited vertices
        visited = set()
        # call the recursive helper function to print DFS traversal starting from all
        # vertices one by one
        for vertex in self.graph:
            if vertex not in visited:
                self.DFSUtil(vertex, visited)
# Driver code
# create a graph given in the above diagram
def listToMatrix(adj, V):
 
    # Initialize a matrix
    matrix = [[0 for j in range(V)]
                 for i in range(V)]
     
    for i in range(V):
        for j in adj[i]:
            matrix[i][j] = 1
     
    return matrix

def matrixToList(a):
    adjList = defaultdict(list)
    for i in range(len(a)):
        for j in range(len(a[i])):
            if a[i][j] == 1:
               adjList[i].append(j)
    return adjList

# print("Following is Depth First Traversal \n")
g = Graph()
g.addEdge(0, 1)
g.addEdge(1, 3)
g.addEdge(3, 4)
print(g.graph)
test_list = list(g.graph.values())
adj_matrix = listToMatrix(test_list, len(test_list))
for m in adj_matrix:
    print(m)
g.DFS()