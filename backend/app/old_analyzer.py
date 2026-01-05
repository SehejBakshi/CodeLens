import ast
from typing import List
import networkx as nx

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

    functions, classes = set(), set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            graph.add_node(node.name, type='class')
            classes.add(node.name)

            for base in node.bases:
                if isinstance(base, ast.Name):
                    graph.add_edge(base.id, node.name, relation='inherits')
        
        elif isinstance(node, ast.FunctionDef):
            graph.add_node(node.name, type='function')
            functions.add(node.name)
            for n in ast.walk(node):
                if isinstance(n, ast.Call):
                    if isinstance(n.func, ast.Name):
                        graph.add_edge(node.name, n.func.id, relation='calls')
                    elif isinstance(n.func, ast.Attribute):
                        graph.add_edge(node.name, n.func.attr, relation='calls')

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in functions:
                graph.add_edge("<module>", node.func.id, relation='calls')
            elif isinstance(node.func, ast.Attribute) and node.func.attr in functions:
                graph.add_edge("<module>", node.func.attr, relation='calls')
    
    dot = nx.nx_agraph.to_agraph(graph).to_string()
    return [ArchitectureMetric(name=filename or "code", dot_diagram=dot)]