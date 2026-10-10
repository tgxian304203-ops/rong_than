"""
app.py - Flask server cho giao diện Rồng Thần.

ĐÃ SỬA: Thêm CustomJSONProvider để chuyển ObjectId sang string.
"""

import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask.json.provider import DefaultJSONProvider
from bson import ObjectId


THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)

THU_MUC_GIAO_DIEN = os.path.dirname(os.path.abspath(__file__))


class CustomJSONProvider(DefaultJSONProvider):
    @staticmethod
    def default(obj):
        if isinstance(obj, ObjectId):
            return str(obj)
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
        return DefaultJSONProvider.default(obj)


def tao_app():
    app = Flask(
        __name__,
        static_folder=THU_MUC_GIAO_DIEN,
        static_url_path="",
    )

    app.json = CustomJSONProvider(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route("/")
    def trang_chu():
        return send_from_directory(THU_MUC_GIAO_DIEN, "index.html")

    @app.route("/<path:ten_file>")
    def file_tinh(ten_file):
        return send_from_directory(THU_MUC_GIAO_DIEN, ten_file)

    try:
        from giao_dien.routes import dang_ky_routes
        dang_ky_routes(app)
    except ImportError:
        from routes import dang_ky_routes
        dang_ky_routes(app)

    return app


if __name__ == "__main__":
    ung_dung = tao_app()
    cong = int(os.environ.get("PORT", 5000))
    ung_dung.run(host="0.0.0.0", port=cong, debug=False)