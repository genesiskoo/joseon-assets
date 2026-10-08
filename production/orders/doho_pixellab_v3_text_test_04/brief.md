# Doho PixelLab V3 Text Test 04

> Director: OpenAI Codex
>
> Generated: 2026-06-07
>
> Status: review

## Goal

Verify the default PixelLab MCP character pipeline with `v3`, high top-down
view, high detail, and eight-direction output.

## PixelLab Job

- Character ID: `66042214-4309-40cb-8d0e-5d638c55ae62`
- Name: `Doho V3 Text High Topdown Test 04`
- Mode: `v3`
- Cost: `3 generations`
- Directions: `8`
- Character size request: `96px`
- Output canvas: `184x184px`
- View: `high top-down`
- Outline: `selective outline`
- Detail: `high detail`

## Prompt

> Joseon fantasy wandering male sword guardian Doho, full-body humanoid pixel
> art character. Signature very wide black gat with a tall cylindrical crown,
> long tied black hair, calm slightly roguish young Korean face. Layered black
> and deep navy-blue dopo robes with subtle bronze talisman patterns, white
> inner collar, dark leather belt with small round jade-blue charm and paper
> talismans. Korean straight sword sheathed at the left waist, one hand resting
> naturally near the hilt. Practical black boots. Neutral idle standing pose,
> readable strong silhouette, no magic effects, no aura, no text, no
> background props. Keep the hat, sword, belt charms, robe layers, and
> navy-black-bronze palette consistent in every direction.

## Result

The v3 result is substantially better than the standard tests in silhouette,
costume readability, scale, and consistency between directions. This test is
the basis for making v3 the default character generation mode.

## Files

```text
raw/
├── south.png
├── south_east.png
├── east.png
├── north_east.png
├── north.png
├── north_west.png
├── west.png
└── south_west.png
```

These are raw review assets. They are not approved for Godot publishing until
alignment, canvas normalization, and visual review are complete.
