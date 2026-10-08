"""
cay_quyet_dinh.py - Cấu trúc cây quyết định Rồng Thần.

Nhiệm vụ:
    - Định nghĩa class Nut (node cây).
    - Định nghĩa class Cay (quản lý toàn bộ cây).
    - Cung cấp hàm chuyển đổi dict <-> object để lưu/đọc MongoDB.

ĐÃ NÂNG CẤP (Giai đoạn 1 — học pattern):
    - FIX 1: Thêm 3 trường mới vào Nut (25 → 28 trường):
             + pattern_regex: regex để khớp task
             + placeholder_map: map placeholder → yếu tố
             + hop_dong: hợp đồng nếu node là cả 1 file
    - FIX 2: Thêm phương thức khop_regex(noi_dung) — kiểm tra task khớp regex.
    - FIX 3: Thêm phương thức lay_bien_tu_regex(noi_dung) — tách nhóm regex.
    - FIX 4: sang_dict() và sang_dict_phang() xuất cả 3 trường mới.

Cấu trúc 4 tầng:
    Tầng 1: lĩnh vực (toán, văn, code, bug, ...)
    Tầng 2: loại vấn đề (số học, tạo mới, syntax, ...)
    Tầng 3: cách giải (cộng số nguyên, làm web, ...)
    Tầng 4: ngữ cảnh (cho học sinh, bằng Python, ...)

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import re
import time
import secrets


# ================================================================
# HẰNG SỐ
# ================================================================
SO_LAN_FAIL_TOI_DA = 3
TY_LE_FAIL_BLACKLIST = 0.5
NGUONG_SCORE_TOI_THIEU = 0.5


# ================================================================
# CLASS NUT — 1 node trong cây (28 trường)
# ================================================================
class Nut:
    """
    Một node trong cây quyết định.

    28 trường:
        - 25 trường cũ (theo Phần 4).
        - 3 trường mới: pattern_regex, placeholder_map, hop_dong.
    """

    def __init__(self, du_lieu=None):
        du_lieu = du_lieu or {}

        # --- Nhóm định danh ---
        self.id = du_lieu.get("id") or self._tao_id()
        self.ten = du_lieu.get("ten", "")
        self.phien_ban = du_lieu.get("phien_ban", 1)

        # --- Nhóm điều kiện / quy tắc ---
        self.dieu_kien = du_lieu.get("dieu_kien", {})
        self.quy_tac = du_lieu.get("quy_tac", "")
        self.thuat_toan = du_lieu.get("thuat_toan", {})
        self.cach_giai = du_lieu.get("cach_giai", {})
        self.hanh_dong = du_lieu.get("hanh_dong", {})

        # --- NHÓM MỚI: 3 trường học pattern ---
        self.pattern_regex = du_lieu.get("pattern_regex", "")
        self.placeholder_map = du_lieu.get("placeholder_map", {})
        self.hop_dong = du_lieu.get("hop_dong", {})

        # --- Nhóm đánh giá ---
        self.score = float(du_lieu.get("score", 1.0))
        self.so_lan_thu = int(du_lieu.get("so_lan_thu", 0))
        self.thanh_cong = int(du_lieu.get("thanh_cong", 0))
        self.that_bai = int(du_lieu.get("that_bai", 0))
        self.do_kho = float(du_lieu.get("do_kho", 0.5))
        self.thoi_gian_uoc_tinh = int(du_lieu.get("thoi_gian_uoc_tinh", 0))

        # --- Nhóm phụ thuộc / ưu tiên ---
        self.phu_thuoc = list(du_lieu.get("phu_thuoc", []))
        self.uu_tien = int(du_lieu.get("uu_tien", 50))

        # --- Nhóm nhánh con ---
        self.nhanh_con = []
        for con in du_lieu.get("nhanh_con", []):
            if isinstance(con, dict):
                self.nhanh_con.append(Nut(con))
            elif isinstance(con, Nut):
                self.nhanh_con.append(con)

        # --- Nhóm chia sẻ / mượn ---
        self.chia_se_voi = list(du_lieu.get("chia_se_voi", []))
        self.muon_tu = du_lieu.get("muon_tu", "")

        # --- Nhóm chống lặp sai ---
        self.failed_paths = list(du_lieu.get("failed_paths", []))
        self.blacklist = bool(du_lieu.get("blacklist", False))

        # --- Nhóm 4 tầng cây ---
        self.linh_vuc = du_lieu.get("linh_vuc", "")
        self.loai_van_de = du_lieu.get("loai_van_de", "")
        self.cach_giai_phap = du_lieu.get("cach_giai_phap", "")
        self.ngu_canh_node = du_lieu.get("ngu_canh_node", "")

        # --- Metadata ---
        self.ngay_tao = du_lieu.get("ngay_tao", int(time.time()))
        self.lan_dung_cuoi = du_lieu.get("lan_dung_cuoi", 0)

    # ------------------------------------------------------------
    # TIỆN ÍCH NỘI BỘ
    # ------------------------------------------------------------
    @staticmethod
    def _tao_id():
        return "nut-" + secrets.token_hex(6)

    # ------------------------------------------------------------
    # KHỚP REGEX (MỚI)
    # ------------------------------------------------------------
    def co_pattern(self):
        """Kiểm tra node có pattern_regex không."""
        return bool(self.pattern_regex and self.pattern_regex.strip())

    def khop_regex(self, noi_dung):
        """
        Kiểm tra nội dung task có khớp pattern_regex không.

        Trả về: (True/False, match_object hoặc None).
        """
        if not self.co_pattern() or not noi_dung:
            return False, None
        try:
            khop = re.search(self.pattern_regex, noi_dung)
            return (khop is not None), khop
        except re.error:
            return False, None

    def lay_bien_tu_regex(self, noi_dung):
        """
        Tách nhóm regex từ nội dung task.

        Trả về dict {ten_bien: gia_tri} dựa trên placeholder_map.

        Ví dụ:
            pattern_regex = r"^(\\d+)\\s*\\+\\s*(\\d+)$"
            placeholder_map = {"a": "$1", "b": "$2"}
            noi_dung = "999 + 888"
            → {"a": "999", "b": "888"}
        """
        if not self.co_pattern() or not noi_dung:
            return {}

        _, khop = self.khop_regex(noi_dung)
        if not khop:
            return {}

        ket_qua = {}
        for ten_bien, vi_tri in (self.placeholder_map or {}).items():
            try:
                if isinstance(vi_tri, str) and vi_tri.startswith("$"):
                    so_nhom = int(vi_tri[1:])
                    if so_nhom <= len(khop.groups()):
                        ket_qua[ten_bien] = khop.group(so_nhom)
                elif isinstance(vi_tri, int):
                    if vi_tri <= len(khop.groups()):
                        ket_qua[ten_bien] = khop.group(vi_tri)
            except (ValueError, IndexError):
                continue

        return ket_qua

    # ------------------------------------------------------------
    # CHUYỂN ĐỔI
    # ------------------------------------------------------------
    def sang_dict(self, gom_nhanh_con=True):
        """Chuyển node thành dict để lưu MongoDB."""
        du_lieu = {
            "id": self.id,
            "ten": self.ten,
            "phien_ban": self.phien_ban,
            "dieu_kien": self.dieu_kien,
            "quy_tac": self.quy_tac,
            "thuat_toan": self.thuat_toan,
            "cach_giai": self.cach_giai,
            "hanh_dong": self.hanh_dong,
            # 3 trường mới
            "pattern_regex": self.pattern_regex,
            "placeholder_map": self.placeholder_map,
            "hop_dong": self.hop_dong,
            # Đánh giá
            "score": self.score,
            "so_lan_thu": self.so_lan_thu,
            "thanh_cong": self.thanh_cong,
            "that_bai": self.that_bai,
            "do_kho": self.do_kho,
            "thoi_gian_uoc_tinh": self.thoi_gian_uoc_tinh,
            "phu_thuoc": self.phu_thuoc,
            "uu_tien": self.uu_tien,
            "chia_se_voi": self.chia_se_voi,
            "muon_tu": self.muon_tu,
            "failed_paths": self.failed_paths,
            "blacklist": self.blacklist,
            "linh_vuc": self.linh_vuc,
            "loai_van_de": self.loai_van_de,
            "cach_giai_phap": self.cach_giai_phap,
            "ngu_canh_node": self.ngu_canh_node,
            "ngay_tao": self.ngay_tao,
            "lan_dung_cuoi": self.lan_dung_cuoi,
        }
        if gom_nhanh_con:
            du_lieu["nhanh_con"] = [c.sang_dict() for c in self.nhanh_con]
        return du_lieu

    def sang_dict_phang(self):
        """Chuyển node thành dict phẳng (không nhánh con)."""
        return self.sang_dict(gom_nhanh_con=False)

    # ------------------------------------------------------------
    # ĐÁNH GIÁ
    # ------------------------------------------------------------
    def ty_le_thanh_cong(self):
        if self.so_lan_thu <= 0:
            return 1.0
        return self.thanh_cong / self.so_lan_thu

    def ty_le_that_bai(self):
        return 1.0 - self.ty_le_thanh_cong()

    def nen_blacklist(self):
        return self.that_bai >= SO_LAN_FAIL_TOI_DA

    def nen_giam_score(self):
        return self.ty_le_that_bai() > TY_LE_FAIL_BLACKLIST

    # ------------------------------------------------------------
    # CẬP NHẬT
    # ------------------------------------------------------------
    def ghi_thanh_cong(self):
        self.so_lan_thu += 1
        self.thanh_cong += 1
        self.lan_dung_cuoi = int(time.time())
        self._cap_nhat_score()

    def ghi_that_bai(self, duong_dan_sai=None):
        self.so_lan_thu += 1
        self.that_bai += 1
        if duong_dan_sai:
            if duong_dan_sai not in self.failed_paths:
                self.failed_paths.append(duong_dan_sai)
        if self.nen_blacklist():
            self.blacklist = True
        self._cap_nhat_score()

    def _cap_nhat_score(self):
        ty_le = self.ty_le_thanh_cong()
        do_tin_cay = 0.9
        uu_tien_chuan = self.uu_tien / 100.0
        do_kho_chuan = 1.0 - self.do_kho

        self.score = round(
            ty_le * 0.4
            + do_tin_cay * 0.2
            + uu_tien_chuan * 0.2
            + do_kho_chuan * 0.2,
            3,
        )

        if self.nen_giam_score():
            self.score = round(max(0.0, self.score - 0.2), 3)

    # ------------------------------------------------------------
    # NHÁNH CON
    # ------------------------------------------------------------
    def them_con(self, node_con):
        if isinstance(node_con, Nut):
            self.nhanh_con.append(node_con)

    def tim_con_theo_id(self, id_con):
        for c in self.nhanh_con:
            if c.id == id_con:
                return c
        return None

    def dem_tat_ca(self):
        dem = 1
        for c in self.nhanh_con:
            dem += c.dem_tat_ca()
        return dem

    # ------------------------------------------------------------
    # BIỂU DIỄN
    # ------------------------------------------------------------
    def __repr__(self):
        pattern_info = f", regex='{self.pattern_regex[:30]}'" if self.pattern_regex else ""
        return (
            f"Nut(id={self.id}, ten='{self.ten}', "
            f"linh_vuc='{self.linh_vuc}', score={self.score}"
            f"{pattern_info}, con={len(self.nhanh_con)})"
        )

    def __eq__(self, khac):
        if not isinstance(khac, Nut):
            return False
        return self.id == khac.id

    def __hash__(self):
        return hash(self.id)


# ================================================================
# CLASS CAY — quản lý toàn bộ cây
# ================================================================
class Cay:
    def __init__(self, du_lieu=None):
        self.goc = None
        self.ban_do = {}

        if du_lieu:
            self._nap_tu_dict(du_lieu)
        else:
            self.goc = Nut({
                "id": "root",
                "ten": "ROOT",
                "score": 1.0,
                "uu_tien": 100,
            })
            self._dang_ky(self.goc)

    def _nap_tu_dict(self, du_lieu):
        if not du_lieu:
            self.goc = Nut({"id": "root", "ten": "ROOT", "score": 1.0})
            self._dang_ky(self.goc)
            return
        self.goc = Nut(du_lieu)
        self._dang_ky_de_quy(self.goc)

    def _dang_ky(self, node):
        if node and node.id:
            self.ban_do[node.id] = node

    def _dang_ky_de_quy(self, node):
        self._dang_ky(node)
        for c in node.nhanh_con:
            self._dang_ky_de_quy(c)

    def sang_dict(self):
        return self.goc.sang_dict() if self.goc else {}

    def them_node(self, node, id_cha=None):
        if not isinstance(node, Nut):
            return False

        if id_cha is None or id_cha == "root":
            self.goc.them_con(node)
        else:
            cha = self.ban_do.get(id_cha)
            if not cha:
                return False
            cha.them_con(node)

        self._dang_ky_de_quy(node)
        return True

    def tim_node(self, id_node):
        return self.ban_do.get(id_node)

    def xoa_node(self, id_node):
        if id_node == "root":
            return False
        return self._xoa_de_quy(self.goc, id_node)

    def _xoa_de_quy(self, node, id_can_xoa):
        for i, con in enumerate(node.nhanh_con):
            if con.id == id_can_xoa:
                node.nhanh_con.pop(i)
                if id_can_xoa in self.ban_do:
                    del self.ban_do[id_can_xoa]
                return True
            if self._xoa_de_quy(con, id_can_xoa):
                return True
        return False

    def duyet_tat_ca(self):
        ket_qua = []
        hang_doi = [self.goc] if self.goc else []
        while hang_doi:
            node = hang_doi.pop(0)
            ket_qua.append(node)
            hang_doi.extend(node.nhanh_con)
        return ket_qua

    def duyet_theo_linh_vuc(self, linh_vuc):
        return [n for n in self.duyet_tat_ca() if n.linh_vuc == linh_vuc]

    def duyet_co_pattern(self):
        """Trả về danh sách node có pattern_regex."""
        return [n for n in self.duyet_tat_ca() if n.co_pattern()]

    def dem_tong_node(self):
        return len(self.ban_do)

    def chia_se(self, id_nguon, id_dich):
        nguon = self.ban_do.get(id_nguon)
        dich = self.ban_do.get(id_dich)
        if not nguon or not dich:
            return False

        if id_dich not in nguon.chia_se_voi:
            nguon.chia_se_voi.append(id_dich)
        if id_nguon not in dich.chia_se_voi:
            dich.chia_se_voi.append(id_nguon)
        return True

    def muon_nhanh(self, id_goc, id_dich):
        goc = self.ban_do.get(id_goc)
        dich = self.ban_do.get(id_dich)
        if not goc or not dich:
            return False
        if goc.score < NGUONG_SCORE_TOI_THIEU:
            return False

        dich.muon_tu = id_goc
        return True

    def __repr__(self):
        return f"Cay(tong_node={self.dem_tong_node()})"


# ================================================================
# HÀM TIỆN ÍCH
# ================================================================
def cay_tu_mongo():
    """Đọc cây từ kho 2 và trả về object Cay."""
    try:
        from dai_nao.ghi_nho import doc_cay
        du_lieu = doc_cay()
        return Cay(du_lieu)
    except Exception as e:
        try:
            from logs.ghi_log import ghi_log
            ghi_log("loi", f"Không đọc được cây từ MongoDB: {e}")
        except Exception:
            pass
        return Cay()


def luu_cay_vao_mongo(cay):
    """Lưu toàn bộ cây vào kho 2 (từng node phẳng)."""
    if not isinstance(cay, Cay):
        return False

    try:
        from dai_nao.ghi_nho import luu_node

        for node in cay.duyet_tat_ca():
            du_lieu = node.sang_dict_phang()
            du_lieu["node_cha"] = _tim_id_cha(cay, node.id)
            luu_node(du_lieu)
        return True
    except Exception as e:
        try:
            from logs.ghi_log import ghi_log
            ghi_log("loi", f"Không lưu được cây vào MongoDB: {e}")
        except Exception:
            pass
        return False


def _tim_id_cha(cay, id_con):
    if not cay or not cay.goc:
        return None
    if cay.goc.id == id_con:
        return None
    return _tim_cha_de_quy(cay.goc, id_con)


def _tim_cha_de_quy(cha, id_con):
    for con in cha.nhanh_con:
        if con.id == id_con:
            return cha.id
        ket_qua = _tim_cha_de_quy(con, id_con)
        if ket_qua:
            return ket_qua
    return None