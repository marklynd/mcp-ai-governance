# mcp-ai-governance

[![CI](https://github.com/marklynd/mcp-ai-governance/actions/workflows/ci.yml/badge.svg)](https://github.com/marklynd/mcp-ai-governance/actions/workflows/ci.yml) [![Container](https://github.com/marklynd/mcp-ai-governance/actions/workflows/publish-container.yml/badge.svg)](https://github.com/marklynd/mcp-ai-governance/actions/workflows/publish-container.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) ![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)

An MCP server that turns AI governance work into callable tools: map a control
description onto **NIST AI RMF 1.0**, **ISO/IEC 42001:2023**, the **EU AI Act
(Regulation (EU) 2024/1689)** and **NIST CSF 2.0**; triage a use case against the
EU AI Act risk tiers; score an organisation's readiness; sequence the resulting
gaps into a roadmap; and produce the evidence list an auditor will actually ask
for.

No API key. No network calls. Deterministic output.

---

## Why this exists

Two things are true at once in every enterprise AI programme:

1. The frameworks overlap heavily. "A human reviews the output before it reaches
   a customer" is simultaneously NIST AI RMF `GOVERN 3.2`, ISO/IEC 42001 `A.9.2`
   and EU AI Act `Art. 14`. Nobody has that crosswalk in their head.
2. The mapping work is repetitive, high-volume and low-judgement, right up to the
   point where it needs a lot of judgement.

That is the shape of a problem worth giving an agent. But an agent that
free-associates clause numbers is worse than useless in this domain, because a
confidently wrong citation survives into a board pack. So the mapping here is
**deterministic and rule-based**: every match points at the exact phrase that
caused it, the same input always produces the same output, and the encoded
subset of each framework is stated honestly so a negative result can be
interpreted.

The model doing the reasoning stays in the loop. The server just makes sure the
clause numbers it cites are real.

---

## Install

Requires Python 3.10 or later.

```bash
git clone https://github.com/marklynd/mcp-ai-governance
cd mcp-ai-governance
pip install -e ".[dev]"
```

Verify it works:

```bash
python examples/smoke_test.py   # imports the server, lists tools, calls each one
python -m pytest                # 215 tests
python evals/run_eval.py        # scores the mapping tool against a labelled set
```

## Run

Over stdio, which is what MCP clients expect:

```bash
mcp-ai-governance
# or, without installing:
PYTHONPATH=src python3 -m mcp_ai_governance
```

### Connect it to Claude Desktop

Add this to `claude_desktop_config.json` (macOS:
`~/Library/Application Support/Claude/claude_desktop_config.json`, Windows:
`%APPDATA%\Claude\claude_desktop_config.json`), then restart the app:

```json
{
  "mcpServers": {
    "ai-governance": {
      "command": "mcp-ai-governance"
    }
  }
}
```

Running from a clone without installing? See
[`examples/claude_desktop_config.json`](examples/claude_desktop_config.json) for
the `PYTHONPATH` variant.

The tools are also importable directly, with no MCP client involved:

```python
from mcp_ai_governance import map_control, classify_risk_tier
result = map_control("we log every model inference to an immutable audit trail")
```

---

## Worked example

**Input**

```python
map_control(
    "A named reviewer must approve every AI-drafted customer email "
    "before it is sent, and can reject it."
)
```

**Output** (abridged: the `nist_ai_rmf` and `iso_42001` blocks are trimmed to one
entry each, everything else is verbatim)

```json
{
  "description": "A named reviewer must approve every AI-drafted customer email before it is sent, and can reject it.",
  "detected_themes": [
    {
      "theme_id": "human_oversight",
      "label": "Human oversight",
      "strength": 1.82,
      "evidence": ["must approve", "reject"]
    }
  ],
  "mappings": {
    "nist_ai_rmf": [
      {
        "control_id": "GOVERN 3.2",
        "title": "Policies define roles and responsibilities for human-AI configurations and oversight of AI systems.",
        "group": "GOVERN 3: Workforce diversity and inclusion",
        "confidence": 0.38,
        "raw_score": 0.819,
        "matched_signals": [],
        "matched_themes": ["human_oversight"],
        "rationale": "Mapped to GOVERN 3.2 because it addresses human oversight.",
        "citation": "NIST AI 100-1 (AI RMF 1.0), Jan 2023, GOVERN 3.2"
      }
    ],
    "iso_42001": [
      {
        "control_id": "A.9.2",
        "title": "Processes for the responsible use of AI systems, including human oversight of outputs.",
        "group": "Annex A.9: Use of AI systems",
        "confidence": 0.53,
        "raw_score": 1.287,
        "matched_signals": [],
        "matched_themes": ["human_oversight"],
        "rationale": "Mapped to A.9.2 because it addresses human oversight.",
        "citation": "ISO/IEC 42001:2023, A.9.2"
      }
    ],
    "eu_ai_act": [
      {
        "control_id": "Art. 14",
        "title": "Human oversight: high-risk systems are designed so natural persons can effectively oversee them, including a stop function.",
        "group": "Chapter III Section 2: Requirements for high-risk systems",
        "confidence": 0.53,
        "raw_score": 1.287,
        "matched_signals": [],
        "matched_themes": ["human_oversight"],
        "rationale": "Mapped to Art. 14 because it addresses human oversight.",
        "citation": "Regulation (EU) 2024/1689 (EU AI Act), Art. 14"
      },
      {
        "control_id": "Art. 26",
        "title": "Obligations of deployers of high-risk AI systems, including using the system per instructions and assigning competent human oversight.",
        "group": "Chapter III Section 3: Obligations of providers and deployers",
        "confidence": 0.53,
        "raw_score": 1.287,
        "matched_signals": [],
        "matched_themes": ["human_oversight"],
        "rationale": "Mapped to Art. 26 because it addresses human oversight.",
        "citation": "Regulation (EU) 2024/1689 (EU AI Act), Art. 26"
      }
    ]
  },
  "notes": [],
  "disclaimer": "Deterministic keyword and theme mapping over an encoded subset of each framework. It is decision support for a qualified reviewer, not a compliance determination and not legal advice."
}
```

Note what the output does **not** do: it does not claim certainty. Confidence is
0.38 to 0.53 because the evidence is thematic rather than a direct phrase hit,
and the `evidence` array tells you exactly which two phrases drove it. A reviewer
can disagree in seconds.

### The tools compose

```python
readiness = score_readiness({"governance": {"ai_policy": 0, "system_inventory": 1}})
roadmap   = generate_roadmap(readiness["gaps"])       # gaps feed straight through
checklist = evidence_checklist("GOVERN 1.6")          # any control_id from map_control
```

---

## Tool reference

| Tool | Arguments | Returns |
|---|---|---|
| `map_control` | `description` (str, 1-4000 chars), `frameworks` (list, optional), `top_k` (1-10, default 3), `min_confidence` (0.0-1.0, default 0.3) | Detected themes, per-framework control matches with confidence, matched signals, rationale and citation |
| `classify_risk_tier` | `use_case` (str, 1-4000 chars) | Tier (`prohibited` / `high-risk` / `limited-risk` / `minimal-risk`), reasoning, every triggered criterion with its article, obligations, penalty band, application dates, caveats |
| `score_readiness` | `answers` (object, 0-4 maturity levels, nested or dotted keys) | Overall score and tier, per-dimension scores with coverage, weakest dimensions, and a `gaps` array shaped for `generate_roadmap` |
| `generate_roadmap` | `gaps` (list of strings or objects, 1-60) | Four phases (0-30 / 31-90 / 91-180 / 181-365 days) with owner role, supporting roles, effort band, dependencies and a concrete first deliverable per item |
| `evidence_checklist` | `control_id` (str, e.g. `"Art. 14"`, `"GOVERN 1.6"`, `"A.6.2.8"`) | Evidence split into documents / records / system artefacts / interviews, why each is requested, likely auditor questions, common failure modes, sampling guidance |
| `list_frameworks` | none | What is encoded per framework, with version, source and an honest coverage statement |
| `list_readiness_questions` | none | The 25-question bank, the 0-4 maturity scale and the roadmap phase definitions |

There is also a resource, `governance://controls`, returning every encoded
control as JSON.

---

## How the mapping works

No LLM, no embeddings. Three stages, all inspectable:

1. **Theme detection.** The description is matched against a controlled
   vocabulary of 23 governance themes (`human_oversight`, `data_governance`,
   `third_party`, and so on) in
   [`knowledge/themes.py`](src/mcp_ai_governance/knowledge/themes.py). Multi-word
   phrases score higher than single words because they are far less ambiguous.
2. **Control scoring.** Each control accumulates direct evidence (hits on its own
   signal phrases), thematic evidence discounted by how *specific* that theme is
   within its framework (a theme carried by one control discriminates; a theme
   carried by fifteen does not), and an agreement bonus when a control matches
   more than one detected theme.
3. **Confidence.** The raw score is squashed through `1 - exp(-raw / 1.7)`,
   bounded at 0.95. It is a calibrated ranking signal, not a probability.

Three bugs found and fixed during development, kept as regression tests because
they are the interesting ones:

- Signal phrases that reduced to the same token sequence were double-counted,
  so `"approve"` plus `"approved by"` scored twice for one piece of evidence.
- Stop words were being stripped, which silently collapsed `"must approve"` into
  `"approve"` - and that then fired on `"an approved policy"`, which is
  governance, not oversight. Stop words are now retained.
- The stemmer applied one pass of suffix rules, so `"triggered"` reduced to
  `"trigger"` while `"trigger"` reduced to `"trigg"`, and the two never matched.
  It now runs two passes.

---

## Evaluation

`evals/mapping_eval_set.json` holds 30 labelled control descriptions with the
controls a governance reviewer would expect for each framework. Labels are gold
*sets* (more than one clause legitimately covers most practices), and where a
framework has no good analogue the expectation is `null` rather than a forced
match, so honesty about coverage is not punished by the score.

```bash
python evals/run_eval.py
python evals/run_eval.py --threshold 0.90   # non-zero exit for CI
```

Current result:

```
framework           n    hit@1    hit@3      MRR    empty
---------------------------------------------------------
eu_ai_act          26    0.885    1.000    0.942    0.000
iso_42001          28    0.750    0.929    0.827    0.000
nist_ai_rmf        30    0.833    1.000    0.906    0.000
---------------------------------------------------------
OVERALL            84    0.821    0.976    0.891    0.000
```

Read that as: the correct control is ranked first 82% of the time and appears in
the top three 98% of the time, and there are no silent empty results.

The two remaining misses are both ISO/IEC 42001 and both instructive:

- *Watermarking synthetic content* returns `A.6.2.7` (technical documentation)
  where the label says `A.8.2` (information for users). ISO/IEC 42001 has no
  content-marking control, so every candidate is a compromise.
- *Environmental impact of training* returns `A.5.3` (documentation of impact
  assessments) where the label says `A.5.5` (societal impacts). Arguably both are
  right; the label picked one.

Neither was patched, because tuning signals until the eval reads 1.000 would be
fitting the test rather than improving the tool.

**Methodology note, stated plainly:** labels were written from the framework
documents before the tool was run, and were never edited to match its output.
Signal vocabulary *was* expanded after reviewing misses - that is ordinary
iterative development - but only by adding general domain language to the
knowledge base, never the literal eval sentences. The set is small (30 cases,
84 scored framework expectations) and written by one person, so treat the
numbers as a regression guard rather than a claim about population accuracy.

---

## Scope and limitations

Read this section before using any output in front of an auditor or a regulator.

**Not legal advice.** Every tool says so in its own payload. `classify_risk_tier`
in particular is a triage aid. Whether a specific system is high-risk under the
EU AI Act is a legal determination that depends on facts a text classifier cannot
see.

**Framework coverage is a subset, and the subset is declared.** Call
`list_frameworks` for the exact statement per framework:

| Framework | Encoded | Not encoded |
|---|---|---|
| NIST AI RMF 1.0 | All 72 subcategories across GOVERN / MAP / MEASURE / MANAGE | Playbook suggested actions, the AI RMF Profiles |
| ISO/IEC 42001:2023 | Clauses 4-10 and the Annex A control set (A.2 to A.10) | Annex B-D guidance, and any ISO text (see below) |
| EU AI Act | 22 obligation articles, all 8 Annex III areas, all 8 Art. 5 prohibitions, Art. 50 triggers | The other ~90 articles, Annex I product legislation, most annexes |
| NIST CSF 2.0 | All 22 categories | Subcategory identifiers such as `GV.SC-01` |

**Titles are paraphrases, not quotations.** Every control title was written for
this project to keep output readable. They are summaries. Quote the source
document, not this repository.

**No ISO text is reproduced.** ISO/IEC 42001 is copyrighted and not freely
redistributable. Only clause numbers and short descriptive titles are used, which
is standard crosswalk practice. You still need a licensed copy of the standard.

**Where approximation is knowingly present**, it is flagged in code comments:

- ISO/IEC 42001 clause 10 ordering (10.1 continual improvement, 10.2
  nonconformity) follows the 2023 edition; some earlier ISO management-system
  standards use the reverse order. Verify against your copy.
- EU AI Act article numbers follow the **adopted** Regulation (EU) 2024/1689, not
  the 2021 Commission proposal. Sources citing "Art. 52 transparency" are quoting
  the proposal; in the adopted text it is Art. 50. There is a test asserting this.
- Annex I high-risk classification under Art. 6(1) - AI as a safety component of
  a regulated product such as machinery, medical devices or vehicles - is **not**
  detected. `classify_risk_tier` says so in its caveats every time.
- The Art. 6(3) derogation (narrow procedural task, no material influence on the
  decision) is surfaced as a caveat, never applied automatically.

**Readiness weights are a judgement call.** Governance 0.25, data 0.22, platform
0.18, strategy 0.18, talent 0.17. They reflect what most often blocks a system
from reaching production. They are visible in every response specifically so you
can disagree with them.

**Roadmap effort figures are planning bands**, derived from gap theme and
severity. They size a plan. They do not cost a statement of work.

**Mapping is lexical.** A description that never uses recognisable governance
vocabulary will not map, and the response says so rather than guessing. Describe
what a control *does*, not what the internal tool is called.

**Frameworks change.** This encodes documents as at July 2026. The EU AI Act in
particular is still generating delegated acts, implementing acts and harmonised
standards.

---

## Development

```bash
python -m pytest        # 215 tests
python -m mypy src      # strict mode
python -m ruff check .
```

Layout:

```
src/mcp_ai_governance/
  server.py             MCP tool definitions (FastMCP)
  mapping.py            control mapping engine
  risk.py               EU AI Act tier classifier
  readiness.py          five-dimension readiness scoring
  roadmap.py            gap sequencing
  evidence.py           audit evidence checklists
  text.py               normalisation and phrase matching
  knowledge/            the encoded frameworks (the part worth reviewing)
evals/                  labelled eval set and scoring harness
examples/               MCP client config and a smoke test
tests/                  pytest suite
```

Adding a framework means adding one module under `knowledge/` whose controls are
tagged with existing themes, then registering it in `knowledge/__init__.py`. The
mapping engine needs no changes.

---

## Licence

MIT. Copyright (c) 2026 Mark Lynd.

---

## Run it as a container

A multi-stage image is published to the GitHub Container Registry on every push to `main`.

```bash
docker pull ghcr.io/marklynd/mcp-ai-governance:latest
docker run --rm -i ghcr.io/marklynd/mcp-ai-governance:latest
```

The server speaks MCP over stdio, so `-i` is required and `-t` must be omitted. To wire it into Claude Desktop, point the command at `docker` with `["run","--rm","-i","ghcr.io/marklynd/mcp-ai-governance:latest"]` as the args.
