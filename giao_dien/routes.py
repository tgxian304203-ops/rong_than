# ============================================================
# KEY MODEL (FIX: truyền loai_nao từ query param)
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
    # FIX: Truyền loai_nao từ query param
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
    # FIX: Truyền loai_nao từ query param
    loai_nao = request.args.get("loai_nao", "") or None
    du_lieu = {"loai_nao": loai_nao} if loai_nao else {}
    return jsonify(ham(du_lieu))