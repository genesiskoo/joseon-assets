#!/usr/bin/env python3
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image

spec=importlib.util.spec_from_file_location('viewer',Path(__file__).with_name('build_catalogue.py'))
viewer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(viewer)

class ViewerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        Image.new('RGB',(300,180),(110,90,80)).save(self.root/'source.png')
        self.file={'repository':'assets','path':'source.png','sha256':hashlib.sha256((self.root/'source.png').read_bytes()).hexdigest(),'width':300,'height':180,'bytes':(self.root/'source.png').stat().st_size}
        self.asset={'asset_id':'card742-h01','character_id':'doho','form_id':'human','version_id':'742-h01','display_name':'H01 추천','role':'player','runtime_aliases':['doho'],'media_type':'concept_board','file':self.file,'decision':{'status':'recommended','scope':['tone'],'evidence':[]},'provenance':{'references':[]},'runtime':{'connection':'not_checked','load':'not_checked','world_display':'not_checked','freshness':'indeterminate','bindings':[]},'panel':{'selection':'H01','crop_rect':[20,10,100,160]}}
        self.roots={'assets':self.root,'game':self.root}
        self.catalog={'schema_version':'1.0.0','characters':[{'character_id':'doho','display_name':'도호','role':'player','forms':[{'form_id':'human','display_name':'인간','runtime_aliases':['doho']}]}],'assets':[self.asset],'runtime_inventory':{'bindings':[{'runtime_id':'doho','model_id':'doho','connection':'connected','load':'not_checked','world_display':'not_checked','definition_config':'raw config'}]}}
    def test_read_only_crop_and_independent_status(self):
        before=copy.deepcopy(self.catalog)
        data,_=viewer.normalise(self.catalog,self.roots,480,60,True,self.root,'file:///stable/index.html')
        group=data['groups'][0]
        self.assertEqual(group['runtime']['connection'],'connected')
        self.assertEqual(group['runtime']['world_display'],'not_checked')
        self.assertEqual(group['assets'][0]['decision']['status'],'recommended')
        self.assertEqual(group['assets'][0]['preview']['crop_rect'],[20,10,100,160])
        self.assertEqual(group['assets'][0]['preview']['width'],100)
        self.assertIn('definition_config_sha256',group['runtime']['bindings'][0])
        self.assertNotIn('definition_config',group['runtime']['bindings'][0])
        self.assertEqual(before,self.catalog)
    def test_paths_hash_and_crop_rejected(self):
        for change in [{'path':'../escape.png'},{'path':str((self.root/'source.png').resolve())},{'sha256':'0'*64}]:
            a=copy.deepcopy(self.asset);a['file'].update(change)
            with self.assertRaises(ValueError): viewer.preview(a,self.roots,100,50,True,self.root,'',[])
        a=copy.deepcopy(self.asset);a['panel']['crop_rect']=[0,0,400,200]
        with self.assertRaises(ValueError): viewer.preview(a,self.roots,100,50,True,self.root,'',[])
    def test_missing_file_and_unmeasured_panel(self):
        a=copy.deepcopy(self.asset);a['file']['path']='missing.png'
        self.assertIsNone(viewer.preview(a,self.roots,100,50,True,self.root,'',[])['src'])
        a=copy.deepcopy(self.asset);a['panel']={'selection':'H01','position':'left'}
        self.assertIsNone(viewer.crop_rectangle(a))
    def test_fragment_inert_json_and_budget(self):
        self.catalog['assets']=[dict(copy.deepcopy(self.asset),asset_id=f'742-h01-{i}') for i in range(40)]
        data,_=viewer.normalise(self.catalog,self.roots,220,40,True,self.root,'file:///stable/index.html')
        data['groups'][0]['name']='</script><script>bad()</script>'
        html=viewer.fragment(data)
        self.assertLess(len(html.encode()),950000)
        self.assertNotIn('<!doctype',html.lower())
        self.assertNotIn('<head>',html)
        self.assertNotIn('fetch(',html)
        self.assertNotIn('</script><script>bad()',html)
    def test_checked_status_not_erased(self):
        status={'connection':'connected','load':'success','world_display':'confirmed','freshness':'current'}
        viewer.merge_status(status,{'connection':'not_checked','load':'not_checked','world_display':'not_checked','freshness':'indeterminate'})
        self.assertEqual(status['load'],'success')
        viewer.merge_status(status,{'load':'failed','freshness':'stale'})
        self.assertEqual(status['load'],'failed')
        self.assertEqual(status['freshness'],'stale')

    def test_validation_freshness_only_and_absolute_original(self):
        before=copy.deepcopy(self.catalog)
        report={'capture_checks':[{'asset_id':'card742-h01','freshness':'stale'}],'errors':[],'warnings':[]}
        data,_=viewer.normalise(self.catalog,self.roots,480,60,False,self.root,'file:///stable/index.html',report)
        asset=data['groups'][0]['assets'][0]
        self.assertEqual(asset['runtime']['freshness'],'stale')
        self.assertEqual(asset['decision']['status'],'recommended')
        self.assertEqual(asset['runtime']['load'],'not_checked')
        self.assertTrue(asset['preview']['original_url'].startswith('file:///'))
        self.assertEqual(asset['preview']['original_path'],str((self.root/'source.png').resolve()))
        self.assertEqual(before,self.catalog)
    def test_inventory_definition_only_authority(self):
        self.catalog['assets'][0]['runtime']['connection']='connected'
        self.catalog['runtime_inventory']['bindings'][0]['connection']='definition_only'
        data,_=viewer.normalise(self.catalog,self.roots,220,40,True,self.root,'')
        self.assertEqual(data['groups'][0]['runtime']['connection'],'definition_only')
if __name__=='__main__': unittest.main()


