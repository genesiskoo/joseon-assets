# Catalogue data contract v1.0.0

Canonical file: catalog/characters/catalog.json. UTF-8 JSON. Root: schema_version, updated_at, characters, assets, runtime_inventory, issues.

Every assets item has globally unique asset_id, stable character_id and form_id, version_id, display_name, role, runtime_aliases, media_type, file, decision, provenance, runtime and notes.

file: repository (assets/game), repository-relative path, lowercase SHA256, bytes, width/height (null for non-image). Resolve against supplied repository roots, never a worktree absolute path. Original file remains byte-identical. panel is optional and states selected portion of a preserved full board; no whole-board approval inference.

decision: status (unreviewed/recommended/approved/rejected/superseded/unknown), scope array, date, card, evidence array, quote, supersedes array. Scope is independent of runtime. tone approval never implies appearance approval.

runtime: connection (connected/not_connected/definition_only/not_checked), load (success/failed/not_checked), world_display (confirmed/not_confirmed/not_checked), freshness (current/stale/indeterminate), bindings array, evidence array. C owns runtime inventory. Merge inventory into runtime_inventory at root; assets runtime may reference matching bindings without changing decisions. Unchecked is not failure.

Bindings use runtime_id, resource_path, model_id, scene_path, portrait_id and optional variant/tint/attachments/dependencies/fingerprint. Capture metadata is optional capture object with conditions, dependencies, fingerprint, evidence and source_commit. Fingerprint never depends solely on global commit.

provenance: source_card, source_commit, inclusion_reason, tool/backend, prompt file object or null, references ordered array of file objects with role/order. Unknown is null, not reconstructed wording. Exact prompt bytes are preserved.

characters contains character_id, display_name, role, forms [{form_id, display_name, runtime_aliases}]. Gumiho forms human_disguise and true_form share character_id gumiho. Portraits/model renders/captures are separate assets from generated concepts. Runtime aliases are retained across forms.

Viewer must tolerate optional/null metadata. Show independent status axes. file original is immutable; crops and thumbnails must explicitly identify derived_from and crop_rect, and may not impersonate the original.

Final v1 clarifications: preview.derived_from is a full file object, not merely SHA. Every game file object records source_commit so the original blob can be recovered after the path changes. Current game atlas/still originals are repository-relative SHA references; only explicitly derived atlas-frame0/still_rect crops are preserved in media. Runtime inventory contains phase1 bindings (7) and portrait definitions (10); definition_only is preserved from C and never promoted by file existence. Evidence entries can be durable file objects or descriptive strings. Initial pending manifest metadata is historical and subordinate to later PD evidence only for the exact stated scope.
