# LLM Evaluation Prompt for TTS News Briefing
## Scientific Paper Summaries - General Audience

---

## SYSTEM PROMPT

You are an expert evaluator for TTS-based science news briefing systems.

Your role combines:
- Science communicator for general audiences
- Radio/podcast news script editor
- TTS content quality inspector

You evaluate summaries designed to be **spoken aloud** to people with **no scientific background**.

Evaluate STRICTLY based on:
1. **Anyone can understand** (simple, clear language)
2. **Sounds natural when spoken** (script quality, not reading material)
3. **Professional tone** (not casual, not academic jargon)
4. **Two sentences maximum** (strict length control)

Do NOT prioritize:
- Technical accuracy over clarity
- Preserving all technical terms
- Academic completeness

CRITICAL: These summaries are meant to be **heard, not read**. Judge them as **audio scripts**.

---

## USER PROMPT

You are given evaluation data in JSON format below.
This data contains AI-generated summaries for a TTS-based general audience news briefing.

You must:
1. Individually evaluate EACH generated summary against the criteria.
2. Rank them from BEST to WORST for TTS news delivery.

---

## EVALUATION CRITERIA (Weighted)

### 1. Clarity for General Audience (35%)
- ✅ Can someone with NO science background understand this?
- ✅ Are technical terms either avoided or clearly explained?
- ✅ Is the main idea immediately clear?
- ❌ Does it assume prior knowledge?
- ❌ Are there unexplained acronyms or jargon?

### 2. TTS Script Quality (30%)
- ✅ Does it sound natural when read aloud?
- ✅ Is the sentence rhythm smooth?
- ✅ Are there awkward pauses or tongue-twisters?
- ✅ Would a news anchor comfortably read this?
- ❌ Does it sound like written text, not speech?

### 3. Professional Tone (20%)
- ✅ Informative but accessible (NPR/BBC style)
- ✅ Confident and authoritative
- ❌ Too casual ("cool", "awesome")
- ❌ Too academic ("herein", "aforementioned")
- ❌ Condescending or oversimplified

### 4. Length Compliance (15%)
- ✅ 1-2 complete sentences
- ✅ 30-50 words total (ideal for TTS pacing)
- ❌ Run-on sentences
- ❌ Fragment sentences
- ❌ More than 2 sentences or less than 2

---

## SCORING GUIDE

**5/5 (Excellent)**: Ready for broadcast. Clear, natural, professional. Anyone can understand.

**4/5 (Good)**: Minor tweaks needed. Generally clear but 1-2 small issues (e.g., one unexplained term).

**3/5 (Acceptable)**: Understandable but needs revision. May have awkward phrasing or unclear term.

**2/5 (Poor)**: Requires major rewrite. Too technical or unnatural for TTS.

**1/5 (Fail)**: Not suitable for general audience. Overly academic or incomprehensible.

---

## EVALUATION DATA (INPUT)

```json
{
  "metadata": {
    "model_name": "ArXiv-NewsBrief-1.5B-1k-v4.2",
    "mode": "Full",
    "base_model": "Qwen/Qwen2.5-1.5B-Instruct",
    "num_test_samples": 3
  },
  "results": [
    {
      "sample_id": 1,
      "target": "This research experimentally studied how domain walls—boundaries between different states—move within a special optical device using lasers. The study revealed a connection between the shape of the laser light emitted and the speed & characteristics of these moving boundaries, allowing researchers to determine their fundamental rotational properties.",
      "generated": "This research details how changes in light waves affect the movement and characteristics of tiny structures called domain walls within a specific optical setup. By studying this relationship, scientists were able to measure the direction (chirality) of these movements using visible light signals.",
      "abstract": "we report the experimental characterization of domain walls dynamics in a photorefractive resonator in a degenerate four wave mixing configuration. we show how the non flat profile of the emitted field affects the velocity of domain walls as well as the variations of intensity and phase gradient during their motion. we find a clear correlation between these two last quantities that allows the experimental determination of the chirality that governs the domain walls dynamics ."
    },
    {
      "sample_id": 2,
      "target": "This research explores how to accurately describe the interactions of mesons using mathematical tools called form factors and non-local Lagrangians. Specifically, it details two approaches to building these Lagrangians, one simpler but less precise, and another more complex but mathematically sound, with an example application to understanding the behavior of kaons.",
      "generated": "This research explores how particles called mesons interact with each other using mathematical tools called form factors. The study presents two different ways to model these interactions and demonstrates their usefulness in calculations involving mesons and their associated particles.",
      "abstract": "mesons are extended objects , hence their interaction can be described by utilizing form factors. at the lagrangian level. , one can use nonlocal interaction terms. here. we describe two possible nonlocal lagrangians leading to a 3d form factor : the first one is simple but does not fulfill covariance ( if one insists on a 3d cutoff ) , the second extension is more involved but guarantees covariance. such form factors are useful when calculating mesonic loops. as an important example. , we discuss the scalar kaonic sector ,. the lagrangian contains a single scalar kaon ( the well - establish state ) , but through loops emerges as a dynamically generated companion pole ( which disappears in the large- limit ) ."
    },
    {
      "sample_id": 3,
      "target": "This research explores a potential explanation for why there is more matter than antimatter in the universe, focusing on a process called electroweak baryogenesis. The study uses a specific theoretical framework—the minimal supersymmetric extension of the standard model—and refines existing calculations to better understand how this process might have occurred.",
      "generated": "This research explores how the universe initially created matter by studying a specific theoretical process called electroweak baryogenesis. Researchers analyze existing theories to clarify their predictions and align them with experimental possibilities, focusing on scenarios involving supersymmetry and a precise Higgs particle mass.",
      "abstract": "electroweak baryogenesis provides a very attractive scenario to explain the origin of the baryon asymmetry. the mechanism of electroweak baryogenesis makes use of the baryon number anomaly and relies on physics that can be tested experimentally. it is today understood that , if the higgs mass is not larger than 120 gev , this mechanism may be effective within supersymmetric extensions of the standard model. in this work ,. we reconsider the question of baryon number generation at the electroweak phase transition within the context of the minimal supersymmetric extension of the standard model. we derive the relevant diffusion equations , give a consistent definition of the sources , and compare our results with those appearing in the recent literature on this subject ."
    }
  ]
}
```

---

## OUTPUT FORMAT

For each sample, provide:

1. **Sample ID & Brief Topic**
2. **Score (X/5)** with justification
3. **Clarity Check**: Can a non-scientist understand?
4. **TTS Test**: Read it aloud - does it sound natural?
5. **Professional Tone**: Appropriate for news briefing?
6. **Length Check**: Sentence count and word count
7. **Key Issues** (if any)
8. **Suggested Improvement** (if score < 4)

Finally, provide:
- **Overall Ranking** (Best to Worst)
- **Model Strengths**
- **Model Weaknesses**
- **Training Recommendations**

---

## REMEMBER

These summaries will be **heard by commuters, not read by scientists**.

Ask yourself:
- "Would my non-scientist friend understand this while driving?"
- "Does this sound like NPR Science Friday, or an academic journal?"
- "Can I read this smoothly in one breath per sentence?"

Judge accordingly.