# Sacha Orchestra 0.1.0 Foundation Stage 0 Review

## Review identity and provenance

- Task ID: `SO-0.1.0-BOOTSTRAP-2026-07-12`
- Review role: independent Reviewer
- Review date: `2026-07-12` (`Asia/Shanghai`)
- Scope authority: `spec.md`, SHA-256 `369038E224BBC4BA6DB43E64523417F42199E86FF596376BAFABAB91694B585F`
- Stage/version guardrail: `docs/architecture/evolution.md`, SHA-256 `A5996976C6C84E3A25BF699B5EA977A3317967B37B24B1CEA53D368EC2214027`
- Provenance: this context did not participate in planning or implementation. It independently read the complete Spec, Execution Report, effective Project AGENTS, Core contracts, Codex Adapter, plugin source, metadata, Role Skills, and current CLI state.
- Permitted write used: this `review.md` only. No source, frozen Artifact, report, installation state, cache, global/system file, or other project was changed.

The frozen Spec still says “draft, awaiting approval”. The Execution Report records later Human Conductor approval. This Review treats that recorded approval and the explicit formal-Review delegation as sufficient entry authorization; the stale label is a documentation inconsistency, not a Scope rewrite by Reviewer.

## Current re-review judgment

**Accept — Stage 0 Foundation accepted.**

The evidence-only repair closes the former blocking runtime-evidence gap. The same independent Reviewer used local Codex task search and read every raw turn for the six human-visible task titles listed in the updated Execution Report. The original prompts, installed Role-hit commentary, scoped write, verification results, disclosed invalid probe, contract repair, exact nine-field handoffs, implicit Planner hit, explicit-only deprecated alias behavior, and SH1 claim limits are directly accessible and agree with the real source and previously reconstructed installation state.

This acceptance is limited to Sacha Orchestra **Stage 0**, product/plugin version **`0.1.0` Foundation**, and **Contract Version `1`**. It accepts the installed three-Role Foundation, runtime forward smoke, and SH1 read-only entry reachability. It does not claim Stage 1, SH2, SH3, bounded self-change, automatic orchestration, Manager/Router, complete Hybrid, full self-hosting, production readiness, or product `1.0.0`.

## Initial judgment (superseded; preserved audit trail)

**Reject — Needs Evidence.**

The Stage 0 implementation is not rejected as defective. Workspace source, official validators, metadata, tree, frozen hashes, Core/Adapter boundaries, exact product version `0.1.0`, Contract Version `1`, current marketplace registration, and current plugin installation were independently reconstructed and passed.

Acceptance is blocked because the required fresh-context runtime claim surface cannot be independently reconstructed from accessible original evidence. The smoke fixture was intentionally removed and `execution-report.md` provides detailed summaries but no persistent raw context transcripts, output Artifacts, or other reachable original evidence for the full Planner → Executor → Reviewer forward path, implicit Planner selection, negative implicit alias behavior, and the completed repair loop. A report and Role self-report are evidence indexes, not substitutes for those runtime observations. The Reviewer contract forbids acceptance while a required check remains unverified.

This is an **insufficient-evidence finding**, not a known plugin-source defect and not a contract defect. Route to Executor for evidence-only reconstruction under the same Task ID and frozen Stage 0 Scope; no redesign or source fix is authorized by this Review.

## Independently reconstructed evidence

### Official validators

Python `3.13.14` with PyYAML `6.0.3` was used directly; no temporary environment was created.

| Check | Exit | Errors | Warnings | Failures | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| `quick_validate.py .../skills/planner` | 0 | 0 | 0 | 0 | `Skill is valid!` |
| `quick_validate.py .../skills/executor` | 0 | 0 | 0 | 0 | `Skill is valid!` |
| `quick_validate.py .../skills/reviewer` | 0 | 0 | 0 | 0 | `Skill is valid!` |
| `quick_validate.py .../skills/spec-author` | 0 | 0 | 0 | 0 | `Skill is valid!` |
| `validate_plugin.py plugins/sacha-orchestra` | 0 | 0 | 0 | 0 | Plugin validation passed |
| `read_marketplace_name.py --marketplace-path .agents/plugins/marketplace.json` | 0 | 0 | 0 | 0 | `personal` |

Repository lint is **not configured / not run**. Build and project test suite are **not applicable** because Stage 0 contains documents and metadata and defines neither a build target nor a test runner. These statuses are not inferred from validator success.

### Static, metadata, tree, hash, and boundary checks

An independent read-only Python probe parsed both JSON files and all Skill YAML/frontmatter; checked the exact 18-file pre-Review allowlist, zero empty directories, one root `AGENTS.md`, marketplace source/policies/category, manifest version/components/capabilities, four Skill identities/prompts/policies, Markdown structure and local links, forbidden Skill paths, machine-local plugin paths, Core leakage terms, and both frozen hashes.

- Final valid probe: exit `0`; checks `83`; errors `0`; warnings `0`; failures `0`.
- `execution-report.md` independently computed SHA-256: `43EF7BE90742DA0202D8875302891AF77BE8A973F0EC390FCEEA8BD1034599BC`.
- Global AGENTS current SHA-256: `5777F15BDD86662B1333F902C63A36C07A28DF4C657D3C0A9F8DE721D7FAAE54`, matching the Execution Report baseline.
- `git rev-parse --show-toplevel`: exit `128`, expected because the workspace is not a Git repository; this is not a failure under the Spec.
- No Manager, `spec-executor`, or `spec-reviewer` Skill exists. No Stage 1 Project Integration, Runtime Registry, Work Packet implementation, parallel writer, hooks, MCP server, app, asset, or plugin script exists.

The first custom static probe exited `1` before producing a valid check count because Python decoded UTF-8 Markdown with the default GBK codec (`UnicodeDecodeError`). It wrote nothing and supported no judgment. The probe was corrected only by specifying UTF-8 and then fully rerun as the authoritative 83-check result above.

### Installation and discovery state

| Check | Exit | Errors | Warnings | Failures | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| `<codex-cli> --version` | 0 | 0 | 0 | 0 | `codex-cli 0.144.0-alpha.4` |
| `<codex-cli> plugin marketplace list` | 0 | 0 | 0 | 0 | `personal` points to this workspace root |
| `<codex-cli> plugin list` | 0 | 0 | 0 | 0 | `sacha-orchestra@personal`, installed and enabled, version `0.1.0`, source is this workspace plugin root |

The current independent Review context itself discovered and loaded the installed `sacha-orchestra:reviewer` entry and successfully read the workspace in Review-only mode. This supports the installed Reviewer and read-only SH1 entry reachability. It does not reconstruct the complete three-Role forward smoke or prove SH2/SH3.

## Findings and claim surfaces

| Surface | Status | Classification | Review limit |
| --- | --- | --- | --- |
| Lint | Not configured / not run | Unverified, non-blocking | No lint claim |
| Official Skill/plugin validators | Passed | Independently verified | Schema/packaging only |
| Metadata/tree/hash/boundary | Passed | Independently verified | Current workspace state only |
| Marketplace registration and plugin installation | Passed | Independently verified | Current CLI observable state only |
| Installed Reviewer discovery and read-only self-inspection entry | Passed | Independently verified | Supports SH1 entry reachability only |
| Full fresh-context Planner → Executor → Reviewer forward smoke | Unverified | **Blocking evidence gap** | Report summary is not original runtime evidence |
| Implicit Planner routing and negative implicit alias behavior | Unverified | **Blocking evidence gap** | Static policy passes; runtime behavior is not independently reconstructable |
| Repaired smoke lifecycle and exact nine-field runtime handoffs | Unverified | **Blocking evidence gap** | Source contract is correct; executed runtime chain lacks reachable original evidence |
| External no-write history outside authorized installation | Partially reconstructable | Residual evidence limit, non-source finding | Current hashes/state support some boundaries; historical absence of all writes cannot be fully proven after the fact |

### Blockers

1. Persist or otherwise expose reachable original evidence for the complete fresh-context Stage 0 smoke: minimal inputs, actual Role hits, exact nine-field handoffs, raw validation outputs/exits/errors/warnings/failure counts, repair routing, and final result.
2. Persist or expose equivalent original runtime evidence for implicit Planner selection and the negative assertion that ordinary planning did not invoke `spec-author`.
3. Let an independent Reviewer rerun or inspect those evidence surfaces before Stage 0 acceptance.

### Non-blockers and residual risks

- The stale “draft, awaiting approval” text in frozen `spec.md` should not be edited within this Review. A later Planner-owned documentation task may reconcile it if a consumer needs the Artifact to be self-contained.
- The invalid initial Reviewer/checker probes recorded by Executor and the invalid GBK probe in this Review are not implementation failures because they were excluded and fully rerun; keeping them visible is correct evidence discipline.
- No approved deviation from the Stage 0 architecture or Scope was found.

## Stage, version, and self-hosting claim limits

- Verified implementation boundary: **Stage 0 Foundation source and installed `0.1.0` state**, pending runtime evidence completion and independent re-review.
- `Contract Version: 1` is verified in both Core contracts and means the first contract schema only.
- SH1 claim limit: installed Reviewer/read-only self-inspection entry is reachable; the broader recorded SH1 smoke is not upgraded beyond accessible evidence.
- Not claimed: Stage 0 acceptance, Stage 1, SH2, SH3, bounded self-change, automatic orchestration, Manager/Router, complete Hybrid, full self-hosting, production readiness, or product `1.0.0`.

## Initial Reviewer Handoff Envelope (superseded; preserved audit trail)

1. `Task ID`: `SO-0.1.0-BOOTSTRAP-2026-07-12`
2. `Source Role`: `Reviewer`
3. `Target Role`: `Executor`
4. `Outcome`: `Independent Review reconstructed and passed the current Stage 0 source, official validators, metadata/tree/hash/boundary checks, marketplace registration, plugin installation, and installed Reviewer read-only entry. Stage 0 acceptance is rejected solely because required fresh-context forward-smoke and routing claims lack reachable original evidence; no implementation defect or contract defect is established.`
5. `Scope Reference`: `spec.md`, Task ID `SO-0.1.0-BOOTSTRAP-2026-07-12`, Stage 0 Slice 8 and final acceptance matrix only; product/plugin version remains `0.1.0`; `docs/architecture/evolution.md` is a read-only guardrail.`
6. `Artifact References`: `spec.md`; `execution-report.md`; `review.md`; `.agents/plugins/marketplace.json`; `AGENTS.md`; `plugins/sacha-orchestra/`.
7. `Evidence References`: `review.md` independent validator/static/CLI results; actual workspace files; current `<codex-cli> plugin marketplace list`; current `<codex-cli> plugin list`; `execution-report.md` Slice 8 as an evidence-gap index only, not proof of the unpersisted runtime observations.`
8. `Deviations and Open Risks`: `No approved Scope or architecture deviation and no known implementation defect. Blocking evidence gap: the cleaned smoke fixture and absence of reachable raw fresh-context outputs prevent independent reconstruction of the complete forward path, implicit routing, alias negative behavior, repair loop, and runtime Handoff chain. SH2, SH3, Stage 1+, complete Hybrid, full self-hosting, production readiness, and product 1.0.0 remain unclaimed.`
9. `Entry Condition`: `Executor may begin only under the same approved Stage 0 Scope with authorization to perform evidence-only fresh-context smoke reconstruction and to persist a bounded, non-sensitive evidence location. Executor must not change frozen Artifacts, plugin source, architecture, version, installation state, cache, global/system files, or other projects. After reachable original evidence exists, hand the unchanged Task ID to a fresh independent Reviewer for re-review.`

## Evidence-only re-review

### Repair scope and unchanged-state verification

- Updated `execution-report.md` SHA-256: `F02C530F416A77A6179D97DDDFE7794A342A0D5B83F9C2EACCEAE3703380C268`.
- Pre-re-review `review.md` SHA-256: `69909394DB7C4689723731A0E0FABE5A59451F42BED9A31AFC4A46A19CDF21C3`, proving the Executor preserved the Reviewer-owned Artifact.
- Seventeen source/frozen/metadata files were compared with their prior accepted hashes: checks `17`, errors `0`, warnings `0`, failures `0`.
- Current marketplace check: exit `0`, errors `0`, warnings `0`, failures `0`; `personal` still points to this workspace.
- Current plugin check: exit `0`, errors `0`, warnings `0`, failures `0`; `sacha-orchestra@personal` remains installed and enabled at exact version `0.1.0` from this workspace source.
- No source fix, frozen Artifact change, installation mutation, cache change, or version change was required for the evidence repair.

### Task search and raw-turn reads

Local Codex task search was executed independently:

- Search `smoke`: returned the five exact expected titles, all idle and rooted at this workspace.
- Search `alias`: returned the exact alias title.
- Locator searches: errors `0`, warnings `0`, failed title assertions `0`.

The first read attempt supplied unsupported optional argument combinations. Six batched reads and one single read returned `invalid arguments`; they yielded no evidence and support no claim. The read method was corrected to the minimal supported call plus cursor pagination. All six tasks and all older turns were then read successfully; corrected-read errors `0`, warnings `0`, failures `0`.

| Human-visible task title | Original evidence independently observed | Judgment |
| --- | --- | --- |
| `Plan planner smoke` | Explicit installed `sacha-orchestra:planner` hit; all three formal Role entries reported visible; planning-only/no-write behavior; initial exact nine-field Planner handoff; original erroneous `41`-byte acceptance; Reviewer-return repair; corrected `39`-byte acceptance under the same Task ID; second exact nine-field handoff | Passed after preserved contract repair |
| `Create smoke artifact` | Explicit installed `sacha-orchestra:executor` hit; Human authorization and sole-writer entry check; only `planner-smoke.txt` added; an automatically introduced LF was detected and removed within the same one-file Scope; final initial check reported exit `1`, errors `0`, warnings `1`, failures `1` solely for the impossible `41/39` condition; verification-only continuation after Planner correction reported exit `0`, errors `0`, warnings `0`, failures `0`, `39/39`, exact bytes, no trailing newline, matching SHA-256, and no further write; both exact nine-field handoffs present | Passed; no silent success upgrade |
| `Review smoke fixture` | Explicit independent installed `sacha-orchestra:reviewer` hit; default no-fix behavior; first generic-call probe explicitly discarded after exit `1`/tool error `1`; authoritative initial check reported exit `1`, errors `0`, warnings `1`, failures `1` and correctly routed the Spec defect to Planner; revised-contract check reported exit `0`, errors `0`, warnings `0`, failures `0`, exact hash and final Accept; exact nine-field Reject and Accept envelopes present | Passed; repair lifecycle and provenance verified |
| `制定隐式路由烟测方案` | Prompt names no Skill; actual commentary identifies installed `sacha-orchestra:planner`; response is planning-only and no-write; no `spec-author` invocation appears | Passed implicit Planner positive and alias-negative check |
| `验证 spec-author alias` | Prompt explicitly invokes `$sacha-orchestra:spec-author`; commentary immediately states deprecated compatibility status and forwards to formal Planner; raw result confirms `allow_implicit_invocation: false`, does not create a fourth Role, and performs no write | Passed explicit alias compatibility |
| `Review SH1 readiness` | Explicit installed `sacha-orchestra:reviewer` hit in an independent read-only context; workspace authorities and references read; two read-only checks reported exit `0`; exactly one bounded future suggestion; exact nine-field Reviewer-to-Human envelope; explicit exclusion of SH2, SH3, full self-hosting, and `1.0.0` | Passed SH1 read-only entry reachability only |

### Re-review finding classification

- Former blocking evidence gap: **closed**. Raw runtime turns are now reachable through stable human-visible local task titles and search terms without embedding prohibited Runtime storage IDs in the Artifact.
- Implementation defects: **none open**. The neutral smoke file satisfied the corrected contract before fixture cleanup.
- Contract defects: **none open**. The smoke Planner's derived byte-count defect was correctly routed and repaired under the same smoke Task ID without changing payload or Scope.
- Approved deviations: **None**.
- Non-blocking follow-up: the SH1 smoke suggested a fixed read-only input/expected-result template under a separately approved future Planner Scope. This is not a Stage 0 acceptance requirement and is not implemented here.
- Lint remains not configured/not run; build and project test suite remain not applicable. Official validators and static checks remain distinct from runtime smoke and installation claims.

## Final Reviewer Handoff Envelope

1. `Task ID`: `SO-0.1.0-BOOTSTRAP-2026-07-12`
2. `Source Role`: `Reviewer`
3. `Target Role`: `Human Conductor`
4. `Outcome`: `Accept. Independent re-review directly inspected all raw local Codex turns for the Stage 0 Planner, Executor, Reviewer, implicit-routing, deprecated-alias, and SH1 smoke surfaces. The former runtime-evidence gap is closed; source, validators, boundaries, installation, discovery, forward repair lifecycle, exact nine-field handoffs, and SH1 read-only entry satisfy the approved 0.1.0 Foundation contract.`
5. `Scope Reference`: `spec.md`, Task ID `SO-0.1.0-BOOTSTRAP-2026-07-12`, Stage 0 only; product/plugin version `0.1.0`; `docs/architecture/evolution.md` remains the read-only stage/version guardrail; Contract Version `1` remains the first contract schema only.`
6. `Artifact References`: `spec.md`; `execution-report.md`; `review.md`; `.agents/plugins/marketplace.json`; `AGENTS.md`; `plugins/sacha-orchestra/`.
7. `Evidence References`: `review.md` initial Review and evidence-only re-review sections; actual workspace files; current marketplace/plugin list state; `execution-report.md` raw-runtime locator; all raw turns found by searches `smoke` and `alias` under exact titles `Plan planner smoke`, `Create smoke artifact`, `Review smoke fixture`, `制定隐式路由烟测方案`, `验证 spec-author alias`, and `Review SH1 readiness`.
8. `Deviations and Open Risks`: `No approved Scope or architecture deviation and no open implementation or contract defect. The initial formal Reject is preserved as audit history and is superseded because the raw runtime evidence is now independently reachable. The optional SH1 template suggestion is non-blocking and requires a separate future Planner Scope. Stage 1, SH2, SH3, bounded self-change, automatic orchestration, Manager/Router, complete Hybrid, full self-hosting, production readiness, and product 1.0.0 remain unclaimed.`
9. `Entry Condition`: `None. The Human Conductor may close Task ID SO-0.1.0-BOOTSTRAP-2026-07-12 as accepted for Stage 0 Foundation only. Any Stage 1 work, higher self-hosting claim, compatibility contraction, Core change, version change, refresh/reinstall, or product 1.0.0 work requires its own approved Scope and applicable authorization.`
