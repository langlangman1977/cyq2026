# Estimation Rates

Use this reference when classifying code and calibrating the calculator input.

## Coding Productivity Rates

| Category Key | Label | Low | High | Typical examples |
| --- | --- | --- | --- | --- |
| `simple_crud_ui_boilerplate` | Simple CRUD/UI/boilerplate | 50 | 80 | Forms, lists, repetitive layouts, config screens |
| `standard_views` | Standard views with logic | 35 | 55 | Typical screens, moderate UI logic |
| `complex_ui` | Complex UI | 25 | 40 | Custom components, transitions, rich onboarding |
| `business_logic` | Business logic / API clients | 30 | 50 | Networking, state transforms, service orchestration |
| `database_persistence` | Database / persistence | 30 | 50 | Queries, migrations, schemas, CRUD storage |
| `audio_video_processing` | Audio/video processing | 20 | 30 | Encoding, streaming, AV pipelines |
| `gpu_shader` | GPU / shader programming | 15 | 25 | Metal, CUDA, render or compute pipelines |
| `native_interop` | Native C/C++ interop | 15 | 25 | FFI, bridging, unsafe integration |
| `system_extensions` | System extensions / plugins | 15 | 25 | OS extensions, daemons, drivers |
| `on_device_ml` | On-device ML inference | 15 | 25 | CoreML, MLX, ONNX integration |
| `tests` | Tests | 50 | 80 | Assertions, fixtures, regression coverage |
| `config_build` | Config / build files | 40 | 60 | CI, manifests, build config |
| `documentation` | Documentation | 60 | 100 | READMEs, markdown docs, comments-only files |

## Overhead Multipliers

Apply these through `cost_calculator.py`, not in the raw category assignment.

| Category | Low | High |
| --- | --- | --- |
| Architecture & design | 12% | 15% |
| Debugging & troubleshooting | 20% | 25% |
| Code review & refactoring | 8% | 12% |
| Documentation | 5% | 8% |
| Integration & testing | 15% | 18% |
| Learning curve | 8% | 15% |

Combined overhead range: roughly 68% to 93% of base coding hours.

## Hourly Market Rates

Baseline: 2025 US market assumptions.

| Role | Low | Mid | High |
| --- | --- | --- | --- |
| Senior Engineer (generalist) | 100 | 150 | 225 |
| Senior Engineer (specialist) | 125 | 175 | 250 |
| Product Management | 125 | 160 | 200 |
| UX/UI Design | 100 | 140 | 175 |
| Engineering Management | 150 | 185 | 225 |
| QA/Testing | 75 | 100 | 125 |
| Project/Program Management | 100 | 125 | 150 |
| Technical Writing | 75 | 100 | 125 |
| DevOps/Platform | 125 | 160 | 200 |

Use these defaults unless the user explicitly asks for another region, market, or pricing basis.

## Role Ratios By Company Stage

These are additional hours as a percentage of engineering hours.

| Role | Solo | Lean Startup | Growth Co | Enterprise |
| --- | --- | --- | --- | --- |
| Product Management | 0% | 15% | 30% | 40% |
| UX/UI Design | 0% | 15% | 25% | 35% |
| Engineering Management | 0% | 5% | 15% | 20% |
| QA/Testing | 0% | 5% | 20% | 25% |
| Project/Program Management | 0% | 0% | 10% | 15% |
| Technical Writing | 0% | 0% | 5% | 10% |
| DevOps/Platform | 0% | 5% | 15% | 20% |

Shortcut team multipliers:

- Solo: `1.0x`
- Lean Startup: `~1.45x`
- Growth Company: `~2.2x`
- Enterprise: `~2.65x`

## Organizational Efficiency

Use these to translate total hours into single-developer calendar time.

| Company Type | Efficiency | Effective Coding Hrs/Week |
| --- | --- | --- |
| Solo/Startup (lean) | 65% | 26 |
| Growth Company | 55% | 22 |
| Enterprise | 45% | 18 |
| Large Bureaucracy | 35% | 14 |

## Sanity Check Bounds

Target effective throughput:

- Too conservative: `< 12` effective lines/hour
- Target range: `15-30` effective lines/hour
- Too aggressive: `> 40` effective lines/hour

If the result falls outside the target range, adjust the classification or explain why the repo is
an outlier.

## Claude ROI Constants

Use these only when real session analysis is unavailable or incomplete.

| Parameter | Value |
| --- | --- |
| Claude coding speed range | 200-500 lines/hr |
| Claude coding speed midpoint | 350 lines/hr |
| Human baseline rate for comparison | $150/hr |
| Claude subscription range | $20-200/month |

## Classification Heuristics

- Default most application code to `business_logic`, `standard_views`, or `database_persistence`.
- Use specialist buckets only when file contents justify them.
- Keep tests, config, and docs separate even if they live next to product code.
- If one file mixes categories, classify by the dominant work.
- When a directory is uniform, group it to save time, but call out exceptions explicitly.
