from pathlib import Path
exec(Path(__file__).with_name('implement558.py').read_text(encoding='utf-8').split("write('core/combat_trace.gd'")[0])
edit('actors/player_combat.gd',lambda text: replace(text,
    'TRACE.event("cast_rejected", "PlayerCombat.cast_active", self, {"reason": "cooldown_or_mp"})',
    'TRACE.event("cast_rejected", "PlayerCombat.cast_active", self, {"reason": "cooldown_or_mp", "cooldown_blocked": cooldowns[active_skill] > 0.0, "mp_blocked": mp < cost, "cost": TRACE.exact(cost)})'))
def ps(text):
    text = replace(text,
        '$contains = (($tokens -contains "balance_boss") -or ($tokens -contains "all" -and @($Phase.Skip) -notcontains "balance_boss"))',
        '$contains = ((($tokens -contains "balance_boss") -or ($tokens -contains "all")) -and @($Phase.Skip) -notcontains "balance_boss")')
    anchor = '    $rawFixture = Join-Path $tmp "phase_raw_fixture"'
    text = replace(text,anchor,'''
    $explicitSkipped = Get-E2ePhaseMetadata ([pscustomobject]@{ Arg = "balance_boss"; Skip = @("balance_boss"); Exclusive = $true }) @("--", "--e2e=balance_boss", "--e2e-skip=balance_boss") 0 $true "fake-godot"
    Confirm-That (-not $explicitSkipped.contains_balance_boss) "Explicit balance token also respects actual scenario skip"
''' + anchor)
    return text
edit('tools/test.ps1',ps)
print('558 cast rejection resources and explicit phase skip metadata applied')
