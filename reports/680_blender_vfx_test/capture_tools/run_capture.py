from pathlib import Path
import subprocess,sys,hashlib,json,shutil,time,zipfile
root=Path.cwd(); base=root/'._tmp/680_blender_vfx_test/capture'
phase=sys.argv[1] if len(sys.argv)>1 else 'before'
files=subprocess.check_output(['git','ls-files','core','actors','items','skills','world','ui','data','assets/vfx'],text=True).splitlines()
files+=subprocess.check_output(['git','ls-files','--others','--exclude-standard','core','actors','items','skills','world','ui','data','assets/vfx'],text=True).splitlines()
files=sorted(set(n for n in files if Path(n).suffix in ['.gd','.gdshader','.tres','.tscn','.png','.glb','.json','.uid','.import']))
snapshot={'card':680,'phase':phase,'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'capture_script_sha256':hashlib.sha256((base/'capture_blender.gd').read_bytes()).hexdigest(),'source_hashes':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in files}}
(base/(phase+'_source_snapshot.json')).write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if phase!='before':
    before=json.loads((base/'before_source_snapshot.json').read_text(encoding='utf-8'))
    rows=[]; target=base/(phase+'_changed_runtime_originals.zip')
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,digest in snapshot['source_hashes'].items():
            if before['source_hashes'].get(n)==digest: continue
            data=(root/n).read_bytes(); assert hashlib.sha256(data).hexdigest()==digest
            z.writestr(n,data); rows.append({'entry':n,'bytes':len(data),'sha256':digest})
    (base/(phase+'_changed_runtime_zip_manifest.json')).write_text(json.dumps({'archive':target.name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'entries':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
godot=shutil.which('godot')
command=[godot,'--path',str(root),'--fixed-fps','60','--write-movie',str(base/(phase+'.avi')),'--resolution','1280x720','--audio-driver','Dummy','res://._tmp/680_blender_vfx_test/capture/capture_scene.tscn','--','--new','--phase='+phase]
snapshot['command']=command
(base/(phase+'_command.json')).write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
start=time.monotonic()
with (base/(phase+'.raw.log')).open('wb') as out:
    process=subprocess.Popen(command,stdout=out,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    code=process.wait()
elapsed=time.monotonic()-start
(base/(phase+'_completion.json')).write_text(json.dumps({'exit_code':code,'elapsed_seconds':elapsed},indent=2)+'\n')
print(json.dumps({'phase':phase,'exit_code':code,'elapsed':elapsed,'raw_log':str(base/(phase+'.raw.log'))},ensure_ascii=False))
sys.exit(code)
