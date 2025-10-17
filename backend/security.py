import tempfile
import ast
from bandit.core import manager, config, constants
import tempfile
from typing import List
from schemas import SecurityFinding

def scan_code(code: str, filename: str=None) -> List[SecurityFinding]:
    findings: List[SecurityFinding] = []

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py') as tmp:
        tmp.write(code)
        tmp.flush()

        b_conf = config.BanditConfig()
        mgr = manager.BanditManager(b_conf, 'file', verbose=False)
        mgr.discover_files([tmp.name])
        mgr.run_tests()

        for issue in mgr.get_issue_list(sev_level=constants.LOW, conf_level=constants.LOW):
            findings.append(SecurityFinding(
                issue=issue.text, 
                severity=str(issue.severity),
                line=issue.lineno or 0
            ))

    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            # detect eval/exec
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ('eval', 'exec'):
                    findings.append(SecurityFinding(
                        issue=f'Use of {node.func.id}()', 
                        severity='HIGH', 
                        line=node.lineno
                    ))

            # detect os.system or subprocess.* with shell=True
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                func_name = f"{getattr(node.func.value, 'id', '')}.{node.func.attr}"
                if func_name in ('os.system', 'subprocess.call', 'subprocess.Popen'):
                    for kw in getattr(node, "keywords", []):
                        if kw.arg == 'shell' and isinstance(kw.value, "value", False) is True:
                            findings.append(SecurityFinding(
                                issue=f'Use of {func_name} with shell=True - potential command injection', 
                                severity='HIGH', 
                                line=node.lineno
                            ))

            # detect possible hardcoded secrets
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
                val = str(node.value.value).lower()
                if any(keyword in val for keyword in ['password', 'secret', 'token', 'api_key']):
                    findings.append(SecurityFinding(
                        issue='Potential hardcoded secret', 
                        severity='MEDIUM', 
                        line=node.lineno
                    ))

            # detect unsafe HTTP requests
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                func_name = f"{getattr(node.func.value, 'id', '')}.{node.func.attr}"
                if func_name.startswith("requests.") and any(arg for arg in node.args if isinstance(arg, ast.Constant)):
                    url_arg = node.args[0].value if node.args and isinstance(node.args[0], ast.Constant) else ''
                    if isinstance(url_arg, str) and url_arg.startswith('http://'):
                        findings.append(SecurityFinding(
                            issue='Insecure HTTP request (not HTTPS)', 
                            severity='MEDIUM', 
                            line=node.lineno
                        ))

                # detect potential data leakage via print/logging
                for kw in getattr(node, "keywords", []):
                    if kw.arg == "data" and isinstance(kw.value, ast.Dict):
                        for val in kw.value.values:
                            if isinstance(val, ast.Constant) and any(
                                s in str(val.value).lower() for s in ['password', 'secret', 'token', 'apikey']
                            ):
                                findings.append(SecurityFinding(
                                    issue='Potential sensitive data leakage via print/logging', 
                                    severity='LOW', 
                                    line=node.lineno
                                ))

    except Exception as e:
        findings.append(SecurityFinding(issue=f'Error parsing AST: {str(e)}', severity='LOW', line=0))

    return findings