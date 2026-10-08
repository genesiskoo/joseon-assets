import json, pathlib, subprocess, sys, time, re
sys.stdout.reconfigure(encoding='utf-8')
root = pathlib.Path(__file__).resolve().parents[2]
out = root / '._tmp' / '550'
label = sys.argv[1]
arguments = sys.argv[2:]
if arguments[0] == 'godot':
    command = [r'C:\Program Files (x86)\Steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe', *arguments[1:]]
else:
    command = arguments
started = time.time()
proc = subprocess.run(command, cwd=root, capture_output=True)
(out / (label + '.stdout.raw')).write_bytes(proc.stdout)
(out / (label + '.stderr.raw')).write_bytes(proc.stderr)
text = proc.stdout.decode('utf-8', errors='replace') + proc.stderr.decode('utf-8', errors='replace')
errors = re.findall(r'^.*(?:SCRIPT ERROR|SHADER ERROR|Parse Error|Compile Error|Compilation failed|^\s*(?:USER )?ERROR:).*$', text, re.M)
ignored = [line for line in errors if 'resources still in use at exit' in line]
errors = [line for line in errors if line not in ignored]
result = {'ignored_known_exit_resources': len(ignored), 'exit': proc.returncode, 'seconds': round(time.time()-started, 3), 'error_lines': len(errors), 'command': command, 'raw': str(out)}
(out / (label + '.result.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
if errors or proc.returncode:
    print(text)
else:
    for line in text.splitlines():
        if 'PASS' in line or 'FAIL' in line or '[Test]' in line or 'E2E ' in line or 'TEST ' in line or 'RUNNER ' in line:
            print(line)
sys.exit(proc.returncode or bool(errors))
