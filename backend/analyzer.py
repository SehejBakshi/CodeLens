import ast
from typing import List, Dict
import networkx as nx
import graphviz

class ArchitectureMetric:
    def __init__(self, name, dot_diagram):
        self.name = name
        self.dot_diagram = dot_diagram
    def dict(self):
        return {"name": self.name, "dot_diagram": self.dot_diagram}
    
def analyze_code(code: str, filename: str=None) -> List[ArchitectureMetric]:
    try:
        tree = ast.parse(code)
    except Exception:
        return []
    
    graph = nx.DiGraph()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            graph.add_node(node.name, type='class')
            for base in node.bases:
                if isinstance(base, ast.Name):
                    graph.add_edge(base.id, node.name)
        elif isinstance(node, ast.FunctionDef):
            graph.add_node(node.name, type='function')
            # for n in ast.walk(node):
            #     if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            #         graph.add_edge(node.name, n.func.id)
    
    dot = nx.nx_agraph.to_agraph(graph).to_string()
    return [ArchitectureMetric(name=filename or "code", dot_diagram=dot)]