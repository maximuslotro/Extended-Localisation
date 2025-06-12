import logging
import os
import json
import re
from pathlib import Path
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page


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
    "zh_cn": "Chinese Simplified (Chinese Mainland) (简体中文（中国大陆)) (zh_cn)",
    #"zh_hk": "Chinese Traditional (Hong Kong SAR) (繁體中文（香港特別行政區)) (zh_hk)",
    "zh_tw": "Chinese Traditional (Taiwan) (繁體中文（台灣)) (zh_tw)",
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

def get_localization_progress(folder_path, title):
    folder = (PROJECT_ROOT / folder_path).resolve()
    base_file = folder / f"{BASE_LANG}.json"
    base = load_locale_file(base_file)

    if not base:
        log.error(f"Base language file missing or empty at {base_file}")
        return None

    base_keys = set(base.keys())
    files = list(folder.glob("*.json"))
    log.info(f"Processing folder: {folder_path}, found {len(files)} JSON files")

    section_data = {
        "section": title,
        "total_strings": len(base_keys),
        "languages": []
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

def build_section_html(section_data):
    if not section_data:
        return "<p><strong>⚠ Base language file missing.</strong></p>"

    translated_langs = [lang for lang in section_data["languages"] if lang["percent"] > 0]
    avg_percent = int(sum(lang["percent"] for lang in translated_langs) / len(translated_langs)) if translated_langs else 0

    html = [
        f'<details class="section-summary">',
        f'<summary>',
        f'<div style="display: flex; justify-content: space-between; align-items: center;">',
        f'<strong>{section_data["section"]} — {len(translated_langs)} languages</strong>',
        f'<span>{avg_percent}% <progress value="{avg_percent}" max="100" style="width: 100px;"></progress></span>',
        f'</div>',
        f'</summary>'
    ]
    for entry in sorted(translated_langs, key=lambda x: (-x["percent"], x["lang"])):
        lang = entry["lang"]
        display_name = LANG_DISPLAY_NAMES.get(lang.lower(), f"Localized ({lang.upper()})")

        html.append(f'<details class="lang-summary"><summary><div style="display: flex; justify-content: space-between;"><span>{display_name}</span><span>{entry["percent"]}% <progress value="{entry["percent"]}" max="100"></progress></span></div></summary>')

        if entry["missing"]:
            html.append("<details><summary>Missing strings</summary><ul>")
            for key in entry["missing"]:
                html.append(f"<li><code>{key}</code></li>")
            html.append("</ul></details>")

        if entry["extra"]:
            html.append("<details><summary>Strings to remove</summary><ul>")
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
        folder_path = entries.get('folder_path', 'locales')

        section_data = get_localization_progress(folder_path, sub_title)

        html = [f'<div class="infobox"><div class="infobox-header"><h2>{title}</h2></div>']
        html.append(build_section_html(section_data))
        html.append('</div>')

        return '\n'.join(html)

    return INFOBOX_RE.sub(render_infobox, markdown)