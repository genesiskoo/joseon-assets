// landing-sections.jsx — 조선헌터스 랜딩 섹션 컴포넌트 + 콘텐츠
const { useState: useStateL, useEffect: useEffectL, useRef: useRefL } = React;

/* ── 콘텐츠 데이터 ─────────────────────────────────── */
const FEATURES = [
  { hanja:"自由", title:"자유 이동 핵앤슬래시", icon:"slash",
    desc:"그리드의 시대는 끝났다. 마우스를 누르고 있으면 도호가 알아서 베어 넘긴다. 향수 어린 픽셀 룩 위에, 묵직한 학살의 손맛을 얹었다.",
    chips:[["자유 이동",1],["마우스 홀드 자동 연타",1],["3/4 탑다운",0]] },
  { hanja:"道術", title:"부적과 도술검", icon:"talisman",
    desc:"떠돌이 도사의 무기는 칼만이 아니다. 부적을 던지고, 도술을 두르고, 도술검을 휘두른다. 핫키로 즉발하는 도술을 엮어 자신만의 콤보를 만든다.",
    chips:[["핫키 즉발",1],["도술 콤보",1],["부적·도술검",0]] },
  { hanja:"封印", title:"봉인된 던전", icon:"gate",
    desc:"봉인이 풀린 던전은 층마다 다른 요사한 기운을 품는다. 청염이 타오르는 기와 폐허를 내려가 미니보스를 베고, 끝내 봉인 너머의 그것과 마주한다.",
    chips:[["층별 진행",1],["미니보스",1],["봉인 너머의 존재",0]] },
  { hanja:"解封", title:"무한 드롭과 Rare 해금", icon:"loot",
    desc:"Affix + Rarity 3등급. 수만 가지 조합이 바닥에 쏟아진다. 그리고 봉인 끝의 그것을 베어 넘긴 뒤에야 진짜 엔드게임 — Rare 해금이 열린다.",
    chips:[["랜덤 드롭",1],["Affix + Rarity",1],["Rare 해금 엔드게임",0]] },
];

const HUNTERS = [
  { hanja:"道虎", name:"도호", title:"악귀를 베는 수호자 — 떠돌이 도사", img:"art/moba_doho.png", pos:"42% center",
    accent:"var(--gold)", status:"EA 플레이 가능", live:true },
  { hanja:"鬼璽", name:"귀새", title:"가면 뒤에 숨은 칼날", img:"art/moba_gwisae.png", pos:"54% center",
    accent:"var(--crimson)", status:"추후 플레이어블", live:false },
  { hanja:"青淵", name:"청연", title:"책의 길을 잇는 자", img:"art/moba_cheongyeon.png", pos:"60% center",
    accent:"var(--jade)", status:"추후 플레이어블", live:false },
];

const GALLERY = [
  { src:"art/map.png", cap:"청염이 타오르는 봉인 던전 — 기와·부적·도술진", cls:"wide" },
  { src:"art/doho_south.png", cap:"도호 · 흑립과 도포", cls:"pixel" },
  { src:"art/bandit_south.png", cap:"산적 — 외곽 마을의 위협", cls:"pixel" },
  { src:"art/map2.png", cap:"한양 외곽 — 자유롭게 누비는 야외", cls:"wide" },
  { src:"art/wild_dog_east.png", cap:"들개 — 떼지어 덤비는 잡몹", cls:"pixel" },
  { src:"art/mudang_south.png", cap:"무당 할매 — 마을 NPC", cls:"pixel" },
];

/* ── 아이콘 ─────────────────────────────────── */
function Ico({ name }){
  const p = {
    slash:<path d="M5 19L19 5M9 5l10 10M5 9l5 5" />,
    talisman:<g><rect x="7" y="3" width="10" height="18" rx="1"/><path d="M12 7v8M9.5 10h5"/></g>,
    gate:<g><path d="M4 21V8l8-4 8 4v13"/><path d="M4 8h16M9 21v-7h6v7"/></g>,
    loot:<g><path d="M3 8l9-5 9 5-9 5-9-5z"/><path d="M3 8v8l9 5 9-5V8M12 13v8"/></g>,
    steam:<g><circle cx="12" cy="12" r="9"/><circle cx="15" cy="9" r="2.4"/><circle cx="8.5" cy="14.5" r="1.8"/><path d="M10 13.5L13 10.5"/></g>,
    play:<path d="M8 5v14l11-7z" fill="currentColor" stroke="none"/>,
    x:<path d="M4 4l16 16M20 4L4 20" />,
    yt:<g><rect x="3" y="6" width="18" height="12" rx="3"/><path d="M10 9l5 3-5 3z" fill="currentColor" stroke="none"/></g>,
    discord:<path d="M7 8c3-1.5 7-1.5 10 0M7 16c3 1.5 7 1.5 10 0M6 8l-1 8 3 1M18 8l1 8-3 1M9.5 12.5h.01M14.5 12.5h.01"/>,
  }[name];
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">{p}</svg>;
}

/* ── 스크롤 등장 훅 ─────────────────────────────────── */
function useReveal(){
  useEffectL(()=>{
    const io = new IntersectionObserver((es)=>{
      es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold:.12, rootMargin:"0px 0px -8% 0px" });
    document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
    return ()=>io.disconnect();
  });
}

/* ════════════ NAV ════════════ */
function Nav(){
  const [scr,setScr] = useStateL(false);
  useEffectL(()=>{ const f=()=>setScr(window.scrollY>40); f(); window.addEventListener('scroll',f); return ()=>window.removeEventListener('scroll',f); },[]);
  return (
    <nav className={`nav ${scr?'scrolled':''}`}>
      <div className="nav-inner">
        <a className="brand" href="#top">
          <span className="mark">虎</span>
          <span className="bt"><b>조선헌터스</b><span>JOSEON HUNTERS</span></span>
        </a>
        <div className="nav-links">
          <a href="#features">특징</a>
          <a href="#doho">도호</a>
          <a href="#hunters">헌터스</a>
          <a href="#boss">봉인</a>
          <a href="#release">소식</a>
        </div>
        <a className="btn btn-primary btn-sm nav-cta" href="#release">소식 받기</a>
      </div>
    </nav>
  );
}

/* ════════════ HERO ════════════ */
function Hero(){
  const tals = Array.from({length:14});
  return (
    <header className="hero" id="top">
      <div className="hero-art"><img src="art/title.png" alt="조선헌터스 키 아트" /></div>
      <div className="hero-fade"/>
      <div className="hero-scrim"/>
      <div className="talismans">
        {tals.map((_,i)=>(
          <span key={i} className="tal" style={{
            left:`${(i*7.3+4)%97}%`, animationDuration:`${14+(i%6)*3}s`, animationDelay:`${-(i*1.7)}s`,
            transform:`scale(${.7+(i%4)*.25})` }} />
        ))}
      </div>
      <div className="hero-inner">
        <div className="wrap">
          <div className="hero-eyebrow"><span className="eyebrow he">First Look</span> <span className="tbd">가제</span></div>
          <h1>조선헌터스<span className="latin">JOSEON HUNTERS</span></h1>
          <div className="hero-tag">조선의 어둠, 그 너머의 진실을 베어내다
            <span className="latin">Cut through the darkness — to the truth beyond.</span></div>
          <p className="hero-pitch">조선풍 가공 세계. 떠돌이 도사 <b style={{color:'var(--paper)'}}>도호</b>가 봉인된 던전에 잠든 장비를 해방하고, 요괴를 베어내는 탑다운 픽셀 액션 RPG.</p>
          <div className="hero-cta">
            <a className="btn btn-primary btn-lg" href="#features">세계관 살펴보기</a>
            <a className="btn btn-ghost btn-lg" href="#boss">봉인 너머 보기</a>
          </div>
          <div className="hero-meta">
            <div className="m"><div className="mk">Genre</div><div className="mv">픽셀 액션 RPG</div></div>
            <div className="m"><div className="mk">Platform</div><div className="mv">PC · Steam</div></div>
            <div className="m"><div className="mk">Mode</div><div className="mv">싱글 플레이</div></div>
            <div className="m"><div className="mk">Language</div><div className="mv">한 · 영 자막</div></div>
          </div>
        </div>
      </div>
      <a className="scroll-cue" href="#pitch"><span>SCROLL</span><span className="line"/></a>
    </header>
  );
}

/* ════════════ 한 줄 피치 ════════════ */
function PitchBand(){
  return (
    <section className="pitch-band" id="pitch">
      <div className="wrap reveal">
        <p className="big">잊고 있던 <span className="em">그 시절의 픽셀</span>, 손끝이 기억하는 <span className="em">베어내는 손맛</span>.<br/>오래 비어 있던 자리에, 조선풍 핵앤슬래시가 선다.</p>
        <div className="sub">— 떠돌이 도사의 칼끝, 그 특유의 박자 —</div>
      </div>
    </section>
  );
}

/* ════════════ 특징 ════════════ */
function Features(){
  return (
    <section className="section" id="features">
      <div className="wrap">
        <div className="sec-head reveal">
          <span className="eyebrow">Core Loop</span>
          <h2 className="sec-title">핵심은 <span className="em">베고, 줍고, 더 깊이</span> 내려가는 것</h2>
          <p className="sec-lead">MORPG의 느린 진행을 버렸다. 솔로 ARPG의 빠른 손맛만 남겼다.</p>
        </div>
        <div className="feat-grid">
          {FEATURES.map((f,i)=>(
            <article key={i} className={`feat-card reveal d${(i%2)+1}`}>
              <div className="feat-num">{String(i+1).padStart(2,'0')}</div>
              <div className="feat-ico"><Ico name={f.icon}/></div>
              <h3>{f.title}<span className="hanja">{f.hanja}</span></h3>
              <p>{f.desc}</p>
              <div className="vs">{f.chips.map(([c,on],j)=><span key={j} className={`chip ${on?'on':''}`}>{c}</span>)}</div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ════════════ 도호 스포트라이트 ════════════ */
function Doho(){
  return (
    <section className="section" id="doho">
      <div className="wrap">
        <div className="spot">
          <div className="spot-art reveal">
            <div className="glow"/>
            <figure className="stage"><img src="art/doho_v4.png" alt="도호 전신 컨셉 일러스트"/></figure>
          </div>
          <div className="spot-body reveal d1">
            <span className="role">The Wanderer · 도호</span>
            <div className="hanja-big">道虎<small>도호</small></div>
            <p><span className="em">능청맞고 시니컬한 떠돌이 도사.</span> 갈색 도포에 회색 목도리, 흑립을 눌러쓴 채 마을과 던전을 떠돈다. 평소엔 술 한 잔의 여유, 결정적 순간엔 부적과 도술검의 진중함. 능청 뒤에 진심을 감춘, 한 자루의 칼 같은 사람.</p>
            <div className="spot-traits">
              <div className="trait"><div className="tk">Class Color</div><div className="tv">갈색 · 회 · 흑</div></div>
              <div className="trait"><div className="tk">Weapon</div><div className="tv">부적 · 도술검</div></div>
              <div className="trait"><div className="tk">Tone</div><div className="tv">능청 · 진중</div></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ════════════ 헌터스 로스터 ════════════ */
function Hunters(){
  return (
    <section className="section" id="hunters">
      <div className="wrap">
        <div className="sec-head center reveal">
          <span className="eyebrow center">The Hunters</span>
          <h2 className="sec-title">밤을 베는 <span className="em">세 자루의 칼</span></h2>
          <p className="sec-lead">얼리 액세스는 도호 한 사람으로 시작한다. 귀새와 청연은 마을 NPC로 함께하며, 추후 플레이어블로 합류한다.</p>
        </div>
        <div className="roster">
          {HUNTERS.map((h,i)=>(
            <article key={i} className={`hunter reveal d${i+1}`} style={{'--h-accent':h.accent}}>
              <img src={h.img} alt={h.name} style={{objectPosition:h.pos}}/>
              <span className={`status ${h.live?'live':''}`}>{h.status}</span>
              <div className="info">
                <div className="hname">{h.name}<span className="hanja">{h.hanja}</span></div>
                <div className="htitle">{h.title}</div>
                <div className="hbar"/>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ════════════ 봉인 너머 (보스 미스터리) ════════════ */
function Boss(){
  const vid = useRefL(null);
  const [playing,setPlaying] = useStateL(false);
  const toggle = ()=>{ const v=vid.current; if(!v) return; if(v.paused){ v.play(); setPlaying(true);} else { v.pause(); setPlaying(false);} };
  return (
    <section className="section boss" id="boss">
      <div className="wrap">
        <div className="boss-grid">
          <div className="boss-media reveal" onClick={toggle}>
            <video ref={vid} src="art/gumiho_vid.mp4" poster="art/gumiho_40.png" loop muted playsInline preload="metadata"/>
            <span className="frame-tag">SEALED · ???</span>
            <div className={`play ${playing?'hide':''}`}><div className="pbtn"><Ico name="play"/></div></div>
          </div>
          <div className="boss-body reveal d1">
            <span className="eyebrow">The Sealed One</span>
            <h2 className="sec-title">봉인, 그 너머의 <span className="em">무언가</span></h2>
            <p>던전 가장 깊은 곳, 풀려가는 봉인의 끝. <span className="em">어둠 속에서 무언가가 당신을 응시한다.</span> 도호가 마침내 마주서는 그것 — 정체는, 직접 확인하라.</p>
            <div className="boss-end">
              <span className="bk">처치 후</span>
              <span className="bv">그것을 베어 넘긴 순간, 진짜 사냥이 시작된다 — <b style={{color:'var(--paper)'}}>Rare 해금 엔드게임</b>. 봉인 너머에서, 끝없이 변주되는 도전이 열린다.</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ════════════ 갤러리 ════════════ */
function Gallery(){
  return (
    <section className="section" id="gallery">
      <div className="wrap">
        <div className="sec-head reveal">
          <span className="eyebrow">In-Game</span>
          <h2 className="sec-title">픽셀로 되살린 <span className="em">조선의 밤</span></h2>
          <p className="sec-lead">128×128 캔버스 위, 한복과 갓과 기와. 손끝이 기억하는 그 시절의 톤 그대로.</p>
        </div>
        <div className="gallery">
          {GALLERY.map((g,i)=>(
            <figure key={i} className={`gtile reveal ${g.cls} d${(i%4)+1}`}>
              <img src={g.src} alt={g.cap}/>
              <figcaption className="cap">{g.cap}</figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ════════════ 출시 정보 + 최종 CTA ════════════ */
function Release(){
  return (
    <section className="section release" id="release">
      <div className="wrap">
        <div className="sec-head center reveal">
          <span className="eyebrow center">Prologue</span>
          <h2 className="sec-title">정식 공개에 앞서, <span className="em">먼저 펼쳐 보이는 한 장</span></h2>
        </div>
        <div className="fact reveal">
          <div className="f"><div className="fk">Release</div><div className="fv"><span className="accent">Early Access</span></div></div>
          <div className="f"><div className="fk">Price</div><div className="fv"><span className="tbd">미정</span></div></div>
          <div className="f"><div className="fk">Platform</div><div className="fv">PC <small>Steam · Deck</small></div></div>
          <div className="f"><div className="fk">Language</div><div className="fv">한 · 영 <small>자막</small></div></div>
        </div>
        <div className="final-cta reveal">
          <h2>전부를 보일 때는 아직.<br/>다만, <span className="em">서막</span>은 지금 엽니다</h2>
          <p>도호의 칼끝, 봉인된 던전, 그리고 그 너머의 무언가 — 정식 공개에 앞서 세계의 단면을 먼저 펼칩니다.</p>
          <div className="cta-row">
            <a className="btn btn-primary btn-lg" href="#boss">봉인 너머 보기</a>
          </div>
          <div className="wishlist-note reveal">
            <div className="wt">Stay Tuned</div>
            <div className="wd">Steam 페이지와 정식 공개는 준비 중입니다. 소식이 열리면 가장 먼저 전해드리겠습니다.</div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ════════════ FOOTER ════════════ */
function Footer(){
  return (
    <footer className="footer">
      <div className="wrap">
        <div className="footer-top">
          <div>
            <a className="brand" href="#top"><span className="mark">虎</span>
              <span className="bt"><b>조선헌터스</b><span>JOSEON HUNTERS</span></span></a>
            <p className="disclosure" style={{marginTop:'20px'}}>본 작품은 AI 도구를 풀활용한 1인 개발로 제작됩니다. 기획·코드·픽셀·일러스트·번역을 한 사람이 엮어, 작품 한 편을 끝까지 완성하기 위한 파이프라인입니다.</p>
          </div>
        </div>
        <div className="footer-bot">
          <span>© 2026 조선헌터스 · Joseon Hunters. 조선풍 가공 세계 — 시대 고증과 무관한 픽션.</span>
          <span className="latin">MADE BY ONE · POWERED BY AI</span>
        </div>
      </div>
    </footer>
  );
}

Object.assign(window, { Nav, Hero, PitchBand, Features, Doho, Hunters, Boss, Gallery, Release, Footer, useReveal, Ico });
