from pathlib import Path
import py_compile
base=Path('._tmp/672_element_flight_v1')
s=Path('._tmp/634_status_structure_v1/encode_video.py').read_text(encoding='utf-8')
s=s.replace('#634','#672').replace('634_status_structure','672_element_flight').replace('capture_status.gd','capture_flight.gd')
s=s.replace("LABELS=['burn','chill','frozen','sal']", "LABELS=['fire','cold','lightning','sal']")
s=s.replace("['fixture','bounds','combat','capture_script_sha256','fps','speed']", "['fixture','bounds','capture_script_sha256','fps','speed']")
s=s.replace('==37','==47')
s=s.replace("if not args.plan_only:\n    assert 'core/vfx_status.gd' in after['source_hashes']", "if not args.plan_only:\n    assert 'core/vfx_status.gd' in after['source_hashes'] and len(after['source_hashes'])>=148\n    assert after['semantic_combat_invariant_equal']")
s=s.replace("'BEFORE/AFTER full combat exact'", "'launch/setup/RNG-final/damage/MP/belt/radius/native-status exact; flight/hit time intentionally different'")
start=s.index('    name={'); end=s.index('    if compare:',start)
s=s[:start]+'''    name={'fire':'불 부적','cold':'한기 부적','lightning':'벽력 부적','sal':'실제 적 살 구슬'}[label]
    old=before['combat'][label]['shots'][0]['initial_speed']; new=after['combat'][label]['shots'][0]['initial_speed']
    draw.text((20,7),f'#672 원소 비행 | {name} · 최초 관측 속도 {old:g} → {new:g} u/s',font=ImageFont.truetype(FONT,23),fill='white')
'''+s[end:]
s=s.replace('변경 후 · 3D 메시 + 붓결 셰이더','변경 후 · 속성별 움직임 / 탄두 / 후류')
s=s.replace('동일 배우/카메라/피해/상태시계/난수 · 정상1× · A/B는 변경 후 실제 원음 · 기록60fps는 실시간 성능 아님','고정5u / 실제 첫발 격리 · 피해/RNG/소모 동일 · 속도/명중시각 변경 · 정상1× · A/B AFTER 원음')
s=s.replace("'card':634", "'card':672")
s=s.replace("'combat_fields_exact':True", "'combat_fields_exact':False,'semantic_combat_invariant_equal':True,'intentional_timing_changes':after['timing_comparison']")
s=s.replace("'combat_sha256':", "'before_original_combat_sha256':")
s=s.replace("'combat_records':'before_metadata.json", "'after_original_combat_sha256':hashlib.sha256(json.dumps(after['combat'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest(),'combat_records':'before_metadata.json")
s=s.replace("'status_end':'burn/chill/frozen expire at unchanged native duration; sal clears by actual salpuri belt input frame240, first observed frame242'", "'status_end':'fire/cold/sal all expire naturally inside each six-second clip; lightning adds no native status; full ticks/initial duration and hit-relative ticks verified'")
s=s.replace('video634_capture.json','video672_capture.json')
(base/'encode_flight_video.py').write_text(s,encoding='utf-8',newline='\n'); py_compile.compile(str(base/'encode_flight_video.py'),doraise=True)
print('encoder syntax PASS')