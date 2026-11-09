# GitHub release preparation notes

This is a **candidate repository**, not an announcement that an online GitHub repository already exists.

### Retained research material

All eight frozen cases, their reference answers, archived raw operator responses, 24 prompt/response transcript pairs, and the four Wikimedia-sourced contextual images are preserved. Original trial responses were **not** edited.

### Engineering changes specific to this GitHub candidate

- Added `.gitignore`, `.gitattributes` and GitHub Actions reproducibility checks.
- Fixed `tests/test_eval.py` to assert that the included descriptive JSON result is **explicitly marked incomplete**, rather than incorrectly asserting that no JSON result files exist. The SHA-256 list was updated for this one altered test. The frozen `source_integrity.json` and the other research materials remain unchanged.
- Included optional provenance-correction tools under `extras/mixed_model_attribution/`; there is no claim the missing identities have been populated.
- Included GitHub publishing and licensing guidance. A top-level blanket license, scholarly citation metadata and publication URL are not invented.

### Outstanding work for an empirical benchmark publication

- Verify exact model/version/channel per response, fix or explicitly exclude the copied-prompt collection error with a traceable record, and verify original chats/screenshots.
- Validate archaeological reference answers independently.
- Insert a verified public video URL and ensure its audio and accessibility satisfy the competition rules.
- Decide repository visibility and software license and confirm rights to third-party images and source terms.

See `results/RESULTS_AND_LIMITATIONS.md` and `review/EVIDENCE_AND_MISSING_ITEMS.md` for the actual limitations.
