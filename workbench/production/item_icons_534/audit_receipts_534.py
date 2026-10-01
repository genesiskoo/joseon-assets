"""Read-only credential scan for the exact #534 receipt/production paths."""
import json
import re

from prepare_534 import REPORT, REPO, ROOT, sha, write_json

SECRET_KEY = re.compile(r'^(?:api[_-]?key|authorization|password|secret|access[_-]?token|refresh[_-]?token|cookie|client[_-]?secret)$', re.I)
TOKEN_VALUE = re.compile(r'(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[A-Z0-9]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|Bearer\s+[A-Za-z0-9_.=-]{20,})')
SIGNED_URL = re.compile(r'[?&](?:X-Amz-(?:Signature|Security-Token|Credential)|access_token|api_key|token)=[^\s"&]+', re.I)


def walk(value, location, findings):
    if isinstance(value, dict):
        for key, child in value.items():
            path = location + '/' + key
            if SECRET_KEY.fullmatch(key) and child not in [None, '', False, '<redacted>', 'REDACTED', '***']:
                findings.append(dict(location=path, reason='Credential-bearing JSON field; value not printed'))
            walk(child, path, findings)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk(child, location + f'/{index}', findings)


def main():
    findings, checked = [], []
    roots = [ROOT, REPO / 'reports/534']
    for folder in roots:
        for path in sorted(folder.rglob('*')):
            if path.suffix.lower() not in ['.json', '.txt', '.md', '.py', '.gd', '.ps1'] or '__pycache__' in path.parts:
                continue
            if path.name in ['receipt_audit.json', 'audit_final_stdout.txt']:
                continue
            body = path.read_text(encoding='utf-8-sig')
            relative = path.relative_to(REPO).as_posix()
            if TOKEN_VALUE.search(body):
                findings.append(dict(location=relative, reason='Credential pattern; value not printed'))
            if SIGNED_URL.search(body):
                findings.append(dict(location=relative, reason='Credential-bearing URL query; value not printed'))
            if path.suffix == '.json':
                walk(json.loads(body), relative, findings)
            checked.append(dict(path=relative, sha256=sha(path)))
    result = dict(card=534, roots=[folder.relative_to(REPO).as_posix() for folder in roots],
                  status='PASS' if not findings else 'FAIL', checked_text_files=len(checked),
                  credential_fields_or_tokens_or_signed_urls=len(findings), checked=checked,
                  findings=findings, secret_values_printed=False)
    write_json(REPORT / 'receipt_audit.json', result)
    assert not findings, 'Credential-like content found; inspect local receipt_audit.json without printing values'
    print(f'PASS #534 receipt audit: {len(checked)} exact-card text/JSON files; credential fields/tokens/signed URLs0; values not printed')


if __name__ == '__main__':
    main()
