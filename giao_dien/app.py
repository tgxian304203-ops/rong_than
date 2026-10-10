"""
app.py - Flask server cho giao diện Rồng Thần.

Nhiệm vụ:
    - Khởi tạo Flask app.
    - Cấu hình thư mục tĩnh (giao_dien/) để phục vụ index.html, style.css, *.js.
    - Đăng ký toàn bộ route API từ routes.py.
    - Bật CORS cho phép gọi API nội bộ.
    - Xử lý ObjectId (MongoDB) để không lỗi JSON.

Không chứa logic nghiệp vụ. Logic nằm ở dai_nao/, tieu_nao/, tra_web/, sanbox/.
"""

import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask.json.provider import DefaultJSONProvider
from bson import ObjectId


# ================================================================
# ĐẢM BẢO IMPORT ĐƯỢC CÁC PACKAGE CÙNG CẤP
# ================================================================
THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)


# ================================================================
# THƯ MỤC FILE TĨNH
# ================================================================
THU_MUC_GIAO_DIEN = os.path.dirname(os.path.abspath(__file__))


# ================================================================
# CUSTOM JSON PROVIDER — CHUYỂN ObjectId SANG STRING
# ================================================================
class CustomJSONProvider(DefaultJSONProvider):
    """
    Xử lý ObjectId (MongoDB) và các kiểu BSON đặc biệt khác
    để không bị lỗi "Object of type ObjectId is not JSON serializable".
    """

    @staticmethod
    def default(obj):
        # ObjectId → string
        if isinstance(obj, ObjectId):
            return str(obj)

        # Các kiểu BSON đặc biệt khác
        try:
            from bson import Decimal128, Binary, Timestamp, Int64

            if isinstance(obj, Decimal128):
                return float(obj.to_decimal())

            if isinstance(obj, Binary):
                return str(obj)

            if isinstance(obj, Timestamp):
                return obj.time

            if isinstance(obj, Int64):
                return int(obj)

        except ImportError:
            pass

        # Fallback: gọi provider mặc định
        return DefaultJSONProvider.default(obj)


# ================================================================
# TẠO FLASK APP
# ================================================================
def tao_app():
    """
    Tạo và cấu hình Flask app.
    Trả về đối tượng Flask đã sẵn sàng chạy.
    """
    app = Flask(
        __name__,
        static_folder=THU_MUC_GIAO_DIEN,
        static_url_path="",
    )

    # Gắn custom JSON provider (xử lý ObjectId)
    app.json = CustomJSONProvider(app)

    # Cho phép CORS cho toàn bộ API nội bộ
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ------------------------------------------------------------
    # Route gốc: phục vụ index.html
    # ------------------------------------------------------------
    @app.route("/")
    def trang_chu():
        return send_from_directory(THU_MUC_GIAO_DIEN, "index.html")

    # ------------------------------------------------------------
    # Route tĩnh: phục vụ các file .css, .js, ảnh...
    # ------------------------------------------------------------
    @app.route("/<path:ten_file>")
    def file_tinh(ten_file):
        return send_from_directory(THU_MUC_GIAO_DIEN, ten_file)

    # ------------------------------------------------------------
    # Đăng ký toàn bộ route API từ routes.py
    # ------------------------------------------------------------
    try:
        from giao_dien.routes import dang_ky_routes
        dang_ky_routes(app)
    except ImportError:
        # Khi chạy trực tiếp từ trong thư mục giao_dien/
        from routes import dang_ky_routes
        dang_ky_routes(app)

    return app


# ================================================================
# CHẠY TRỰC TIẾP
# ================================================================
if __name__ == "__main__":
    ung_dung = tao_app()
    cong = int(os.environ.get("PORT", 5000))
    ung_dung.run(host="0.0.0.0", port=cong, debug=False)