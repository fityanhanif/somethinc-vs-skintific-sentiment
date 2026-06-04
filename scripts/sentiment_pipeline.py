#!/usr/bin/env python3
"""
Sentiment & Analysis Pipeline
InSet Lexicon (Indonesian sentiment) + 10 Problem Statements
"""

import json
import csv
import math
import re
import random
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DASHBOARD_DATA = PROJECT_ROOT / "dashboard" / "data"

# ═══════════════════════════════════════════════════════════════════
# 1. InSet Lexicon — Indonesian Sentiment Words
# ═══════════════════════════════════════════════════════════════════

POSITIVE_LEXICON = {
    # Core positive sentiment
    "bagus": 3, "baik": 2, "mantap": 4, "keren": 4, "cocok": 3,
    "recommended": 4, "recomended": 4, "rekomendasi": 3, "rekomen": 3,
    "suka": 3, "sangat": 2, "terbaik": 5, "terima kasih": 3, "makasih": 3,
    "puas": 4, "memuaskan": 4, "senang": 3, "happy": 3, "love": 4,

    # Product quality
    "lembut": 3, "ringan": 2, "halus": 3, "cerah": 3, "glowing": 4,
    "glow": 3, "kenyal": 3, "sehat": 3, "lembab": 4, "melembabkan": 4,
    "mencerahkan": 4, "bersih": 3, "wangi": 2, "fresh": 3, "segar": 3,
    "natural": 2, "alus": 2, "mulus": 3, "kencang": 2, "kenyang": 2,

    # Efficacy
    "works": 4, "berhasil": 3, "berfungsi": 3, "efektif": 4, "ampuh": 4,
    "manjur": 4, "berkhasiat": 4, "hasil": 3, "berubah": 2, "perubahan": 2,

    # Price value
    "murah": 3, "worth": 4, "ekonomis": 3, "hemat": 3, "sebanding": 3,
    "terjangkau": 3, "murah meriah": 4, "cocok di kantong": 3,

    # Packaging
    "cantik": 2, "estetik": 3, "elegan": 3, "praktis": 3, "simple": 2,
    "aman": 2, "kedap": 3, "higienis": 3,

    # Operations
    "cepat": 3, "cepat sampai": 4, "packing rapi": 4, "packing bagus": 4,
    "responsive": 3, "ramah": 2, "cepat respon": 3, "good": 3, "nice": 3,
    "ok": 2, "oke": 2, "okelah": 1, "lumayan": 1,

    # Loyalty signals
    "langganan": 4, "repeat": 4, "order lagi": 4, "beli lagi": 4,
    "restock": 4, "setia": 3,

    # Intensifiers
    "sangat": 1, "banget": 1, "sekali": 1, "super": 2, "bangett": 1,
    "sungguh": 1, "benar-benar": 1,

    # Textures (positive)
    "creamy": 2, "lotion": 1, "gel": 1, "watery": 1, "mousse": 1,
}

NEGATIVE_LEXICON = {
    # Core negative sentiment
    "jelek": -4, "buruk": -4, "tidak cocok": -4, "gak cocok": -4,
    "nggak cocok": -4, "kecewa": -4, "mengecewakan": -5, "kapok": -4,
    "menyesal": -4, "nyesel": -4, "gak suka": -3, "nggak suka": -3,
    "gasuka": -3, "benci": -5, "parah": -3, "busuk": -4,

    # Product issues
    "breakout": -5, "bruntus": -4, "beruntusan": -4, "jerawatan": -4,
    "iritasi": -5, "perih": -4, "pedih": -4, "gatal": -4, "kemerahan": -4,
    "merah-merah": -4, "kering": -3, "kasar": -3, "lengket": -3,
    "berat": -2, "minyak": -2, "berminyak": -3, "komedo": -2,
    "bopeng": -3, "bekas jerawat": -2, "beruntus": -3, "bruntusan": -3,

    # Quality complaints
    "tidak bagus": -4, "gak bagus": -4, "nggak bagus": -4,
    "nggak enak": -3, "gak enak": -3, "tidak enak": -3,
    "tidak nyaman": -3, "gak nyaman": -3,
    "tidak ada efek": -4, "gak ada efek": -4, "nggak ada efek": -4,
    "gak ada perubahan": -3, "nggak ada perubahan": -3,
    "tidak berfungsi": -4, "gak works": -4, "nggak works": -4,
    "standar": -1, "biasa": -1, "biasa aja": -2,
    "begitu-begitu aja": -2, "standar banget": -2,

    # Price complaints
    "mahal": -3, "kemahalan": -4, "overpriced": -4, "pricey": -2,
    "gak worth": -4, "nggak worth": -4, "sayang duit": -5,
    "boros": -3, "percuma": -4, "uang terbuang": -5,

    # Operational issues
    "lama": -3, "lambat": -3, "lama banget": -4, "telat": -3,
    "bocor": -3, "tumpah": -4, "penyok": -3, "rusak": -4,
    "packing jelek": -4, "packing buruk": -4, "packing rusak": -4,
    "packing bocor": -4, "packing penyok": -3,
    "bubble wrap": -1, "dus penyok": -3,

    # Customer service
    "cs lambat": -3, "admin slow": -3, "respon lama": -3,
    "customer service": -1, "admin": -1,

    # Negation + disappointment
    "tidak": -1, "nggak": -1, "gak": -1, "ga": -1,
    "tidak sesuai": -3, "gak sesuai": -3, "nggak sesuai": -3,
    "tidak sebagus": -3, "gak sebagus": -3,
    "overrated": -4, "hype": -2, "viral doang": -3,

    # Texture (negative)
    "berpasir": -3, "menggumpal": -2, "terlalu cair": -2,
    "terlalu kental": -2, "lengket": -3, "sticky": -3,
    "berat di wajah": -3, "berat dimuka": -3, "gerah": -2,
}


def tokenize(text):
    """Tokenize Indonesian text into words and bigrams."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    tokens = text.split()
    # Add bigrams for multi-word expressions
    bigrams = [' '.join(tokens[i:i+2]) for i in range(len(tokens)-1)]
    return tokens + bigrams


def calculate_sentiment(text):
    """
    Score sentiment using InSet-derived lexicon.
    Returns: (score, positive_count, negative_count, label)
    """
    tokens = tokenize(text)
    score = 0
    pos_count = 0
    neg_count = 0
    matched_words = []

    for token in tokens:
        if token in POSITIVE_LEXICON:
            val = POSITIVE_LEXICON[token]
            score += val
            pos_count += 1
            matched_words.append((token, pos_count))
        elif token in NEGATIVE_LEXICON:
            val = NEGATIVE_LEXICON[token]
            score += val
            neg_count += 1
            matched_words.append((token, neg_count))

    if score > 1:
        label = "positive"
    elif score < -1:
        label = "negative"
    else:
        label = "neutral"

    return score, pos_count, neg_count, label


# ═══════════════════════════════════════════════════════════════════
# 2. Load & Process Data
# ═══════════════════════════════════════════════════════════════════

def load_reviews():
    """Load raw reviews from JSON."""
    path = DATA_RAW / "tiktok_reviews_raw.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def process_all_reviews(reviews):
    """Run sentiment on all reviews and add scores."""
    for r in reviews:
        score, pos_c, neg_c, label = calculate_sentiment(r["text"])
        r["sentiment_score"] = score
        r["sentiment_pos_count"] = pos_c
        r["sentiment_neg_count"] = neg_c
        r["sentiment_ml_label"] = label  # machine-labeled (override generated label)
    return reviews


# ═══════════════════════════════════════════════════════════════════
# 3. Analysis Modules — 10 Problem Statements
# ═══════════════════════════════════════════════════════════════════

def analyze_01_product_improvement(reviews, brand="somethinc"):
    """
    1. Peningkatan Produk — Quality Gap Analysis
    What specific improvements needed per product?
    """
    brand_reviews = [r for r in reviews if r["brand"] == brand]
    products = set(r["product_name"] for r in brand_reviews)

    # Aspect extraction from negative reviews
    aspects_def = {
        "tekstur": ["tekstur", "krim", "cair", "lotion", "kental", "ringan", "berat", "lengket", "kasar", "halus", "creamy", "gel", "mousse"],
        "aroma": ["wangi", "aroma", "bau", "scent", "fragrance", "parfum", "wewangian"],
        "kemasan": ["kemasan", "packaging", "botol", "tube", "dus", "segel", "bocor", "penyok", "tumpah"],
        "hasil": ["hasil", "efek", "perubahan", "glowing", "cerah", "lembab", "kering", "jerawat", "breakout"],
        "kecocokan_kulit": ["cocok", "iritasi", "perih", "gatal", "merah", "breakout", "bruntus", "beruntusan"],
        "harga": ["harga", "mahal", "murah", "worth", "pricey", "ekonomis"],
    }

    results = {}
    for prod in sorted(products):
        prod_revs = [r for r in brand_reviews if r["product_name"] == prod]
        neg_revs = [r for r in prod_revs if r["sentiment_ml_label"] == "negative"]
        neg_count = len(neg_revs)
        total = len(prod_revs)

        # Aspect complaint count
        aspect_complaints = Counter()
        aspect_reviews = {}
        for asp, keywords in aspects_def.items():
            count = 0
            sample_texts = []
            for r in neg_revs:
                txt_lower = r["text"].lower()
                if any(kw in txt_lower for kw in keywords):
                    count += 1
                    if len(sample_texts) < 3:
                        sample_texts.append(r["text"][:120] + "...")
            aspect_complaints[asp] = count
            aspect_reviews[asp] = sample_texts

        # Top complaint keywords from negative reviews
        all_words = Counter()
        for r in neg_revs:
            words = re.findall(r'\w+', r["text"].lower())
            for w in words:
                if len(w) > 3 and w not in ['dengan', 'untuk', 'karena', 'tetapi', 'adalah', 'dimana']:
                    all_words[w] += 1
        top_complaints = dict(all_words.most_common(10))

        avg_rating = sum(r["rating"] for r in prod_revs) / total if total else 0
        avg_score = sum(r["sentiment_score"] for r in prod_revs) / total if total else 0

        results[prod] = {
            "total_reviews": total,
            "negative_reviews": neg_count,
            "negative_pct": round(neg_count / total * 100, 1) if total else 0,
            "avg_rating": round(avg_rating, 2),
            "avg_sentiment": round(avg_score, 2),
            "aspect_complaints": {k: {"count": v, "pct": round(v/neg_count*100, 1) if neg_count else 0, "samples": aspect_reviews[k]}
                                  for k, v in aspect_complaints.most_common() if v > 0},
            "top_complaint_words": top_complaints,
        }

    return results


def analyze_02_competitive_benchmark(reviews):
    """
    2. Keunggulan Kompetitor — Brand Sentiment Comparison
    Why is competitor selling more?
    """
    brands = ["somethinc", "skintific"]
    results = {}
    for brand in brands:
        br = [r for r in reviews if r["brand"] == brand]
        neg = [r for r in br if r["sentiment_ml_label"] == "negative"]
        pos = [r for r in br if r["sentiment_ml_label"] == "positive"]

        # Most praised words (in positive reviews)
        praised = Counter()
        for r in pos:
            words = re.findall(r'\w+', r["text"].lower())
            praised.update(w for w in words if len(w) > 3 and w not in ['dengan', 'untuk', 'karena', 'tetapi', 'adalah'])
        top_praised = dict(praised.most_common(15))

        # Most complained words (in negative reviews)
        complained = Counter()
        for r in neg:
            words = re.findall(r'\w+', r["text"].lower())
            complained.update(w for w in words if len(w) > 3 and w not in ['dengan', 'untuk', 'karena', 'tetapi', 'adalah'])
        top_complained = dict(complained.most_common(10))

        # Rating distribution
        rating_dist = Counter(r["rating"] for r in br)

        results[brand] = {
            "total_reviews": len(br),
            "avg_rating": round(sum(r["rating"] for r in br) / len(br), 2) if br else 0,
            "avg_sentiment_score": round(sum(r["sentiment_score"] for r in br) / len(br), 2) if br else 0,
            "positive_pct": round(len(pos) / len(br) * 100, 1) if br else 0,
            "negative_pct": round(len(neg) / len(br) * 100, 1) if br else 0,
            "neutral_pct": round(sum(1 for r in br if r["sentiment_ml_label"] == "neutral") / len(br) * 100, 1) if br else 0,
            "rating_distribution": {str(k): v for k, v in sorted(rating_dist.items())},
            "most_praised_words": top_praised,
            "most_complained_words": top_complained,
        }

    # Sentiment gap analysis
    som = results.get("somethinc", {})
    skn = results.get("skintific", {})
    gap = {
        "sentiment_gap": round(skn.get("avg_sentiment_score", 0) - som.get("avg_sentiment_score", 0), 2),
        "rating_gap": round(skn.get("avg_rating", 0) - som.get("avg_rating", 0), 2),
        "positive_gap": round(skn.get("positive_pct", 0) - som.get("positive_pct", 0), 1),
        "better_in": None,  # computed below
    }

    # Which aspects each brand wins
    aspects_check = {
        "tekstur": ["tekstur", "lembut", "ringan", "creamy", "halus"],
        "harga": ["murah", "ekonomis", "terjangkau", "worth", "hemat", "mahal"],
        "hasil": ["hasil", "cerah", "lembab", "glowing", "kering", "efek"],
        "kemasan": ["kemasan", "packaging", "botol", "tube", "dus"],
    }
    wins = {}
    for asp, keywords in aspects_check.items():
        som_score = sum(r["sentiment_score"] for r in reviews if r["brand"] == "somethinc" and any(kw in r["text"].lower() for kw in keywords))
        som_count = sum(1 for r in reviews if r["brand"] == "somethinc" and any(kw in r["text"].lower() for kw in keywords))
        skn_score = sum(r["sentiment_score"] for r in reviews if r["brand"] == "skintific" and any(kw in r["text"].lower() for kw in keywords))
        skn_count = sum(1 for r in reviews if r["brand"] == "skintific" and any(kw in r["text"].lower() for kw in keywords))
        som_avg = som_score / som_count if som_count else 0
        skn_avg = skn_score / skn_count if skn_count else 0
        wins[asp] = {
            "somethinc_avg": round(som_avg, 2),
            "skintific_avg": round(skn_avg, 2),
            "winner": "somethinc" if som_avg > skn_avg else "skintific" if skn_avg > som_avg else "tie",
            "gap": round(som_avg - skn_avg, 2),
        }

    gap["aspect_wins"] = wins
    results["sentiment_gap"] = gap

    return results


def analyze_03_feature_evaluation(reviews):
    """
    3. Evaluasi Fitur Utama — Product Anatomy Matrix
    Which product aspects are most complained about?
    """
    aspects_def = {
        "tekstur_konsistensi": ["tekstur", "konsistensi", "krim", "cair", "lotion", "kental", "berat", "ringan", "lengket", "kasar", "halus", "creamy", "mousse", "gel"],
        "aroma_wangi": ["wangi", "aroma", "bau", "scent", "fragrance", "parfum", "wewangian", "smell"],
        "kemasan_design": ["kemasan", "packaging", "botol", "tube", "dus", "segel", "desain", "bentuk", "ukuran", "praktis"],
        "formula_kandungan": ["formula", "kandungan", "bahan", "ceramide", "niacinamide", "retinol", "vitamin", "SPF", "PA", "actives", "bahan aktif"],
        "hasil_efek": ["hasil", "efek", "perubahan", "glowing", "cerah", "lembab", "kering", "halus", "kenyal", "kencang"],
        "after_feel": ["lengket", "berat", "ringan", "sticky", "gerah", "segar", "fresh", "nyaman", "nempel"],
    }

    # Per brand
    results = {}
    for brand in ["somethinc", "skintific"]:
        brand_revs = [r for r in reviews if r["brand"] == brand]
        neg_revs = [r for r in brand_revs if r["sentiment_ml_label"] == "negative"]
        pos_revs = [r for r in brand_revs if r["sentiment_ml_label"] == "positive"]

        brand_result = {}
        for asp, keywords in aspects_def.items():
            neg_asp = [r for r in neg_revs if any(kw in r["text"].lower() for kw in keywords)]
            pos_asp = [r for r in pos_revs if any(kw in r["text"].lower() for kw in keywords)]
            total_asp = len(neg_asp) + len(pos_asp)

            brand_result[asp] = {
                "total_mentions": total_asp,
                "negative_count": len(neg_asp),
                "positive_count": len(pos_asp),
                "complaint_ratio": round(len(neg_asp) / total_asp * 100, 1) if total_asp else 0,
                "net_sentiment": round(sum(r["sentiment_score"] for r in pos_asp) + sum(r["sentiment_score"] for r in neg_asp), 1) if total_asp else 0,
            }
        results[brand] = brand_result

    return results


def analyze_04_operational_issues(reviews):
    """
    4. Kendala Operasional — Logistics & CS Sentiment
    """
    ops_keywords = {
        "pengiriman_lambat": ["lama", "lambat", "telat", "nggak cepet", "gak cepet", "lama banget", "lama sekali"],
        "kemasan_rusak": ["rusak", "penyok", "bocor", "tumpah", "sobek", "remuk", "hancur", "dus penyok"],
        "packing_kurang": ["packing", "bubble wrap", "dus", "packing jelek", "packing buruk", "tanpa dus", "tanpa bubble"],
        "cs_respon": ["admin", "CS", "customer service", "respon", "slow respon", "lama respon", "dibalas"],
        "barang_salah": ["salah", "nggak sesuai", "gak sesuai", "salah kirim", "salah produk", "salah varian"],
        "ekspedisi": ["kurir", "ekspedisi", "jne", "jnt", "sicepat", "grab", "anteraja", "ninja"],
    }

    results = {}
    for brand in ["somethinc", "skintific"]:
        brand_revs = [r for r in reviews if r["brand"] == brand]

        # Find all reviews with TEXT evidence of operational issues (not random flag)
        ops_keywords_list = list(ops_keywords.values())
        brand_ops_revs = [
            r for r in brand_revs
            if any(kw in r["text"].lower() for kwlist in ops_keywords_list for kw in kwlist)
        ]
        total_ops_revs = len(brand_ops_revs)

        ops_detail = {}
        for issue, keywords in ops_keywords.items():
            matching = [r for r in brand_ops_revs if any(kw in r["text"].lower() for kw in keywords)]
            neg_matching = [r for r in matching if r["sentiment_ml_label"] == "negative"]

            # Average rating impact
            avg_rating = sum(r["rating"] for r in matching) / len(matching) if matching else 0

            ops_detail[issue] = {
                "total_mentions": len(matching),
                "negative_count": len(neg_matching),
                "avg_rating": round(avg_rating, 2),
                "sentiment_impact": round(sum(r["sentiment_score"] for r in matching) / len(matching), 2) if matching else 0,
                "pct_of_ops": round(len(matching) / total_ops_revs * 100, 1) if total_ops_revs else 0,
            }

        # False negatives: good product, bad ops → low rating
        false_negatives = [r for r in brand_revs if r not in brand_ops_revs and r["rating"] <= 3 and r["sentiment_ml_label"] == "neutral"]
        false_neg_count = len(false_negatives)
        ops_rating_impact = sum(r["rating"] for r in brand_ops_revs) / len(brand_ops_revs) if brand_ops_revs else 0
        non_ops_rating = sum(r["rating"] for r in brand_revs if r not in brand_ops_revs) / max(len([r for r in brand_revs if r not in brand_ops_revs]), 1)

        results[brand] = {
            "total_operational_mentions": total_ops_revs,
            "pct_of_all_reviews": round(total_ops_revs / len(brand_revs) * 100, 1) if brand_revs else 0,
            "operational_breakdown": ops_detail,
            "false_negatives_from_ops": false_neg_count,
            "avg_rating_with_ops_issue": round(ops_rating_impact, 2),
            "avg_rating_without_ops_issue": round(non_ops_rating, 2),
            "rating_gap_due_to_ops": round(ops_rating_impact - non_ops_rating, 2),
        }

    return results


def analyze_05_price_sensitivity(reviews):
    """
    5. Sensitivitas Harga — Price Elasticity of Sentiment
    """
    results = {}
    for brand in ["somethinc", "skintific"]:
        brand_revs = [r for r in reviews if r["brand"] == brand]

        # Reviews with price mentions
        price_mentions = [r for r in brand_revs if r["has_price_mention"]]
        discount_mentions = [r for r in brand_revs if r["has_discount_mention"]]
        no_price_mentions = [r for r in brand_revs if not r["has_price_mention"]]

        # Price sentiment: positive vs negative price mentions
        price_positive = [r for r in price_mentions if r["sentiment_ml_label"] == "positive"]
        price_negative = [r for r in price_mentions if r["sentiment_ml_label"] == "negative"]

        # Discount effect
        discount_positive = [r for r in discount_mentions if r["sentiment_ml_label"] == "positive"]
        discount_negative = [r for r in discount_mentions if r["sentiment_ml_label"] == "negative"]

        results[brand] = {
            "total_reviews": len(brand_revs),
            "price_mention_reviews": len(price_mentions),
            "discount_mention_reviews": len(discount_mentions),
            "no_price_mention_reviews": len(no_price_mentions),
            "avg_rating_price_mentioners": round(sum(r["rating"] for r in price_mentions) / len(price_mentions), 2) if price_mentions else 0,
            "avg_rating_discount_mentioners": round(sum(r["rating"] for r in discount_mentions) / len(discount_mentions), 2) if discount_mentions else 0,
            "avg_rating_no_price_mention": round(sum(r["rating"] for r in no_price_mentions) / len(no_price_mentions), 2) if no_price_mentions else 0,
            "avg_sentiment_price_mentioners": round(sum(r["sentiment_score"] for r in price_mentions) / len(price_mentions), 2) if price_mentions else 0,
            "avg_sentiment_no_price_mention": round(sum(r["sentiment_score"] for r in no_price_mentions) / len(no_price_mentions), 2) if no_price_mentions else 0,
            "discount_positive_pct": round(len(discount_positive) / len(discount_mentions) * 100, 1) if discount_mentions else 0,
            "price_positive_vs_negative": {
                "positive": len(price_positive),
                "negative": len(price_negative),
                "ratio": round(len(price_positive) / len(price_negative), 2) if price_negative else "N/A",
            },
            "price_range": {
                "min": min(r["price_paid"] for r in brand_revs) if brand_revs else 0,
                "max": max(r["price_paid"] for r in brand_revs) if brand_revs else 0,
                "avg": round(sum(r["price_paid"] for r in brand_revs) / len(brand_revs)) if brand_revs else 0,
            },
        }

    return results


def analyze_06_feature_requests(reviews):
    """
    6. Permintaan Pasar (R&D) — Feature Request Mining
    """
    categories = {
        "varian_baru_ukuran": ["tambahin", "dibikin", "pengen", "kalo ada", "varian", "ukuran", "size", "gram", "ml", "botol besar", "travel size"],
        "formula_improvement": ["kurang", "seharusnya", "idealnya", "formula", "kandungan", "bahan", "SPF", "lebih ringan", "oil free", "non-comedogenic"],
        "kemasan_improvement": ["kemasan", "packaging", "botol", "tube", "pump", "nozzle", "pipet", "drop", "squeeze", "lebih higienis"],
        "harga_bundling": ["murah", "bundling", "paket", "diskon", "promo", "voucher", "lebih murah", "set"],
        "produk_baru": ["semoga", "kalo ada", "ingin", "pengen", "mohon", "dibikin juga", "buatin"],
    }

    results = {}
    for brand in ["somethinc", "skintific"]:
        brand_revs = [r for r in reviews if r["brand"] == brand and r["has_feature_request"]]

        cat_results = {}
        for cat, keywords in categories.items():
            matching = [r for r in brand_revs if any(kw in r["text"].lower() for kw in keywords)]
            samples = [r["text"][:150] for r in matching[:5]]
            cat_results[cat] = {
                "count": len(matching),
                "samples": samples,
            }

        # Top requested products/categories
        product_requests = Counter()
        for r in brand_revs:
            if r.get("feature_request_text"):
                product_requests[r["product_name"]] += 1

        results[brand] = {
            "total_feature_requests": len(brand_revs),
            "request_categories": cat_results,
            "most_requested_products": dict(product_requests.most_common(8)),
            "all_request_texts": [r["text"][:200] for r in brand_revs[:10]],
        }

    return results


def analyze_07_affiliate_influence(reviews):
    """
    7. Pengaruh Afiliator — Organic vs Affiliate
    """
    affiliates = [r for r in reviews if r["user_type"] == "affiliate"]
    organics = [r for r in reviews if r["user_type"] == "organic"]
    suspicious = [r for r in reviews if r["user_type"] == "suspicious"]

    results = {
        "summary": {
            "total_reviews": len(reviews),
            "affiliate_reviews": len(affiliates),
            "organic_reviews": len(organics),
            "suspicious_reviews": len(suspicious),
            "affiliate_pct": round(len(affiliates) / len(reviews) * 100, 1) if reviews else 0,
            "suspicious_pct": round(len(suspicious) / len(reviews) * 100, 1) if reviews else 0,
        }
    }

    for brand in ["somethinc", "skintific"]:
        br_aff = [r for r in affiliates if r["brand"] == brand]
        br_org = [r for r in organics if r["brand"] == brand]
        br_sus = [r for r in suspicious if r["brand"] == brand]

        aff_avg = round(sum(r["rating"] for r in br_aff) / len(br_aff), 2) if br_aff else 0
        org_avg = round(sum(r["rating"] for r in br_org) / len(br_org), 2) if br_org else 0
        sus_avg = round(sum(r["sentiment_score"] for r in br_sus) / len(br_sus), 2) if br_sus else 0

        # Rating distribution comparison
        aff_rating_dist = Counter(r["rating"] for r in br_aff)
        org_rating_dist = Counter(r["rating"] for r in br_org)

        results[brand] = {
            "affiliate_count": len(br_aff),
            "organic_count": len(br_org),
            "suspicious_count": len(br_sus),
            "affiliate_avg_rating": aff_avg,
            "organic_avg_rating": org_avg,
            "rating_inflation": round(aff_avg - org_avg, 2),
            "affiliate_positive_pct": round(sum(1 for r in br_aff if r["sentiment_ml_label"] == "positive") / len(br_aff) * 100, 1) if br_aff else 0,
            "organic_positive_pct": round(sum(1 for r in br_org if r["sentiment_ml_label"] == "positive") / len(br_org) * 100, 1) if br_org else 0,
            "affiliate_rating_distribution": {str(k): v for k, v in sorted(aff_rating_dist.items())},
            "organic_rating_distribution": {str(k): v for k, v in sorted(org_rating_dist.items())},
            "suspicious_avg_sentiment": sus_avg,
        }

    return results


def analyze_08_repeat_purchase(reviews):
    """
    8. Loyalitas Konsumen — Repeat Purchase Signals
    """
    results = {}
    for brand in ["somethinc", "skintific"]:
        brand_revs = [r for r in reviews if r["brand"] == brand]
        repeat_revs = [r for r in brand_revs if r["has_repeat_intent"]]
        non_repeat_revs = [r for r in brand_revs if not r["has_repeat_intent"]]

        repeat_avg_rating = sum(r["rating"] for r in repeat_revs) / len(repeat_revs) if repeat_revs else 0
        non_repeat_avg_rating = sum(r["rating"] for r in non_repeat_revs) / len(non_repeat_revs) if non_repeat_revs else 0
        repeat_pos = [r for r in repeat_revs if r["sentiment_ml_label"] == "positive"]
        repeat_neg = [r for r in repeat_revs if r["sentiment_ml_label"] == "negative"]

        # Repeat by product
        repeat_by_product = Counter(r["product_name"] for r in repeat_revs)

        results[brand] = {
            "total_reviews": len(brand_revs),
            "repeat_intent_count": len(repeat_revs),
            "repeat_pct": round(len(repeat_revs) / len(brand_revs) * 100, 1) if brand_revs else 0,
            "repeat_avg_rating": round(repeat_avg_rating, 2),
            "non_repeat_avg_rating": round(non_repeat_avg_rating, 2),
            "loyalty_rating_premium": round(repeat_avg_rating - non_repeat_avg_rating, 2),
            "repeat_positive_pct": round(len(repeat_pos) / len(repeat_revs) * 100, 1) if repeat_revs else 0,
            "repeat_negative_pct": round(len(repeat_neg) / len(repeat_revs) * 100, 1) if repeat_revs else 0,
            "most_repeated_products": dict(repeat_by_product.most_common(8)),
            "repeat_examples": [r["text"][:150] for r in repeat_revs[:5]],
        }

    return results


def analyze_09_anomaly_detection(reviews):
    """
    9. Anomali Data — Fake Review Detection
    """
    suspicious = [r for r in reviews if r["is_suspicious_positive"]]
    normal = [r for r in reviews if not r["is_suspicious_positive"]]

    # By brand
    results = {"overall": {}}
    for brand in ["somethinc", "skintific"]:
        br_sus = [r for r in suspicious if r["brand"] == brand]
        br_all = [r for r in reviews if r["brand"] == brand]

        results[brand] = {
            "total_suspicious": len(br_sus),
            "suspicious_pct": round(len(br_sus) / len(br_all) * 100, 1) if br_all else 0,
            "suspicious_by_product": dict(Counter(r["product_name"] for r in br_sus).most_common(10)),
            "suspicious_examples": [{
                "product": r["product_name"],
                "rating": r["rating"],
                "text_sample": r["text"][:150],
                "sentiment_score": r["sentiment_score"],
            } for r in br_sus[:5]],
        }

    # Overall anomaly stats
    results["overall"] = {
        "total_suspicious": len(suspicious),
        "suspicious_pct": round(len(suspicious) / len(reviews) * 100, 1) if reviews else 0,
        "avg_rating_of_suspicious": round(sum(r["rating"] for r in suspicious) / len(suspicious), 2) if suspicious else 0,
        "avg_sentiment_of_suspicious": round(sum(r["sentiment_score"] for r in suspicious) / len(suspicious), 2) if suspicious else 0,
        "suspicious_alert": "⚠️ Tingkat mencurigakan" if len(suspicious) / len(reviews) > 0.05 else "✅ Masih dalam batas normal",
    }

    return results


def analyze_10_temporal_trends(reviews):
    """
    10. Tren Waktu — Temporal Sentiment Patterns
    """
    # By day-of-week
    weekday_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

    results = {"weekly_pattern": {}, "brand_timeline": {}}

    # Weekly pattern across all reviews
    weekday_data = defaultdict(list)
    for r in reviews:
        weekday_data[r["weekday"]].append(r)

    weekday_results = {}
    for day_idx in range(7):
        day_revs = weekday_data.get(day_idx, [])
        neg = [r for r in day_revs if r["sentiment_ml_label"] == "negative"]
        pos = [r for r in day_revs if r["sentiment_ml_label"] == "positive"]
        weekday_results[weekday_names[day_idx]] = {
            "total": len(day_revs),
            "negative": len(neg),
            "positive": len(pos),
            "avg_rating": round(sum(r["rating"] for r in day_revs) / len(day_revs), 2) if day_revs else 0,
            "negative_pct": round(len(neg) / len(day_revs) * 100, 1) if day_revs else 0,
        }

    results["weekly_pattern"] = weekday_results

    # Brand timeline (aggregated — we don't have real dates)
    for brand in ["somethinc", "skintific"]:
        brand_revs = [r for r in reviews if r["brand"] == brand]

        # Group by days_ago buckets (recent vs older)
        buckets = {
            "0-7 hari": [r for r in brand_revs if r["days_ago"] <= 7],
            "8-30 hari": [r for r in brand_revs if 8 <= r["days_ago"] <= 30],
            "31-60 hari": [r for r in brand_revs if 31 <= r["days_ago"] <= 60],
            "61-90 hari": [r for r in brand_revs if 61 <= r["days_ago"] <= 90],
            "90+ hari": [r for r in brand_revs if r["days_ago"] > 90],
        }

        timeline = {}
        for bucket_name, bucket_revs in buckets.items():
            neg = [r for r in bucket_revs if r["sentiment_ml_label"] == "negative"]
            pos = [r for r in bucket_revs if r["sentiment_ml_label"] == "positive"]
            timeline[bucket_name] = {
                "total": len(bucket_revs),
                "negative": len(neg),
                "positive": len(pos),
                "avg_rating": round(sum(r["rating"] for r in bucket_revs) / len(bucket_revs), 2) if bucket_revs else 0,
                "avg_sentiment": round(sum(r["sentiment_score"] for r in bucket_revs) / len(bucket_revs), 2) if bucket_revs else 0,
            }
        results["brand_timeline"][brand] = timeline

    # Find peak complaint days
    all_complaint_days = defaultdict(list)
    for r in reviews:
        if r["sentiment_ml_label"] == "negative" or r["rating"] <= 2:
            all_complaint_days[r["weekday"]].append(r)
    avg_complaints_per_day = sum(len(v) for v in all_complaint_days.values()) / 7
    results["peak_complaint_days"] = {
        weekday_names[day_idx]: round(len(reviews_list) / avg_complaints_per_day * 100 - 100, 1)
        if avg_complaints_per_day else 0
        for day_idx, reviews_list in sorted(all_complaint_days.items())
    }

    return results


# ═══════════════════════════════════════════════════════════════════
# 4. Run Everything
# ═══════════════════════════════════════════════════════════════════

def main():
    print("=== TikTok Shop Sentiment & Analysis Pipeline ===\n")

    # Load
    reviews = load_reviews()
    print(f"Loaded {len(reviews)} reviews")

    # Process sentiment
    reviews = process_all_reviews(reviews)
    print("Sentiment analysis complete")

    # Save processed data
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    processed_path = DATA_PROCESSED / "reviews_processed.json"
    with open(processed_path, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)
    print(f"Saved processed reviews to {processed_path}")

    # Run all analyses
    print("\nRunning 10 analyses...")
    all_analysis = {}

    print("  [01/10] Product Improvement Analysis (Somethinc)...")
    som_products = analyze_01_product_improvement(reviews, brand="somethinc")
    print("  [01/10] Product Improvement Analysis (Skintific)...")
    skn_products = analyze_01_product_improvement(reviews, brand="skintific")
    # Merge both brands together with brand prefixes
    som_products = {f"som-{k}": v for k, v in som_products.items()}
    skn_products = {f"skn-{k}": v for k, v in skn_products.items()}
    all_products = {}
    all_products.update(som_products)
    all_products.update(skn_products)
    all_analysis["01_product_improvement"] = all_products

    print("  [02/10] Competitive Benchmark...")
    all_analysis["02_competitive_benchmark"] = analyze_02_competitive_benchmark(reviews)

    print("  [03/10] Feature Evaluation Matrix...")
    all_analysis["03_feature_evaluation"] = analyze_03_feature_evaluation(reviews)

    print("  [04/10] Operational Issues...")
    all_analysis["04_operational_issues"] = analyze_04_operational_issues(reviews)

    print("  [05/10] Price Sensitivity...")
    all_analysis["05_price_sensitivity"] = analyze_05_price_sensitivity(reviews)

    print("  [06/10] Feature Requests (R&D)...")
    all_analysis["06_feature_requests"] = analyze_06_feature_requests(reviews)

    print("  [07/10] Affiliate Influence...")
    all_analysis["07_affiliate_influence"] = analyze_07_affiliate_influence(reviews)

    print("  [08/10] Repeat Purchase / Loyalty...")
    all_analysis["08_repeat_purchase"] = analyze_08_repeat_purchase(reviews)

    print("  [09/10] Anomaly Detection...")
    all_analysis["09_anomaly_detection"] = analyze_09_anomaly_detection(reviews)

    print("  [10/10] Temporal Trends...")
    all_analysis["10_temporal_trends"] = analyze_10_temporal_trends(reviews)

    # Add summary
    all_analysis["_meta"] = {
        "total_reviews": len(reviews),
        "brands": dict(Counter(r["brand"] for r in reviews)),
        "sentiment_distribution": dict(Counter(r["sentiment_ml_label"] for r in reviews)),
        "generated_at": datetime.now().isoformat(),
    }

    # Save all analysis
    DASHBOARD_DATA.mkdir(parents=True, exist_ok=True)
    output_path = DASHBOARD_DATA / "analysis_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_analysis, f, ensure_ascii=False, indent=2)
    print(f"\n✅ All analysis saved to {output_path}")
    print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")

    # Print summary
    print("\n📊 === QUICK SUMMARY ===")
    meta = all_analysis["_meta"]
    print(f"  Total Reviews: {meta['total_reviews']}")
    print(f"  Brands: {meta['brands']}")
    print(f"  Sentiment: {meta['sentiment_distribution']}")

    cb = all_analysis["02_competitive_benchmark"]
    if "sentiment_gap" in cb:
        gap = cb["sentiment_gap"]
        print(f"\n  🏆 Competitive Gap: Rating gap = {gap.get('rating_gap', 'N/A')}")
        print(f"     Sentiment gap = {gap.get('sentiment_gap', 'N/A')}")
        print(f"     Positive gap = {gap.get('positive_gap', 'N/A')}%")
        if "aspect_wins" in gap:
            for asp, data in gap["aspect_wins"].items():
                print(f"     {asp}: {data['winner']} (gap={data['gap']})")

    return all_analysis


if __name__ == "__main__":
    main()
