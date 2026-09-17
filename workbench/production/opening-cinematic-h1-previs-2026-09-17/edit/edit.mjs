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

