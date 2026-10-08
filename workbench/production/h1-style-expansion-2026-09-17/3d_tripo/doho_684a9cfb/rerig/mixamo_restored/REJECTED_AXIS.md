# Rejected axis experiment

rejected_axis_doho_mixamo25_walk_attack.glb is a reproduced failed experiment. The original FBX Armature transform was not applied before the existing retarget tool, causing a 90-degree lying-down pose. Do not use it. canonical_rig_transform.py creates a separate rig copy with applied rotation/scale, allowing correct upright rest-space retargeting. Original restored rig is unchanged.
