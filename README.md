# TikTok Shop Sentiment Analysis

## Somethinc vs Skintific — 2.000 Reviews Compared

Live dashboard → [somethinc-vs-skintific.vercel.app](https://somethinc-vs-skintific.vercel.app)

---

### What this is

A side-by-side sentiment breakdown of two Indonesian skincare brands on TikTok Shop. I scraped 1.000 reviews per brand (2.000 total) and ran them through InSet Lexicon sentiment analysis — a rule-based Indonesian sentiment dictionary, not a black-box model. No GPT, no API calls for the analysis itself.

---

### What I looked at

- **Sentiment distribution** — positive / neutral / negative ratios
- **Product-level complaints** — which SKUs drive dissatisfaction
- **Competitive gaps** — where Somethinc loses to Skintific (and vice versa)
- **Operational issues** — shipping, packaging, wrong items
- **Price sensitivity** — how often price comes up and what it does to ratings
- **Affiliate influence** — inflasi rating dari review afiliasi
- **Anomaly detection** — reviews with 5-star rating and negative text body
- **Temporal patterns** — do complaints cluster on certain days?
- **Repeat purchase & feature requests** — loyalty and R&D signals

---

### Tech stack

| Layer | Tool |
|---|---|
| Data | Python scraping (Tokopedia), pandas |
| Sentiment | InSet Lexicon Indonesia |
| Dashboard | Vanilla HTML + CSS + Chart.js |
| Deploy | Vercel (static) |

No React, no database, no backend. The dashboard reads a single JSON file — a deliberate choice to keep load times fast and hosting free.

---

### Key findings (data, not opinion)

- Somethinc rating **4.73** vs Skintific **4.36** — gap **0.37**
- Somethinc positive % **81.7%** vs Skintific **78%**
- **68%** of Somethinc reviews mention price — it's the #1 barrier to entry
- **96 suspicious reviews** (4.8% of total) — high rating + negative text. Mostly Skintific affiliate reviews
- Skintific operational complaints **20.1%** vs Somethinc **13.3%**
- Somethinc repeat purchase **36.3%** vs Skintific **16.5%** — stronger brand loyalty
- Skintific rating inflation from affiliates **10%** vs Somethinc **-1%** (yes, negative — affiliate reviews actually rate Somethinc slightly lower)

---

### How to run locally

```bash
git clone https://github.com/fityanhanif/TikTok-Shop-Sentiment-Analysis-Somethinc-VS-Skintific.git
cd TikTok-Shop-Sentiment-Analysis-Somethinc-VS-Skintific
# Open dashboard/index.html in a browser — no build step
```

---

### Limitations

- **Synthetic-like preprocessing**: review text was cleaned and normalized before sentiment scoring. Edge cases (sarcasm, mixed language) are not handled well by lexicon-based analysis
- **Temporal bias**: reviews span different time windows — trend comparisons should be read as directional, not exact
- **No causal inference**: correlation between affiliate mentions and high ratings doesn't prove causation
- **Data volume**: 2.000 reviews is enough for patterns, not for statistical significance on sub-group comparisons

---

### Author

Fityan Hanif — Data Analyst.
Built as a portfolio project. CV and other work on request.
