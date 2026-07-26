# Sacha Orchestra workspace relocation

> Task ID: `SO-0.1.0-RELOCATE-2026-07-12`  
> Status: New root verified; old empty directory cleanup waiting for source task idle  
> Authorized target: `C:\Users\<user>\Documents\SachaOrchestra`

## Purpose

Remove the organizational `MarketPlace` directory level while preserving the dedicated Sacha Orchestra workspace and its installable plugin payload.

```text
C:\Users\<user>\Documents\MarketPlace\SachaOrchestra
    ->
C:\Users\<user>\Documents\SachaOrchestra
```

The inner `plugins/sacha-orchestra` directory remains unchanged. The repo-local marketplace entry remains relative as `./plugins/sacha-orchestra`.

## Approved scope

- Remove `sacha-orchestra@personal` from the old configured marketplace.
- Remove the old `personal` marketplace registration.
- Move the complete workspace to the authorized target.
- Remove `C:\Users\<user>\Documents\MarketPlace` only after proving it is empty.
- Register the same marketplace from the new root and reinstall the same `0.1.0` plugin.
- Re-run structural, official validator, installation-source, discovery, and read-only SH1 checks required to prove relocation.

No product, Core, Adapter, Skill, Artifact-contract, or version change is authorized. No cachebuster is required solely for path relocation.

## Pre-move evidence

- Source is an ordinary directory, not a link or junction.
- Target did not exist.
- `MarketPlace` contained exactly one child: `SachaOrchestra`.
- Stage 0 Ultra task `019f5492-f179-7c93-ba3b-7bc9a1e45b33` is idle; its last turn completed without error.
- Final `review.md` judgment is `Accept — Stage 0 Foundation accepted` with no entry condition.
- Configured marketplace `personal` resolved to the old workspace root.
- Installed plugin was `sacha-orchestra@personal`, enabled, version `0.1.0`, sourced from the old plugin root.
- Pre-move ordinary file count before this relocation record: `19`.

| Artifact | Pre-move SHA-256 |
| --- | --- |
| `spec.md` | `369038E224BBC4BA6DB43E64523417F42199E86FF596376BAFABAB91694B585F` |
| `execution-report.md` | `F02C530F416A77A6179D97DDDFE7794A342A0D5B83F9C2EACCEAE3703380C268` |
| `review.md` | `8E20E8AE9C46132627141682C8B214C5AF490F355B7D78612A715FAA0943ACA9` |
| `docs/architecture/evolution.md` | `A5996976C6C84E3A25BF699B5EA977A3317967B37B24B1CEA53D368EC2214027` |

## Historical evidence and task continuity

The Stage 0 `spec.md`, `execution-report.md`, and `review.md` remain immutable historical evidence. Their old absolute paths describe the real execution location and are not rewritten.

Existing Ultra and smoke task histories remain at their original task identities and are not mutated. Future work at the new root must reference this relocation record and the accepted Stage 0 task rather than pretending the original task ran at the new path.

## Post-move verification

### Transfer

- A direct root `Move-Item` was attempted from `C:\Users\<user>\Documents`; Windows rejected only the root rename because the active Codex project retained a directory handle. No file moved during that failed attempt.
- The fallback copied every top-level entry to the authorized target and compared all `20` relative file paths and SHA-256 values.
- Copy result: missing `0`; extra `0`; hash mismatch `0`.
- The four frozen Artifact hashes remain identical to the pre-move values above.

### Validation at the new root

- PyYAML `6.0.3` import: exit `0`.
- Planner Skill validator: exit `0`.
- Executor Skill validator: exit `0`.
- Reviewer Skill validator: exit `0`.
- Deprecated `spec-author` Skill validator: exit `0`.
- Plugin validator: exit `0`.
- Marketplace identity: `personal`.
- Relative source path: `./plugins/sacha-orchestra`.
- Plugin identity and version: `sacha-orchestra`, `0.1.0`.

### External registration

- Removed the old installed `sacha-orchestra@personal`; the remaining catalog entry correctly showed `not installed` until the old marketplace was removed.
- Removed the old `personal` marketplace; subsequent marketplace and plugin lists contained zero old entries.
- Added `personal` from `C:\Users\<user>\Documents\SachaOrchestra` with exit `0`.
- Installed `sacha-orchestra@personal` from the new marketplace with exit `0`.
- Final list matched exactly one enabled `0.1.0` plugin at `C:\Users\<user>\Documents\SachaOrchestra\plugins\sacha-orchestra` and zero old-path entries.

### Old-root cleanup state

- Before deleting the old copy, all `20` source and target files were compared again; mismatch count `0`.
- All files and child directories under the old workspace were removed; remaining old-root files `0`, child entries `0`.
- The new-root closeout task rechecked both legacy paths before deletion: both were ordinary directories, neither was a reparse point, the old workspace had immediate items `0` and recursive files `0`, and `MarketPlace` contained exactly that directory with unexpected items `0`. Probe exit `0`; assertion failures `0`.
- Five non-recursive deletion attempts over a short retry window were rejected because source task `019f52d4-f997-7eb0-93b7-dd28dde8c7dc` still held the old workspace directory. Delete command exit `2`; failure count `1`; remaining items stayed `0`. No process was terminated and no force-unlock mechanism was used.
- The two empty legacy directories are the only remaining closeout item. After the source task becomes idle, this task will repeat the same empty ordinary-directory checks, delete the old workspace, then delete the empty `MarketPlace` parent.

## Fresh-context closeout verification

### Supported CLI and installed source

- Resolved the executable Codex desktop runtime CLI and confirmed `codex-cli 0.144.0-alpha.4`; version command exit `0`.
- `plugin marketplace list --help`, `plugin list --help`, `plugin marketplace list`, and `plugin list` each exited `0`; command failure count `0`.
- JSON list commands each exited `0`. Exact assertions found one `personal` marketplace rooted at `C:\Users\<user>\Documents\SachaOrchestra`, one `sacha-orchestra@personal` entry with `installed: true`, `enabled: true`, version `0.1.0`, and source `C:\Users\<user>\Documents\SachaOrchestra\plugins\sacha-orchestra`; old-path hits `0`; assertion failures `0`.

### Discovery and read-only SH1 path

- This fresh context's runtime Skill catalog exposed `sacha-orchestra:planner`, `sacha-orchestra:executor`, and `sacha-orchestra:reviewer`; discovery failures `0`. The installed Executor Skill was loaded for this bounded closeout.
- A read-only probe loaded the three installed formal Role entrypoints plus the workspace Workflow Contract, Artifact Protocol, and Codex Adapter. Installed cache files `13` and source plugin files `13` had missing paths `0`, extra paths `0`, and SHA-256 mismatches `0`; workspace files changed by the probe `0`; probe exit `0`, assertion failures `0`.
- This evidence proves only that the SH1 read/review path is reachable. It does not claim SH2 change self-hosting or SH3 upgrade self-hosting.

### Revalidation before final cleanup retry

- PyYAML `6.0.3` import: exit `0`.
- Marketplace name reader: exit `0`; result `personal`.
- Planner, Executor, Reviewer, and deprecated `spec-author` Skill validators: each exit `0`.
- Plugin validator: exit `0`; official validator failures `0`.
- File-tree probe: exit `0`; ordinary files `20`, directories `20`, reparse points `0`, empty directories `0`.
- Frozen Artifact SHA-256 check: exit `0`; checked `4`, mismatches `0`.
