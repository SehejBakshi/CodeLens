import ast
from typing import List, Optional
import networkx as nx
from schemas import ArchitectureMetric

def _node_id(prefix: str, name: str) -> str:
    return f"{prefix}_{name.replace('.', '_').replace(' ', '_')}"

def analyze_code(code: str, filename: Optional[str] = None) -> List[ArchitectureMetric]:
    try:
        tree = ast.parse(code)
    except Exception as e:
        dot = f'strict digraph "" {{\n\t// parse error: {str(e)}\n}}\n'
        return [ArchitectureMetric(name=filename or "code", dot_diagram=dot)]

    G = nx.DiGraph()

    module_node = "<module>"
    G.add_node(module_node, type="module", label=module_node)

    imports = {}
    variables = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modname = alias.asname or alias.name
                nid = _node_id("import", modname)
                G.add_node(nid, type="import", label=f"import {modname}")
                G.add_edge(module_node, nid, relation="imports")
                imports[modname] = nid
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            for alias in node.names:
                name = alias.asname or alias.name
                full = f"{base}.{alias.name}" if base else alias.name
                nid = _node_id("import", name)
                G.add_node(nid, type="import", label=f"from {base} import {name}")
                G.add_edge(module_node, nid, relation="imports")
                imports[name] = nid

    for node in tree.body:  # top-level statements only
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    varname = target.id
                    nid = _node_id("var", varname)
                    G.add_node(nid, type="variable", label=varname)
                    G.add_edge(module_node, nid, relation="defines")
                    variables.add(varname)
        elif isinstance(node, ast.AnnAssign):  # annotated assignment
            target = node.target
            if isinstance(target, ast.Name):
                varname = target.id
                nid = _node_id("var", varname)
                G.add_node(nid, type="variable", label=varname)
                G.add_edge(module_node, nid, relation="defines")
                variables.add(varname)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fname = node.name
            nid = _node_id("func", fname)
            G.add_node(nid, type="function", label=fname)
            G.add_edge(module_node, nid, relation="defines_function")
        elif isinstance(node, ast.ClassDef):
            cname = node.name
            nid = _node_id("class", cname)
            G.add_node(nid, type="class", label=cname)
            G.add_edge(module_node, nid, relation="defines_class")

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            call_name = None
            if isinstance(func, ast.Name):
                call_name = func.id
            elif isinstance(func, ast.Attribute):
                base = func.value
                if isinstance(base, ast.Name):
                    call_name = f"{base.id}.{func.attr}"
                else:
                    call_name = func.attr

            if call_name:
                call_nid = _node_id("call", call_name)
                G.add_node(call_nid, type="call", label=call_name)
                parent = getattr(node, "parent", None)
                G.add_edge(module_node, call_nid, relation="calls")

                for imp_name, imp_nid in imports.items():
                    if call_name == imp_name or call_name.startswith(imp_name + "."):
                        G.add_edge(call_nid, imp_nid, relation="calls_import")
    try:
        dot = nx.nx_pydot.to_pydot(G).to_string()
    except Exception:
        lines = ["strict digraph \"\" {"]
        for n, d in G.nodes(data=True):
            label = d.get("label", n)
            lines.append(f'\t"{n}" [label="{label}"];')
        for u, v, d in G.edges(data=True):
            rel = d.get("relation", "")
            if rel:
                lines.append(f'\t"{u}" -> "{v}" [label="{rel}"];')
            else:
                lines.append(f'\t"{u}" -> "{v}";')
        lines.append("}")
        dot = "\n".join(lines)

    return [ArchitectureMetric(name=filename or "code", dot_diagram=dot)]