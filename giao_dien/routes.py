"""
routes.py - Định nghĩa toàn bộ route API cho Rồng Thần.

ĐÃ SỬA:
    - Đọc SECRET_KEY từ env trước → không mất session khi Render rebuild.
    - Nếu không có env → đọc file → nếu không có → tạo mới.
"""

import os
import io
import json
import secrets
from functools import wraps

from flask import jsonify, request, session, send_file


THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_DU_LIEU = os.path.join(THU_MUC_GOC, "du_lieu")
FILE_CAU_HINH_KHO = os.path.join(THU_MUC_DU_LIEU, "cau_hinh_kho.json")


def _doc_hoac_tao_secret_key():
    """Đọc SECRET_KEY từ env → file → tạo mới."""
    # 1. Ưu tiên env — không mất khi Render rebuild
    secret_env = os.environ.get("SECRET_KEY")
    if secret_env:
        return secret_env

    # 2. Fallback: đọc từ file
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
    # TIN NHẮN CHAT NHANH
    # ============================================================
    @app.route("/api/tin-nhan-chat-nhanh", methods=["GET"])
    def api_tin_nhan_chat_nhanh():
        ham = _goi_an_toan("giao_dien.session", "lay_tin_nhan_chat_nhanh_cua")
        if ham is None:
            return _chua_trien_khai("lấy tin nhắn chat nhanh")
        id_chat = request.args.get("id_chat", "")
        return jsonify(ham(id_chat))

    # ============================================================
    # CHAT TRONG DỰ ÁN
    # ============================================================
    @app.route("/api/gui-tin-nhan-du-an", methods=["POST"])
    def api_gui_tin_nhan_du_an():
        du_lieu = request.get_json(silent=True) or {}
        id_du_an = du_lieu.get("id_du_an")
        id_tro_chuyen = du_lieu.get("id_tro_chuyen")
        noi_dung = (du_lieu.get("noi_dung") or "").strip()
        urls_anh = du_lieu.get("urls_anh") or []
        urls_file = du_lieu.get("urls_file") or []

        if not id_du_an or not id_tro_chuyen:
            return jsonify({"thanh_cong": False, "loi": "Thiếu thông tin."})

        if not noi_dung and not urls_anh and not urls_file:
            return jsonify({"thanh_cong": False, "loi": "Không có nội dung để gửi."})

        ten_tk = session.get("ten_dang_nhap")

        if ten_tk:
            ham_luu = _goi_an_toan("giao_dien.session", "luu_tin_nhan")
            if ham_luu:
                ham_luu({
                    "id_du_an": id_du_an,
                    "id_tro_chuyen": id_tro_chuyen,
                    "vai_tro": "nguoi",
                    "noi_dung": noi_dung,
                    "urls_anh": urls_anh,
                    "urls_file": urls_file,
                })

        ham_xu_ly = _goi_an_toan("dai_nao.nhan_task", "nhan_task")
        if ham_xu_ly is None:
            return _chua_trien_khai("đại não xử lý")

        try:
            ket_qua = ham_xu_ly({"noi_dung": noi_dung, "chu_so_huu": ten_tk or "khach"})
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
        loai_nao = request.args.get("loai_nao", "") or None
        du_lieu = {"loai_nao": loai_nao} if loai_nao else {}
        return jsonify(ham(du_lieu))

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
        loai_nao = request.args.get("loai_nao", "") or None
        du_lieu = {"loai_nao": loai_nao} if loai_nao else {}
        return jsonify(ham(du_lieu))

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
        try:
            danh_sach = ham() or []
        except Exception as e:
            return jsonify({
                "thanh_cong": False,
                "loi": f"Lỗi đọc log: {e}",
                "danh_sach": [],
            })
        return jsonify({
            "thanh_cong": True,
            "danh_sach": danh_sach,
            "da_loc": False,
        })

    @app.route("/api/logs/loc", methods=["GET"])
    def api_logs_loc():
        loai = request.args.get("loai", "tat-ca")
        ham = _goi_an_toan("logs.loc_log", "loc_log")
        if ham is None:
            return _chua_trien_khai("lọc log")
        try:
            danh_sach = ham(loai) or []
        except Exception as e:
            return jsonify({
                "thanh_cong": False,
                "loi": f"Lỗi lọc log: {e}",
                "danh_sach": [],
            })
        return jsonify({
            "thanh_cong": True,
            "danh_sach": danh_sach,
            "da_loc": True,
        })

    @app.route("/api/logs/xoa", methods=["POST"])
    def api_logs_xoa():
        ham = _goi_an_toan("logs.doc_log", "xoa_log")
        if ham is None:
            return _chua_trien_khai("xóa log")
        try:
            so_xoa = ham() or 0
        except Exception as e:
            return jsonify({
                "thanh_cong": False,
                "loi": f"Lỗi xóa log: {e}",
            })
        return jsonify({
            "thanh_cong": True,
            "so_xoa": so_xoa,
        })

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
        id_tro_chuyen = request.form.get("id_tro_chuyen") or None
        id_du_an = request.form.get("id_du_an") or None
        return jsonify(ham(request.files, id_tro_chuyen, id_du_an))

    @app.route("/api/upload-file", methods=["POST"])
    def api_upload_file():
        ham = _goi_an_toan("giao_dien.upload", "upload_file")
        if ham is None:
            return _chua_trien_khai("upload file")
        id_tro_chuyen = request.form.get("id_tro_chuyen") or None
        id_du_an = request.form.get("id_du_an") or None
        return jsonify(ham(request.files, id_tro_chuyen, id_du_an))

    # ============================================================
    # PHỤC VỤ FILE TỪ GRIDFS
    # ============================================================
    @app.route("/api/file/<id_file>", methods=["GET"])
    def api_file(id_file):
        from dai_nao.ghi_nho import lay_file_theo_id, doc_file_gridfs
        metadata = lay_file_theo_id(id_file)
        if not metadata:
            return jsonify({"thanh_cong": False, "loi": "Không tìm thấy file."}), 404

        id_gridfs = metadata.get("id_gridfs")
        if not id_gridfs:
            return jsonify({"thanh_cong": False, "loi": "File không có trong GridFS."}), 404

        noi_dung = doc_file_gridfs(id_gridfs)
        if not noi_dung:
            return jsonify({"thanh_cong": False, "loi": "Không đọc được file."}), 404

        ten_file = metadata.get("ten_file") or "file"
        duoi_file = (metadata.get("duoi_file") or "").lower()

        mime_map = {
            "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "webp": "image/webp", "bmp": "image/bmp",
            "svg": "image/svg+xml", "pdf": "application/pdf",
            "txt": "text/plain; charset=utf-8", "md": "text/plain; charset=utf-8",
            "json": "application/json", "csv": "text/csv", "log": "text/plain",
        }
        mime = mime_map.get(duoi_file, "application/octet-stream")

        hien_thi_inline = duoi_file in (
            "png", "jpg", "jpeg", "gif", "webp", "bmp", "svg",
            "pdf", "txt", "md", "json", "csv", "log",
        )

        return send_file(
            io.BytesIO(noi_dung),
            mimetype=mime,
            as_attachment=not hien_thi_inline,
            download_name=ten_file,
        )

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

    @app.route("/api/sandbox/ket-qua", methods=["POST"])
    def api_sandbox_ket_qua():
        du_lieu = request.get_json(silent=True) or {}
        code = du_lieu.get("code") or ""
        stdout = du_lieu.get("stdout") or ""
        stderr = du_lieu.get("stderr") or ""
        ngon_ngu = du_lieu.get("ngon_ngu") or "python"
        id_chat = du_lieu.get("id_chat") or ""
        id_node = du_lieu.get("id_node") or ""
        la_lan_hai = bool(du_lieu.get("la_lan_hai", False))

        if not code:
            return jsonify({
                "thanh_cong": False,
                "loi": "Thiếu code.",
            })

        ket_qua_client = {
            "console": [],
            "error": stderr if stderr else None,
        }
        if stdout:
            for dong in stdout.split("\n"):
                if dong.strip():
                    ket_qua_client["console"].append({
                        "method": "log",
                        "args": [dong],
                    })
        if stderr:
            for dong in stderr.split("\n"):
                if dong.strip():
                    ket_qua_client["console"].append({
                        "method": "error",
                        "args": [dong],
                    })

        ket_qua_chuan = {}
        try:
            from sanbox.tra_ket_qua import tra_ket_qua
            ket_qua_chuan = tra_ket_qua(ket_qua_client) or {}
        except ImportError:
            ket_qua_chuan = {
                "thanh_cong": not bool(stderr),
                "stdout": stdout,
                "stderr": stderr,
                "result_html": "",
                "tests": [],
                "loi": "",
            }
        except Exception as e:
            return jsonify({
                "thanh_cong": False,
                "loi": f"Lỗi chuẩn hóa kết quả: {e}",
            })

        ket_qua_loi = {}
        try:
            from sanbox.kiem_tra_loi import kiem_tra_loi
            ket_qua_loi = kiem_tra_loi(ket_qua_client) or {}
        except ImportError:
            ket_qua_loi = {
                "thanh_cong": not bool(stderr),
                "co_loi": bool(stderr),
                "loai_loi": "runtime" if stderr else "",
                "thong_diep": stderr[:500] if stderr else "",
                "dong": None,
                "goi_y": [],
            }
        except Exception as e:
            return jsonify({
                "thanh_cong": False,
                "loi": f"Lỗi kiểm tra lỗi: {e}",
            })

        if not ket_qua_loi.get("co_loi"):
            if id_node:
                try:
                    from dai_nao.xu_ly_task import ghi_thanh_cong_vao_cay
                    ghi_thanh_cong_vao_cay(id_node, code)
                except ImportError:
                    pass
                except Exception as e:
                    print(f"Lỗi ghi thành công: {e}")

            return jsonify({
                "thanh_cong": True,
                "co_loi": False,
                "stdout": ket_qua_chuan.get("stdout", ""),
                "result_html": ket_qua_chuan.get("result_html", ""),
                "tests": ket_qua_chuan.get("tests", []),
                "thong_bao": "Code chạy thành công.",
            })

        thong_diep_loi = ket_qua_loi.get("thong_diep") or stderr
        loai_loi = ket_qua_loi.get("loai_loi") or "runtime"

        if id_node:
            try:
                from dai_nao.xu_ly_task import ghi_that_bai_vao_cay
                ghi_that_bai_vao_cay(id_node, code, thong_diep_loi[:200])
            except ImportError:
                pass
            except Exception as e:
                print(f"Lỗi ghi thất bại: {e}")

        if la_lan_hai:
            return jsonify({
                "thanh_cong": True,
                "co_loi": True,
                "loai_loi": loai_loi,
                "thong_diep_loi": thong_diep_loi[:500],
                "dong_loi": ket_qua_loi.get("dong"),
                "goi_y": ket_qua_loi.get("goi_y", []),
                "code_moi": code,
                "da_sua": False,
                "thong_bao": "Đã thử sửa nhưng vẫn còn lỗi.",
            })

        code_moi = code
        cach_sua = ""
        nguon = ""
        da_sua = False

        try:
            from dai_nao.tu_sua_loi import tu_sua_loi
            ket_qua_sua = tu_sua_loi(code, thong_diep_loi, ngon_ngu)
            if ket_qua_sua and ket_qua_sua.get("thanh_cong"):
                code_moi = ket_qua_sua.get("code_moi", code)
                cach_sua = ket_qua_sua.get("cach_sua", "")
                nguon = ket_qua_sua.get("nguon", "")
                da_sua = code_moi != code
        except ImportError:
            pass
        except Exception as e:
            return jsonify({
                "thanh_cong": False,
                "co_loi": True,
                "loi": f"Lỗi tự sửa: {e}",
                "thong_diep_loi": thong_diep_loi,
            })

        if da_sua and loai_loi:
            try:
                from dai_nao.cap_nhat_tu_dien_loi import hoc_tu_loi_moi
                hoc_tu_loi_moi(loai_loi, thong_diep_loi, cach_sua, code_moi)
            except ImportError:
                pass
            except Exception as e:
                print(f"Lỗi học lỗi mới: {e}")

        return jsonify({
            "thanh_cong": True,
            "co_loi": True,
            "loai_loi": loai_loi,
            "thong_diep_loi": thong_diep_loi[:500],
            "dong_loi": ket_qua_loi.get("dong"),
            "goi_y": ket_qua_loi.get("goi_y", []),
            "code_moi": code_moi,
            "da_sua": da_sua,
            "cach_sua": cach_sua,
            "nguon": nguon,
        })

    # ============================================================
    # CÂY QUYẾT ĐỊNH
    # ============================================================
    @app.route("/api/cay", methods=["GET"])
    def api_cay():
        ham = _goi_an_toan("dai_nao.ghi_nho", "doc_cay")
        if ham is None:
            return _chua_trien_khai("đọc cây quyết định")
        return jsonify(ham())

    # ============================================================
    # GLOBAL ERROR HANDLER — Trả JSON thay vì HTML
    # ============================================================
    @app.errorhandler(Exception)
    def _xu_ly_loi_chung(e):
        import traceback
        try:
            from logs.ghi_log import ghi_log
            ghi_log("loi", f"Flask exception: {e}\n{traceback.format_exc()}")
        except Exception:
            pass
        return jsonify({
            "thanh_cong": False,
            "loi": f"Lỗi server: {e}",
        }), 500

    @app.errorhandler(404)
    def _xu_ly_404(e):
        return jsonify({
            "thanh_cong": False,
            "loi": "Không tìm thấy route.",
        }), 404

    @app.errorhandler(500)
    def _xu_ly_500(e):
        return jsonify({
            "thanh_cong": False,
            "loi": "Lỗi server nội bộ.",
        }), 500