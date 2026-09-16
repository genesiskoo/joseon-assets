export default async ({project}) => {
  const p = await project({size:"1280x720", fps:24, background:"#000000"});
  const a = await p.add("inputs/A.mp4");
  const b = await p.add("inputs/B.mp4");
  const c = await p.add("inputs/C.mp4");
  p.cut(a,{from:48/24,dur:48/24,at:0,fit:"contain"});
  p.cut(b,{from:0,dur:18/24,at:48/24,fit:"contain"});
  p.cut(b,{from:42/24,dur:30/24,at:66/24,fit:"contain"});
  p.cut(c,{from:18/24,dur:96/24,at:96/24,fit:"contain"});
  if(Math.abs(p.duration()-8)>1e-6) throw new Error("Expected duration 8 seconds");
  const report = await p.render("renders/native.mp4",{depth:8,bitrate:6000000,concurrency:2});
  console.log(JSON.stringify(report));
}
