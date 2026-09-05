# QuantyCoin Autonomous Protocol Rebuild Agent Operating Specification

**Protocol Version**: QTY3 (QuantyCoin 3.0)  
**Agent Mode**: LONG_HORIZON_AUTONOMOUS_ENGINEERING  
**Repository**: https://github.com/timfromhcs/QuantyCoin  
**Architectural Reference**: https://github.com/bitcoinknots/bitcoin (Reference Only — Never import Bitcoin network identity)

---

## 1. Absolute Agent Rules

1. **R001 - INVESTIGATE_BEFORE_ACTING**: Never modify unknown code based on assumptions.
2. **R002 - NEVER_INVENT_REPOSITORY_FACTS**: Unknown files, APIs, commands, tests and behavior remain UNKNOWN until directly inspected.
3. **R003 - VERIFY_BEFORE_CLAIM**: Every important claim must have execution evidence, direct source evidence or independent verification.
4. **R004 - NO_FALSE_COMPLETION**: Never declare completion because code compiles, because tests exist, because documentation exists, or because the agent believes the implementation looks correct.
5. **R005 - NEVER_DISABLE_FAILURES**: Never hide failures by deleting, weakening, skipping or redefining tests.
6. **R006 - ROOT_CAUSE_FIRST**: Fix defects at their actual layer.
7. **R007 - CONSENSUS_FIRST**: Never allow wallet, GUI, RPC or mining code to create alternate consensus behavior.
8. **R008 - NETWORK_INPUT_IS_HOSTILE**: Validate all attacker-controlled data.
9. **R009 - REFERENCE_IS_NOT_IDENTITY**: Bitcoin Knots is architecture/reference material only. Do not import Bitcoin network identity accidentally.
10. **R010 - PERSISTENT_STATE**: Agent progress must survive context loss through files in `docs/agent/`.
11. **R011 - NO_SECRET_UPLOADING**: Private Genesis working material and all other secrets must never be committed or pushed.
12. **R012 - NO_SECRET_LOGGING**: Never print secret values to terminal logs, CI logs, GitHub issues, commits, reports or chat.
13. **R013 - DO_NOT_GUESS_WHAT_IS_SECRET**: When uncertain whether an artifact is sensitive, default to keeping it local.

---

## 2. Local Secret Vault Architecture

Canonical Location:
- Windows: `%USERPROFILE%\Desktop\QuantySecrets\QuantyCoin\`
- Linux/macOS: `~/Desktop/QuantySecrets/QuantyCoin/`

Required Subdirectories:
- `genesis/`
- `genesis/working/`
- `genesis/generated/`
- `genesis/verification/`
- `genesis/archive/`
- `signing/`
- `release/`
- `manifests/`

Rules:
- Auto-create directories if missing.
- Zero secrets inside the repository.
- Full isolation of private generator inputs, raw nonce search runs, uncompressed keys, seeds, and mnemonics.

---

## 3. Persistent State Tracking Structure

State is preserved continuously in:
- `docs/agent/STATE.md`: Active phase, completed milestones, subsystem health.
- `docs/agent/NEXT_ACTIONS.md`: Ordered queue of tasks according to scope priority.
- `docs/agent/EVIDENCE.md`: Cryptographic proofs, test outputs, benchmark logs.
- `docs/agent/FAILURES.md`: Failure incident reports, root causes, fixes, regression tests.
- `docs/agent/DECISIONS.md`: Protocol design decisions, parameter freezing records.
- `docs/agent/OPEN_QUESTIONS.md`: Unresolved architectural options or trade-offs.

---

## 4. Autonomous Execution & End Conditions

The agent will autonomously execute the workflow:
`load_state` -> `inspect_git_state` -> `inspect_current_code` -> `identify_current_objective` -> `identify_required_evidence` -> `consult_reference_when_useful` -> `design_change` -> `implement` -> `compile` -> `run_targeted_tests` -> `run_regression_tests` -> `run_integration_tests` -> `inspect_output`

Completion Gate requires 100% verified PASS across all mandatory checkpoints with verifiable proof in `docs/agent/EVIDENCE.md`.
