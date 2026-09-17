extends SceneTree
func _init():
	var doc=GLTFDocument.new()
	var state=GLTFState.new()
	doc.append_from_file("C:/workspace/joseon/assets/models/doho/doho.glb",state)
	var scene=doc.generate_scene(state)
	var ap=scene.find_children("*","AnimationPlayer",true,false)[0]
	var names=ap.get_animation_list()
	var clips={}
	for n in names: clips[n]=ap.get_animation(n).duplicate(true)
	for lib in ap.get_animation_library_list():ap.remove_animation_library(lib)
	for n in names:
		var lib=AnimationLibrary.new()
		lib.add_animation(n,clips[n])
		ap.add_animation_library("",lib)
		var st=GLTFState.new()
		var d=GLTFDocument.new()
		d.append_from_scene(scene,st)
		d.write_to_filesystem(st,"C:/workspace/joseon/tmp/doho_tailored_rig/source_"+n+".glb")
		ap.remove_animation_library("")
	print(names)
	scene.free()
	quit()
