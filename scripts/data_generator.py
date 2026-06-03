#!/usr/bin/env python3
"""
Data Generator — Synthetic TikTok Shop Reviews
Somethinc vs Skintific (Skincare Category)
Calibrated with realistic Indonesian review patterns
"""

import json
import random
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

# ── PRODUCT CATALOG ──────────────────────────────────────────────

PRODUCTS_SOMETHINC = [
    {"id": "som-01", "name": "Something Serum", "category": "Serum", "price_range": (55000, 85000)},
    {"id": "som-02", "name": "Glow Maker Moisturizer", "category": "Moisturizer", "price_range": (45000, 75000)},
    {"id": "som-03", "name": "Clay Mask", "category": "Mask", "price_range": (35000, 55000)},
    {"id": "som-04", "name": "Acne Pore Serum", "category": "Serum", "price_range": (50000, 80000)},
    {"id": "som-05", "name": "Physical Sunscreen SPF50", "category": "Sunscreen", "price_range": (40000, 65000)},
    {"id": "som-06", "name": "Gentle Cleansing Balm", "category": "Cleanser", "price_range": (38000, 58000)},
    {"id": "som-07", "name": "Retinol Night Cream", "category": "Moisturizer", "price_range": (65000, 95000)},
    {"id": "som-08", "name": "Vitamin C Brightening Serum", "category": "Serum", "price_range": (55000, 85000)},
]

PRODUCTS_SKINTIFIC = [
    {"id": "skn-01", "name": "5X Ceramide Barrier Repair Moisturizer", "category": "Moisturizer", "price_range": (45000, 70000)},
    {"id": "skn-02", "name": "Moisture Bomb", "category": "Moisturizer", "price_range": (40000, 65000)},
    {"id": "skn-03", "name": "Retinol Serum", "category": "Serum", "price_range": (55000, 80000)},
    {"id": "skn-04", "name": "Sunscreen Moisturizer SPF50", "category": "Sunscreen", "price_range": (35000, 55000)},
    {"id": "skn-05", "name": "Brightening Clay Mask", "category": "Mask", "price_range": (30000, 50000)},
    {"id": "skn-06", "name": "Centella Acne Patch", "category": "Acne", "price_range": (20000, 35000)},
    {"id": "skn-07", "name": "Niacinamide Serum", "category": "Serum", "price_range": (40000, 60000)},
    {"id": "skn-08", "name": "Hyaluronic Acid Toner", "category": "Toner", "price_range": (35000, 55000)},
]

ALL_PRODUCTS = PRODUCTS_SOMETHINC + PRODUCTS_SKINTIFIC

# ── REVIEW TEMPLATES ─────────────────────────────────────────────

# Positive templates (Sentiment: ≥ 4)
POSITIVE_REVIEWS = [
    "Produknya bagus banget, cocok di kulit aku yang {skin_type}. {aspect}nya oke, {benefit}. Recommended banget!",
    "Udah {usage_count} kali beli, gak pernah mengecewakan. {aspect} enak, hasilnya keliatan. {repeat_intent}",
    "Cocok banget buat kulit {skin_type}. Awalnya ragu tapi setelah {time_period} pemakaian, {result}. {pricing_mention}",
    "Beneran works! {aspect}nya ringan, gak lengket, {benefit}. {skin_type} friendly banget. {closing}",
    "Udah pake {time_period}, {result}. Teksturnya {texture_desc}, wanginya {scent_desc}. Bakal repeat order! {repeat_intent}",
    "Harganya {pricing_opinion} untuk kualitas segini. Lebih murah dibanding brand lain yang {competitor_note}. {aspect}nya sip!",
    "Kemasan bagus, {aspect}nya {texture_desc}. Cepet ngiranya juga. Pokoknya worth it lah buat harga segitu.",
    "Aku punya kulit {skin_type} dan ini cocok banget. Gak bikin breakout, {result}. Recommended buat kalian yang {skin_type}.",
]

# Negative templates (Sentiment: ≤ 2)
NEGATIVE_REVIEWS = [
    "Gak cocok di kulitku yang {skin_type}. {problem_detail}. Sayang banget, {money_mention}.",
    "Ekspektasi tinggi tapi {disappointment}. {aspect}nya {negative_aspect_desc}. {will_return}",
    "Bikin breakout parah!! {problem_detail}. Udah coba {time_period} tapi makin parah. Uang {money_waste}",
    "Kemasan jelek, {aspect}nya {negative_aspect_desc}. Kayaknya gak cocok sama {skin_type}.",
    "Pas pertama pake {mild_positive} tapi lama-lama {worsening}. {problem_detail}. No repeat!",
    "Overrated banget. Harganya {pricing_opinion_neg} tapi kualitas {quality_neg}. Mending beli {competitor_brand}",
    "Pengirimannya lama banget, {shipping_issue}. Terus pas sampe, {packaging_issue}. Bintang 1 buat operasionalnya.",
    "Aku cocok-cocok aja. Gak ada perubahan {time_period} pake. Kayak gak ada efek. {pricing_opinion_neg}",
]

# Neutral/mixed templates (Sentiment: 3)
NEUTRAL_REVIEWS = [
    "Lumayan sih, {aspect}nya {mild_positive_aspect}. Tapi {but_critique}. Overall okelah buat nyoba.",
    "Awalnya {initial_positive} tapi setelah {time_period} {but_critique}. {neutral_closing}",
    "Tergantung jenis kulit mungkin ya. Aku {skin_type} {user_experience}. Mungkin kalian bisa cocok.",
    "Baru pake 2 minggu, belum keliatan hasilnya. {aspect}nya sih enak. Dilihat nanti aja.",
    "Lumayan membantu, tapi {but_critique}. Harganya {pricing_opinion}, mending tunggu diskon aja.",
]

# ── VOCABULARY POOLS ─────────────────────────────────────────────

SKIN_TYPES = ["kombinasi", "berminyak", "kering", "sensitif", "berjerawat", "normal", "kombinasi berminyak", "kering sensitif"]
ASPECTS = ["Tekstur", "Wanginya", "Kemasannya", "Formulanya", "Hasilnya", "Aplikasinya", "Kandungannya", "PHnya"]
BENEFITS = ["melembabkan", "mencerahkan", "nggak bikin breakout", "pori-pori mengecil", "kulit jadi halus", "jerawat berkurang", "kusan jadi lebih cerah"]
TIME_PERIODS = ["2 minggu", "1 bulan", "3 minggu", "sebulan lebih", "2 bulan", "seminggu"]

# Positive
POSITIVE_RESULTS = [
    "kulit jadi lebih lembab dan kenyal", "jerawat mulai kering", "wajah keliatan lebih cerah",
    "pori-pori mengecil", "tekstur kulit membaik", "gak ada breakout baru", "kusan merata",
    "wajah glowing natural", "minyak wajah berkurang", "skincare routine jadi lebih enak"
]
TEXTURE_DESC_POS = ["ringan", "cair", "lembut creamy", "gak lengket", "mousse-like", "gel ringan", "lotion tipis", "akan terasa dingin"]
SCENT_DESC_POS = ["enak", "wangi soft", "fresh", "natural", "gak overpowering", "mild", "seger", "subtle", "nyaman"]

# Negative
PROBLEM_DETAILS = [
    "langsung breakout dalam seminggu", "kulit jadi merah-merah", "perih pas dipake",
    "terasa lengket banget", "gak nyerap ke kulit", "malah bikin lebih berminyak",
    "beruntusan muncul dimana-mana", "rasanya perih", "gatal-gatal setelah pemakaian",
    "komedo malah nambah", "bruntus", "kulit mengelupas"
]
NEGATIVE_ASPECT_DESC = ["kayak plastik", "lengket banget", "gak enak", "ke mana-mana", "berat di muka", "bikin gerah", "kasar", "kayak minyak", "pedih"]

# Pricing
PRICING_OPINION = ["worth it", "cocok di kantong", "ekonomis", "sebanding", "agak pricey tapi worth", "pas buat quality segini"]
PRICING_OPINION_NEG = ["kemahalan", "nggak worth", "mahal", "overpriced", "terlalu mahal", "gak sebanding"]
COMPETITOR_NOTE = ["lebih mahal", "belum tentu cocok", "lebih irit", "bagusan ini"]

# Shipping
SHIPPING_ISSUES = ["packingnya bubble wrap doang", "gak pake dus", "dibuang satpam", "ditaruh di luar pagar", "gak ada double box"]
PACKAGING_ISSUES = ["kemasan penyok", "produknya tumpah", "bocor", "segel rusak", "kemasan rusak", "produk keluar sedikit"]

# Brand comparison
COMPETITOR_BRANDS = ["Skintific", "Somethinc", "The Originote", "Avoskin", "Wardah", "Scarlett"]

# Affiliate-specific phrases
AFFILIATE_PHRASES = [
    "dapet dari affiliate @", "gas cobain rekomendasi dari", "katanya sih best seller jadi aku beli",
    "viral banget di FYP, akhirnya nyoba", "udah banyak review bagus, ternyata beneran works",
    "thanks bund atas rekomendasinya", "rekomendasi dari sini, makasih banyak",
    "produknya bagus sesuai yang di review", "dapet link dari affiliate, gak nyesel beli",
]

ORDINAL = ["Pertama", "Kedua", "Ke-3", "Ke-empat", "Lima"]


def pick_product(brand_bias=None):
    """Pick a product, optionally biased toward a brand."""
    pool = ALL_PRODUCTS
    if brand_bias == "somethinc":
        pool = PRODUCTS_SOMETHINC
    elif brand_bias == "skintific":
        pool = PRODUCTS_SKINTIFIC
    return random.choice(pool)


def generate_rating(sentiment_label, brand, is_affiliate=False, is_fake=False):
    """
    Generate rating biased by brand + sentiment.
    Skintific: slightly lower quality ratings, but heavier discount-driven positivity.
    Somethinc: more stable ratings.
    """
    if is_fake:
        return random.choices([5, 5, 5, 4, 5], weights=[50, 30, 10, 5, 5])[0]
    if is_affiliate:
        return random.choices([5, 5, 4, 4, 3], weights=[45, 30, 15, 8, 2])[0]

    if sentiment_label == "positive":
        base_weights = [30, 55, 15]  # 5, 4, 3
        if brand == "skintific":
            base_weights = [20, 60, 20]  # slightly fewer 5s, more 4s
        return random.choices([5, 4, 3], weights=base_weights)[0]
    elif sentiment_label == "negative":
        base_weights = [5, 10, 35, 30, 20]
        return random.choices([5, 4, 3, 2, 1], weights=base_weights)[0]
    else:
        return random.choices([5, 4, 3, 2], weights=[5, 20, 60, 15])[0]


def get_price(pricing_opinion):
    if pricing_opinion == "murah":
        return random.randint(15000, 35000)
    elif pricing_opinion == "ekonomis":
        return random.randint(25000, 45000)
    elif pricing_opinion == "worth":
        return random.randint(35000, 60000)
    elif pricing_opinion == "premium":
        return random.randint(55000, 95000)
    else:
        return random.randint(20000, 80000)


def generate_review_text(sentiment_label, product, brand, is_affiliate=False):
    """Generate a single review text with realistic language."""
    skin_type = random.choice(SKIN_TYPES)
    aspect = random.choice(ASPECTS)
    time_period = random.choice(TIME_PERIODS)

    if sentiment_label == "positive":
        template = random.choice(POSITIVE_REVIEWS)
        result = random.choice(POSITIVE_RESULTS)
        texture_desc = random.choice(TEXTURE_DESC_POS)
        scent_desc = random.choice(SCENT_DESC_POS)
        usage_count = random.choice(["2x", "3x", "4x", "beberapa kali", "berkali-kali"])
        repeat_intent = random.choice(["Bakalan repeat order!", "Udah repeat berkali-kali.", "Udah restock berkali-kali."])

        text = template.format(
            skin_type=skin_type, aspect=aspect, result=result,
            time_period=time_period, texture_desc=texture_desc,
            scent_desc=scent_desc, usage_count=usage_count,
            benefit=random.choice(BENEFITS), repeat_intent=repeat_intent,
            pricing_mention=random.choice(["", "Harganya worth banget.", "Murah meriah.", "Harga sesuai kualitas."]),
            pricing_opinion=random.choice(PRICING_OPINION),
            competitor_note=random.choice(COMPETITOR_NOTE),
            closing=random.choice(["Love it!", "Big yes!", "Pokoknya must have!"]),
        )
    elif sentiment_label == "negative":
        template = random.choice(NEGATIVE_REVIEWS)
        problem_detail = random.choice(PROBLEM_DETAILS)
        negative_aspect_desc = random.choice(NEGATIVE_ASPECT_DESC)
        money_mention = random.choice(["uang keluar percuma", "sayang duit", "boros", "uang terbuang"])
        will_return = random.choice(["Gak bakal beli lagi.", "No repeat.", "Kapok.", "Jangan beli."])
        mild_positive = random.choice(["okelah", "lumayan", "biasa aja"])
        worsening = random.choice(["kok makin jelek", "hasilnya makin buruk", "malah bikin masalah baru"])

        text = template.format(
            skin_type=skin_type, aspect=aspect, result=random.choice(POSITIVE_RESULTS),
            time_period=time_period, texture_desc=random.choice(TEXTURE_DESC_POS),
            scent_desc=random.choice(SCENT_DESC_POS), benefit=random.choice(BENEFITS),
            repeat_intent="", pricing_mention="",
            problem_detail=problem_detail, negative_aspect_desc=negative_aspect_desc,
            money_mention=money_mention, will_return=will_return,
            mild_positive=mild_positive, worsening=worsening,
            disappointment=random.choice(["mengecewakan", "nggak sesuai ekspektasi", "biasa aja", "gak wow", "standar banget"]),
            pricing_opinion_neg=random.choice(PRICING_OPINION_NEG),
            quality_neg=random.choice(["biasa aja", "standar", "gak istimewa", "mengecewakan"]),
            competitor_brand=random.choice(COMPETITOR_BRANDS),
            shipping_issue=random.choice(SHIPPING_ISSUES),
            packaging_issue=random.choice(PACKAGING_ISSUES),
            money_waste=random.choice(["terbuang", "percuma", "sayang"]),
        )
    else:  # neutral
        template = random.choice(NEUTRAL_REVIEWS)
        mild_positive_aspect = random.choice(["enak", "cukup baik", "lumayan", "pas", "gak jelek"])
        but_critique = random.choice([
            "kurasa kurang maksimal", "masih belum keliatan hasilnya", "agak berat di kulit",
            "bikin sedikit berminyak", "kurang cocok di aku", "hasilnya biasalah",
            "masih belum sesuai ekspektasi", "perlu waktu lebih lama"
        ])

        text = template.format(
            aspect=aspect, time_period=time_period, skin_type=skin_type,
            mild_positive_aspect=mild_positive_aspect, but_critique=but_critique,
            initial_positive=random.choice(["lumayan", "cukup bagus", "okelah"]),
            user_experience=random.choice([
                "pas pake rasanya enak", "gak ada masalah sih", "so far so good",
                "lumayan cocok", "belum ada reaksi negatif"
            ]),
            neutral_closing=random.choice([
                "Semoga cocok", "Coba aja dulu", "Mungkin cocok buat yang lain",
                "Siapa tau cocok di lo"
            ]),
            pricing_opinion=random.choice(["standar", "lumayan", "agak pricey", "sebanding", "agak mahal tapi ok"]),
        )

    if is_affiliate and sentiment_label == "positive":
        # Prepend affiliate phrase to positive reviews
        prefix = random.choice(AFFILIATE_PHRASES)
        text = f"{prefix}. {text[0].lower() + text[1:]}" if text[0].isupper() else f"{prefix}. {text}"

    return text


def generate_date(base_date, spread_days=120):
    """Generate a random date within range."""
    days_back = random.randint(0, spread_days)
    hour = random.randint(8, 23)
    minute = random.randint(0, 59)
    dt = base_date - timedelta(days=days_back, hours=hour, minutes=minute)
    return dt.isoformat(), dt.weekday(), days_back


def has_repeat_intent(text):
    keywords = ["beli lagi", "repeat order", "repeat", "restock", "langganan", "ke-3", "ke-2",
                "bakal repeat", "udah 2x", "udah 3x", "sudah ke", "order lagi"]
    return any(kw in text.lower() for kw in keywords)


def has_discount_mention(text):
    keywords = ["diskon", "promo", "voucher", "flash sale", "bundling", "cashback", "COD",
                "harga diskon", "murah banget", "hemat", "gratis ongkir"]
    return any(kw in text.lower() for kw in keywords)


def has_price_mention(text):
    keywords = ["harga", "mahal", "murah", "worth", "pricey", "ekonomis", "sebanding",
                "cocok di kantong", "overpriced", "kemahalan"]
    return any(kw in text.lower() for kw in keywords)


def has_logistic_mention(text):
    keywords = ["lama", "kirim", "pack", "packing", "bubble", "dus", "kurir", "ekspedisi",
                "pengiriman", "rusak", "bocor", "tumpah", "penyok", "segel", "double box",
                "sampai", "nyampe"]
    return any(kw in text.lower() for kw in keywords)


def has_aspect_mention(text):
    aspects = ["tekstur", "wangi", "kemasan", "packaging", "aroma", "kandungan", "bahan",
               "botol", "tube", "krim", "cairan", "konsistensi", "formula"]
    return any(a in text.lower() for a in aspects)


def has_feature_request(text):
    keywords = ["kalo ada", "sayangnya", "pengen", "semoga", "kurang", "tambahin", "ingin",
                "mohon", "dibikin", "seharusnya", "kalo bisa", "idealnya", "mending",
                "saran", "sebaiknya", "ditingkatin", "ditingkatkan", "dikurangin"]
    return any(kw in text.lower() for kw in keywords)


def extract_feature_request(text):
    """If text has a feature request, extract the keyword and context."""
    keywords = ["kalo ada", "sayangnya", "pengen", "semoga", "kurang", "tambahin",
                "saran", "sebaiknya", "kalo bisa"]
    for kw in keywords:
        if kw in text.lower():
            idx = text.lower().index(kw)
            start = max(0, idx - 30)
            end = min(len(text), idx + 80)
            return text[start:end]
    return ""


def is_affiliate_pattern(text):
    """Check if review looks like affiliate-driven content."""
    patterns = ["dapet dari affiliate", "rekomendasi dari", "viral banget di FYP",
                "thanks bund", "makasih banyak", "best seller", "linknya dong",
                "gas cobain", "sesuai yang di review", "sudah banyak review"]
    return any(p in text.lower() for p in patterns)


def is_suspicious_positive(rating, text):
    """High rating but negative language → possible fake."""
    negative_signals = ["gak cocok", "nggak cocok", "breakout", "perih", "gatal",
                        "kecewa", "mengecewakan", "jangan beli", "gak works",
                        "nggak works", "boros", "percuma", "sayang duit", "kapok",
                        "tidak cocok", "gak ada efek", "jelek", "menyesal",
                        "mending beli", "gak rekomen", "gasuka"]
    neg_count = sum(1 for s in negative_signals if s in text.lower())
    return rating >= 4 and neg_count >= 2


def generate_review(product, brand, base_date, sentiment_label=None,
                    is_affiliate=False, is_fake=False):
    """Generate a single review entry."""

    # Bias sentiment by brand + product category
    if sentiment_label is None:
        brand = brand or ("somethinc" if any(p["id"] == product["id"] for p in PRODUCTS_SOMETHINC) else "skintific")
        r = random.random()
        if brand == "somethinc":
            # Somethinc: more mixed/positive (loyal userbase)
            if r < 0.35: sentiment_label = "positive"
            elif r < 0.60: sentiment_label = "neutral"
            else: sentiment_label = "negative"
        else:
            # Skintific: more polarizing (hype-driven, cheaper)
            if r < 0.40: sentiment_label = "positive"
            elif r < 0.55: sentiment_label = "neutral"
            else: sentiment_label = "negative"

    text = generate_review_text(sentiment_label, product, brand, is_affiliate)
    rating = generate_rating(sentiment_label, brand, is_affiliate, is_fake)
    date_str, weekday, days_ago = generate_date(base_date)

    # User type
    if is_affiliate:
        user_type = "affiliate"
    elif is_fake:
        user_type = "suspicious"
    else:
        user_type = "organic"

    # Price paid (simulate discount effect)
    base_price = random.randint(*product["price_range"])
    had_discount = has_discount_mention(text) or random.random() < 0.15
    if had_discount and random.random() < 0.7:
        price_paid = int(base_price * random.uniform(0.5, 0.85))
    else:
        price_paid = base_price

    return {
        "review_id": f"rev-{random.randint(10000, 99999)}",
        "product_id": product["id"],
        "product_name": product["name"],
        "category": product["category"],
        "brand": brand,
        "price_paid": price_paid,
        "rating": rating,
        "text": text,
        "sentiment_label": sentiment_label,
        "date": date_str,
        "weekday": weekday,
        "days_ago": days_ago,
        "user_type": user_type,
        "has_repeat_intent": has_repeat_intent(text),
        "has_discount_mention": has_discount_mention(text),
        "has_price_mention": has_price_mention(text),
        "has_logistic_mention": has_logistic_mention(text),
        "has_aspect_mention": has_aspect_mention(text),
        "has_feature_request": has_feature_request(text),
        "feature_request_text": extract_feature_request(text) if has_feature_request(text) else "",
        "is_suspicious_positive": is_suspicious_positive(rating, text),
        "location": random.choice(["Jakarta", "Bandung", "Surabaya", "Medan", "Makassar",
                                    "Yogyakarta", "Semarang", "Palembang", "Bali", "Lampung"]),
    }


def generate_dataset(n_reviews=1500, base_date=None):
    """Generate the full dataset with controlled distributions."""
    if base_date is None:
        base_date = datetime(2026, 6, 3)

    reviews = []

    # Somethinc reviews (45%)
    n_somethinc = int(n_reviews * 0.45)
    for _ in range(n_somethinc):
        product = random.choice(PRODUCTS_SOMETHINC)
        is_affil = random.random() < 0.08  # fewer affiliates for Somethinc
        is_fake = random.random() < 0.03
        r = generate_review(product, "somethinc", base_date,
                           is_affiliate=is_affil, is_fake=is_fake)
        reviews.append(r)

    # Skintific reviews (45%)
    n_skintific = int(n_reviews * 0.45)
    for _ in range(n_skintific):
        product = random.choice(PRODUCTS_SKINTIFIC)
        is_affil = random.random() < 0.20  # more affiliates for Skintific
        is_fake = random.random() < 0.06  # more fake reviews
        r = generate_review(product, "skintific", base_date,
                           is_affiliate=is_affil, is_fake=is_fake)
        reviews.append(r)

    # Cross-brand comparison reviews (10%) — people mention competitor
    n_cross = n_reviews - n_somethinc - n_skintific
    for _ in range(n_cross):
        if random.random() < 0.5:
            product = random.choice(PRODUCTS_SOMETHINC)
            brand = "somethinc"
        else:
            product = random.choice(PRODUCTS_SKINTIFIC)
            brand = "skintific"
        # Mention competitor in text
        r = generate_review(product, brand, base_date)
        competitor = "Skintific" if brand == "somethinc" else "Somethinc"
        r["text"] += f" Mending {competitor} lebih {random.choice(['murah', 'bagus', 'cocok'])}."
        reviews.append(r)

    random.shuffle(reviews)
    return reviews


def main():
    print("=== TikTok Shop Review Generator ===")
    print("Generating Somethinc vs Skintific review dataset...")

    dataset = generate_dataset(2000)
    DATA_RAW.mkdir(parents=True, exist_ok=True)

    # Save raw dataset
    raw_path = DATA_RAW / "tiktok_reviews_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(dataset)} raw reviews to {raw_path}")

    # Save as CSV (for easy Pandas processing)
    import csv
    csv_path = DATA_RAW / "tiktok_reviews_raw.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        if dataset:
            writer = csv.DictWriter(f, fieldnames=dataset[0].keys())
            writer.writeheader()
            writer.writerows(dataset)
    print(f"Saved CSV to {csv_path}")

    # Quick stats
    from collections import Counter
    brands = Counter(r["brand"] for r in dataset)
    sentiments = Counter(r["sentiment_label"] for r in dataset)
    ratings_dist = Counter(r["rating"] for r in dataset)
    user_types = Counter(r["user_type"] for r in dataset)

    print(f"\n📊 Dataset Stats:")
    print(f"  Brands: {dict(brands)}")
    print(f"  Sentiment: {dict(sentiments)}")
    print(f"  Ratings: {dict(sorted(ratings_dist.items()))}")
    print(f"  User Types: {dict(user_types)}")
    print(f"  Fake/Palnny: {sum(1 for r in dataset if r['is_suspicious_positive'])}")
    print(f"  Feature Requests: {sum(1 for r in dataset if r['has_feature_request'])}")
    print(f"  Repeat Intent: {sum(1 for r in dataset if r['has_repeat_intent'])}")
    print(f"  Logistic Mentions: {sum(1 for r in dataset if r['has_logistic_mention'])}")

    return dataset


if __name__ == "__main__":
    dataset = main()
