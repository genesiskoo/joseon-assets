"""Local preview of the H1 gallery and its explicitly archived art only."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
ARCHIVE = REPO / 'archive/art-history-2026-09-17'
H1_PREFIX = '/workbench/production/h1-style-expansion-2026-09-17/'
ARCHIVE_PREFIX = '/archive/art-history-2026-09-17/'

class GalleryHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        route = unquote(urlsplit(path).path)
        if route.startswith(ARCHIVE_PREFIX):
            base, suffix = ARCHIVE, route[len(ARCHIVE_PREFIX):]
        elif route.startswith(H1_PREFIX):
            base, suffix = ROOT, route[len(H1_PREFIX):]
        else:
            base, suffix = ROOT, route.lstrip('/')
        candidate = (base / suffix).resolve()
        if not candidate.is_relative_to(base.resolve()) or any(part.startswith('.') for part in Path(suffix).parts):
            return str(ROOT / '__unavailable__')
        return str(candidate)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8769)
    args = parser.parse_args()
    ThreadingHTTPServer(('127.0.0.1', args.port), GalleryHandler).serve_forever()
