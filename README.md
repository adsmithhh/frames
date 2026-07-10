# Frames

> A framework for consistent, evolving AI cognitive experiments

## ⚠️ Note on this README

The first version of this README described the framework's status in aspirational
terms ("stable," "fixed," "active" across the board) that didn't match what the
code actually did when run. This version was rewritten after an AI-assisted audit
that traced each claim back to the source and either confirmed or corrected it.
The goals and design philosophy below are unchanged — only the status claims are.
If you're pulling this repo into a chat-mode session as a memory container (as
intended), this note is here so whichever engine reads it next inherits the
verified state, not the optimistic one.

## Vision & Philosophy

Frames aims to make AI cognitive experiments swappable by editing a single file
— change `task_payload.yaml`, keep everything else, get a different experiment.
It's meant to be a low-friction way to build intuition for how AI systems behave
under different cognitive-science paradigms, growing in complexity as the person
running it learns more.

## Core Philosophy

- **One file, one experiment**: the task payload defines what's being tested;
  the rest of the framework should stay untouched.
- **Learn by running things**: the framework is meant to be poked at, not just
  read.
- **Accessible complexity**: cognitive-science paradigms (Stroop, oddball,
  theory of mind) as a way into understanding model behavior, not as an academic
  exercise.

## Quick Start

### Prerequisites
- Python 3.8+
- API keys for whichever model backends you intend to use

### Setup
```bash
git clone https://github.com/adsmithhh/frames.git
cd frames
cp .env.example .env   # then fill in the keys you actually use
```

### Running an experiment
```bash
python main.py
# choose a model when prompted (or accept the default)
```

## Project Structure

```
frames/
├── main.py                          # entry point
├── .env                             # API keys (never commit this)
├── task_payloads/                   # experiment definitions
│   ├── oddbal_task_payload.yaml
│   ├── stroop_task_payload.yaml
│   └── theory_of_mind_task_payload.yaml
├── experiment configurations/       # per-model run settings
│   └── ...
├── Task_Loader.py / PromptBuilder.py / ExperimentRunner.py /
│   AnalysisEngine.py / ReportBuilder.py / Validator.py / ParserEngine.py
└── *ModelAdapter.py                 # one per backend
```

## The Single-File-Change Idea

The intent: edit a task payload, run `main.py`, get a different experiment with
no code changes. That's the design target. Whether it currently holds without
exception is covered honestly below — it mostly does, with specific gaps.

## Current Experiments

1. **Oddball** (`oddbal_task_payload.yaml`) — classify Unicode shapes as
   STANDARD (⬢ ▲ ■) or ODDBALL (⬟ ★), 100 trials, ~80/20 split.
2. **Stroop** (`stroop_task_payload.yaml`) — name the ink color of color words,
   classic word/color interference.
3. **Theory of Mind** (`theory_of_mind_task_payload.yaml`) — false-belief
   reasoning tasks.

## Supported Models

| Model | Adapter |
|---|---|
| OpenAI GPT | `OpenAiModelAdapter` |
| Anthropic Claude | `AnthropicModelAdapter` |
| Gemini | `GeminiModelAdapter` |
| DeepSeek | `DeepSeekModelAdapter` |
| Ollama (local) | `OllamaModelAdapter` |

All five adapters exist and are wired into `ModelAdapter.py`'s dispatch. Whether
a given run succeeds also depends on the issues below.

## Known Issues (from direct code audit)

These were found by actually running the pipeline against real payloads, not by
reading code in isolation. Status reflects this repo's code as last checked —
verify against your current local copy before trusting it.

- **`Task_Loader._normalize_response_contract`**: for any payload using the v2
  `response_contract:` shape, this silently discards the built contract
  (`return {}` instead of `return normalized`). Affects any experiment where the
  payload declares `response_contract` explicitly (the oddball payload does).
  Symptom: crashes on the first trial with
  `ValueError: expected_answer.field is required...`.
- **`PromptBuilder._get_field_order`**: fields marked `display: false` in the
  schema, or fields not declared in the schema at all (like `correct_label`),
  can still leak into the rendered prompt via the "show undeclared fields"
  fallback. Confirmed this exposed the ground-truth answer directly in the
  stimulus block on at least one real model run — treat any accuracy numbers
  from before this is fixed as unreliable.
- **`ExperimentRunner.finish()`**: unconditionally reads
  `summary['accuracy_rate']` and `summary['protocol_adherence_rate']`. Crashes
  on any experiment (e.g. a pure reaction-time task) that doesn't enable both
  metrics.
- **`ReportBuilder`**: text report output joins lines with a literal two-character
  `\n` instead of a real newline in at least one code path — produces a
  single-line summary/report file instead of a readable one.
- `stop_after_trials: null` handling in `ExperimentRunner.start()`/
  `execute_trials()` — this one **is** handled correctly here.

None of these require a redesign — each is a one-line fix once caught by
actually running the code end to end rather than trusting a status comment.

## Experiment Workflow

1. Load model + experiment configuration
2. Load and normalize the task payload
3. Run trials against the selected model
4. Analyze responses (accuracy, protocol adherence, response time)
5. Generate reports

## Creating a New Experiment

1. Copy an existing payload under `task_payloads/`
2. Edit stimuli, instructions, and rules
3. Update the experiment metadata (id, name, description)
4. Run `python main.py` and check the actual rendered prompt and output files,
   not just that it ran without an exception — a clean exit doesn't mean the
   ground truth stayed hidden or the scoring was correct.

See `Configuration_Schema.yaml` for the full schema.

## Work in Progress

- Core framework: functional, with the caveats above
- Multi-model support: all five adapters present
- Three experiment types ready
- Web interface, real-time analysis, curated experiment library, richer export
  formats: not yet started

## Contribution Philosophy

Suggestions and contributions are welcome — new experiments, schema
improvements, new metrics, documentation, and bug reports (including anything
this audit missed).

## Acknowledgments

- ExecutiveAudit: original framework design
- AI-assisted audit: verified runtime behavior against the claims in the first
  README and corrected this version accordingly
- AI community and cognitive science research for inspiration and grounding

---

*Frames — understanding AI systems by actually running the experiment, not just
reading the summary of it.*
