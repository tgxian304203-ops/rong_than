"""
upload.py - Upload ảnh + file tài liệu Rồng Thần.

Nhiệm vụ:
    - upload_anh(files): nhận file ảnh, lưu vào GridFS kho 1,
      trích xuất nội dung (dùng Gemini Vision nếu có key).
    - upload_file(files): nhận file tài liệu, lưu GridFS kho 1,
      trích xuất nội dung (PDF, DOCX, XLSX, TXT).

Quy tắc:
    - File thật lưu GridFS kho 1 (collection fs.files, fs.chunks).
    - Metadata lưu collection anh_file.
    - Nội dung trích xuất lưu collection noi_dung_da_trich_xuat.
    - Lịch sử gửi lưu collection lich_su_gui.
    - Khách (chưa đăng nhập) cũng upload được, chu_so_huu = "khach".
    - User đã đăng nhập: chu_so_huu = tên tài khoản.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import io
import os
import time
import secrets

from flask import session as phien_flask


# ----------------------------------------------------------------
# IMPORT TẦNG DỮ LIỆU
# ----------------------------------------------------------------
from dai_nao.ghi_nho import (
    luu_file_gridfs,
    luu_metadata_anh_file,
    luu_noi_dung_trich_xuat,
    luu_lich_su_gui,
)


# ----------------------------------------------------------------
# GHI LOG
# ----------------------------------------------------------------
def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


# ----------------------------------------------------------------
# TIỆN ÍCH
# ----------------------------------------------------------------
def _lay_chu_so_huu():
    """Trả về tên tài khoản đang đăng nhập, hoặc 'khach' nếu chưa đăng nhập."""
    ten_tk = phien_flask.get("ten_dang_nhap")
    if ten_tk:
        return ten_tk
    return "khach"


def _tao_id():
    return "file-" + secrets.token_hex(8)


def _lay_duoi_file(ten_file):
    """Lấy phần mở rộng của file, viết thường, không có dấu chấm."""
    if not ten_file or "." not in ten_file:
        return ""
    return ten_file.rsplit(".", 1)[-1].lower()


# ----------------------------------------------------------------
# TRÍCH XUẤT NỘI DUNG
# ----------------------------------------------------------------
def _trich_xuat_txt(noi_dung_bytes):
    """Trích xuất file text đơn giản."""
    try:
        return noi_dung_bytes.decode("utf-8", errors="replace")
    except Exception:
        return ""


def _trich_xuat_pdf(noi_dung_bytes):
    """Trích xuất nội dung PDF bằng PyPDF2."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(noi_dung_bytes))
        ket_qua = []
        for trang in reader.pages[:50]:  # tối đa 50 trang
            ket_qua.append(trang.extract_text() or "")
        return "\n".join(ket_qua).strip()
    except ImportError:
        return ""
    except Exception:
        return ""


def _trich_xuat_docx(noi_dung_bytes):
    """Trích xuất nội dung DOCX bằng python-docx."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(noi_dung_bytes))
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except ImportError:
        return ""
    except Exception:
        return ""


def _trich_xuat_xlsx(noi_dung_bytes):
    """Trích xuất nội dung XLSX bằng openpyxl."""
    try:
        from openpyxl import load_workbook
        wb = load_workbook(io.BytesIO(noi_dung_bytes), read_only=True, data_only=True)
        ket_qua = []
        for sheet in wb.worksheets:
            ket_qua.append(f"[Sheet: {sheet.title}]")
            for hang in sheet.iter_rows(values_only=True):
                ket_qua.append("\t".join("" if c is None else str(c) for c in hang))
        return "\n".join(ket_qua).strip()
    except ImportError:
        return ""
    except Exception:
        return ""


def _trich_xuat_anh_gemini(noi_dung_bytes, duoi_file):
    """
    Trích xuất nội dung ảnh bằng Gemini Vision (nếu có Gemini key đã lưu).
    Nếu không có key → trả về "".
    """
    try:
        import base64
        import requests
        from dai_nao.ghi_nho import lay_danh_sach_key_cua

        chu_so_huu = _lay_chu_so_huu()

        # Tìm key Gemini đầu tiên
        danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []
        gemini_key = None
        for k in danh_sach:
            if k.get("provider") == "Gemini":
                gemini_key = k.get("key")
                break

        if not gemini_key:
            return ""

        # Gọi Gemini Vision
        duoi = duoi_file or "png"
        mime = "image/" + ("jpeg" if duoi == "jpg" else duoi)
        du_lieu_base64 = base64.b64encode(noi_dung_bytes).decode("utf-8")

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.0-flash:generateContent?key={gemini_key}"
        )
        body = {
            "contents": [{
                "parts": [
                    {"text": "Đọc và trích xuất toàn bộ nội dung trong ảnh này. "
                             "Nếu là code, giữ nguyên định dạng. Nếu là văn bản, "
                             "ghi lại đầy đủ. Chỉ trả về nội dung, không giải thích."},
                    {"inline_data": {"mime_type": mime, "data": du_lieu_base64}},
                ]
            }]
        }

        r = requests.post(url, json=body, timeout=30)
        if r.status_code != 200:
            return ""

        du_lieu = r.json()
        try:
            return du_lieu["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError):
            return ""
    except Exception:
        return ""


def _trich_xuat_noi_dung(noi_dung_bytes, duoi_file):
    """
    Điều phối trích xuất theo loại file.
    Trả về chuỗi nội dung đã trích xuất (rỗng nếu không trích được).
    """
    if duoi_file == "txt":
        return _trich_xuat_txt(noi_dung_bytes)
    if duoi_file == "pdf":
        return _trich_xuat_pdf(noi_dung_bytes)
    if duoi_file in ("doc", "docx"):
        return _trich_xuat_docx(noi_dung_bytes)
    if duoi_file in ("xls", "xlsx", "csv"):
        return _trich_xuat_xlsx(noi_dung_bytes)
    if duoi_file in ("png", "jpg", "jpeg", "webp", "bmp", "gif"):
        return _trich_xuat_anh_gemini(noi_dung_bytes, duoi_file)
    return ""


# ----------------------------------------------------------------
# UPLOAD 1 FILE
# ----------------------------------------------------------------
def _xu_ly_mot_file(file_storage, loai_file):
    """
    Xử lý 1 file: đọc nội dung, lưu GridFS, lưu metadata, trích xuất.
    loai_file: "anh" hoặc "tai_lieu"
    Trả về: { thanh_cong, url?, id?, loi? }
    """
    chu_so_huu = _lay_chu_so_huu()

    ten_file = file_storage.filename or "khong_ten"
    duoi_file = _lay_duoi_file(ten_file)

    # Đọc nội dung file vào bộ nhớ
    try:
        file_storage.seek(0)
        noi_dung_bytes = file_storage.read()
    except Exception as e:
        return {"thanh_cong": False, "loi": f"Không đọc được file: {e}"}

    if not noi_dung_bytes:
        return {"thanh_cong": False, "loi": "File rỗng."}

    # Giới hạn kích thước: 20MB
    if len(noi_dung_bytes) > 20 * 1024 * 1024:
        return {"thanh_cong": False, "loi": "File quá lớn (tối đa 20MB)."}

    id_file = _tao_id()
    thoi_gian = int(time.time())

    # Lưu file thật vào GridFS kho 1
    try:
        id_gridfs = luu_file_gridfs(
            ten_file=ten_file,
            noi_dung=noi_dung_bytes,
            metadata={
                "id_file": id_file,
                "chu_so_huu": chu_so_huu,
                "loai_file": loai_file,
                "duoi_file": duoi_file,
                "thoi_gian": thoi_gian,
            },
        )
    except Exception as e:
        return {"thanh_cong": False, "loi": f"Không lưu được file: {e}"}

    # URL để client tải lại
    url = f"/api/file/{id_file}"

    # Lưu metadata vào collection anh_file
    metadata = {
        "id_file": id_file,
        "id_gridfs": str(id_gridfs),
        "ten_file": ten_file,
        "duoi_file": duoi_file,
        "kich_thuoc": len(noi_dung_bytes),
        "loai_file": loai_file,
        "chu_so_huu": chu_so_huu,
        "url": url,
        "thoi_gian": thoi_gian,
    }
    luu_metadata_anh_file(metadata)

    # Trích xuất nội dung
    noi_dung_trich_xuat = _trich_xuat_noi_dung(noi_dung_bytes, duoi_file)
    if noi_dung_trich_xuat:
        luu_noi_dung_trich_xuat({
            "id_file": id_file,
            "chu_so_huu": chu_so_huu,
            "noi_dung": noi_dung_trich_xuat,
            "thoi_gian": thoi_gian,
        })

    # Lưu lịch sử gửi
    luu_lich_su_gui({
        "id_file": id_file,
        "chu_so_huu": chu_so_huu,
        "ten_file": ten_file,
        "loai_file": loai_file,
        "thoi_gian": thoi_gian,
    })

    _ghi_log(
        loai_file,
        f"Upload {loai_file}: {ten_file} ({len(noi_dung_bytes)} bytes)"
    )

    return {
        "thanh_cong": True,
        "id": id_file,
        "url": url,
        "ten_file": ten_file,
        "co_noi_dung": bool(noi_dung_trich_xuat),
    }


# ----------------------------------------------------------------
# HÀM CHÍNH: UPLOAD ẢNH
# ----------------------------------------------------------------
def upload_anh(files):
    """
    Upload nhiều ảnh.
    files: request.files.
    Trả về: { thanh_cong, urls: [..], chi_tiet: [..], loi? }
    """
    danh_sach_file = files.getlist("anh") if hasattr(files, "getlist") else []
    if not danh_sach_file:
        return {"thanh_cong": False, "loi": "Không có ảnh nào được gửi."}

    urls = []
    chi_tiet = []
    for f in danh_sach_file:
        ket_qua = _xu_ly_mot_file(f, "anh")
        if ket_qua.get("thanh_cong"):
            urls.append(ket_qua["url"])
        chi_tiet.append(ket_qua)

    return {
        "thanh_cong": len(urls) > 0,
        "urls": urls,
        "chi_tiet": chi_tiet,
    }


# ----------------------------------------------------------------
# HÀM CHÍNH: UPLOAD FILE TÀI LIỆU
# ----------------------------------------------------------------
def upload_file(files):
    """
    Upload nhiều file tài liệu.
    files: request.files.
    Trả về: { thanh_cong, urls: [..], chi_tiet: [..], loi? }
    """
    danh_sach_file = files.getlist("file") if hasattr(files, "getlist") else []
    if not danh_sach_file:
        return {"thanh_cong": False, "loi": "Không có file nào được gửi."}

    urls = []
    chi_tiet = []
    for f in danh_sach_file:
        ket_qua = _xu_ly_mot_file(f, "tai_lieu")
        if ket_qua.get("thanh_cong"):
            urls.append(ket_qua["url"])
        chi_tiet.append(ket_qua)

    return {
        "thanh_cong": len(urls) > 0,
        "urls": urls,
        "chi_tiet": chi_tiet,
    }