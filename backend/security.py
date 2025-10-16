import bandit
from bandit.core import manager, config, constants, issue
import tempfile
from typing import List
from schemas import SecurityFinding

def scan_code(code: str, filename: str=None) -> List[SecurityFinding]:
    findings = []
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py') as tmp:
        tmp.write(code)
        tmp.flush()

        b_conf = config.BanditConfig()
        mgr = manager.BanditManager(b_conf, 'file', verbose=False)

        mgr.discover_files([tmp.name])
        mgr.run_tests()

        for issue in mgr.get_issue_list(sev_level=constants.LOW, conf_level=constants.LOW):
            findings.append(SecurityFinding(issue=issue.text, severity=issue.severity))


    # Additional naive heuristics
    if 'eval(' in code:
        findings.append(SecurityFinding(issue='Use of eval()', severity='HIGH'))
    if 'exec(' in code:
        findings.append(SecurityFinding(issue='Use of exec()', severity='HIGH'))
    if 'password' in code.lower() or 'secret' in code.lower():
        findings.append(SecurityFinding(issue='Potential hardcoded secret', severity='MEDIUM'))


    return findings