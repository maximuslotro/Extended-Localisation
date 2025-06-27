import logging
import os
import json
import re
from pathlib import Path
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from collections import defaultdict

INFOBOX_RE = re.compile(r'::infobox\n(.*?)\n::end-infobox', re.DOTALL)
BASE_LANG = "en_us"
PLUGIN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PLUGIN_ROOT.parent.parent.parent  # Assuming plugin is in `Extended-Localization/website/docs/plugins`

# There are 10 languages removed in 1.17 that are not on this list. (https://minecraft.wiki/w/Language#Removed_languages)
LANG_DISPLAY_NAMES = {
    "af_za": "Afrikaans (Afrikaans (Suid-Afrika)) (af_za)",
    "ar_sa": "Arabic (العالم العربي) (ar_sa)",
    "ast_es": "Asturian (Asturianu (Asturies)) (ast_es)",
    "az_az": "Azerbaijani (Azərbaycanca (Azərbaycan)) (az_az)",
    "ba_ru": "Bashkir (Башҡортса (Башҡортостан, Рәсәй)) (ba_ru)",
    "bar": "Bavarian (Boarisch (Bayern)) (bar)",
    "be_by": "Belarusian (Cyrillic) (Беларуская (Беларусь)) (be_by)",
    "be_latn": "Belarusian (Latin) (Biełaruskaja (Biełaruś)) (be_latn)",
    "bg_bg": "Bulgarian (Български (България)) (bg_bg)",
    "br_fr": "Breton (Brezhoneg (Breizh)) (br_fr)",
    "brb": "Brabantian (Braobans (Braobant)) (brb)",
    "bs_ba": "Bosnian (Bosanski (Bosna i Hercegovina)) (bs_ba)",
    "ca_es": "Catalan (Català (Catalunya)) (ca_es)",
    "cs_cz": "Czech (Čeština (Česko)) (cs_cz)",
    "cy_gb": "Welsh (Cymraeg (Cymru)) (cy_gb)",
    "da_dk": "Danish (Dansk (Danmark)) (da_dk)",
    "de_at": "Austrian German (Deitsch (Österreich)) (de_at)",
    "de_ch": "Swiss German (Schwiizerdutsch (Schwiiz)) (de_ch)",
    "de_de": "German (Deutsch (Deutschland)) (de_de)",
    "el_gr": "Greek (Ελληνικά (Ελλάδα)) (el_gr)",
    "en_au": "Australian English (English (Australia)) (en_au)",
    "en_ca": "Canadian English (English (Canada)) (en_ca)",
    "en_gb": "British English (English (United Kingdom)) (en_gb)",
    "en_nz": "New Zealand English (English (New Zealand)) (en_nz)",
    "en_pt": "Pirate English (Pirate Speak (The Seven Seas)) (en_pt)",
    "en_ud": "Upside Down British English (ɥsᴉꞁᵷuƎ (uʍoᗡ ǝpᴉsd∩)) (en_ud)",
    "en_us": "American English (English (US)) (en_us)",
    "enp": "Modern English minus borrowed words (Anglish (Oned Riches)) (enp)",
    "enws": "Early Modern English (Shakespearean English (Kingdom of England)) (enws)",
    "eo_uy": "Esperanto (Esperanto (Esperantujo)) (eo_uy)",
    "es_ar": "Argentinian Spanish (Español (Argentina)) (es_ar)",
    "es_cl": "Chilean Spanish (Español (Chile)) (es_cl)",
    "es_ec": "Ecuadorian Spanish (Español (Ecuador)) (es_ec)",
    "es_es": "Spanish (Español (España)) (es_es)",
    "es_mx": "Mexican Spanish (Español (México)) (es_mx)",
    "es_uy": "Uruguayan Spanish (Español (Uruguay)) (es_uy)",
    "es_ve": "Venezuelan Spanish (Español (Venezuela)) (es_ve)",
    "esan": "Andalusian (Andalûh (Andaluçía)) (esan)",
    "et_ee": "Estonian (Eesti (Eesti)) (et_ee)",
    "eu_es": "Basque (Euskara (Euskal Herria)) (eu_es)",
    "fa_ir": "Persian (فارسی (ایران)) (fa_ir)",
    "fi_fi": "Finnish (Suomi (Suomi)) (fi_fi)",
    "fil_ph": "Filipino (Filipino (Pilipinas)) (fil_ph)",
    "fo_fo": "Faroese (Føroyskt (Føroyar)) (fo_fo)",
    "fr_ca": "Canadian French (Français (Canada)) (fr_ca)",
    "fr_fr": "European French (Français (France)) (fr_fr)",
    "fra_de": "East Franconian (Fränggisch (Franggn)) (fra_de)",
    #"fur_it": "Friulian (Furlan (Friûl)) (fur_it)",
    "fy_nl": "Frisian (Frysk (Fryslân)) (fy_nl)",
    "ga_ie": "Irish (Gaeilge (Éire)) (ga_ie)",
    "gd_gb": "Scottish Gaelic (Gàidhlig (Alba)) (gd_gb)",
    "gl_es": "Galician (Galego (Galicia / Galiza)) (gl_es)",
    "haw_us": "Hawaiian (ʻŌlelo Hawaiʻi (Hawaiʻi)) (haw_us)",
    "he_il": "Hebrew (עברית (ישראל)) (he_il)",
    "hi_in": "Hindi (हिंदी (भारत)) (hi_in)",
    #"hn_no": "High Norwegian (Høgnorsk (Norig)) (hn_no)",
    "hr_hr": "Croatian (Hrvatski (Hrvatska)) (hr_hr)",
    "hu_hu": "Hungarian (Magyar (Magyarország)) (hu_hu)",
    "hy_am": "Armenian (Հայերեն (Հայաստան)) (hy_am)",
    "id_id": "Indonesian (Bahasa Indonesia (Indonesia)) (id_id)",
    "ig_ng": "Igbo (Igbo (Naigeria)) (ig_ng)",
    "io_en": "Ido (Ido (Idia)) (io_en)",
    "is_is": "Icelandic (Íslenska (Ísland)) (is_is)",
    "isv": "Interslavic (Medžuslovjansky (Slovjanščina)) (isv)",
    "it_it": "Italian (Italiano (Italia)) (it_it)",
    "ja_jp": "Japanese (日本語 (日本)) (ja_jp)",
    "jbo_en": "Lojban (la .lojban. (la jboguʼe)) (jbo_en)",
    "ka_ge": "Georgian (ქართული (საქართველო)) (ka_ge)",
    "kk_kz": "Kazakh (Қазақша (Қазақстан)) (kk_kz)",
    "kn_in": "Kannada (ಕನ್ನಡ (ಭಾರತ)) (kn_in)",
    "ko_kr": "Korean (한국어 (대한민국)) (ko_kr)",
    "ksh": "Ripuarian (Kölsch/Ripoarisch) (ksh)",
    "kw_gb": "Cornish (Kernewek (Kernow)) (kw_gb)",
    #"ky_kg": "Kyrgyz (Кыргызча (Кыргызстан)) (ky_kg)",
    "la_la": "Latin (Latina (Latium)) (la_la)",
    "lb_lu": "Luxembourgish (Lëtzebuergesch (Lëtzebuerg)) (lb_lu)",
    "li_li": "Limburgish (Limburgs (Limburg)) (li_li)",
    #"lmo": "Lombard (Lombard (Lombardia)) (lmo)",
    "lo_la": "Lao (ລາວ (ປະເທດລາວ)) (lo_la)",
    "lol_us": "LOLCAT (LOLCAT (Kingdom of Cats)) (lol_us)",
    "lt_lt": "Lithuanian (Lietuvių (Lietuva)) (lt_lt)",
    "lv_lv": "Latvian (Latviešu (Latvija)) (lv_lv)",
    "lzh": "Literary Chinese (文言（華夏）) (lzh)",
    "mk_mk": "Macedonian (Македонски (Северна Македонија)) (mk_mk)",
    "mn_mn": "Mongolian (Монгол (Монгол Улс)) (mn_mn)",
    "ms_my": "Malay (Bahasa Melayu (Malaysia)) (ms_my)",
    "mt_mt": "Maltese (Malti (Malta)) (mt_mt)",
    #"nah": "Nahuatl (Mēxikatlahtōlli (Mēxiko)) (nah)",
    "nds_de": "Low German (Plattdüütsh (Düütschland)) (nds_de)",
    "nl_be": "Dutch, Flemish (Vlaams (België)) (nl_be)",
    "nl_nl": "Dutch (Nederlands (Nederland)) (nl_nl)",
    "nn_no": "Norwegian Nynorsk (Norsk nynorsk (Noreg)) (nn_no)",
    "no_no": "Norwegian Bokmål (Norsk bokmål (Norge)) (nob_no)",
    "oc_fr": "Occitan (Occitan (Occitània)) (oc_fr)",
    "ovd": "Elfdalian (Övdalska (Swerre)) (ovd)",
    "pl_pl": "Polish (Polski (Polska)) (pl_pl)",
    "pls": "Popoloca (Ngiiwa (Ndanìngà)) (pls)",
    "pt_br": "Brazilian Portuguese (Português (Brasil)) (pt_br)",
    "pt_pt": "European Portuguese (Português (Portugal)) (pt_pt)",
    "qya_aa": "Quenya (Form of Elvish from LOTR) (Quenya (Arda)) (qya_aa)",
    "ro_ro": "Romanian (Română (România)) (ro_ro)",
    #"rpr": "Russian (Pre-revolutionary) (Русскій дореформенный (Россійская имперія)) (rpr)",
    "ru_ru": "Russian (Русский (Россия)) (ru_ru)",
    #"ry_ua": "Rusyn (Руснацькый (Пудкарпатя, Украина)) (ry_ua)",
    "sah_sah": "Yakut (Сахалыы (Саха Сирэ)) (sah_sah)",
    "se_no": "Northern Sami (Davvisámegiella (Sápmi)) (se_no)",
    "sk_sk": "Slovak (Slovenčina (Slovensko)) (sk_sk)",
    "sl_si": "Slovenian (Slovenščina (Slovenija)) (sl_si)",
    "so_so": "Somali (Af-Soomaali (Soomaaliya)) (so_so)",
    "sq_al": "Albanian (Shqip (Shqiperia)) (sq_al)",
    "sr_cs": "Serbian (Latin) (Srpski (Srbija)) (sr_cs)",
    "sr_sp": "Serbian (Cyrillic) (Српски (Србија)) (sr_sp)",
    "sv_se": "Swedish (Svenska (Sverige)) (sv_se)",
    "sxu": "Upper Saxon German (Säggs’sch (Saggsn)) (sxu)",
    "szl": "Silesian (Ślōnski (Gōrny Ślōnsk)) (szl)",
    "ta_in": "Tamil (தமிழ் (இந்தியா)) (ta_in)",
    "th_th": "Thai (ไทย (ประเทศไทย)) (th_th)",
    "tl_ph": "Tagalog (Tagalog (Pilipinas)) (tl_ph)",
    "tlh_aa": "Klingon (tlhIngan Hol (tlhIngan wo')) (tlh_aa)",
    #"tok": "Toki Pona (toki pona (ma pona)) (tok)",
    "tr_tr": "Turkish (Türkçe (Türkiye)) (tr_tr)",
    "tt_ru": "Tatar (Татарча (Татарстан, Рәсәй)) (tt_ru)",
    "tzo_mx": "Tzotzil (Bats'i k'op (Jobel)) (tzo_mx)",
    "uk_ua": "Ukrainian (Українська (Україна)) (uk_ua)",
    "val_es": "Valencian (Català (Valencià)) (val_es)",
    "vec_it": "Venetian (Vèneto (Veneto)) (vec_it)",
    "vi_vn": "Vietnamese (Tiếng Việt (Việt Nam)) (vi_vn)",
    "vp_vl": "Viossa (Viossa (Vilant)) (vp_vl)",
    "yi_de": "Yiddish (ייִדיש (אשכנזיש יידן)) (yi_de)",
    "yo_ng": "Yoruba (Yorùbá (Nàìjíríà)) (yo_ng)",
    "zh_cn": "Chinese Simplified (Mainland China; Mandarin) (简体中文（中国大陆)) (zh_cn)",
    #"zh_hk": "Chinese Traditional (Hong Kong SAR) (繁體中文（香港特別行政區)) (zh_hk)",
    "zh_tw": "Chinese Traditional (Taiwan; Mandarin) (繁體中文（台灣)) (zh_tw)",
    "zlm_arab": "Malay (Jawi) (بهاس ملايو (مليسيا)) (zlm_arab)"
}

log = logging.getLogger("mkdocs.plugins")

def on_pre_build(config):
    log.info(">>> Localization Status Generator: Present")

def load_locale_file(file_path):
    if not os.path.exists(file_path):
        log.warning(f"Locale file not found: {file_path}")
        return {}
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Error loading {file_path}: {e}")
        return {}

def get_localization_progress(folder_name, title, datatype):
    folder_path = (PROJECT_ROOT / folder_name).resolve()
    if datatype == 'lang':
        return get_localization_progress_lang(folder_path, folder_name, title)
    elif datatype == 'speechbank':
        return get_localization_progress_speechbank(folder_path, folder_name, title)
    elif datatype == 'sign_texts':
        return get_localization_progress_sign_texts(folder_path, folder_name, title)
    elif datatype == 'fast_travel':
        return get_localization_progress_fast_travel(folder_path, folder_name, title)
    else:
        log.error(f"Unknown datatype: {datatype}")
        return None

def get_localization_progress_lang(folder_path, folder_name, title):
    base_file = folder_path / f"{BASE_LANG}.json"
    base = load_locale_file(base_file)

    if not base:
        log.error(f"Base language file missing or empty at {base_file}")
        return None

    base_keys = set(base.keys())
    files = list(folder_path.glob("*.json"))
    log.info(f"Processing folder: {folder_name}, found {len(files)} JSON files")

    section_data = {
        "section": title,
        "total_strings": len(base_keys),
        "languages": [],
        "use_progress" : True
    }

    for file in files:
        lang = file.stem
        if lang == BASE_LANG:
            continue

        localized = load_locale_file(file)
        if not localized:
            continue

        localized_keys = set(localized.keys())
        missing = base_keys - localized_keys
        extra = localized_keys - base_keys
        completed = len(base_keys) - len(missing)

        percent = 100 if not missing else int(100 * completed / len(base_keys))

        section_data["languages"].append({
            "lang": lang,
            "percent": percent,
            "missing": sorted(missing),
            "extra": sorted(extra)
        })

    return section_data

def get_localization_progress_speechbank(folder_path, folder_name, title):
    base_lang = BASE_LANG  # typically 'en_us'
    #speechbank_folders = [f for f in folder.rglob('') if f.is_dir() and any(f.glob(f"{base_lang}.json"))]
    
    all_langs = set()
    lang_file_map = defaultdict(set) # lang -> set of speechbank folder names

    for speechbank_folder in folder_path.rglob(''):
        if not speechbank_folder.is_dir():
            continue

        for file in speechbank_folder.glob("*.json"):
            lang = file.stem.lower()
            relative_path = speechbank_folder.relative_to(folder_path)
            lang_file_map.setdefault(lang, set()).add(str(relative_path))
            all_langs.add(lang)

    if BASE_LANG not in lang_file_map:
        log.error(f"Base language '{BASE_LANG}' not found in {folder_name}")
        return None

    base_set = lang_file_map[BASE_LANG]  # This now contains full relative paths (strings)
    total = len(base_set)
    log.info(f"Processing folder: {folder_name}, found {total} JSON files")
    section_data = {
        "section": title,
        "total_strings": total,
        "languages": [],
        "use_progress" : True
    }

    for lang in sorted(all_langs):
        if lang == base_lang:
            continue
        present = lang_file_map.get(lang, set())
        missing = sorted(base_set - present)
        percent = 100 if not missing else int(100 * (total - len(missing)) / total)
        
        section_data["languages"].append({
            "lang": lang,
            "percent": percent,
            "missing": missing,
            "extra": sorted(present - base_set)
        })

    return section_data

def get_localization_progress_sign_texts(folder_path, folder_name, title):
    base_lang = BASE_LANG  # e.g., "en_us"
    all_files = list(folder_path.glob("*.json"))
    pattern = re.compile(r"^(?P<type>.+?)_(?P<lang>[a-z]{2}_[a-z]{2})\.json$", re.IGNORECASE)

    file_map = {}  # lang -> set of <sign_type>
    all_langs = set()

    for file in all_files:
        match = pattern.match(file.name)
        if not match:
            continue
        sign_type = match.group("type")
        lang = match.group("lang").lower()
        file_map.setdefault(lang, set()).add(sign_type)
        all_langs.add(lang)

    if base_lang not in file_map:
        log.error(f"Base language '{base_lang}' has no sign_text files in {folder_name}")
        return None

    base_types = file_map[base_lang]
    total = len(base_types)
    log.info(f"Processing folder: {folder_name}, found {total} JSON files")

    section_data = {
        "section": title,
        "total_strings": total,
        "languages": [],
        "use_progress" : True
    }

    for lang in sorted(all_langs):
        if lang == base_lang:
            continue

        types_present = file_map.get(lang, set())
        missing_types = sorted(base_types - types_present)
        extra_types = sorted(types_present - base_types)

        missing_files = [f"{t}_{lang}.json" for t in missing_types]
        extra_files = [f"{t}_{lang}.json" for t in extra_types]

        percent = 100 if not missing_files else int(100 * (total - len(missing_files)) / total)

        section_data["languages"].append({
            "lang": lang,
            "percent": percent,
            "missing": missing_files,
            "extra": extra_files
        })

    return section_data

def get_localization_progress_fast_travel(folder_path, folder_name, title):
    files = list(folder_path.glob("*.txt"))
    langs = [f.stem.lower() for f in files if f.is_file()]
    langs = sorted(set(langs))
    log.info(f"Processing folder: {folder_name}, found {len(langs)} TXT files")
    section_data = {
        "section": title,
        "total_strings": len(langs),  # not actually strings, but localized files
        "languages": [],
        "use_progress" : False
    }

    for lang in langs:
        section_data["languages"].append({
            "lang": lang,
            "percent": 100,
            "missing": [],
            "extra": []
        })

    return section_data

def build_section_html(section_data):
    if not section_data:
        return "<p><strong>⚠ Base language file missing.</strong></p>"

    translated_langs = [lang for lang in section_data["languages"] if lang["percent"] > 0]
    avg_percent = int(sum(lang["percent"] for lang in translated_langs) / len(translated_langs)) if translated_langs else 0

    html = [
        f'<details class="section-summary">',
        f'<summary>',
        f'<div style="display: flex; justify-content: space-between; align-items: center;">',
        f'<strong>{section_data["section"]} — {len(translated_langs)} languages present</strong>',
    ]
    if section_data.get("use_progress", True):
        html.append(f'<span>{avg_percent}% <progress value="{avg_percent}" max="100" style="width: 100px;"></progress></span>')
    html.extend([
        f'</div>',
        f'</summary>'
    ])

    for entry in sorted(translated_langs, key=lambda x: (-x["percent"], x["lang"])):
        lang = entry["lang"]
        display_name = LANG_DISPLAY_NAMES.get(lang.lower(), f"Localized ({lang.upper()})")

        if section_data["use_progress"]:
            html.append(f'<details class="lang-summary"><summary><div style="display: flex; justify-content: space-between;"><span>{display_name}</span><span>{entry["percent"]}% <progress value="{entry["percent"]}" max="100"></progress></span></div></summary>')
        else:
            html.append(f'<details class="lang-summary"><summary><div style="display: flex; justify-content: space-between;"><span>{display_name}</span></div></summary>')

        if entry["missing"]:
            html.append("<details><summary>Missing entries</summary><ul>")
            for key in entry["missing"]:
                html.append(f"<li><code>{key}</code></li>")
            html.append("</ul></details>")

        if entry["extra"]:
            html.append("<details><summary>Entries to remove</summary><ul>")
            for key in entry["extra"]:
                html.append(f"<li><code>{key}</code></li>")
            html.append("</ul></details>")

        html.append("</details>")  # Close lang summary

    html.append("</details>")  # Close section summary
    return '\n'.join(html)

def on_page_markdown(markdown, page: Page, config: MkDocsConfig, files):
    def render_infobox(match):
        block = match.group(1).strip()
        lines = block.splitlines()
        entries = {}
        for line in lines:
            if ':' in line:
                key, value = map(str.strip, line.split(':', 1))
                entries[key.lower()] = value

        title = entries.get('title', 'Localizations')
        sub_title = entries.get('sub_title', 'Localizations count')
        folder_name = entries.get('folder_name', 'locales')
        datatype = entries.get('type', 'lang')

        section_data = get_localization_progress(folder_name, sub_title, datatype)

        html = [f'<div class="infobox"><div class="infobox-header"><h4>  - {title}</h4></div>']
        #html = [f'<div class="infobox">']
        html.append(build_section_html(section_data))
        html.append('</div>')

        return '\n'.join(html)

    return INFOBOX_RE.sub(render_infobox, markdown)