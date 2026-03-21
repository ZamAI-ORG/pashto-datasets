#!/usr/bin/env python3
"""
Simple standalone ZamAI dataset creator.

Produces a small but representative Pashto instruction-response dataset using
the same canonical category names as the full pipeline
(zamai_training_dataset.py) so the outputs are interchangeable.

Categories used:
    tutor_chat         – educational Q&A and general tutoring
    language_learning  – Pashto / English language practice
    islamic_content    – religious guidance and teachings
    cultural_content   – Afghan traditions and customs
    general_qa         – general knowledge and health
    business_automation – business letters, forms, documents
    news_summarization – text summarisation examples
"""

import csv
import json
import os
from pathlib import Path
from datetime import datetime


# ---------------------------------------------------------------------------
# Canonical category mapping from the older, ad-hoc names used in this file
# to the standard names shared with zamai_training_dataset.py.
# ---------------------------------------------------------------------------
_CATEGORY_MAP = {
    "geography":    "tutor_chat",
    "language":     "language_learning",
    "history":      "tutor_chat",
    "grammar":      "language_learning",
    "islamic":      "islamic_content",
    "culture":      "cultural_content",
    "education":    "tutor_chat",
    "health":       "general_qa",
    "business":     "business_automation",
    "conversation": "tutor_chat",
    "summarization":"news_summarization",
    "literature":   "tutor_chat",
}

# Standard categories (defines the order in dataset_info output)
STANDARD_CATEGORIES = [
    "tutor_chat",
    "language_learning",
    "islamic_content",
    "cultural_content",
    "general_qa",
    "business_automation",
    "news_summarization",
]


def _normalize_category(cat: str) -> str:
    """Return the canonical category name, passing through already-standard names."""
    return _CATEGORY_MAP.get(cat, cat)


def create_simple_dataset(output_dir: str = "zamai_final_dataset") -> Path:
    """Create and save the ZamAI simple training dataset.

    Returns the Path of the output directory.
    """
    out = Path(output_dir)
    out.mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    # Raw training examples – category tags are normalised automatically.
    # ------------------------------------------------------------------
    training_data_raw = [
        # Afghanistan and Geography → tutor_chat
        {
            "instruction": "د افغانستان پایتخت چه شی دی؟",
            "response": "د افغانستان پایتخت کابل دی. کابل د افغانستان تر ټولو لوی ښار او د دغه هیواد سیاسي، اقتصادي او کلتوري مرکز دی.",
            "category": "geography",
        },
        {
            "instruction": "د افغانستان رسمي ژبې کومې دي؟",
            "response": "د افغانستان رسمي ژبې پښتو او دري دي. پښتو د افغان ولس اصلي ژبه ده او دري هم د پراخو برخو لخوا کارول کیږي.",
            "category": "geography",
        },
        {
            "instruction": "د افغانستان مهم تاریخي ځایونه کوم دي؟",
            "response": "د افغانستان مهم تاریخي ځایونه پدې دي: د بامیانو تاریخي مجسمې، د ننګرهار تاریخي بودایي ځایونه، د غزني تاریخي ماڼۍ، د هرات جامع جومات، د کندهار زرغونه خرقه، او د کابل د بالاحصار کلا.",
            "category": "history",
        },

        # Language Learning
        {
            "instruction": "د پښتو ژبې زده کړه څنګه پیل کړم؟",
            "response": "د پښتو ژبې د زده کړې لپاره دا مرحلې تعقیب کړئ: ۱) د پښتو الفبا او املا زده کړئ ۲) اساسي کلمې او جملې تمرین کړئ ۳) ورځني استعمال ته پاملرنه وکړئ ۴) د پښتو شاعرۍ او ادبیاتو لوستل پیل کړئ ۵) د ویناوالانو سره خبرې اترې وکړئ",
            "category": "language_learning",
        },
        {
            "instruction": "د پښتو ژبې ګرامر راته وښیه",
            "response": "د پښتو ژبې ګرامر پدې ډول دی: ۱) د ناستو ویش: نارینه او ښځینه ۲) د شمیر ویش: یوګړی او څو ګړی ۳) د حالت ویش: فاعلي، مفعولي، اضافي حالت ۴) د وخت ویش: تیر، اوسنی، راتلونکی ۵) د فعل بڼې: اوسنۍ، تیرې، امر",
            "category": "grammar",
        },

        # Islamic Content
        {
            "instruction": "د اسلام د پنځو ستنو په اړه راته ووایه",
            "response": "د اسلام پنځه ستنې دا دي: ۱) کلمه (د الله توحید او د محمد رسالت تصدیق) ۲) لمونځ (د ورځې پنځه وخته لمونځونه) ۳) زکات (د شتمنۍ څخه د فقیرانو حق ورکول) ۴) روژه (د رمضان میاشت روژه نیول) ۵) حج (د مکې ته زیارت که چیرې وړتیا ولري)",
            "category": "islamic",
        },
        {
            "instruction": "د پنجګانه لمونځ وختونه کوم دي؟",
            "response": "د پنجګانه لمونځ وختونه دا دي: ۱) د سهار لمونځ (د سپیدې څخه تر لمر پورته کیدو) ۲) د غرمې لمونځ (د لمر د ماشومۍ څخه تر ماسپښین) ۳) د ماسپښین لمونځ (د ماسپښین څخه تر لمر لویدو) ۴) د ماښام لمونځ (د لمر له لویدو وروسته) ۵) د شپې لمونځ (د ماښام څخه تر سپیدې)",
            "category": "islamic",
        },
        {
            "instruction": "د قرآن کریم د ځانګړتیاوو په اړه راته ووایه",
            "response": "قرآن کریم د الله تعالی آخری کتاب دی چې د محمد صلی الله علیه وسلم باندې نازل شوی. دا د ۱۱۴ سورتونو او شاوخوا ۶۲۳۶ ایاتونو څخه جوړ دی. قرآن د ۲۳ کلونو په اوږدو کې نازل شوی او د ټولو مسلمانانو لپاره د ژوند د لارښوونې سرچینه ده.",
            "category": "islamic",
        },

        # Cultural Content
        {
            "instruction": "د پښتنو دودونه او رواجونه راته ووایه",
            "response": "د پښتنو مهم دودونه دا دي: میلمستیا (د میلمه درناوی)، ننګ (د غیرتونو ساتل)، بدل (انتقام اخیستل)، پښتونولي (د پښتون ارزښتونه)، جرګه (ټولنیز پریکړه کول)، او د کورنۍ درناوی.",
            "category": "culture",
        },
        {
            "instruction": "د افغانستان دودیز خواړه کوم دي؟",
            "response": "د افغانستان دودیز خواړه پدې دي: پلاو (د وریجو سره)، کباب، مانتو، بولاني، قورمه، آش، شولې پلاو، قابلي پلاو، کچالو چپلي، او نان. دا ټول د افغان کلتور مهم برخه ده.",
            "category": "culture",
        },
        {
            "instruction": "د افغانستان دودیز جامو په اړه راته ووایه",
            "response": "د افغانستان دودیز جامې دا دي: د نارینه وو لپاره – شلوار قمیص، چپن، پکول، تویې، او کولا. د ښځو لپاره – فرقه، شلوار قمیص، چادر، او دودیز ګاڼۍ.",
            "category": "culture",
        },

        # Education → tutor_chat
        {
            "instruction": "د ریاضیاتو بنسټیز مفاهیم راته وروښیه",
            "response": "د ریاضیاتو بنسټیز مفاهیم پدې دي: شمېرنه (۱، ۲، ۳...)، جمع کول (+)، لرې کول (-)، ضرب (×)، وېش (÷)، کسرونه (۱/۲، ۲/۳)، فیصدې (%)، او اندازه اخیستل (اوږدوالی، وزن، مساحت).",
            "category": "education",
        },
        {
            "instruction": "د علومو څانګې کومې دي؟",
            "response": "د علومو اصلي څانګې دا دي: فزیک (د طبیعت علم)، کیمیا (د مادو علم)، بیولوژي (د ژویو علم)، ریاضي (د شمېرونو علم)، ځمکپوهنه (د ځمکې علم)، ستورپوهنه (د اسمانو علم)، او طب (د روغتیا علم).",
            "category": "education",
        },

        # Health → general_qa
        {
            "instruction": "د روغتیا د ساتلو لپاره څه وکړم؟",
            "response": "د روغتیا د ساتلو لپاره دا کارونه وکړئ: ۱) پاک او صحي خواړه وخورئ ۲) ورځني ورزش وکړئ ۳) کافي اوبه وښه ۴) د کافي خوب واخلئ ۵) له تنبکو او نشه ایزو توکو ډډه وکړئ ۶) دکتور ته منظم ولاړ شئ",
            "category": "health",
        },

        # Business Automation
        {
            "instruction": "د سوداګرۍ خط راته ولیکه",
            "response": "درناوي ملګري، موږ ستاسو ته زموږ د نوي محصول په اړه خبر ورکوو. موږ ډېر خوښ یو چې دا ستاسو ته وړاندې کړو. که تاسو د نورو معلوماتو اړتیا لرئ، مهرباني وکړئ زموږ سره اړیکه ونیسئ. ډېر مننه.",
            "category": "business",
        },
        {
            "instruction": "د رښتون غوښتنلیک ولیکه",
            "response": "د محترم ریس ته، زه د دندې د رخصتۍ لپاره دا غوښتنلیک وړاندې کوم. زه د [نیټه] څخه تر [نیټه] پورې رخصتي ته اړتیا لرم د [دلیل] له امله. هیله لرم چې زما غوښتنه به منل شي. ډېر مننه، [نوم]",
            "category": "business",
        },

        # Conversational → tutor_chat
        {
            "instruction": "سلام وروره!",
            "response": "سلام ورور! ښه راغلاست. د کورنۍ میره د خیر؟ د څه مرستې اړتیا لرئ؟",
            "category": "conversation",
        },
        {
            "instruction": "ستاسو حال څنګه دی؟",
            "response": "زموږ حال د الله په مهربانۍ ښه دی. ستاسو حال څنګه دی؟ د کورنۍ میره د خیر؟",
            "category": "conversation",
        },
        {
            "instruction": "ډېر مننه ستاسو د مرستې لپاره",
            "response": "دا زموږ خوښي ده چې ستاسو سره مرسته وکړو. که بل ځل د مرستې اړتیا ولرئ، موږ دلته یو.",
            "category": "conversation",
        },

        # News Summarization
        {
            "instruction": "دا خبر لنډ کړه: د افغانستان په فاریاب ولایت کې په یوه پارک کې ښځو په برقعو کې ورزش کړی دی. د سیمې چارواکي وايي، د ښځو د ورزش لپاره ځانګړی ځای نه لري.",
            "response": "په فاریاب کې ښځو د برقعو سره ورزش وکړ ځکه چې د ښځو لپاره ځانګړی ورزش ځای نشته.",
            "category": "summarization",
        },

        # Language Learning – English
        {
            "instruction": "د انګلیسي ژبې زده کړه څنګه پیل کړم؟",
            "response": "د انګلیسي ژبې د زده کړې لپاره دا لارې تعقیب کړئ: ۱) د انګلیسي توري (A-Z) زده کړئ ۲) اساسي کلمې لکه شمېرې، رنګونه، کورنۍ غړي زده کړئ ۳) ساده جملې جوړول زده کړئ ۴) ورځني غږیدل او لوستل تمرین کړئ ۵) د انګلیسي فلمونه او سندرې واورئ",
            "category": "language_learning",
        },

        # Literature and Poetry → tutor_chat
        {
            "instruction": "د پښتو ادبیاتو مشهور شاعران کوم دي؟",
            "response": "د پښتو ادبیاتو مشهور شاعران دا دي: خوشحال خان ختک (د پښتو شاعرۍ پلار)، رحمان بابا (د عشق شاعر)، احمد شاه ابدالي، عبدالحمید مومند، غني خان، او قلندر مومند. دا ټول د پښتو ژبې او کلتور لپاره زیات اغېز لري.",
            "category": "literature",
        },
    ]

    # Normalise every category to the canonical name
    training_data = []
    for item in training_data_raw:
        normalised = dict(item)
        normalised["category"] = _normalize_category(item.get("category", "tutor_chat"))
        training_data.append(normalised)

    print(f"Creating ZamAI training dataset with {len(training_data)} examples...")

    # Save as JSONL for HuggingFace
    with open(out / "zamai_training_dataset.jsonl", "w", encoding="utf-8") as f:
        for item in training_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # Save as JSON
    with open(out / "zamai_training_dataset.json", "w", encoding="utf-8") as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)

    # Save as CSV
    if training_data:
        fieldnames = list(training_data[0].keys())
        with open(out / "zamai_training_dataset.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(training_data)

    # Build category counts using standard names
    category_counts = {cat: 0 for cat in STANDARD_CATEGORIES}
    for item in training_data:
        cat = item.get("category", "tutor_chat")
        if cat in category_counts:
            category_counts[cat] += 1
        else:
            category_counts[cat] = 1

    # Create dataset info
    dataset_info = {
        "name": "ZamAI Pashto Training Dataset",
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "total_examples": len(training_data),
        "categories": {k: v for k, v in category_counts.items() if v > 0},
        "description": "High-quality Pashto language dataset for tutor bots, chat assistants, and business automation",
        "format": "instruction-response pairs with category labels",
    }

    with open(out / "dataset_info.json", "w", encoding="utf-8") as f:
        json.dump(dataset_info, f, ensure_ascii=False, indent=2)

    print("Dataset created successfully!")
    print(f"Location: {out}")
    print(f"Total examples: {len(training_data)}")
    print("Category breakdown:")
    for category, count in dataset_info["categories"].items():
        print(f"  {category}: {count}")

    return out


if __name__ == "__main__":
    create_simple_dataset()

