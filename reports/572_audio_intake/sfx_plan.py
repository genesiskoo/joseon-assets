import pathlib,json,re
root=pathlib.Path('C:/workspace/joseon');out=root/'tmp/audio572'
aliases={'sword_swing':['sword_air'],'hit':['flesh_hit'],'hit_crit':['critical_hit'],'hit_crit_low':['critical_hit'],'talisman_throw':['talisman_paper'],'seal_release':['seal_unbind'],'portal_open':['portal'],'portal_use':['portal'],'pickup_coin':['coin'],'pickup':['equip'],'enemy_attack':['monster_attack'],'enemy_die':['monster_death']}
descriptions={
'hit_crit_low':'One low compact blunt critical sword impact, firm fleshy thud, controlled bass',
'hit_crit':'One compact heavy critical sword strike, crisp steel snap and firm fleshy thud',
'waypoint_wake':'An ancient stone waypoint awakens, small resonant bronze chime and airy stone resonance',
'waypoint_use':'A brief airy spatial passage with a soft low bronze chime',
'stairs':'A short leather boot step across a stone threshold then faint hollow movement',
'revive':'A quiet inhalation and restrained airy life returning shimmer',
'level_up':'A satisfying short traditional Korean bronze bell reward accent, no melody',
'doho_levelup':'One confident adult Korean male relieved exhalation, no words',
'drop':'One small leather equipment bundle falls onto stone with a dull compact thud',
'boss_heukrang_attack':'A large spectral wolf makes one aggressive guttural short attack growl',
'boss_die':'A large monstrous wolf dies with a deep fading growl and final breath',
'body_fall':'A heavy body collapses onto dry stone, one soft dense thud',
'blood_splat':'A brief close wet blood spatter, compact moist slap',
'bisect':'A decisive heavy blade slices thick flesh, brief tearing and dense wet impact',
'bat_attack':'One large cave bat attacks with leathery wing snap and tiny squeak',
'bandit_attack':'One adult male bandit exertion grunt, no words, dry close',
'burn':'A compact small flame ignition and brief natural crackle',
'boss_roar':'A terrifying huge spectral wolf deep brief roar, restrained bass',
'combo_3':'A small crisp steel accent marking a three-hit sword combo, no melody',
'combo_5':'A weighty short steel snap marking a five-hit sword combo, no melody',
'combo_8':'A forceful short steel crack with compact low thud marking a sword combo',
'doho_die':'One adult Korean male death gasp and final fading exhale, no words',
'doho_hurt':'One adult Korean male brief restrained pain grunt, no words',
'doho_kiai':'One adult Korean male energetic martial arts exertion grunt, no words',
'whiff':'A light rapid sword whoosh through empty air, no impact',
'talisman_master_attack':'A sinister adult male short attack exertion grunt with paper snap, no words',
'soul_scatter':'A spirit disperses into a thin airy hiss and faint ceramic-like crackle',
'skill_whirl_impact':'A compact circular sword hit, crisp dense flesh thud and brief steel edge',
'skill_slash_impact':'A strong sweeping sword impact, short close heavy flesh thud',
'skill_dash_strike_impact':'A rushing sword thrust enters a monster body, compact sharp wet thud',
'shoot':'A short wooden bow release, taut string snap and swift arrow whoosh',
'shatter':'A frozen monster body shatters with a compact icy crack and few fragments',
'player_hurt':'One adult male swordsman restrained brief pain grunt, no words',
'player_die':'One adult male swordsman brief final gasp and fading breath, no words',
'kill_extra':'A dense brief sword finishing impact into flesh, dry wet thud',
'freeze':'A small localized ice frost burst, sharp crisp crack with tiny icy tail',
'enemy_hurt':'One dark fantasy beast brief low pain growl, no words',
'enemy_die':'One dark fantasy beast dies, short subdued fading growl and breath',
'ui_close':'One old wooden chest lid gently shuts with soft latch click',
}
files=sorted((root/'assets/audio/sfx').rglob('*.wav')); grouped={}
for f in files:grouped.setdefault(re.sub(r'_\d+$','',f.stem),[]).append(str(f.relative_to(root)))
selection={};batch=[]
for cue,targets in grouped.items():
 candidates=[]
 for b in [567,566,559]:
  for alias in [cue]+aliases.get(cue,[]):
   for meta in (root/f'tmp/audio{b}/sfx'/alias).glob('*_v*.json'):
    j=json.loads(meta.read_text(encoding='utf-8'));raw=j.get('clean',{}).get('raw',{})
    if raw.get('clipped',1)==0 and meta.with_suffix('.wav').exists():candidates.append(str(meta.with_suffix('.wav')))
 selection[cue]={'targets':targets,'candidates':candidates}
 if not candidates:
  desc=descriptions.get(cue) or next((x['prompt'] for x in json.loads((root/'tmp/audio559/sfx_batch.json').read_text()) if x['cue']==cue),None)
  assert desc, cue
  sec=1.4 if cue in ['boss_die','player_die','doho_die','enemy_die','revive','waypoint_wake'] else 1.0 if 'boss' in cue or cue=='level_up' else .6
  batch.append(dict(cue=cue,n=2,seconds=sec,prompt=desc+'. One isolated close game effect, moderate intensity, clean unclipped recording, no music, no speech, no long reverberation.',influence=.3))
(out/'sfx_selection.json').write_text(json.dumps(selection,indent=2),encoding='utf-8')
(out/'sfx_batch.json').write_text(json.dumps(batch,indent=2),encoding='utf-8')
print('SFX_PLAN',len(grouped),'cues',len(files),'existing files;',sum(bool(x['candidates']) for x in selection.values()),'cues reused;',len(batch),'cues need generation',sum(x['n'] for x in batch),'clips')
