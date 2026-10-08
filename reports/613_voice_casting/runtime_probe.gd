extends SceneTree

var _done := false

func _process(_delta: float) -> bool:
	if not _done:
		_done = true
		_probe()
	return false

func _probe() -> void:
	var audio := root.get_node("Audio")
	var manifest = JSON.parse_string(FileAccess.get_file_as_string("res://docs/design/audio_cast_613.json"))
	var count := 0
	for row in manifest.lines:
		var id: String = row.id
		var stream = load("res://assets/audio/voice/%s.wav" % id)
		if stream == null or stream.get_length() <= 0.0:
			push_error("VOICE_RESOURCE_FAIL " + id)
			quit(1)
			return
		if not audio.play_voice(id) or audio.voice_id != id:
			push_error("VOICE_PLAY_FAIL " + id)
			quit(1)
			return
		count += 1
	audio.stop_voice()
	if audio.voice_playing() or audio.voice_id != "":
		push_error("VOICE_STOP_FAIL")
		quit(1)
		return
	print("CAST613_ENGINE_PASS resources=", count, " play_id=", count, " stop=PASS")
	audio._voice.stream = null
	# Give the audio mixer time to release playback handles after the batch of stop calls.
	await create_timer(0.5).timeout
	quit(0)
