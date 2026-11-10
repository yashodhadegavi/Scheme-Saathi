"""All user-facing text, in English, Hindi and Telugu.

Numbers inside text that will be *spoken* are written as words on purpose: Gnani's TTS guide
warns that raw digits and currency strings can be mispronounced.

NOTE FOR REVIEWERS: Hindi and Telugu copy was written for this prototype and should be
reviewed by a native speaker before any public deployment.
"""
from __future__ import annotations

LANGS = ("en", "hi", "te", "kn")

QUESTIONS = {
    "age": {
        "en": "How old are you?",
        "hi": "आपकी उम्र कितनी है?",
        "te": "మీ వయసు ఎంత?",
    },
    "has_bank_account": {
        "en": "Do you have a savings account in a bank or post office?",
        "hi": "क्या आपका किसी बैंक या डाकघर में बचत खाता है?",
        "te": "మీకు బ్యాంకులో లేదా పోస్టాఫీసులో పొదుపు ఖాతా ఉందా?",
    },
    "owns_farmland": {
        "en": "Does your family own farmland?",
        "hi": "क्या आपके परिवार के पास खेती की ज़मीन है?",
        "te": "మీ కుటుంబానికి వ్యవసాయ భూమి ఉందా?",
    },
    "self_income_tax_payer": {
        "en": "Have you ever paid income tax?",
        "hi": "क्या आपने कभी आयकर भरा है?",
        "te": "మీరు ఎప్పుడైనా ఆదాయపు పన్ను చెల్లించారా?",
    },
    "family_income_tax_payer": {
        "en": "In the last year, did you or anyone in your family, like your husband, wife or children, pay income tax?",
        "hi": "पिछले साल क्या आपने या आपके परिवार में किसी ने, जैसे पति, पत्नी या बच्चों ने, आयकर भरा?",
        "te": "గత ఏడాది మీరు లేదా మీ కుటుంబంలో ఎవరైనా, అంటే భర్త, భార్య లేదా పిల్లలు, ఆదాయపు పన్ను చెల్లించారా?",
    },
    "govt_pension_10k": {
        "en": "Does anyone in your family get a retired government pension of ten thousand rupees or more a month? Retired class four staff do not count.",
        "hi": "क्या आपके परिवार में किसी को महीने में दस हज़ार रुपये या उससे ज़्यादा की सरकारी पेंशन मिलती है? सेवानिवृत्त चतुर्थ श्रेणी कर्मचारी इसमें नहीं गिने जाते।",
        "te": "మీ కుటుంబంలో ఎవరికైనా నెలకు పది వేల రూపాయలు లేదా అంతకంటే ఎక్కువ ప్రభుత్వ పెన్షన్ వస్తుందా? రిటైర్ అయిన నాలుగో తరగతి ఉద్యోగులను లెక్కించకండి.",
    },
    "higher_status_member": {
        "en": "Is anyone in your family a minister, MP, MLA, mayor, a government officer, or a registered doctor, engineer, lawyer, chartered accountant or architect? Class four staff do not count.",
        "hi": "क्या आपके परिवार में कोई मंत्री, सांसद, विधायक, मेयर, सरकारी अधिकारी, या पंजीकृत डॉक्टर, इंजीनियर, वकील, चार्टर्ड अकाउंटेंट या आर्किटेक्ट है? चतुर्थ श्रेणी कर्मचारी इसमें नहीं गिने जाते।",
        "te": "మీ కుటుంబంలో ఎవరైనా మంత్రి, ఎంపీ, ఎమ్మెల్యే, మేయర్, ప్రభుత్వ అధికారి, లేదా రిజిస్టర్ అయిన డాక్టర్, ఇంజినీర్, లాయర్, చార్టర్డ్ అకౌంటెంట్ లేదా ఆర్కిటెక్ట్ ఉన్నారా? నాలుగో తరగతి ఉద్యోగులను లెక్కించకండి.",
    },
}

SLOT_LABELS = {
    "age": {"en": "Age", "hi": "उम्र", "te": "వయసు"},
    "has_bank_account": {"en": "Bank or post office account", "hi": "बैंक या डाकघर खाता", "te": "బ్యాంకు / పోస్టాఫీసు ఖాతా"},
    "owns_farmland": {"en": "Family owns farmland", "hi": "परिवार के पास खेती की ज़मीन", "te": "కుటుంబానికి వ్యవసాయ భూమి"},
    "self_income_tax_payer": {"en": "Ever paid income tax", "hi": "कभी आयकर भरा", "te": "ఎప్పుడైనా ఆదాయపు పన్ను చెల్లించారు"},
    "family_income_tax_payer": {"en": "Family paid income tax last year", "hi": "परिवार ने पिछले साल आयकर भरा", "te": "కుటుంబం గత ఏడాది ఆదాయపు పన్ను చెల్లించింది"},
    "govt_pension_10k": {"en": "Family pension of 10,000+ a month", "hi": "परिवार में दस हज़ार+ की पेंशन", "te": "కుటుంబంలో పది వేలు+ పెన్షన్"},
    "higher_status_member": {"en": "Officer, office-holder or professional in family", "hi": "परिवार में अधिकारी, पदाधिकारी या पेशेवर", "te": "కుటుంబంలో అధికారి, పదవిలో ఉన్నవారు లేదా వృత్తిపరులు"},
}

VALUE_WORDS = {
    True: {"en": "Yes", "hi": "हाँ", "te": "అవును"},
    False: {"en": "No", "hi": "नहीं", "te": "కాదు"},
    "unsure": {"en": "Not sure", "hi": "पता नहीं", "te": "తెలియదు"},
    None: {"en": "Not asked yet", "hi": "अभी नहीं पूछा", "te": "ఇంకా అడగలేదు"},
}

MESSAGES = {
    "greeting": {
        "en": "Namaste! I'm Scheme Saathi. I'll ask a few short questions and tell you which government schemes you may qualify for. You can speak or type.",
        "hi": "नमस्ते! मैं स्कीम साथी हूँ। मैं कुछ छोटे सवाल पूछूँगा और बताऊँगा कि आप किन सरकारी योजनाओं के पात्र हो सकते हैं। आप बोल सकते हैं या टाइप कर सकते हैं।",
        "te": "నమస్తే! నేను స్కీమ్ సాథీని. కొన్ని చిన్న ప్రశ్నలు అడిగి, మీరు ఏ ప్రభుత్వ పథకాలకు అర్హులు కావచ్చో చెబుతాను. మీరు మాట్లాడవచ్చు లేదా టైప్ చేయవచ్చు.",
    },
    "reprompt_yn": {
        "en": "Sorry, I didn't catch that. Please say yes, no, or not sure.",
        "hi": "माफ़ कीजिए, मैं समझ नहीं पाया। कृपया हाँ, नहीं, या पता नहीं कहें।",
        "te": "క్షమించండి, నాకు అర్థం కాలేదు. దయచేసి అవును, లేదు, లేదా తెలియదు అని చెప్పండి.",
    },
    "reprompt_age": {
        "en": "Sorry, I didn't catch your age. Please say it as a number, for example thirty five.",
        "hi": "माफ़ कीजिए, मैं आपकी उम्र समझ नहीं पाया। कृपया संख्या में बताइए, जैसे पैंतीस।",
        "te": "క్షమించండి, మీ వయసు అర్థం కాలేదు. దయచేసి సంఖ్యలో చెప్పండి, ఉదాహరణకు ముప్పై ఐదు.",
    },
    "no_speech": {
        "en": "I couldn't hear anything. Please try again.",
        "hi": "मुझे कुछ सुनाई नहीं दिया। कृपया दोबारा बोलिए।",
        "te": "నాకు ఏమీ వినిపించలేదు. దయచేసి మళ్లీ చెప్పండి.",
    },
    "gave_up": {
        "en": "That's fine, I'll mark that as not sure and continue.",
        "hi": "कोई बात नहीं, मैं इसे 'पता नहीं' मानकर आगे बढ़ता हूँ।",
        "te": "పర్వాలేదు, దీన్ని 'తెలియదు' గా నమోదు చేసి ముందుకు వెళ్తాను.",
    },
    "already_done": {
        "en": "Your results are shown above. Press Start over to check again.",
        "hi": "आपके नतीजे ऊपर दिखाए गए हैं। दोबारा जाँचने के लिए फिर से शुरू करें दबाएँ।",
        "te": "మీ ఫలితాలు పైన చూపించబడ్డాయి. మళ్లీ చూడాలంటే మళ్లీ మొదలుపెట్టండి నొక్కండి.",
    },
    "summary_intro": {"en": "Here is what I found.", "hi": "यह रहा नतीजा।", "te": "ఫలితం ఇదిగో."},
    "summary_eligible": {
        "en": "You may qualify for: {names}.",
        "hi": "आप इन योजनाओं के लिए पात्र हो सकते हैं: {names}।",
        "te": "మీరు ఈ పథకాలకు అర్హులు కావచ్చు: {names}.",
    },
    "summary_none": {
        "en": "I could not confirm any scheme from your answers.",
        "hi": "आपके जवाबों से मैं किसी योजना की पुष्टि नहीं कर पाया।",
        "te": "మీ సమాధానాల ఆధారంగా నేను ఏ పథకాన్నీ నిర్ధారించలేకపోయాను.",
    },
    "summary_not": {
        "en": "You do not seem to qualify for: {names}.",
        "hi": "इन योजनाओं के लिए आप पात्र नहीं लगते: {names}।",
        "te": "ఈ పథకాలకు మీరు అర్హులు కారు: {names}.",
    },
    "summary_check": {
        "en": "I cannot be sure about: {names}. Please confirm at your bank or Common Service Centre.",
        "hi": "इनके बारे में मैं पक्का नहीं कह सकता: {names}। कृपया बैंक या कॉमन सर्विस सेंटर में पुष्टि करें।",
        "te": "వీటి గురించి నేను ఖచ్చితంగా చెప్పలేను: {names}. దయచేసి బ్యాంకులో లేదా కామన్ సర్వీస్ సెంటర్‌లో నిర్ధారించుకోండి.",
    },
    "summary_closing": {
        "en": "This is guidance only, and the final decision rests with the authorities. Never share your OTP or PIN with anyone.",
        "hi": "यह सिर्फ़ जानकारी है, अंतिम फ़ैसला संबंधित अधिकारियों का होगा। अपना ओटीपी या पिन किसी को न बताएँ।",
        "te": "ఇది కేవలం సమాచారం మాత్రమే. తుది నిర్ణయం సంబంధిత అధికారులదే. మీ ఓటీపీ లేదా పిన్ ఎవరికీ చెప్పకండి.",
    },
    "noted": {"en": "Noted", "hi": "दर्ज किया", "te": "నమోదు చేశాను"},
}

UI = {
    "title": {"en": "Scheme Saathi", "hi": "स्कीम साथी", "te": "స్కీమ్ సాథీ"},
    "tagline": {
        "en": "Speak in your language. Find out which government schemes you may qualify for.",
        "hi": "अपनी भाषा में बोलिए। जानिए आप किन सरकारी योजनाओं के पात्र हो सकते हैं।",
        "te": "మీ భాషలో మాట్లాడండి. మీరు ఏ ప్రభుత్వ పథకాలకు అర్హులో తెలుసుకోండి.",
    },
    "speak": {"en": "Press the mic and answer", "hi": "माइक दबाकर जवाब दीजिए", "te": "మైక్ నొక్కి సమాధానం చెప్పండి"},
    "type": {"en": "Or type your answer", "hi": "या अपना जवाब टाइप करें", "te": "లేదా మీ సమాధానం టైప్ చేయండి"},
    "start_over": {"en": "Start over", "hi": "फिर से शुरू करें", "te": "మళ్లీ మొదలుపెట్టండి"},
    "your_details": {"en": "What I know about you", "hi": "आपके बारे में मेरी जानकारी", "te": "మీ గురించి నాకు తెలిసినవి"},
    "correct": {"en": "Fix a wrong answer", "hi": "गलत जवाब सुधारें", "te": "తప్పు సమాధానం సరిదిద్దండి"},
    "apply_changes": {"en": "Update and re-check", "hi": "अपडेट करके दोबारा जाँचें", "te": "అప్‌డేట్ చేసి మళ్లీ చూడండి"},
    "eligible": {"en": "You may qualify", "hi": "आप पात्र हो सकते हैं", "te": "మీరు అర్హులు కావచ్చు"},
    "not_eligible": {"en": "Does not seem to apply", "hi": "लागू नहीं लगता", "te": "వర్తించకపోవచ్చు"},
    "check": {"en": "Please confirm locally", "hi": "स्थानीय स्तर पर पुष्टि करें", "te": "స్థానికంగా నిర్ధారించుకోండి"},
    "documents": {"en": "Keep ready", "hi": "तैयार रखें", "te": "సిద్ధంగా ఉంచుకోండి"},
    "how_to_apply": {"en": "How to apply", "hi": "आवेदन कैसे करें", "te": "ఎలా దరఖాస్తు చేయాలి"},
    "official_source": {"en": "Official source", "hi": "आधिकारिक स्रोत", "te": "అధికారిక వనరు"},
    "why": {"en": "Why", "hi": "कारण", "te": "కారణం"},
    "speak_replies": {"en": "Speak the replies aloud", "hi": "जवाब बोलकर सुनाएँ", "te": "సమాధానాలను చదివి వినిపించండి"},
    "no_key": {
        "en": "No Gnani API key found, so voice is off. Typing still works. Add GNANI_API_KEY to a .env file to turn voice on.",
        "hi": "Gnani API key नहीं मिली, इसलिए आवाज़ बंद है। टाइप करना काम करता है। आवाज़ चालू करने के लिए .env फ़ाइल में GNANI_API_KEY जोड़ें।",
        "te": "Gnani API కీ కనిపించలేదు, కాబట్టి వాయిస్ ఆఫ్‌లో ఉంది. టైప్ చేయడం పని చేస్తుంది. వాయిస్ ఆన్ చేయడానికి .env ఫైల్‌లో GNANI_API_KEY జోడించండి.",
    },
    "heard": {"en": "I heard", "hi": "मैंने सुना", "te": "నాకు వినిపించింది"},
    "stt_failed": {
        "en": "I couldn't process the audio. You can type your answer instead.",
        "hi": "मैं आवाज़ को समझ नहीं पाया। आप अपना जवाब टाइप कर सकते हैं।",
        "te": "నేను ఆడియోను ప్రాసెస్ చేయలేకపోయాను. మీరు బదులుగా మీ సమాధానాన్ని టైప్ చేయవచ్చు.",
    },
    "disclaimer": {
        "en": "Prototype for guidance only. Final eligibility is decided by the authorities. Rules checked on {date}.",
        "hi": "यह सिर्फ़ मार्गदर्शन के लिए एक प्रोटोटाइप है। अंतिम पात्रता अधिकारी तय करते हैं। नियम {date} को जाँचे गए।",
        "te": "ఇది కేవలం మార్గదర్శకం కోసం ప్రోటోటైప్. తుది అర్హతను అధికారులే నిర్ణయిస్తారు. నియమాలు {date} న తనిఖీ చేయబడ్డాయి.",
    },
}


from . import i18n_extra, i18n_kn  # noqa: E402

_TABLES = {"QUESTIONS": QUESTIONS, "SLOT_LABELS": SLOT_LABELS, "VALUE_WORDS": VALUE_WORDS,
           "MESSAGES": MESSAGES, "UI": UI}
i18n_kn.merge(_TABLES)
i18n_extra.merge(_TABLES)



def t(table: dict, key: str, lang: str, **fmt) -> str:
    """Look up ``table[key][lang]`` (falls back to English) and format placeholders."""
    entry = table[key]
    s = entry.get(lang) or entry["en"]
    return s.format(**fmt) if fmt else s
