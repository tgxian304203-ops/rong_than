"""
routes.py - Định nghĩa toàn bộ route API cho Rồng Thần.
"""

import os
import json
import secrets
from functools import wraps

from flask import jsonify, request, session


THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_DU_LIEU = os.path.join(THU_MUC_GOC, "du_lieu")
FILE_CAU_HINH_KHO = os.path.join(THU_MUC_DU_LIEU, "cau_hinh_kho.json")


def _doc_hoac_tao_secret_key():
    os.makedirs(THU_MUC_DU_LIEU, exist_ok=True)
    du_lieu = {}
    if os.path.exists(FILE_CAU_HINH_KHO):
        try:
            with open(FILE_CAU_HINH_KHO, "r", encoding="utf-8") as f:
                du_lieu = json.load(f)
        except (json.JSONDecodeError, OSError):
            du_lieu = {}

    if "secret_key" not in du_lieu or not du_lieu["secret_key"]:
        du_lieu["secret_key"] = secrets.token_hex(32)
        try:
            with open(FILE_CAU_HINH_KHO, "w", encoding="utf-8") as f:
                json.dump(du_lieu, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    return du_lieu["secret_key"]


def yeu_cau_dang_nhap(f):
    @wraps(f)
    def bao_boc(*args, **kwargs):
        if not session.get("da_dang_nhap"):
            return jsonify({"thanh_cong": False, "loi": "Chưa đăng nhập"}), 401
        return f(*args, **kwargs)
    return bao_boc


def _goi_an_toan(duong_dan_module, ten_ham):
    try:
        module = __import__(duong_dan_module, fromlist=[ten_ham])
        return getattr(module, ten_ham, None)
    except ImportError:
        return None


def _chua_trien_khai(ten_chuc_nang):
    return jsonify({
        "thanh_cong": False,
        "loi": f"Chức năng '{ten_chuc_nang}' chưa được triển khai.",
    }), 501


def dang_ky_routes(app):
    app.secret_key = _doc_hoac_tao_secret_key()

    # ============================================================
    # CHAT CHÍNH
    # ============================================================
    @app.route("/api/gui-tin-nhan", methods=["POST"])
    def api_gui_tin_nhan():
        ham = _goi_an_toan("giao_dien.gui_tin_nhan", "xu_ly_gui_tin_nhan")
        if ham is None:
            return _chua_trien_khai("gửi tin nhắn")
        return jsonify(ham(request.get_json(silent=True) or {}))

    # ============================================================
    # CHAT TRONG DỰ ÁN
    # ============================================================
    @app.route("/api/gui-tin-nhan-du-an", methods=["POST"])
    def api_gui_tin_nhan_du_an():
        du_lieu = request.get_json(silent=True) or {}
        id_du_an = du_lieu.get("id_du_an")
        id_tro_chuyen = du_lieu.get("id_tro_chuyen")
        noi_dung = (du_lieu.get("noi_dung") or "").strip()

        if not id_du_an or not id_tro_chuyen or not noi_dung:
            return jsonify({"thanh_cong": False, "loi": "Thiếu thông tin."})

        ten_tk = session.get("ten_dang_nhap")

        if ten_tk:
            ham_luu = _goi_an_toan("giao_dien.session", "luu_tin_nhan")
            if ham_luu:
                ham_luu({
                    "id_du_an": id_du_an,
                    "id_tro_chuyen": id_tro_chuyen,
                    "vai_tro": "nguoi",
                    "noi_dung": noi_dung,
                })

        ham_xu_ly = _goi_an_toan("dai_nao.nhan_task", "nhan_task")
        if ham_xu_ly is None:
            return _chua_trien_khai("đại não xử lý")

        try:
            ket_qua = ham_xu_ly({"noi_dung": noi_dung})
            tra_loi = ""
            if isinstance(ket_qua, dict):
                tra_loi = ket_qua.get("tra_loi") or ket_qua.get("ket_qua") or ""
            else:
                tra_loi = str(ket_qua)
        except Exception as e:
            tra_loi = f"⚠️ Lỗi xử lý: {e}"

        if ten_tk and tra_loi:
            ham_luu = _goi_an_toan("giao_dien.session", "luu_tin_nhan")
            if ham_luu:
                ham_luu({
                    "id_du_an": id_du_an,
                    "id_tro_chuyen": id_tro_chuyen,
                    "vai_tro": "rong",
                    "noi_dung": tra_loi,
                })

        return jsonify({
            "thanh_cong": True,
            "tra_loi": tra_loi,
        })

    # ============================================================
    # TRÒ CHUYỆN TRONG DỰ ÁN
    # ============================================================
    @app.route("/api/tao-tro-chuyen", methods=["POST"])
    def api_tao_tro_chuyen():
        ham = _goi_an_toan("giao_dien.session", "tao_tro_chuyen")
        if ham is None:
            return _chua_trien_khai("tạo trò chuyện")
        return jsonify(ham(request.get_json(silent=True) or {}))

    @app.route("/api/danh-sach-tro-chuyen", methods=["GET"])
    def api_danh_sach_tro_chuyen():
        ham = _goi_an_toan("giao_dien.session", "lay_danh_sach_tro_chuyen")
        if ham is None:
            return _chua_trien_khai("lấy danh sách trò chuyện")
        return jsonify(ham())

    @app.route("/api/xoa-tro-chuyen", methods=["POST"])
    def api_xoa_tro_chuyen():
        ham = _goi_an_toan("giao_dien.session", "xoa_tro_chuyen")
        if ham is None:
            return _chua_trien_khai("xóa trò chuyện")
        return jsonify(ham(request.get_json(silent=True) or {}))

    @app.route("/api/tin-nhan-tro-chuyen", methods=["GET"])
    def api_tin_nhan_tro_chuyen():
        ham = _goi_an_toan("giao_dien.session", "lay_tin_nhan")
        if ham is None:
            return _chua_trien_khai("lấy tin nhắn trò chuyện")
        return jsonify(ham())

    # ============================================================
    # KEY MODEL
    # ============================================================
    @app.route("/api/luu-key-model", methods=["POST"])
    def api_luu_key_model():
        ham = _goi_an_toan("giao_dien.luu_key", "luu_key_model")
        if ham is None:
            return _chua_trien_khai("lưu key model")
        return jsonify(ham(request.get_json(silent=True) or {}))

    @app.route("/api/danh-sach-key", methods=["GET"])
    def api_danh_sach_key():
        ham = _goi_an_toan("giao_dien.luu_key", "lay_danh_sach_key")
        if ham is None:
            return _chua_trien_khai("lấy danh sách key")
        return jsonify(ham())

    @app.route("/api/xoa-key", methods=["POST"])
    def api_xoa_key():
        ham = _goi_an_toan("giao_dien.luu_key", "xoa_key")
        if ham is None:
            return _chua_trien_khai("xóa key")
        return jsonify(ham(request.get_json(silent=True) or {}))

    @app.route("/api/quota-key", methods=["GET"])
    def api_quota_key():
        ham = _goi_an_toan("giao_dien.luu_key", "lay_quota_key")
        if ham is None:
            return _chua_trien_khai("lấy quota key")
        return jsonify(ham())

    # ============================================================
    # KEY TRA WEB
    # ============================================================
    @app.route("/api/luu-key-web", methods=["POST"])
    def api_luu_key_web():
        ham = _goi_an_toan("giao_dien.luu_key_web", "luu_key_web")
        if ham is None:
            return _chua_trien_khai("lưu key tra web")
        return jsonify(ham(request.get_json(silent=True) or {}))

    @app.route("/api/danh-sach-key-web", methods=["GET"])
    def api_danh_sach_key_web():
        ham = _goi_an_toan("giao_dien.luu_key_web", "lay_danh_sach_key_web")
        if ham is None:
            return _chua_trien_khai("lấy danh sách key tra web")
        return jsonify(ham())

    @app.route("/api/xoa-key-web", methods=["POST"])
    def api_xoa_key_web():
        ham = _goi_an_toan("giao_dien.luu_key_web", "xoa_key_web")
        if ham is None:
            return _chua_trien_khai("xóa key tra web")
        return jsonify(ham(request.get_json(silent=True) or {}))

    @app.route("/api/quota-key-web", methods=["GET"])
    def api_quota_key_web():
        ham = _goi_an_toan("giao_dien.luu_key_web", "lay_quota_key_web")
        if ham is None:
            return _chua_trien_khai("lấy quota key tra web")
        return jsonify(ham())

    # ============================================================
    # URI KHO
    # ============================================================
    @app.route("/api/luu-uri-kho", methods=["POST"])
    def api_luu_uri_kho():
        ham = _goi_an_toan("giao_dien.luu_uri_kho", "luu_uri_kho")
        if ham is None:
            return _chua_trien_khai("lưu URI kho")
        return jsonify(ham(request.get_json(silent=True) or {}))

    @app.route("/api/lay-uri-kho", methods=["GET"])
    def api_lay_uri_kho():
        ham = _goi_an_toan("giao_dien.luu_uri_kho", "lay_uri_kho")
        if ham is None:
            return _chua_trien_khai("lấy URI kho")
        return jsonify(ham())

    # ============================================================
    # LOGS
    # ============================================================
    @app.route("/api/logs", methods=["GET"])
    def api_logs():
        ham = _goi_an_toan("logs.doc_log", "doc_log")
        if ham is None:
            return _chua_trien_khai("đọc log")
        return jsonify(ham())

    @app.route("/api/logs/loc", methods=["GET"])
    def api_logs_loc():
        loai = request.args.get("loai", "tat-ca")
        ham = _goi_an_toan("logs.loc_log", "loc_log")
        if ham is None:
            return _chua_trien_khai("lọc log")
        return jsonify(ham(loai))

    @app.route("/api/logs/xoa", methods=["POST"])
    def api_logs_xoa():
        ham = _goi_an_toan("logs.doc_log", "xoa_log")
        if ham is None:
            return _chua_trien_khai("xóa log")
        return jsonify(ham())

    # ============================================================
    # TÀI KHOẢN
    # ============================================================
    @app.route("/api/dang-ky", methods=["POST"])
    def api_dang_ky():
        ham = _goi_an_toan("giao_dien.xac_thuc", "dang_ky")
        if ham is None:
            return _chua_trien_khai("đăng ký")
        return jsonify(ham(request.get_json(silent=True) or {}))

    @app.route("/api/dang-nhap", methods=["POST"])
    def api_dang_nhap():
        ham = _goi_an_toan("giao_dien.xac_thuc", "dang_nhap")
        if ham is None:
            return _chua_trien_khai("đăng nhập")
        ket_qua = ham(request.get_json(silent=True) or {})
        if ket_qua.get("thanh_cong"):
            session["da_dang_nhap"] = True
            session["ten_dang_nhap"] = ket_qua.get("ten_dang_nhap", "")
        return jsonify(ket_qua)

    @app.route("/api/dang-xuat", methods=["POST"])
    def api_dang_xuat():
        session.clear()
        return jsonify({"thanh_cong": True})

    @app.route("/api/phien", methods=["GET"])
    def api_phien():
        if session.get("da_dang_nhap"):
            return jsonify({
                "thanh_cong": True,
                "da_dang_nhap": True,
                "ten_dang_nhap": session.get("ten_dang_nhap", ""),
            })
        return jsonify({"thanh_cong": True, "da_dang_nhap": False})

    @app.route("/api/doi-mat-khau", methods=["POST"])
    @yeu_cau_dang_nhap
    def api_doi_mat_khau():
        ham = _goi_an_toan("giao_dien.doi_mat_khau", "doi_mat_khau")
        if ham is None:
            return _chua_trien_khai("đổi mật khẩu")
        return jsonify(ham(request.get_json(silent=True) or {}))

    # ============================================================
    # UPLOAD
    # ============================================================
    @app.route("/api/upload-anh", methods=["POST"])
    def api_upload_anh():
        ham = _goi_an_toan("giao_dien.upload", "upload_anh")
        if ham is None:
            return _chua_trien_khai("upload ảnh")
        return jsonify(ham(request.files))

    @app.route("/api/upload-file", methods=["POST"])
    def api_upload_file():
        ham = _goi_an_toan("giao_dien.upload", "upload_file")
        if ham is None:
            return _chua_trien_khai("upload file")
        return jsonify(ham(request.files))

    # ============================================================
    # DỰ ÁN / CHAT NHANH
    # ============================================================
    @app.route("/api/danh-sach-du-an", methods=["GET"])
    def api_danh_sach_du_an():
        ham = _goi_an_toan("giao_dien.session", "lay_danh_sach_du_an")
        if ham is None:
            return _chua_trien_khai("lấy danh sách dự án")
        return jsonify(ham())

    @app.route("/api/tao-du-an", methods=["POST"])
    def api_tao_du_an():
        ham = _goi_an_toan("giao_dien.session", "tao_du_an")
        if ham is None:
            return _chua_trien_khai("tạo dự án")
        return jsonify(ham(request.get_json(silent=True) or {}))

    @app.route("/api/xoa-du-an", methods=["POST"])
    def api_xoa_du_an():
        ham = _goi_an_toan("giao_dien.session", "xoa_du_an")
        if ham is None:
            return _chua_trien_khai("xóa dự án")
        return jsonify(ham(request.get_json(silent=True) or {}))

    @app.route("/api/danh-sach-chat-nhanh", methods=["GET"])
    def api_danh_sach_chat_nhanh():
        ham = _goi_an_toan("giao_dien.session", "lay_danh_sach_chat_nhanh")
        if ham is None:
            return _chua_trien_khai("lấy danh sách chat nhanh")
        return jsonify(ham())

    @app.route("/api/tao-chat-nhanh", methods=["POST"])
    def api_tao_chat_nhanh():
        ham = _goi_an_toan("giao_dien.session", "tao_chat_nhanh")
        if ham is None:
            return _chua_trien_khai("tạo chat nhanh")
        return jsonify(ham(request.get_json(silent=True) or {}))

    @app.route("/api/xoa-chat-nhanh", methods=["POST"])
    def api_xoa_chat_nhanh():
        ham = _goi_an_toan("giao_dien.session", "xoa_chat_nhanh")
        if ham is None:
            return _chua_trien_khai("xóa chat nhanh")
        return jsonify(ham(request.get_json(silent=True) or {}))

    @app.route("/api/doi-ten-chat-nhanh", methods=["POST"])
    def api_doi_ten_chat_nhanh():
        ham = _goi_an_toan("giao_dien.session", "doi_ten_chat_nhanh")
        if ham is None:
            return _chua_trien_khai("đổi tên chat nhanh")
        return jsonify(ham(request.get_json(silent=True) or {}))

    @app.route("/api/new-chat", methods=["POST"])
    def api_new_chat():
        ham = _goi_an_toan("giao_dien.session", "tao_chat_moi")
        if ham is None:
            return _chua_trien_khai("tạo chat mới")
        return jsonify(ham(request.get_json(silent=True) or {}))

    # ============================================================
    # SANDBOX
    # ============================================================
    @app.route("/api/sandbox/chay", methods=["POST"])
    def api_sandbox_chay():
        du_lieu = request.get_json(silent=True) or {}
        ngon_ngu = du_lieu.get("ngon_ngu", "python")
        if ngon_ngu == "html":
            ham = _goi_an_toan("sanbox.chay_html", "chay_html")
        else:
            ham = _goi_an_toan("sanbox.chay_python", "chay_python")
        if ham is None:
            return _chua_trien_khai("chạy sandbox")
        return jsonify(ham(du_lieu))

    # ============================================================
    # CÂY QUYẾT ĐỊNH
    # ============================================================
    @app.route("/api/cay", methods=["GET"])
    def api_cay():
        ham = _goi_an_toan("dai_nao.ghi_nho", "doc_cay")
        if ham is None:
            return _chua_trien_khai("đọc cây quyết định")
        return jsonify(ham())