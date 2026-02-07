"""
VISUAL DIAGRAMS: Confidence Score Mathematics
==============================================
"""

print("""
╔══════════════════════════════════════════════════════════════════════╗
║          DIAGRAM 1: NLI MODEL CONFIDENCE (Softmax Function)          ║
╚══════════════════════════════════════════════════════════════════════╝

INPUT:
+------------------------------------------------------------------+
| Premise:    "New employees serve a probation period of 3 months"|
| Hypothesis: "The probation period is 6 months"                  |
+------------------------------------------------------------------+
                              |
                              v
                    +---------+---------+
                    |   NLI MODEL       |
                    |  RoBERTa-large    |
                    +---------+---------+
                              |
                              v
STEP 1: RAW LOGITS (Neural Network Output)
+------------------------------------------------------------------+
| Contradiction:  3.2   (highest - claims contradict)             |
| Neutral:       -1.5                                              |
| Entailment:    -2.1                                              |
+------------------------------------------------------------------+
                              |
                              v
STEP 2: SOFTMAX TRANSFORMATION
+------------------------------------------------------------------+
|            e^x                                                   |
|  P(x) = --------    (x = each logit)                            |
|          Σ e^x                                                   |
|                                                                  |
|  e^3.2  = 24.53                                                  |
|  e^-1.5 = 0.22                                                   |
|  e^-2.1 = 0.12                                                   |
|  ─────────────────                                               |
|  Sum    = 24.87                                                  |
+------------------------------------------------------------------+
                              |
                              v
STEP 3: PROBABILITIES (Normalized to 0-1)
+------------------------------------------------------------------+
|                                                                  |
|  ████████████████████████████████████████████████  98.6%        |
|  CONTRADICTION                                                   |
|                                                                  |
|  █  0.9%                                                         |
|  NEUTRAL                                                         |
|                                                                  |
|  ▌ 0.5%                                                          |
|  ENTAILMENT                                                      |
|                                                                  |
+------------------------------------------------------------------+
                              |
                              v
FINAL RESULT:
+------------------------------------------------------------------+
| Classification: CONTRADICTED                                     |
| Confidence:     98.6%  <--- This is the individual claim score!  |
+------------------------------------------------------------------+




╔══════════════════════════════════════════════════════════════════════╗
║          DIAGRAM 2: TRUST SCORE CALCULATION FORMULA                  ║
╚══════════════════════════════════════════════════════════════════════╝

                    OVERALL TRUST SCORE FORMULA
                    ===========================

              Supported Claims           Contradicted Claims
              ----------------    -      -------------------  × 0.5
               Total Claims                 Total Claims

                    |                            |
                    v                            v
              +----------+                 +-----------+
              |   +1.0   |                 |   -0.5    |
              | per claim|                 | per claim |
              +----------+                 +-----------+
                    |                            |
                    +------------+---------------+
                                 |
                                 v
                      +---------------------+
                      |   Clamp to [0, 1]   |
                      +---------------------+
                                 |
                                 v
                          TRUST SCORE %




╔══════════════════════════════════════════════════════════════════════╗
║                  DIAGRAM 3: REAL EXAMPLES                            ║
╚══════════════════════════════════════════════════════════════════════╝

EXAMPLE 1: Legal Demo (37.5%)
┌────────────────────────────────────────────────────────────────┐
│ Claims Visualization:                                          │
│                                                                │
│  ●  ●  ●  ●                                                    │
│  ✓  ✓  ✗  ?                                                    │
│  ↑  ↑  ↑  ↑                                                    │
│  2x      1x   1x                                               │
│  Supported  Contradicted  Unverifiable                         │
│                                                                │
│ Calculation:                                                   │
│  Trust = (2/4) - (1/4) × 0.5                                   │
│        = 0.50  - 0.125                                         │
│        = 0.375                                                 │
│        = 37.5%                                                 │
│                                                                │
│ Visual Meter:                                                  │
│  [███████░░░░░░░░░░░] 37.5%                                    │
└────────────────────────────────────────────────────────────────┘


EXAMPLE 2: Medical Demo (75.0%)
┌────────────────────────────────────────────────────────────────┐
│ Claims Visualization:                                          │
│                                                                │
│  ●  ●  ●  ●                                                    │
│  ✓  ✓  ✓  ?                                                    │
│  ↑  ↑  ↑  ↑                                                    │
│  3x          1x                                                │
│  Supported    Unverifiable                                     │
│                                                                │
│ Calculation:                                                   │
│  Trust = (3/4) - (0/4) × 0.5                                   │
│        = 0.75  - 0.00                                          │
│        = 0.75                                                  │
│        = 75.0%                                                 │
│                                                                │
│ Visual Meter:                                                  │
│  [███████████████░░░] 75.0%                                    │
└────────────────────────────────────────────────────────────────┘


EXAMPLE 3: Perfect Score (100%)
┌────────────────────────────────────────────────────────────────┐
│ Claims Visualization:                                          │
│                                                                │
│  ●  ●  ●  ●  ●                                                 │
│  ✓  ✓  ✓  ✓  ✓                                                 │
│  ↑  ↑  ↑  ↑  ↑                                                 │
│  5x ALL Supported!                                             │
│                                                                │
│ Calculation:                                                   │
│  Trust = (5/5) - (0/5) × 0.5                                   │
│        = 1.00  - 0.00                                          │
│        = 1.00                                                  │
│        = 100%                                                  │
│                                                                │
│ Visual Meter:                                                  │
│  [████████████████████] 100%                                   │
└────────────────────────────────────────────────────────────────┘


EXAMPLE 4: All Wrong (0%)
┌────────────────────────────────────────────────────────────────┐
│ Claims Visualization:                                          │
│                                                                │
│  ●  ●  ●  ●                                                    │
│  ✗  ✗  ✗  ✗                                                    │
│  ↑  ↑  ↑  ↑                                                    │
│  4x ALL Contradicted                                           │
│                                                                │
│ Calculation:                                                   │
│  Trust = (0/4) - (4/4) × 0.5                                   │
│        = 0.00  - 0.50                                          │
│        = -0.50 → Clamped to 0.0                                │
│        = 0%                                                    │
│                                                                │
│ Visual Meter:                                                  │
│  [░░░░░░░░░░░░░░░░░░░░] 0%                                     │
└────────────────────────────────────────────────────────────────┘




╔══════════════════════════════════════════════════════════════════════╗
║             DIAGRAM 4: COMPLETE PIPELINE WITH SCORES                 ║
╚══════════════════════════════════════════════════════════════════════╝

                         FULL WORKFLOW
                         =============

┌──────────────────────────────────────────────────────────────┐
│  LLM TEXT:                                                   │
│  "Employee probation is 6 months. Annual leave is 20 days." │
└──────────────────────────────────────────────────────────────┘
                          |
                          v
                 ┌────────────────┐
                 │ CLAIM SPLITTER │
                 └────────────────┘
                    |           |
        +-----------+           +-----------+
        |                                   |
        v                                   v
┌─────────────────┐                ┌─────────────────┐
│ Claim 1:        │                │ Claim 2:        │
│ "probation      │                │ "annual leave   │
│  is 6 months"   │                │  is 20 days"    │
└─────────────────┘                └─────────────────┘
        |                                   |
        v                                   v
┌─────────────────┐                ┌─────────────────┐
│ RAG RETRIEVAL   │                │ RAG RETRIEVAL   │
│ Evidence:       │                │ Evidence:       │
│ "3 months"      │                │ "20 days"       │
└─────────────────┘                └─────────────────┘
        |                                   |
        v                                   v
┌─────────────────┐                ┌─────────────────┐
│ NLI VERIFY      │                │ NLI VERIFY      │
│ Result:         │                │ Result:         │
│ CONTRADICTED    │                │ SUPPORTED       │
│ Conf: 95.4%     │                │ Conf: 97.2%     │
└─────────────────┘                └─────────────────┘
        |                                   |
        +-------------------+---------------+
                            |
                            v
                   ┌────────────────┐
                   │ AGGREGATE ALL  │
                   │ CLAIM RESULTS  │
                   └────────────────┘
                            |
                            v
              +---------------------------+
              | Trust Score Calculation:  |
              |                           |
              | (1/2) - (1/2) × 0.5       |
              | = 0.50 - 0.25             |
              | = 0.25                    |
              | = 25%                     |
              +---------------------------+




╔══════════════════════════════════════════════════════════════════════╗
║                       KEY INSIGHTS                                   ║
╚══════════════════════════════════════════════════════════════════════╝

LEGEND:
-------
●  = Individual claim
✓  = Supported (adds +1.0/total to score)
✗  = Contradicted (subtracts 0.5/total from score)
?  = Unverifiable (adds 0.0 to score)

WEIGHTS:
--------
Supported:     +1.0  (full positive contribution)
Contradicted:  -0.5  (penalized, but not as harsh as -1.0)
Unverifiable:   0.0  (neutral, neither helps nor hurts)

WHY 0.5 PENALTY?
----------------
- Balance between strictness and leniency
- Contradictions are serious but not catastrophic
- Allows for some forgiveness in mixed-quality outputs
- Tunable parameter: can adjust based on use case

INTERPRETATION:
--------------
100%  = Perfect, all claims verified
75%+  = High trust, mostly accurate
50%   = Moderate trust, half verified
25%   = Low trust, significant issues
0%    = No trust, mostly/all wrong
""")
