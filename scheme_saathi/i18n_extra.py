"""Text for the housing, health and scholarship questions, in English, Hindi, Telugu, Kannada.

Merged into the tables in i18n.py at import time. Numbers are words on purpose (clean TTS).
NOTE FOR REVIEWERS: Hindi, Telugu and Kannada copy was written for this prototype; have native
speakers review it before any public deployment.
"""
L = ("en", "hi", "te", "kn")


def T(en, hi, te, kn):
    return dict(zip(L, (en, hi, te, kn)))


QUESTIONS = {
    "lives_in_city": T(
        "Do you live in a city or town, and not in a village?",
        "क्या आप शहर या कस्बे में रहते हैं, गाँव में नहीं?",
        "మీరు గ్రామంలో కాకుండా పట్టణంలో లేదా నగరంలో నివసిస్తున్నారా?",
        "ನೀವು ಹಳ್ಳಿಯಲ್ಲಿ ಅಲ್ಲ, ನಗರ ಅಥವಾ ಪಟ್ಟಣದಲ್ಲಿ ವಾಸಿಸುತ್ತಿದ್ದೀರಾ?"),
    "owns_pucca_house": T(
        "Does your family own a pucca house anywhere in India? A pucca house has strong walls and a permanent roof.",
        "क्या आपके परिवार के पास भारत में कहीं भी पक्का मकान है? पक्के मकान की दीवारें और छत मज़बूत और स्थायी होती हैं।",
        "మీ కుటుంబానికి భారతదేశంలో ఎక్కడైనా పక్కా ఇల్లు ఉందా? పక్కా ఇంటికి గట్టి గోడలు, శాశ్వత పైకప్పు ఉంటాయి.",
        "ನಿಮ್ಮ ಕುಟುಂಬಕ್ಕೆ ಭಾರತದಲ್ಲಿ ಎಲ್ಲಿಯಾದರೂ ಪಕ್ಕಾ ಮನೆ ಇದೆಯೇ? ಪಕ್ಕಾ ಮನೆಗೆ ಗಟ್ಟಿ ಗೋಡೆಗಳು ಮತ್ತು ಶಾಶ್ವತ ಛಾವಣಿ ಇರುತ್ತದೆ."),
    "annual_income": T(
        "What is your family's total income in a year, from all sources? You can say it like two lakh, or ten thousand a month.",
        "आपके परिवार की सभी स्रोतों से साल भर की कुल आय कितनी है? आप इसे ऐसे बता सकते हैं, दो लाख, या दस हज़ार रुपये महीना।",
        "మీ కుటుంబానికి అన్ని మార్గాల నుంచి ఏడాదికి మొత్తం ఆదాయం ఎంత? దీన్ని రెండు లక్షలు, లేదా నెలకు పది వేలు అని చెప్పవచ్చు.",
        "ಎಲ್ಲಾ ಮೂಲಗಳಿಂದ ನಿಮ್ಮ ಕುಟುಂಬದ ವರ್ಷದ ಒಟ್ಟು ಆದಾಯ ಎಷ್ಟು? ಇದನ್ನು ಎರಡು ಲಕ್ಷ, ಅಥವಾ ತಿಂಗಳಿಗೆ ಹತ್ತು ಸಾವಿರ ಎಂದು ಹೇಳಬಹುದು."),
    "pmjay_group": T(
        "Does your family fit any of these: living in a one room house with kutcha walls and roof, belonging to a Scheduled Caste or Tribe, having no adult earning member, having a disabled member, living on daily wage labour without land, or working as a domestic worker, street vendor, construction worker or driver?",
        "क्या आपका परिवार इनमें से किसी में आता है: कच्ची दीवारों और छत वाले एक कमरे के घर में रहना, अनुसूचित जाति या जनजाति का होना, कमाने वाला कोई वयस्क न होना, कोई दिव्यांग सदस्य होना, बिना ज़मीन के दिहाड़ी मज़दूरी पर निर्भर होना, या घरेलू कामगार, रेहड़ी-पटरी वाला, निर्माण मज़दूर या ड्राइवर के रूप में काम करना?",
        "మీ కుటుంబం వీటిలో ఏదైనా వర్గంలోకి వస్తుందా: కచ్చా గోడలు, కచ్చా పైకప్పు ఉన్న ఒక గది ఇంట్లో నివసించడం, ఎస్సీ లేదా ఎస్టీ కుటుంబం కావడం, సంపాదించే పెద్దలు ఎవరూ లేకపోవడం, దివ్యాంగ సభ్యుడు ఉండటం, భూమి లేకుండా రోజువారీ కూలీ పనిపై ఆధారపడటం, లేదా ఇంటి పనివారు, వీధి వ్యాపారి, నిర్మాణ కార్మికుడు లేదా డ్రైవర్‌గా పనిచేయడం?",
        "ನಿಮ್ಮ ಕುಟುಂಬ ಇವುಗಳಲ್ಲಿ ಯಾವುದಕ್ಕಾದರೂ ಸೇರುತ್ತದೆಯೇ: ಕಚ್ಚಾ ಗೋಡೆ ಮತ್ತು ಛಾವಣಿಯ ಒಂದು ಕೋಣೆಯ ಮನೆಯಲ್ಲಿ ವಾಸ, ಪರಿಶಿಷ್ಟ ಜಾತಿ ಅಥವಾ ಪಂಗಡ, ಸಂಪಾದಿಸುವ ವಯಸ್ಕ ಸದಸ್ಯರಿಲ್ಲದಿರುವುದು, ಅಂಗವಿಕಲ ಸದಸ್ಯರಿರುವುದು, ಜಮೀನಿಲ್ಲದೆ ದಿನಗೂಲಿ ಕೆಲಸದ ಮೇಲೆ ಅವಲಂಬನೆ, ಅಥವಾ ಮನೆಕೆಲಸದವರು, ಬೀದಿ ವ್ಯಾಪಾರಿ, ಕಟ್ಟಡ ಕಾರ್ಮಿಕ ಅಥವಾ ಚಾಲಕರಾಗಿ ಕೆಲಸ?"),
    "has_student": T(
        "Is there a student, in your family or yourself, for whom you want to check scholarships?",
        "क्या आपके परिवार में या आप खुद कोई छात्र हैं जिसके लिए आप छात्रवृत्ति जाँचना चाहते हैं?",
        "ఉపకార వేతనాలు తెలుసుకోవాలనుకునే విద్యార్థి మీ కుటుంబంలో ఉన్నారా, లేదా మీరే విద్యార్థినా?",
        "ವಿದ್ಯಾರ್ಥಿವೇತನ ಪರಿಶೀಲಿಸಲು ಬಯಸುವ ವಿದ್ಯಾರ್ಥಿ ನಿಮ್ಮ ಕುಟುಂಬದಲ್ಲಿ ಇದ್ದಾರೆಯೇ, ಅಥವಾ ನೀವೇ ವಿದ್ಯಾರ್ಥಿಯೇ?"),
    "student_class8_govt": T(
        "Is the student in class eight, in a government, government aided or local body school?",
        "क्या छात्र आठवीं कक्षा में है, किसी सरकारी, सरकारी सहायता प्राप्त या स्थानीय निकाय के स्कूल में?",
        "విద్యార్థి ప్రభుత్వ, ప్రభుత్వ సహాయ లేదా స్థానిక సంస్థ పాఠశాలలో ఎనిమిదో తరగతి చదువుతున్నారా?",
        "ವಿದ್ಯಾರ್ಥಿ ಸರ್ಕಾರಿ, ಸರ್ಕಾರಿ ಅನುದಾನಿತ ಅಥವಾ ಸ್ಥಳೀಯ ಸಂಸ್ಥೆಯ ಶಾಲೆಯಲ್ಲಿ ಎಂಟನೇ ತರಗತಿಯಲ್ಲಿ ಓದುತ್ತಿದ್ದಾರೆಯೇ?"),
    "student_post_matric": T(
        "Is the student studying after class ten, that is class eleven, class twelve, a diploma, ITI or college?",
        "क्या छात्र दसवीं के बाद पढ़ रहा है, यानी ग्यारहवीं, बारहवीं, डिप्लोमा, आईटीआई या कॉलेज में?",
        "విద్యార్థి పదో తరగతి తర్వాత, అంటే పదకొండు, పన్నెండు, డిప్లొమా, ఐటీఐ లేదా కళాశాలలో చదువుతున్నారా?",
        "ವಿದ್ಯಾರ್ಥಿ ಹತ್ತನೇ ತರಗತಿಯ ನಂತರ, ಅಂದರೆ ಹನ್ನೊಂದು, ಹನ್ನೆರಡು, ಡಿಪ್ಲೊಮಾ, ಐಟಿಐ ಅಥವಾ ಕಾಲೇಜಿನಲ್ಲಿ ಓದುತ್ತಿದ್ದಾರೆಯೇ?"),
    "student_is_sc": T(
        "Does the student belong to a Scheduled Caste?",
        "क्या छात्र अनुसूचित जाति का है?",
        "విద్యార్థి షెడ్యూల్డ్ కులానికి చెందినవారా?",
        "ವಿದ್ಯಾರ್ಥಿ ಪರಿಶಿಷ್ಟ ಜಾತಿಗೆ ಸೇರಿದವರೇ?"),
    "student_is_st": T(
        "Does the student belong to a Scheduled Tribe?",
        "क्या छात्र अनुसूचित जनजाति का है?",
        "విద్యార్థి షెడ్యూల్డ్ తెగకు చెందినవారా?",
        "ವಿದ್ಯಾರ್ಥಿ ಪರಿಶಿಷ್ಟ ಪಂಗಡಕ್ಕೆ ಸೇರಿದವರೇ?"),
    "marks_percent": T(
        "What percentage of marks did the student score in class seven? You can say it like sixty.",
        "छात्र को सातवीं कक्षा में कितने प्रतिशत अंक मिले थे? आप इसे ऐसे बता सकते हैं, साठ।",
        "విద్యార్థికి ఏడో తరగతిలో ఎంత శాతం మార్కులు వచ్చాయి? దీన్ని అరవై అని చెప్పవచ్చు.",
        "ವಿದ್ಯಾರ್ಥಿ ಏಳನೇ ತರಗತಿಯಲ್ಲಿ ಎಷ್ಟು ಶೇಕಡಾ ಅಂಕ ಗಳಿಸಿದ್ದಾರೆ? ಇದನ್ನು ಅರವತ್ತು ಎಂದು ಹೇಳಬಹುದು."),
}

SLOT_LABELS = {
    "lives_in_city": T("Lives in a city or town", "शहर या कस्बे में रहते हैं", "పట్టణం లేదా నగరంలో నివాసం", "ನಗರ ಅಥವಾ ಪಟ್ಟಣದಲ್ಲಿ ವಾಸ"),
    "owns_pucca_house": T("Family owns a pucca house", "परिवार के पास पक्का मकान", "కుటుంబానికి పక్కా ఇల్లు", "ಕುಟುಂಬಕ್ಕೆ ಪಕ್ಕಾ ಮನೆ"),
    "annual_income": T("Family income per year (rupees)", "परिवार की सालाना आय (रुपये)", "కుటుంబ వార్షిక ఆదాయం (రూపాయలు)", "ಕುಟುಂಬದ ವಾರ್ಷಿಕ ಆದಾಯ (ರೂಪಾಯಿ)"),
    "pmjay_group": T("Fits a health cover group", "स्वास्थ्य बीमा वर्ग में आता है", "ఆరోగ్య బీమా వర్గానికి సరిపోతుంది", "ಆರೋಗ್ಯ ವಿಮೆ ವರ್ಗಕ್ಕೆ ಸೇರುತ್ತದೆ"),
    "has_student": T("Has a student to check", "जाँचने के लिए छात्र है", "తనిఖీ చేయాల్సిన విద్యార్థి ఉన్నారు", "ಪರಿಶೀಲಿಸಬೇಕಾದ ವಿದ್ಯಾರ್ಥಿ ಇದ್ದಾರೆ"),
    "student_class8_govt": T("Student in class eight, government school", "छात्र आठवीं में, सरकारी स्कूल", "విద్యార్థి ఎనిమిదో తరగతి, ప్రభుత్వ పాఠశాల", "ವಿದ್ಯಾರ್ಥಿ ಎಂಟನೇ ತರಗತಿ, ಸರ್ಕಾರಿ ಶಾಲೆ"),
    "student_post_matric": T("Student studying after class ten", "छात्र दसवीं के बाद पढ़ रहा है", "విద్యార్థి పదో తరగతి తర్వాత చదువుతున్నారు", "ವಿದ್ಯಾರ್ಥಿ ಹತ್ತನೇ ತರಗತಿಯ ನಂತರ ಓದುತ್ತಿದ್ದಾರೆ"),
    "student_is_sc": T("Student is Scheduled Caste", "छात्र अनुसूचित जाति का है", "విద్యార్థి ఎస్సీ", "ವಿದ್ಯಾರ್ಥಿ ಪರಿಶಿಷ್ಟ ಜಾತಿ"),
    "student_is_st": T("Student is Scheduled Tribe", "छात्र अनुसूचित जनजाति का है", "విద్యార్థి ఎస్టీ", "ವಿದ್ಯಾರ್ಥಿ ಪರಿಶಿಷ್ಟ ಪಂಗಡ"),
    "marks_percent": T("Class seven marks (percent)", "सातवीं के अंक (प्रतिशत)", "ఏడో తరగతి మార్కులు (శాతం)", "ಏಳನೇ ತರಗತಿ ಅಂಕ (ಶೇಕಡಾ)"),
}

MESSAGES = {
    "reprompt_income": T(
        "Sorry, I didn't catch the income. Please say it like two lakh, or ten thousand a month.",
        "माफ़ कीजिए, मैं आय समझ नहीं पाया। कृपया ऐसे बताइए, दो लाख, या दस हज़ार रुपये महीना।",
        "క్షమించండి, ఆదాయం అర్థం కాలేదు. దయచేసి రెండు లక్షలు, లేదా నెలకు పది వేలు అని చెప్పండి.",
        "ಕ್ಷಮಿಸಿ, ಆದಾಯ ಅರ್ಥವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಎರಡು ಲಕ್ಷ, ಅಥವಾ ತಿಂಗಳಿಗೆ ಹತ್ತು ಸಾವಿರ ಎಂದು ಹೇಳಿ."),
    "reprompt_marks": T(
        "Sorry, I didn't catch the marks. Please say a percentage, for example sixty.",
        "माफ़ कीजिए, मैं अंक समझ नहीं पाया। कृपया प्रतिशत बताइए, जैसे साठ।",
        "క్షమించండి, మార్కులు అర్థం కాలేదు. దయచేసి శాతం చెప్పండి, ఉదాహరణకు అరవై.",
        "ಕ್ಷಮಿಸಿ, ಅಂಕ ಅರ್ಥವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಶೇಕಡಾವಾರು ಹೇಳಿ, ಉದಾಹರಣೆಗೆ ಅರವತ್ತು."),
}

UI = {
    "topics": T("What do you want to check?", "आप क्या जाँचना चाहते हैं?", "మీరు ఏమి తనిఖీ చేయాలనుకుంటున్నారు?", "ನೀವು ಏನನ್ನು ಪರಿಶೀಲಿಸಲು ಬಯಸುತ್ತೀರಿ?"),
    "note": T("Good to know", "जानना ज़रूरी", "తెలుసుకోవాల్సినవి", "ತಿಳಿದಿರಬೇಕಾದದ್ದು"),
    "topic_farm": T("Farmers' income support", "किसानों को आय सहायता", "రైతులకు ఆదాయ సహాయం", "ರೈತರಿಗೆ ಆದಾಯ ಸಹಾಯ"),
    "topic_pension": T("Pension and insurance", "पेंशन और बीमा", "పెన్షన్ మరియు బీమా", "ಪಿಂಚಣಿ ಮತ್ತು ವಿಮೆ"),
    "topic_housing": T("Housing", "आवास", "ఇళ్లు", "ವಸತಿ"),
    "topic_health": T("Health cover", "स्वास्थ्य बीमा", "ఆరోగ్య బీమా", "ಆರೋಗ್ಯ ವಿಮೆ"),
    "topic_scholarship": T("Scholarships", "छात्रवृत्ति", "ఉపకార వేతనాలు", "ವಿದ್ಯಾರ್ಥಿವೇತನ"),
}


def merge(tables: dict) -> None:
    for slot, text in QUESTIONS.items():
        tables["QUESTIONS"].setdefault(slot, {}).update(text)
    for slot, text in SLOT_LABELS.items():
        tables["SLOT_LABELS"].setdefault(slot, {}).update(text)
    for k, text in MESSAGES.items():
        tables["MESSAGES"].setdefault(k, {}).update(text)
    for k, text in UI.items():
        tables["UI"].setdefault(k, {}).update(text)
