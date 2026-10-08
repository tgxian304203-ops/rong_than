# ================================================================
# KIỂM TRA CÓ CẦN BOSS KHÔNG
# ================================================================
def can_boss(noi_dung):
    """
    Kiểm tra task có cần Boss không.

    Boss cần cho:
        - Task dài (> 25 ký tự).
        - Có từ khoá hành động + đối tượng (làm/tạo/viết/xây + web/app/dự án/game/tool).
        - Có nhiều yêu cầu.

    Boss KHÔNG cần cho:
        - Task ngắn, đơn giản, hỏi đáp nhanh.
    """
    if not noi_dung:
        return False

    noi_dung_lower = noi_dung.lower().strip()

    # Câu rất ngắn → không cần Boss
    if len(noi_dung_lower) < 10:
        return False

    # Câu hỏi thời gian → không cần Boss
    for tk in ("hôm nay", "bây giờ", "mấy giờ", "ngày mấy"):
        if tk in noi_dung_lower:
            return False

    # Câu chào hỏi → không cần Boss
    for tk in ("chào", "hello", "hi ", "cảm ơn"):
        if noi_dung_lower.startswith(tk):
            return False

    # ============================================================
    # TỪ KHOÁ HÀNH ĐỘNG + ĐỐI TƯỢNG
    # ============================================================
    tu_hanh_dong = ("làm", "tạo", "xây", "viết", "dựng", "thiết kế", "code", "lập trình")
    tu_doi_tuong = (
        "web", "app", "ứng dụng", "dự án", "game", "tool", "công cụ",
        "hệ thống", "phần mềm", "website", "trang web", "api", "bot",
        "chatbot", "ai", "trò chơi", "quản lý", "sinh viên", "bán hàng",
        "thẻ bài", "shop", "cửa hàng", "landing", "portfolio",
    )

    co_hanh_dong = any(tk in noi_dung_lower for tk in tu_hanh_dong)
    co_doi_tuong = any(tk in noi_dung_lower for tk in tu_doi_tuong)

    if co_hanh_dong and co_doi_tuong:
        return True

    # ============================================================
    # TASK DÀI → CẦN BOSS
    # ============================================================
    if len(noi_dung_lower) > 25:
        # Nhưng phải có động từ hành động
        if co_hanh_dong:
            return True

    # ============================================================
    # NHIỀU YÊU CẦU (nhiều dấu phẩy/chấm/"và")
    # ============================================================
    so_dau_cau = (
        noi_dung_lower.count(",") +
        noi_dung_lower.count(";") +
        noi_dung_lower.count(" và ")
    )
    if so_dau_cau >= 3 and co_hanh_dong:
        return True

    return False