"""Word lists used by the parser.

Everything is lower-case and NFC-normalised via ``text_utils.norm_text`` at import time so
that lookups behave the same for text typed by hand and text returned by Prisma STT.
Indic words are matched by *prefix* (Telugu and Hindi attach suffixes such as "-andi"),
Latin words are matched exactly.
"""
from __future__ import annotations

from .text_utils import EXACT_WORDS, norm_text


def _set(*words: str) -> frozenset[str]:
    return frozenset(norm_text(w) for w in words if w)


# ---------------------------------------------------------------------------------------------
# Yes / No / Not sure
# ---------------------------------------------------------------------------------------------
YES = _set(
    # English
    "yes", "yeah", "yep", "yup", "sure", "correct", "right", "absolutely", "definitely", "affirmative",
    "have", "has", "own", "owns", "do", "does", "pay", "pays", "paying", "paid",
    # Hindi (native + romanised)
    "हाँ", "हां", "हा", "जी", "है", "हैं", "बिल्कुल", "सही", "haan", "han", "haa", "ji", "hai", "hain",
    "bilkul", "hanji",
    # Telugu (native + romanised)
    "అవును", "ఔను", "ఉంది", "ఉన్నది", "ఉన్నాయి", "ఉన్నారు", "ఉన్నాను", "ఉందండి", "అవునండి",
    "చెల్లిస్తాను", "చెల్లిస్తున్నాను", "చెల్లించాను", "కడతాను", "కట్టాను",
    "avunu", "avnu", "aunu", "undi", "unnayi", "unnaru", "avunandi",
    # Kannada
    "ಹೌದು", "ಹೌದ್ರಿ", "ಇದೆ", "ಇವೆ", "ಇದ್ದಾರೆ", "ಇದ್ದೇನೆ", "ಪಾವತಿಸುತ್ತೇನೆ", "ಪಾವತಿಸಿದ್ದೇನೆ", "ಕಟ್ಟುತ್ತೇನೆ",
    "houdu", "haudu", "avdu", "ide", "ive", "iddare",
)

NO = _set(
    # English (apostrophes are stripped by normalisation, so "don't" -> "dont")
    "no", "not", "nope", "never", "dont", "doesnt", "didnt", "havent", "hasnt", "cant", "cannot",
    "wont", "none", "nobody", "without", "nothing",
    # Hindi
    "नहीं", "नही", "नहि", "ना", "न", "nahi", "nahin", "nahee", "nai", "na",
    # Telugu
    "లేదు", "లేదండి", "లేవు", "లేరు", "కాదు", "కాదండి",
    "ledu", "ledhu", "ledandi", "levu", "leru", "kaadu", "kadu", "kaadandi",
    # Kannada (exact-match only, see below)
    "ಇಲ್ಲ", "ಇಲ್ಲಾ", "ಇಲ್ಲರೀ", "ಇಲ್ಲಾರಿ", "ಇಲ್ಲಪ್ಪ", "ಇಲ್ಲಮ್ಮ", "ಇಲ್ಲಸರ್", "ಅಲ್ಲ", "ಅಲ್ಲಾ", "ಅಲ್ಲರೀ",
    "illa", "illaa", "alla",
)
EXACT_WORDS.update(norm_text(w) for w in ("ಇಲ್ಲ", "ಇಲ್ಲಾ", "ಅಲ್ಲ", "ಅಲ್ಲಾ"))

# Multi-word phrases checked with substring search BEFORE yes/no (so "pata nahi" is not a "no").
UNSURE_PHRASES = tuple(
    norm_text(p)
    for p in (
        "not sure", "dont know", "do not know", "no idea", "idk", "unsure", "not certain",
        "पता नहीं", "पता नही", "मालूम नहीं", "मालूम नही", "pata nahi", "pata nahin", "maloom nahi",
        "malum nahi", "पक्का नहीं",
        "తెలియదు", "తెలీదు", "తెలియదండి", "teliyadu", "telidu", "teliyadandi", "ఏమో", "గుర్తులేదు",
        "ಗೊತ್ತಿಲ್ಲ", "ಗೊತ್ತಿಲ್ಲಾ", "ತಿಳಿದಿಲ್ಲ", "ಖಚಿತವಿಲ್ಲ", "gottilla", "tilidilla",
    )
)

# ---------------------------------------------------------------------------------------------
# Number words (ages are the only numbers we need; ITN from Prisma usually gives digits)
# ---------------------------------------------------------------------------------------------
_EN_UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
_EN_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fourty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
}

_TE_UNITS = {
    "ఒకటి": 1, "రెండు": 2, "మూడు": 3, "నాలుగు": 4, "ఐదు": 5, "అయిదు": 5, "ఆరు": 6, "ఏడు": 7,
    "ఎనిమిది": 8, "తొమ్మిది": 9,
}
_TE_SINGLE = {  # 10-19 are single words in Telugu
    "పది": 10, "పదకొండు": 11, "పన్నెండు": 12, "పదమూడు": 13, "పద్నాలుగు": 14, "పధ్నాలుగు": 14,
    "పదిహేను": 15, "పదహారు": 16, "పదిహేడు": 17, "పద్దెనిమిది": 18, "పందొమ్మిది": 19, "పంతొమ్మిది": 19,
}
_TE_TENS = {
    "ఇరవై": 20, "ముప్పై": 30, "నలభై": 40, "యాభై": 50, "ఏభై": 50, "అరవై": 60, "డెబ్బై": 70, "ఎనభై": 80,
    "తొంభై": 90,
}

_HI_SINGLE = {
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पाँच": 5, "पांच": 5, "छह": 6, "छः": 6, "छ": 6, "सात": 7,
    "आठ": 8, "नौ": 9, "दस": 10, "ग्यारह": 11, "बारह": 12, "तेरह": 13, "चौदह": 14, "पंद्रह": 15,
    "पन्द्रह": 15, "सोलह": 16, "सत्रह": 17, "अठारह": 18, "अट्ठारह": 18, "उन्नीस": 19, "बीस": 20,
    "इक्कीस": 21, "बाईस": 22, "तेईस": 23, "चौबीस": 24, "पच्चीस": 25, "छब्बीस": 26, "सत्ताईस": 27,
    "अट्ठाईस": 28, "अठाईस": 28, "उनतीस": 29, "तीस": 30, "इकतीस": 31, "बत्तीस": 32, "तैंतीस": 33,
    "चौंतीस": 34, "पैंतीस": 35, "छत्तीस": 36, "सैंतीस": 37, "अड़तीस": 38, "उनतालीस": 39, "चालीस": 40,
    "इकतालीस": 41, "बयालीस": 42, "तैंतालीस": 43, "चवालीस": 44, "चौवालीस": 44, "पैंतालीस": 45,
    "छियालीस": 46, "सैंतालीस": 47, "अड़तालीस": 48, "उनचास": 49, "पचास": 50, "इक्यावन": 51, "बावन": 52,
    "तिरपन": 53, "चौवन": 54, "पचपन": 55, "छप्पन": 56, "सत्तावन": 57, "अट्ठावन": 58, "उनसठ": 59,
    "साठ": 60, "इकसठ": 61, "बासठ": 62, "तिरसठ": 63, "चौंसठ": 64, "पैंसठ": 65, "छियासठ": 66,
    "सड़सठ": 67, "अड़सठ": 68, "उनहत्तर": 69, "सत्तर": 70, "इकहत्तर": 71, "बहत्तर": 72, "तिहत्तर": 73,
    "चौहत्तर": 74, "पचहत्तर": 75, "छिहत्तर": 76, "सतहत्तर": 77, "अठहत्तर": 78, "उनासी": 79, "अस्सी": 80,
    "नब्बे": 90,
}

# value tables after normalisation. UNITS can combine after a TENS word ("thirty five").
UNITS: dict[str, int] = {}
TENS: dict[str, int] = {}
SINGLES: dict[str, int] = {}  # words that are complete numbers by themselves
for _d in (_EN_UNITS, _TE_UNITS):
    for _w, _v in _d.items():
        UNITS[norm_text(_w)] = _v
for _d in (_EN_TENS, _TE_TENS):
    for _w, _v in _d.items():
        TENS[norm_text(_w)] = _v
for _d in (_TE_SINGLE, _HI_SINGLE):
    for _w, _v in _d.items():
        SINGLES[norm_text(_w)] = _v
# "one..nineteen" in English are also complete numbers
for _w, _v in _EN_UNITS.items():
    SINGLES.setdefault(norm_text(_w), _v)
# Hindi has no tens+unit compounds, but "छ" is too short to trust as a prefix; exact match only.

# ---- Kannada numbers -------------------------------------------------------------------------
_KN_UNITS = {"ಒಂದು": 1, "ಎರಡು": 2, "ಮೂರು": 3, "ನಾಲ್ಕು": 4, "ಐದು": 5, "ಆರು": 6, "ಏಳು": 7, "ಎಂಟು": 8, "ಒಂಬತ್ತು": 9}
_KN_SINGLE = {
    "ಹತ್ತು": 10, "ಹನ್ನೊಂದು": 11, "ಹನ್ನೆರಡು": 12, "ಹದಿಮೂರು": 13, "ಹದಿನಾಲ್ಕು": 14, "ಹದಿನೈದು": 15,
    "ಹದಿನಾರು": 16, "ಹದಿನೇಳು": 17, "ಹದಿನೆಂಟು": 18, "ಹತ್ತೊಂಬತ್ತು": 19, "ಹತ್ತೊಂಬತ್ತು": 19,
}
_KN_TENS = {
    "ಇಪ್ಪತ್ತು": 20, "ಮೂವತ್ತು": 30, "ನಲವತ್ತು": 40, "ಐವತ್ತು": 50, "ಅರವತ್ತು": 60, "ಎಪ್ಪತ್ತು": 70,
    "ಎಂಬತ್ತು": 80, "ತೊಂಬತ್ತು": 90,
}
# Kannada joins tens and units into one word with sandhi: ಮೂವತ್ತು + ಐದು -> ಮೂವತ್ತೈದು (35).
_KN_UNIT_JOIN = {1: "ೊಂದು", 2: "ೆರಡು", 3: "ಮೂರು", 4: "ನಾಲ್ಕು", 5: "ೈದು", 6: "ಾರು", 7: "ೇಳು", 8: "ೆಂಟು", 9: "ೊಂಬತ್ತು"}
for _w, _v in _KN_UNITS.items():
    UNITS[norm_text(_w)] = _v
for _w, _v in _KN_TENS.items():
    TENS[norm_text(_w)] = _v
    _stem = _w[:-1]  # drop the final "ು" vowel sign: ಮೂವತ್ತು -> ಮೂವತ್ತ
    for _u, _suffix in _KN_UNIT_JOIN.items():
        SINGLES[norm_text(_stem + _suffix)] = _v + _u
for _w, _v in _KN_SINGLE.items():
    SINGLES[norm_text(_w)] = _v

# ---------------------------------------------------------------------------------------------
# Keywords
# ---------------------------------------------------------------------------------------------
AGE_WORDS = _set(
    "year", "years", "yrs", "yr", "old", "age", "aged", "am", "im",
    "साल", "वर्ष", "उम्र", "आयु", "saal", "sal", "umar", "umr",
    "ఏళ్లు", "ఏళ్ళు", "ఏళ్ల", "ఏళ్ళ", "ఏండ్లు", "సంవత్సరాలు", "సంవత్సరాల", "సంవత్సరం", "వయసు", "వయస్సు",
    "vayasu", "yella", "ellu",
    "ವರ್ಷ", "ವರ್ಷಗಳು", "ವರುಷ", "ವಯಸ್ಸು", "ವಯಸ್ಸಿನ", "ವಯಸು", "varsha", "vayassu",
)

LAND_WORDS = _set(
    "acre", "acres", "hectare", "hectares", "farmland", "land", "field", "fields",
    "ekar", "ekad", "ekkad", "khet", "zameen", "jameen", "zamin", "एकड़", "एकड", "हेक्टेयर", "खेत", "ज़मीन", "जमीन",
    "ఎకరం", "ఎకరాలు", "ఎకరా", "ఎకరాల", "ఎకరము", "పొలం", "పొలము", "భూమి", "ekaram", "ekaralu", "polam", "bhoomi",
    "ಎಕರೆ", "ಎಕರೆಗಳು", "ಹೆಕ್ಟೇರ್", "ಜಮೀನು", "ಹೊಲ", "ಭೂಮಿ", "ekare", "jameenu", "hola",
)
# Words that mean "someone else's land" - we refuse to infer ownership from the sentence.
TENANCY_WORDS = _set(
    "rent", "rented", "lease", "leased", "tenant", "sharecrop", "sharecropper", "others", "someone",
    "किराए", "किराये", "बटाई", "पट्टे", "कौल", "కౌలు", "కౌలుకు", "అద్దె", "ఇతరుల",
    "ಗುತ್ತಿಗೆ", "ಬಾಡಿಗೆ", "ಗೇಣಿ", "ಬೇರೆಯವರ",
)
BANK_WORDS = _set("bank", "बैंक", "బ్యాంక్", "బ్యాంకు", "బ్యాంకులో", "bainku", "ಬ್ಯಾಂಕ್", "ಬ್ಯಾಂಕಿನಲ್ಲಿ")
ACCOUNT_WORDS = _set("account", "acount", "खाता", "खाते", "ఖాతా", "ఖాతాలో", "khata", "khaata", "khatha", "ಖಾತೆ", "ಅಕೌಂಟ್")

# ---------------------------------------------------------------------------------------------
# Money, place and unit words (income, rural/urban)
# ---------------------------------------------------------------------------------------------
LAKH_WORDS = _set("lakh", "lakhs", "lac", "lacs", "लाख", "లక్ష", "లక్షలు", "లక్షల", "ಲಕ್ಷ", "ಲಕ್ಷಗಳು")
THOUSAND_WORDS = _set(
    "thousand", "thousands", "k", "हज़ार", "हजार", "hazar", "hazaar", "వేలు", "వేల", "ಸಾವಿರ", "ಸಾವಿರಗಳು",
)
MONTH_WORDS = _set(
    "month", "monthly", "mahina", "mahine", "mahinay", "महीना", "महीने", "मासिक", "నెల", "నెలకు", "నెలవారీ",
    "ತಿಂಗಳು", "ತಿಂಗಳಿಗೆ", "ತಿಂಗಳ",
)
VILLAGE_WORDS = _set(
    "village", "rural", "gram", "gaon", "gaanv", "गांव", "गाँव", "ग्राम", "ग्रामीण",
    "గ్రామం", "గ్రామంలో", "పల్లె", "పల్లెటూరు", "ಹಳ್ಳಿ", "ಹಳ್ಳಿಯಲ್ಲಿ", "ಗ್ರಾಮ",
)
CITY_WORDS = _set(
    "city", "town", "urban", "shehar", "sheher", "शहर", "नगर", "పట్టణం", "పట్టణంలో", "నగరం", "నగరంలో",
    "ನಗರ", "ನಗರದಲ್ಲಿ", "ಪಟ್ಟಣ", "ಪಟ್ಟಣದಲ್ಲಿ",
)
