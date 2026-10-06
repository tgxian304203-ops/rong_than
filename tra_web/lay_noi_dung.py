"""
lay_noi_dung.py - Lấy nội dung trang web Tra web Rồng Thần.

Nhiệm vụ:
    - lay_noi_dung(url): lấy nội dung chính từ 1 URL.
    - lay_noi_dung_nhieu(urls, so_toi_da): lấy từ nhiều URL.
    - _trich_text_tu_html(html): trích text từ HTML.
    - _loai_bo_the_khong_can(html): bỏ script, style, nav, footer.
    - _gioi_han_do_dai(text, toi_da): giới hạn độ dài.

Quy tắc:
    - Lấy nội dung chính, bỏ quảng cáo, menu, footer.
    - Giới hạn độ dài để không quá tải Đại não.
    - Timeout 10s.
    - Không lưu kết quả.

Trả về:
    - chuỗi nội dung đã làm sạch.

Tầng dữ liệu: Không.
"""

import re
import time


# ================================================================
# GHI LOG
# ================================================================
def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


# ================================================================
# HẰNG SỐ
# ================================================================
TIMEOUT = 10
DO_DAI_TOI_DA = 5000       # ký tự tối đa trả về
DO_DAI_TOI_THIEU = 100     # nếu ngắn hơn → coi như không lấy được
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


# ================================================================
# LẤY NỘI DUNG TỪ URL
# ================================================================
def lay_noi_dung(url):
    """
    Lấy nội dung chính từ 1 URL.

    url: địa chỉ trang web.

    Trả về: chuỗi nội dung đã làm sạch, hoặc "" nếu thất bại.
    """
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

        # Đoán encoding
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


# ================================================================
# LẤY NHIỀU URL
# ================================================================
def lay_noi_dung_nhieu(urls, so_toi_da=3):
    """
    Lấy nội dung từ nhiều URL.

    urls: list URL.
    so_toi_da: số URL tối đa lấy.

    Trả về: dict { url: noi_dung }.
    """
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


# ================================================================
# TRÍCH TEXT TỪ HTML
# ================================================================
def _trich_text_tu_html(html):
    """
    Trích text từ HTML:
        1. Bỏ thẻ script, style, nav, footer, header, aside.
        2. Bỏ toàn bộ thẻ HTML.
        3. Chuẩn hóa khoảng trắng.
        4. Giới hạn độ dài.
    """
    if not html:
        return ""

    # 1. Bỏ các thẻ không cần
    html = _loai_bo_the_khong_can(html)

    # 2. Bỏ comment HTML
    html = re.sub(r"<!--[\s\S]*?-->", "", html)

    # 3. Bỏ toàn bộ thẻ HTML (nhưng giữ khoảng trắng giữa block)
    html = re.sub(r"<(br|p|div|h[1-6]|li|tr)[^>]*>", "\n", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)

    # 4. Giải mã HTML entities
    html = _giai_ma_entities(html)

    # 5. Chuẩn hóa khoảng trắng
    html = re.sub(r"[ \t]+", " ", html)
    html = re.sub(r"\n\s*\n+", "\n\n", html)
    html = html.strip()

    # 6. Giới hạn độ dài
    html = _gioi_han_do_dai(html, DO_DAI_TOI_DA)

    # 7. Nếu quá ngắn → coi như không lấy được
    if len(html) < DO_DAI_TOI_THIEU:
        return ""

    return html


# ================================================================
# LOẠI BỎ THẺ KHÔNG CẦN
# ================================================================
def _loai_bo_the_khong_can(html):
    """Bỏ các thẻ script, style, nav, footer, header, aside, form, iframe."""
    the_can_bo = [
        "script", "style", "nav", "footer", "header",
        "aside", "form", "iframe", "noscript", "svg",
        "button", "input", "select", "textarea",
    ]

    for the in the_can_bo:
        # Bỏ <the ...>...</the>
        mau = rf"<{the}\b[^>]*>[\s\S]*?</{the}>"
        html = re.sub(mau, " ", html, flags=re.I)

        # Bỏ <the .../> tự đóng
        mau_tu_dong = rf"<{the}\b[^>]*/>"
        html = re.sub(mau_tu_dong, " ", html, flags=re.I)

    return html


# ================================================================
# GIẢI MÃ HTML ENTITIES
# ================================================================
def _giai_ma_entities(text):
    """Giải mã các entities HTML phổ biến."""
    if not text:
        return ""

    bang = {
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&#39;": "'",
        "&apos;": "'",
        "&nbsp;": " ",
        "&hellip;": "...",
        "&mdash;": "—",
        "&ndash;": "–",
        "&laquo;": "«",
        "&raquo;": "»",
        "&copy;": "©",
        "&reg;": "®",
        "&trade;": "™",
        "&deg;": "°",
        "&plusmn;": "±",
        "&times;": "×",
        "&divide;": "÷",
        "&frac12;": "½",
        "&frac14;": "¼",
        "&frac34;": "¾",
        "&sup2;": "²",
        "&sup3;": "³",
        "&euro;": "€",
        "&pound;": "£",
        "&yen;": "¥",
        "&cent;": "¢",
    }

    for k, v in bang.items():
        text = text.replace(k, v)

    # Entities dạng &#123;
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    # Entities dạng &#x1F600;
    text = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), text)

    return text


# ================================================================
# GIỚI HẠN ĐỘ DÀI
# ================================================================
def _gioi_han_do_dai(text, toi_da):
    """Giới hạn độ dài text, cắt ở ranh giới câu."""
    if not text:
        return ""

    if len(text) <= toi_da:
        return text

    # Cắt ở ranh giới câu gần nhất
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


# ================================================================
# HÀM PHỤ: TRÍCH ĐOẠN CHÍNH
# ================================================================
def _trich_doan_chinh(html):
    """
    Cố gắng trích đoạn chính (article, main, content).
    Nếu không có → trả toàn bộ.
    """
    if not html:
        return html

    # Thử tìm <article>, <main>, class chứa "content"/"article"/"post"
    mau_chinh = [
        r"<article\b[^>]*>([\s\S]*?)</article>",
        r"<main\b[^>]*>([\s\S]*?)</main>",
        r'<div[^>]*class="[^"]*(?:content|article|post|entry)[^"]*"[^>]*>([\s\S]*?)</div>',
    ]

    for mau in mau_chinh:
        khop = re.search(mau, html, re.I)
        if khop:
            doan = khop.group(1)
            if len(doan) > 200:
                return doan

    return html


# ================================================================
# HÀM PHỤ: ĐẾM TỪ
# ================================================================
def dem_tu(text):
    """Đếm số từ trong text."""
    if not text:
        return 0
    return len(re.findall(r"\b\w+\b", text))


# ================================================================
# HÀM PHỤ: TÓM TẮT TEXT
# ================================================================
def tom_tat_text(text, so_ky_tu=200):
    """Tạo tóm tắt ngắn từ text."""
    if not text:
        return ""

    if len(text) <= so_ky_tu:
        return text

    return text[:so_ky_tu].strip() + "..."


# ================================================================
# HÀM PHỤ: KIỂM TRA URL HỢP LỆ
# ================================================================
def url_hop_le(url):
    """Kiểm tra URL có hợp lệ không."""
    if not url or not isinstance(url, str):
        return False

    mau = r"^https?://[\w\-._~:/?#\[\]@!$&'()*+,;=%]+$"
    return bool(re.match(mau, url))


# ================================================================
# HÀM PHỤ: LẤY NHANH 1 URL (chỉ trả text)
# ================================================================
def lay_nhanh(url, so_ky_tu=1000):
    """Lấy nhanh nội dung, chỉ trả N ký tự đầu."""
    noi_dung = lay_noi_dung(url)
    if not noi_dung:
        return ""
    return tom_tat_text(noi_dung, so_ky_tu)


# ================================================================
# HÀM PHỤ: LẤY TIÊU ĐỀ TRANG
# ================================================================
def lay_tieu_de(url):
    """Lấy tiêu đề trang từ URL."""
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