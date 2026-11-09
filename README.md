# IONIAN SANCTUARY — Archaeological Evidence Evaluation

**Status:** reproducible research *instrument* and descriptive replay of a mixed, manually collected 24-slot sample. **NOT YET a fully attributed frontier-model comparison.**

**Domain:** archaeology, numismatics, field survey and source criticism. **Cases:** 8. **Access:** free, offline Python grading; no API key required. **Submission video:** hosted separately; publicly accessible URL **PENDING**. **Release:** judge-facing source package based on v1.3.2.

## 1. Short description and key finding

The instrument measures whether a tested system can respect boundaries between a numismatic catalogue **type**, individual **specimens**, archaeological **findspots**, iconographic parallels and the strength of survey/stratigraphic evidence. In publication and digital collections work, confusing these layers can create false provenances, duplicate object counts and unsupported settlement histories.

The available mixed-system operator-recorded export contains **24 numbered slots, one copied-prompt collection error and 23 other response-like entries**. The frozen grader finds **17 strict passes among those 23** (73.9% descriptive) or **17/24 (70.8%)** counting the copied-prompt slot as a strict nonpass. Without per-trial model identity and original session verification these numbers do **not** demonstrate a measurable limitation of any specific frontier model. See `results/RESULTS_AND_LIMITATIONS.md`.

## 2. Video walkthrough link

**PENDING — paste accessible YouTube/Drive/Vimeo/Loom URL here after upload.** The video must be under five minutes and publicly viewable by anyone with the link. The original 4:36 silent MP4 is not bundled, consistent with submission size rules. The participant guide asks for a video that plays with audio; the supplied silent copy has no audio stream, so choose an ambient non-narrated edition or obtain official clarification.

## 3. Domain and expertise

This domain requires archaeological source criticism and classical numismatic expertise: reading catalogue attributions, tallying catalogue specimens, understanding physical provenance and assessing the inferential limitations of archaeological surface survey. The evaluation builds on the researcher's earlier Ionian sanctuary and numismatic research. The earlier V4/C8 development archive contained **synthetic** accessions/plates that are not treated here as genuine finds; see `PROVENANCE_AND_REVIEW.md`.

## 4. What the eight tasks measure

| ID | Professional research challenge |
|---|---|
| ION-REAL-01 | Coin types vs specimens and excavated Claros inventory |
| ION-REAL-02 | Revised city/region attribution, type identity and die link |
| ION-REAL-03 | Apollo attributes and sanctuary provenance |
| ION-REAL-04 | Greek obverse legends and distinct Tiberian catalogue types |
| ION-REAL-05 | Archaeological survey and later excavation versus specimen counts |
| ION-REAL-06 | Earlier pottery and the limitations of disturbed contexts |
| ION-REAL-07 | Evidence of decline versus proof of total abandonment |
| ION-REAL-08 | Whether publication claims are supported or unestablished |

Every input is a frozen task JSON file in `tasks/`; all documented factual assertions originate from the source identifiers in `sources/`. The reference answers in `reference/answers.json` must never be supplied to the evaluated system.

## 5. Reproduce from a clean environment

**Requirement:** Python 3.9+; only the Python standard library. No API credentials, internet, installation of Ollama, external LLM judge, additional library downloads or signed PowerShell scripts are needed to **replay and grade the archived record**. Free chat interfaces are manual response-collection channels, not independently replayable APIs.

On Windows, extract the ZIP and double-click `RUN_REPRODUCE_WINDOWS.cmd`, or use:

```powershell
cd IONIAN_SANCTUARY_ARCH_EVAL
py -3 verify_package.py
py -3 grade_responses.py --self-test
py -3 -m unittest discover -s tests -v
py -3 reproduce.py
```

On macOS/Linux, run the same Python scripts with `python3` and no Windows launcher. `reproduce.py` replays **only the archived operator-recorded responses** and writes deterministic reports into `results/reproduced/`. It explicitly does not turn unattributed mixed-system responses into a valid per-model experiment.

To run **new trials**, open `FRONTIER_REAL_TEST.html`, copy one task at a time into a fresh independent frontier-system session, preserve the entire unmodified reply and the exact model/version/settings/session URL in a linked trial log, and apply `python grade_responses.py --grade export.json`. Complete three independent trials **for each identified model and task** if reporting `pass^3`; sessions from different models cannot be pooled for that metric.

## 6. Grading methodology and reliability

- **Exact pass:** single parseable JSON object, exact keys, correct types and all expected values, including proper booleans and Greek legends where specified. JSON code fences are accepted; unrelated prose or typographic quotation marks are not.
- **Partial field credit:** correct required fields divided by required fields; malformed JSON gets zero field credit under the current published parser.
- **Critical decisions:** subset of archaeological inference/provenance fields, separately scored to avoid inflation by easy identifiers.
- **Reference oracle:** all eight frozen answers pass `grade_responses.py --self-test`. Deliberately incorrect empty objects fail; `tests/` adds negative, tamper and media checks.
- **Grader limitation:** output-contract failure is not always a substantive archaeological error. Inspect original raw responses and separate semantic, syntactic and copying mistakes.

No LLM-as-judge is used. The deterministic grader grades end-state structured output rather than textual reasoning. `source_integrity.json` stores the frozen task and code hashes; `photos/download_integrity.json` records the four locally embedded licensed photos.

## 7. Models tested, results, settings, cost and runtime

The uploaded trial export has global `model_reported: unreported`, empty access channel and no per-response provider IDs. The author indicated responses came from **multiple models**. Hence a *per-model table, model-specific pass rate and pass^3 statistic remain unavailable*. Do not invent them.

| Recorded sample | Trials | Exact pass | Critical accuracy | Validated per-model pass^3 |
|---|---:|---:|---:|---|
| Unattributed mixed-system operator record | 24 slots (23 response-like) | 17/24 strict; 17/23 descriptive | 72.2% across 24 slots | Not estimable |

The 24 raw records are in `trials/operator_export_original_2026-11-07.json`. Per-task transcripts and original frozen prompts are in `transcripts/`. Full detailed scores and examples are in `results/`. Date and time for each recorded response are present where supplied in the raw JSON; these are operator timestamps, not provider authentication.

**Costs:** Local scorer and benchmark code free, no API key or provider fees required by the evaluator. Any provider-specific access costs and model inference costs were not recorded; report them after trial attribution. **Runtime:** local grading is typically seconds on a standard Python environment; human original-session durations are not independently documented. Exact temperature/reasoning settings were not included; do not claim settings held constant.

## 8. Failure analysis

The principal illustrated substantive numerical discrepancy is `ION-REAL-01` trial 3: an apparent seven core specimens instead of the reference five, coupled with unparseable typographic quotation marks. The illustrated strict schema discrepancy is `ION-REAL-06` trial 2: strings in place of required booleans. `ION-REAL-01` trial 2 contains a copied prompt, which is a collection error, not a system failure. Each claim is supported by the preserved original operator response in `transcripts/`; see `results/RESULTS_AND_LIMITATIONS.md`.

**Provisional interpretation:** The recorded responses expose possible confusion between evidence content, source attribution and constrained reporting contracts. This is not yet a validated finding about a specific frontier-system family. A defensible conclusion requires accurate provenance of the response and independent expert review.

## 9. Prior work, public sources and photograph rights

Real-source factual abstracts: RPC I coin types 2521–2525, Çizmeli Öğün's 2007 Claros coin study, and Notion archaeological survey reports. Full source identifiers and original links: `sources/source_manifest.json` and `sources/FACTS_AND_PROVENANCE.md`. Reused real archaeological/contextual photography is credited in `PHOTOGRAPH_CREDITS.md` and `photos/manifest.json`; the four named JPEGs are included in `photos/`. The comparative Aurelian coin has a British findspot and is **not** a Claros excavation coin or an RPC I 2523 specimen. The original v4/c8 synthetic development archive is disclosed as **prior work only** and is not included as misleading excavation evidence.

Only rights-cleared photos and short public-source factual summaries are reproduced. Preserve source attribution and the relevant Creative Commons terms, including any share-alike obligations. Do not assume an image's subject is the actual catalogue specimen described by a task.

## 10. Human review and assistance disclosure

The software, graphics, task scaffolding and documentation were developed with language-model assistance. The submitting researcher must personally check the archaeological source claims, reference answers, images, exact trial records and interpretive statements. The assistance disclosure is retained for integrity, even though the public video is brand-neutral. `review/HUMAN_REVIEW_SIGNOFF_TEMPLATE.md` is **not yet signed** and no external expert approval is claimed.

## 11. Package and submission inventory

- `tasks/` — eight frozen exact prompts, output schemas and task/source metadata
- `reference/` — defensible expected answers; excluded from the worksheet's client-side task payload
- `graders/`, `grade_responses.py`, `reproduce.py`, `tests/` — scorer, one-command replay, unit tests
- `photos/`, `sources/`, `PHOTOGRAPH_CREDITS.md` — four real JPEGs and their licenses, documentary summaries
- `trials/`, `transcripts/`, `results/` — unedited operator export, task-scoped raw replies, scores and cautions
- `review/`, `video/`, `SUBMISSION_DESCRIPTION.md` — outstanding authenticity checklist, video verification and short submission description
- `.env.example`, `requirements.txt` — no credentials required

The maximum event ZIP size is **50 MB**, and **no video is included inside this ZIP**. See `review/EVIDENCE_AND_MISSING_ITEMS.md` for the remaining evidence needed to make this an independently verifiable, model-attributed research submission.
