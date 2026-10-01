"""Bounded, resumable Cloud queue: never retry a submitted/unknown job."""
import argparse
import json
import time
from pathlib import Path
import comfy_image_production as production

parser = argparse.ArgumentParser()
parser.add_argument('config')
parser.add_argument('labels', nargs='+')
parser.add_argument('--parallel', type=int, default=2)
args = parser.parse_args()
config = json.loads(Path(args.config).read_text(encoding='utf-8'))
specs = {row['id']: row for row in config['jobs']}
assert args.parallel in (1, 2)
assert len(set(args.labels)) == len(args.labels)
assert set(args.labels).issubset(specs)
report = Path(config['report'])
pending = list(args.labels)
active = []
failures = []
while pending or active:
    while pending and len(active) < args.parallel:
        label = pending.pop(0)
        job = report / f'{label}.job.json'
        if not job.exists():
            production.submit(config, specs[label])
        state = json.loads(job.read_text(encoding='utf-8'))
        if state['state'] in ('downloaded', 'failed_recorded', 'rejected_before_queue'):
            if state['state'] != 'downloaded':
                failures.append(label)
            continue
        if not state.get('prompt_id'):
            raise RuntimeError(f'{label}: unknown submission outcome; stop, never resubmit')
        active.append(label)
    if not active:
        continue
    time.sleep(45)
    for label in tuple(active):
        try:
            production.collect(config, specs[label])
        except Exception as error:
            # Keep acknowledged job state. An HTTP challenge is not generation failure.
            print(f'{label}: collection deferred: {error}', flush=True)
            time.sleep(60)
            continue
        state = json.loads((report / f'{label}.job.json').read_text(encoding='utf-8'))
        if state['state'] in ('downloaded', 'failed_recorded', 'rejected_before_queue'):
            active.remove(label)
            if state['state'] != 'downloaded':
                failures.append(label)
    print(f'QUEUE remaining={len(pending)} active={active} terminal_failures={failures}', flush=True)
print(f'COMPLETE labels={len(args.labels)} failures={failures}', flush=True)
raise SystemExit(1 if failures else 0)
