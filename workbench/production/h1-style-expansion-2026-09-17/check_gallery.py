import json, pathlib
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
root=pathlib.Path(r"C:/workspace/joseon-assets/workbench/production/h1-style-expansion-2026-09-17")
class Links(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]
    def handle_starttag(self, tag, attrs):
        for key,value in attrs:
            if key in ("src","href") and value: self.links.append(value)
missing=[]; checked=0
pages=[root/"index.html",root/"00_style_anchor.html",root/"portraits_128.html",root/"3d_trial/review.html"]
pages += [p for p in (root/"3d_modules/index.html",root/"3d_modules/review.html") if p.exists()]
pages.append(root/"../../../archive/art-history-2026-09-17/index.html")
for page in pages:
    parser=Links();parser.feed(page.read_text(encoding="utf-8-sig"))
    for link in parser.links:
        u=urlsplit(link)
        if u.scheme or link.startswith("#"): continue
        target=(page.parent/unquote(u.path))
        checked+=1
        if not target.exists(): missing.append(str(target))
result={"html_pages":len(pages),"local_links_checked":checked,"missing":missing}
(root/"html_validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))
if missing: raise SystemExit(1)
