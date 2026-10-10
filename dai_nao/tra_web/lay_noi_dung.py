"""
lay_noi_dung.py - Lấy nội dung trang web Tra web Rồng Thần.
"""

import re
import time


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


TIMEOUT = 10
DO_DAI_TOI_DA = 5000
DO_DAI_TOI_THIEU = 100
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def lay_noi_dung(url):
    if not url or not isinstance(url, str):
        return ""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        import requests
        r = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
            allow_redirects=True,
        )

        if r.status_code != 200:
            _ghi_log("tra-web", f"URL trả {r.status_code}: {url[:80]}")
            return ""

        if r.encoding and r.encoding.lower() in ("iso-8859-1", "latin-1"):
            r.encoding = r.apparent_encoding or "utf-8"

        html = r.text
        return _trich_text_tu_html(html)

    except ImportError:
        _ghi_log("loi", "Chưa cài requests.")
        return ""
    except Exception as e:
        _ghi_log("loi", f"Lấy nội dung lỗi: {e}")
        return ""


def lay_noi_dung_nhieu(urls, so_toi_da=3):
    ket_qua = {}

    if not urls or not isinstance(urls, list):
        return ket_qua

    for url in urls[:so_toi_da]:
        if not url:
            continue
        noi_dung = lay_noi_dung(url)
        if noi_dung:
            ket_qua[url] = noi_dung

    return ket_qua


def _trich_text_tu_html(html):
    if not html:
        return ""

    html = _loai_bo_the_khong_can(html)
    html = re.sub(r"<!--[\s\S]*?-->", "", html)
    html = re.sub(r"<(br|p|div|h[1-6]|li|tr)[^>]*>", "\n", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    html = _giai_ma_entities(html)
    html = re.sub(r"[ \t]+", " ", html)
    html = re.sub(r"\n\s*\n+", "\n\n", html)
    html = html.strip()
    html = _gioi_han_do_dai(html, DO_DAI_TOI_DA)

    if len(html) < DO_DAI_TOI_THIEU:
        return ""

    return html


def _loai_bo_the_khong_can(html):
    the_can_bo = [
        "script", "style", "nav", "footer", "header",
        "aside", "form", "iframe", "noscript", "svg",
        "button", "input", "select", "textarea",
    ]

    for the in the_can_bo:
        mau = rf"<{the}\b[^>]*>[\s\S]*?</{the}>"
        html = re.sub(mau, " ", html, flags=re.I)
        mau_tu_dong = rf"<{the}\b[^>]*/>"
        html = re.sub(mau_tu_dong, " ", html, flags=re.I)

    return html


def _giai_ma_entities(text):
    if not text:
        return ""

    bang = {
        "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"',
        "&#39;": "'", "&apos;": "'", "&nbsp;": " ",
        "&hellip;": "...", "&mdash;": "—", "&ndash;": "–",
        "&laquo;": "«", "&raquo;": "»", "&copy;": "©",
        "&reg;": "®", "&trade;": "™", "&deg;": "°",
        "&plusmn;": "±", "&times;": "×", "&divide;": "÷",
        "&frac12;": "½", "&frac14;": "¼", "&frac34;": "¾",
        "&sup2;": "²", "&sup3;": "³", "&euro;": "€",
        "&pound;": "£", "&yen;": "¥", "&cent;": "¢",
    }

    for k, v in bang.items():
        text = text.replace(k, v)

    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    text = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), text)

    return text


def _gioi_han_do_dai(text, toi_da):
    if not text:
        return ""

    if len(text) <= toi_da:
        return text

    cat = text[:toi_da]
    vi_tri_cuoi = max(
        cat.rfind(". "),
        cat.rfind("! "),
        cat.rfind("? "),
        cat.rfind("\n"),
    )

    if vi_tri_cuoi > toi_da * 0.7:
        cat = cat[:vi_tri_cuoi + 1]

    return cat.strip() + "..."


def dem_tu(text):
    if not text:
        return 0
    return len(re.findall(r"\b\w+\b", text))


def tom_tat_text(text, so_ky_tu=200):
    if not text:
        return ""

    if len(text) <= so_ky_tu:
        return text

    return text[:so_ky_tu].strip() + "..."


def url_hop_le(url):
    if not url or not isinstance(url, str):
        return False

    mau = r"^https?://[\w\-._~:/?#\[\]@!$&'()*+,;=%]+$"
    return bool(re.match(mau, url))


def lay_nhanh(url, so_ky_tu=1000):
    noi_dung = lay_noi_dung(url)
    if not noi_dung:
        return ""
    return tom_tat_text(noi_dung, so_ky_tu)


def lay_tieu_de(url):
    if not url:
        return ""

    try:
        import requests
        r = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            return ""

        khop = re.search(r"<title[^>]*>([\s\S]*?)</title>", r.text, re.I)
        if khop:
            return _giai_ma_entities(khop.group(1).strip())

        return ""
    except Exception:
        return ""