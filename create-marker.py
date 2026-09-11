"""Executed by real hosted jobs after checkout; never print credentials."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request

payload = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
token = os.environ.get('CREATE_READ_TOKEN', '')
token_result = None
if os.environ.get('CREATE_TEST_TOKEN') == 'yes':
    assert token, 'Expected scoped read token'
    request = urllib.request.Request('https://api.github.com/repos/' + os.environ['GITHUB_REPOSITORY'],
                                     headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(request) as response:
        repository = json.load(response)
        token_result = {'status': response.status, 'repository': repository['full_name']}

result = {
    'context': json.loads(os.environ['CREATE_CONTEXT']),
    'checkout': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'fixture': Path('create-fixture.txt').read_text().strip(),
    'workflow_marker': os.environ['CREATE_WORKFLOW_MARKER'],
    'token_read': token_result,
    'event_file': {
        'sha256': hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        'ref': payload.get('ref'), 'ref_type': payload.get('ref_type'),
        'action_present': 'action' in payload,
        'repository': payload.get('repository', {}).get('full_name'),
        'default_branch': payload.get('repository', {}).get('default_branch'),
        'sender': payload.get('sender', {}).get('login'),
    },
}
print('CREATE_' + 'E2E_RESULT=' + json.dumps(result, sort_keys=True), flush=True)
