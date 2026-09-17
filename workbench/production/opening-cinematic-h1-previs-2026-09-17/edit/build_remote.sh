#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/user/joseon-h1-previs-v001
P="$ROOT/project"
mkdir -p "$P/inputs" "$P/renders"
export P
python3 - <<'PY'
import concurrent.futures, urllib.request, os, json
items=[{"filename":"H01.mp4","url":"https://d8j0ntlcm91z4.cloudfront.net/user_3B5zywdwiIrmBJfbwnbi8b1onpk/hf_20260917_092505_33b9b649-c37f-4be3-9919-d9273c327035.mp4"},{"filename":"H02.mp4","url":"https://d8j0ntlcm91z4.cloudfront.net/user_3B5zywdwiIrmBJfbwnbi8b1onpk/hf_20260917_092505_ddba1817-5a67-4ebe-834a-4636e64fa617.mp4"},{"filename":"H03.mp4","url":"https://d8j0ntlcm91z4.cloudfront.net/user_3B5zywdwiIrmBJfbwnbi8b1onpk/hf_20260917_092505_38bf752c-39aa-4f5c-8e96-67d386dbe9ce.mp4"},{"filename":"H04.mp4","url":"https://d8j0ntlcm91z4.cloudfront.net/user_3B5zywdwiIrmBJfbwnbi8b1onpk/hf_20260917_093229_629d73eb-6c39-4d0b-a95d-9fc35c8da43d.mp4"},{"filename":"H05A.mp4","url":"https://d8j0ntlcm91z4.cloudfront.net/user_3B5zywdwiIrmBJfbwnbi8b1onpk/hf_20260917_093729_43b48a89-f0c0-486b-b03f-dc2489052530.mp4"},{"filename":"H05B.mp4","url":"https://d8j0ntlcm91z4.cloudfront.net/user_3B5zywdwiIrmBJfbwnbi8b1onpk/hf_20260917_093729_c86b6d0e-9b34-4980-b2d2-63b692e70925.mp4"},{"filename":"H06.mp4","url":"https://d8j0ntlcm91z4.cloudfront.net/user_3B5zywdwiIrmBJfbwnbi8b1onpk/hf_20260917_092505_552b2bad-7c7d-4722-8ab0-ba44d3ecd2ef.mp4"},{"filename":"H07.mp4","url":"https://d8j0ntlcm91z4.cloudfront.net/user_3B5zywdwiIrmBJfbwnbi8b1onpk/hf_20260917_093229_a66fd4c2-2a91-4597-b2d2-f7f5c74b41ff.mp4"},{"filename":"H08.mp4","url":"https://d8j0ntlcm91z4.cloudfront.net/user_3B5zywdwiIrmBJfbwnbi8b1onpk/hf_20260917_093229_c8822238-7ed0-4999-b20a-afa63c106a9d.mp4"},{"filename":"H10_r2.mp4","url":"https://d8j0ntlcm91z4.cloudfront.net/user_3B5zywdwiIrmBJfbwnbi8b1onpk/hf_20260917_094621_7c066f65-3211-475c-808a-bd8f86797fe6.mp4"},{"filename":"H09.mp4","url":"https://d8j0ntlcm91z4.cloudfront.net/user_3B5zywdwiIrmBJfbwnbi8b1onpk/hf_20260917_054939_4248a709-d718-4f44-8981-067c4d857d90.mp4"},{"filename":"H12.mp4","url":"https://d2ol7oe51mr4n9.cloudfront.net/user_3B5zywdwiIrmBJfbwnbi8b1onpk/31a7c1a3-89bc-4416-afc1-49aac191ee64.mp4"},{"filename":"temp_soundtrack.mp3","url":"https://d2ol7oe51mr4n9.cloudfront.net/user_3B5zywdwiIrmBJfbwnbi8b1onpk/3a759ddd-dee5-4bfe-af70-1f85d09f5549.mp3"}]
def fetch(item):
    urllib.request.urlretrieve(item["url"],os.environ["P"]+"/inputs/"+item["filename"])
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    list(pool.map(fetch,items))
json.dump(items,open(os.environ["P"]+"/inputs-manifest.json","w"),indent=2)
PY
higgsedit init "$P" --size 1280x720 --fps 24 > "$ROOT/init.log"
higgsedit fonts add "$P" 'Nanum Myeongjo:400' > "$ROOT/fonts.log"
curl -fsSL 'https://raw.githubusercontent.com/google/fonts/main/ofl/nanummyeongjo/NanumMyeongjo-Regular.ttf' -o "$P/fonts/NanumMyeongjo-Regular.ttf"
curl -fsSL 'https://raw.githubusercontent.com/google/fonts/main/ofl/nanummyeongjo/OFL.txt' -o "$P/fonts/OFL-NanumMyeongjo.txt"
python3 - <<'PY'
import os,json
from fontTools.ttLib import TTFont
p=os.environ["P"]
f=p+"/fonts/NanumMyeongjo-Regular.ttf"
font=TTFont(f)
cmap=font.getBestCmap()
text="조선헌터스깊은봉인에금이들더니사람살던못골에도괴질돌고열린문마다빗장걸리네달빛아래꼬리가아홉이라어슬렁"
assert all(ord(c) in cmap for c in text)
j=p+"/project.json"; d=json.load(open(j))
for a in d["assets"]:
    if a.get("kind")=="font" and a.get("fontFace",{}).get("family")=="Nanum Myeongjo":
        a.update(name="fonts/NanumMyeongjo-Regular.ttf",uri="fs:fonts/NanumMyeongjo-Regular.ttf",mimeType="font/ttf",byteSize=os.path.getsize(f))
json.dump(d,open(j,"w"),ensure_ascii=False,indent=2)
PY
cat > "$P/edit.mjs" <<'JS'
// Editable native Higgsedit 0.14 project. All times seconds, at 24 fps.
// Previs: generation sources, authored narration text (no voice), temporary sound.
const EDL = [
  {
    "id": "H01",
    "file": "inputs/H01.mp4",
    "from": 0.5,
    "dur": 4,
    "at": 0
  },
  {
    "id": "H02",
    "file": "inputs/H02.mp4",
    "from": 0.75,
    "dur": 4,
    "at": 4
  },
  {
    "id": "H03",
    "file": "inputs/H03.mp4",
    "from": 0.75,
    "dur": 5,
    "at": 8
  },
  {
    "id": "H04",
    "file": "inputs/H04.mp4",
    "from": 0.75,
    "dur": 4,
    "at": 13
  },
  {
    "id": "H05A",
    "file": "inputs/H05A.mp4",
    "from": 1,
    "dur": 2,
    "at": 17
  },
  {
    "id": "H05B",
    "file": "inputs/H05B.mp4",
    "from": 0.5,
    "dur": 2,
    "at": 19
  },
  {
    "id": "H06",
    "file": "inputs/H06.mp4",
    "from": 0.5,
    "dur": 3,
    "at": 21
  },
  {
    "id": "H07",
    "file": "inputs/H07.mp4",
    "from": 0.75,
    "dur": 3,
    "at": 24
  },
  {
    "id": "H08",
    "file": "inputs/H08.mp4",
    "from": 1,
    "dur": 4,
    "at": 27
  },
  {
    "id": "H09",
    "file": "inputs/H09.mp4",
    "from": 0,
    "dur": 8,
    "at": 31
  },
  {
    "id": "H10",
    "file": "inputs/H10_r2.mp4",
    "from": 0.5,
    "dur": 4,
    "at": 39
  },
  {
    "id": "H12",
    "file": "inputs/H12.mp4",
    "from": 0,
    "dur": 3,
    "at": 47
  }
];
const CAPTIONS = [
  {
    "text": "깊은 봉인에 금이 들더니.",
    "at": 0.5,
    "dur": 3
  },
  {
    "text": "사람 살던 못골에도—",
    "at": 4.25,
    "dur": 3.5
  },
  {
    "text": "괴질이 돌고,\n열린 문마다 빗장이 걸리네.",
    "at": 8.5,
    "dur": 8
  },
  {
    "text": "달빛 아래 꼬리가 아홉이라.",
    "at": 17.25,
    "dur": 2.75
  },
  {
    "text": "고개 너머 갓 하나 넘어오니—",
    "at": 27.25,
    "dur": 3.5
  },
  {
    "text": "어슬렁어슬렁, 못골로 들어서더라.",
    "at": 39.25,
    "dur": 3.5
  }
];
export default async ({ project, text, rect }) => {
 const p = await project({size:"1280x720",fps:24,background:"#070b11"});
 for (const s of EDL) { const h = await p.add(s.file); p.cut(h,{from:s.from,dur:s.dur,at:s.at,fit:"contain"}); }
 const fade = (dur,max=1,enter=.25,exit=.25) => [{property:"opacity",keyframes:[{at:0,value:0,easing:"linear"},{at:enter,value:max,easing:"linear"},{at:dur-exit,value:max,easing:"linear"},{at:dur,value:0}]}];
 for (const c of CAPTIONS) {
  const two = c.text.includes("\n");
  p.compose([
    rect({x:0,y:two?570:604,width:1280,height:two?150:116,fill:"#05070b",animate:fade(c.dur,.36)}),
    text(c.text,{x:90,y:two?583:621,width:1100,height:two?102:62,fontFamily:"Nanum Myeongjo",fontSize:34,fontWeight:400,lineHeight:1.28,align:"center",color:"#f0e6d2",strokeColor:"#11141a",strokeWidth:1,shadow:{x:0,y:2,blur:5,color:"#000000"},animate:fade(c.dur)})
  ],{at:c.at,dur:c.dur,name:"saseol-"+c.at});
 }
 p.compose([
  rect({width:1280,height:720,fill:"#080c13"}),
  rect({x:530,y:266,width:220,height:1,fill:"#756447",animate:fade(4,.8,.6,.4)}),
  text("조선헌터스",{x:100,y:294,width:1080,height:116,fontFamily:"Nanum Myeongjo",fontSize:88,fontWeight:400,lineHeight:1.15,align:"center",color:"#dfcba4",animate:fade(4,1,.6,.4)}),
  text("JOSEON HUNTERS",{x:100,y:414,width:1080,height:42,fontFamily:"Nanum Myeongjo",fontSize:23,fontWeight:400,align:"center",color:"#a4947b",animate:fade(4,.9,.6,.4)})
 ],{at:43,dur:4,name:"title"});
 p.compose(rect({width:1280,height:720,fill:"#000000",animate:[{property:"opacity",keyframes:[{at:0,value:1},{at:.35,value:0}]}]}),{at:0,dur:.35,name:"opening-fade"});
 p.compose(rect({width:1280,height:720,fill:"#000000",animate:[{property:"opacity",keyframes:[{at:0,value:0},{at:.25,value:1}]}]}),{at:42.75,dur:.25,name:"into-title"});
 p.compose(rect({width:1280,height:720,fill:"#000000",animate:[{property:"opacity",keyframes:[{at:0,value:1},{at:.5,value:0}]}]}),{at:47,dur:.5,name:"into-current-game"});
 await p.add("inputs/temp_soundtrack.mp3");
 const doc=await p.read();
 if (Math.abs(p.duration()-50)>.00001) throw new Error("Expected 50-second picture timeline");
};

JS
cat > "$P/edl.json" <<'JSON'
{
  "EDL": [
    {
      "id": "H01",
      "file": "inputs/H01.mp4",
      "from": 0.5,
      "dur": 4,
      "at": 0
    },
    {
      "id": "H02",
      "file": "inputs/H02.mp4",
      "from": 0.75,
      "dur": 4,
      "at": 4
    },
    {
      "id": "H03",
      "file": "inputs/H03.mp4",
      "from": 0.75,
      "dur": 5,
      "at": 8
    },
    {
      "id": "H04",
      "file": "inputs/H04.mp4",
      "from": 0.75,
      "dur": 4,
      "at": 13
    },
    {
      "id": "H05A",
      "file": "inputs/H05A.mp4",
      "from": 1,
      "dur": 2,
      "at": 17
    },
    {
      "id": "H05B",
      "file": "inputs/H05B.mp4",
      "from": 0.5,
      "dur": 2,
      "at": 19
    },
    {
      "id": "H06",
      "file": "inputs/H06.mp4",
      "from": 0.5,
      "dur": 3,
      "at": 21
    },
    {
      "id": "H07",
      "file": "inputs/H07.mp4",
      "from": 0.75,
      "dur": 3,
      "at": 24
    },
    {
      "id": "H08",
      "file": "inputs/H08.mp4",
      "from": 1,
      "dur": 4,
      "at": 27
    },
    {
      "id": "H09",
      "file": "inputs/H09.mp4",
      "from": 0,
      "dur": 8,
      "at": 31
    },
    {
      "id": "H10",
      "file": "inputs/H10_r2.mp4",
      "from": 0.5,
      "dur": 4,
      "at": 39
    },
    {
      "id": "H12",
      "file": "inputs/H12.mp4",
      "from": 0,
      "dur": 3,
      "at": 47
    }
  ],
  "CAPTIONS": [
    {
      "text": "깊은 봉인에 금이 들더니.",
      "at": 0.5,
      "dur": 3
    },
    {
      "text": "사람 살던 못골에도—",
      "at": 4.25,
      "dur": 3.5
    },
    {
      "text": "괴질이 돌고,\n열린 문마다 빗장이 걸리네.",
      "at": 8.5,
      "dur": 8
    },
    {
      "text": "달빛 아래 꼬리가 아홉이라.",
      "at": 17.25,
      "dur": 2.75
    },
    {
      "text": "고개 너머 갓 하나 넘어오니—",
      "at": 27.25,
      "dur": 3.5
    },
    {
      "text": "어슬렁어슬렁, 못골로 들어서더라.",
      "at": 39.25,
      "dur": 3.5
    }
  ],
  "duration": 50,
  "fps": 24
}
JSON
cd "$P"
higgsedit build edit.mjs > renders/build.log 2>&1
AID=$(jq -r '.assets[]|select(.kind=="audio")|.id' project.json)
test -n "$AID"
higgsedit do . place --assetId "$AID" --at 0 --duration 50 > renders/audio-place.log
higgsedit check . > renders/check.log
higgsedit render . --workers 2 --depth 8 --bitrate 5M --out renders/joseon_h1_opening_previs_50s_v001.mp4 > renders/render.log 2>&1
ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames,sample_rate,channels:format=duration,size -of json renders/joseon_h1_opening_previs_50s_v001.mp4 > renders/probe.json
ffmpeg -hide_banner -v error -i renders/joseon_h1_opening_previs_50s_v001.mp4 -f null -
higgsedit sheet . --times 2,6,10.5,15.5,18.5,20.5,22.5,25.5,30,35.75,41,45,48.5 --out renders/review.png --cols 3 > renders/sheet.log 2>&1
python3 - <<'PY'
import json,os,hashlib
from fractions import Fraction
p=json.load(open("renders/probe.json"))
v=[x for x in p["streams"] if x["codec_type"]=="video"][0]
a=[x for x in p["streams"] if x["codec_type"]=="audio"]
assert(v["width"],v["height"])==(1280,720),p
assert Fraction(v["r_frame_rate"])==24,p
assert int(v["nb_frames"])==1200,p
assert len(a)==1 and a[0]["channels"]==2,p
assert abs(float(p["format"]["duration"])-50)<1/24,p
audit={"probe":p,"native_renderer":"higgsedit 0.14.0","full_decode":"passed","duration_target":50,"frame_target":1200,"caption_font":"full Nanum Myeongjo Regular TTF (OFL); Hangul cmap checked","inputs":[{"name":f,"sha256":hashlib.sha256(open("inputs/"+f,"rb").read()).hexdigest()} for f in sorted(os.listdir("inputs"))],"review_scope":"native contact frames and technical verification; normal-speed perceived performance not yet assessed"}
json.dump(audit,open("renders/render-audit.json","w"),ensure_ascii=False,indent=2)
print(json.dumps(audit["probe"]))
PY
cp renders/render-audit.json build-info.json
cat > README.txt <<'TXT'
JOSEON HUNTERS — H1 opening previs v001
50 seconds / 1280x720 / 24fps. Review candidate, not game import.
Sources: Seedance 2.5, existing 8s H1 Doho r3, actual current GT1 Godot runtime capture.
Temporary original procedural music/Foley; no voice. Not final Korean music recording.
Edit native script edit.mjs. Fonts and inputs are portable.
To rebuild: higgsedit build edit.mjs ; place the audio asset once at 0 for 50 seconds ; higgsedit render .
Building replaces the timeline. Do not repeat audio place on an existing built timeline.
Title 43-47s; actual prototype game 47-50s. No implemented input/dialogue handoff.
TXT
cd "$ROOT"
zip -qr joseon_h1_opening_previs_50s_v001_project.zip project -x 'project/renders/*'
echo LOCAL_RENDER_COMPLETE

