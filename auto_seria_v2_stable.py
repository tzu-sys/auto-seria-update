"""
AutoSeria V2 - Phiên bản Tinh Gọn, Thực Chiến 100% cho Seria (Crystal of Atlan)
Hệ điều hành: Windows 10/11 | Độ phân giải: 1366x768 Cửa Sổ | Chế độ game: Mobile
Tích hợp:
- Đổi Nhân Vật Chuẩn Xác: Bấm Slot 2 không cuộn chuột để lần lượt đôn các con 2, 3, 4, 5, 6, 7.
- Ghép Nhanh & Chuẩn Bị Vào Trận:
    + Bỏ qua hoàn toàn dòng cảnh báo đỏ.
    + Đếm chính xác số người trong phòng (Dưới 4 người thì Bấm TỪ CHỐI để ghép lại, Đủ 4 người thì Spam CHUẨN BỊ vào trận ngay 100%).
- Chinh Phạt & Ngục Tối: Đầy đủ các bước Ghép Với Bot 4 người, nhận đôi quà, combo chiến đấu (1, 2, 3, 4, E).
- Daily (Tuyệt đối bỏ tách đồ): Phúc Lợi, Mua Pin, Hạm Đội, Hòm Thư, Sổ Tay.
- Hộp Tinh Thể & Vật Phẩm: Mua 2 Hộp Tinh Thể Kỳ Dị, Dùng Vé Sạp, Dùng Vé Mật (giữ 3.5s), Đổi 7 Chìa Raid.
"""

import sys
import os
import time
import json
import base64
import ctypes
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# BẬT CHẾ ĐỘ DPI AWARENESS CHO WINDOWS (CHỐNG GIẬT LAG KHI KÉO CỬA SỔ TOOL)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import win32gui
import win32con
import win32api
import win32process
import pydirectinput
import cv2
import numpy as np
from PIL import ImageGrab

# Import templates vật phẩm
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
try:
    from item_templates_data import ITEM_TEMPLATES_B64, RAID_KEYS_META
except Exception:
    ITEM_TEMPLATES_B64 = {}
    RAID_KEYS_META = []

# Thiết lập pydirectinput an toàn
pydirectinput.FAILSAFE = False
pydirectinput.PAUSE = 0.04

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seria_v2_config.json")

# ==============================================================================
# BẢNG TỌA ĐỘ CHUẨN XÁC 100% (ĐÃ ĐƯỢC ĐO ĐẠC & KIỂM CHỨNG TẠI 1366x768)
# ==============================================================================
COORDS = {
    # --- Menu Đổi nhân vật & Sảnh ---
    "btn_menu": (1303, 412),               # Nút Menu mở rộng cạnh phải ở sảnh
    "btn_cai_dat_gear": (1338, 690),       # Bánh răng Cài Đặt (góc dưới phải)
    "btn_doi_nhan_vat": (1284, 712),       # Nút [Đổi Nhân Vật] trong popup Cài Đặt
    "btn_vao_game": (1117, 605),           # Nút to màu xanh [VÀO GAME] góc dưới phải (chuẩn 100%)

    # --- Tọa độ Slot Nhân Vật ---
    "slot_1": (216, 172),                  # Slot 1 (Đầu danh sách)
    "slot_2": (208, 264),                  # Slot 2 (VỊ TRÍ THAY THẾ: Bấm vào đây để lần lượt đổi sang 2, 3, 4, 5, 6, 7)
    "slot_3": (214, 369),                  # Slot 3 (Trang trên)
    "slot_4": (207, 469),                  # Slot 4 (Trang trên)
    "slot_5": (218, 567),                  # Slot 5 (Trang trên)
    "slot_6": (213, 668),                  # Slot 6 (Trang trên)

    # --- 5 Slot Cuối (Khi cuộn kịch đáy) ---
    "slot_8": (183, 307),                  # Đáy 1
    "slot_9": (192, 409),                  # Đáy 2
    "slot_10": (189, 499),                 # Đáy 3
    "slot_11": (209, 608),                 # Đáy 4
    "slot_12": (203, 704),                 # Đáy 5 (Acc 12 con)

    # --- Ải Chinh Phạt & Bảng Ghép 4 Người ---
    "btn_menu_chien_dau": (1308, 308),     # Nút Menu Chiến Đấu ở sảnh (tâm chuẩn kiếm chéo)
    "btn_khieu_chien": (780, 560),          # Nút Khiêu Chiến (tâm chuẩn thẻ chữ KHIÊU CHIẾN)
    "tab_chinh_phat_gioi_han": (149, 488), # Tab Chinh Phạt Giới Hạn bên trái
    "tab_boss_3": (1075, 452),             # Thẻ Boss 3
    "btn_nhan_doi_qua": (1036, 507),       # Nút Nhận Đôi Quà Chinh Phạt
    "btn_lap_doi_chinh_phat": (790, 585),  # Nút Lập Đội Chinh Phạt
    "btn_ghep_cap_nhanh": (835, 687),      # Nút Ghép Cặp Nhanh
    "btn_tu_choi": (537, 620),             # Nút Từ Chối (khi dưới 4 người - chuẩn 100%)
    "btn_chuan_bi": (866, 615),            # Nút Chuẩn Bị (khi đủ 4 người - chuẩn 100%)

    # --- Ải Ngục Tối ---
    "tab_tham_hiem": (371, 322),           # Tab Thám Hiểm (Ngục Tối)
    "btn_nhan_doi_qua_nguc": (761, 740),   # Nút Nhận Đôi Quà Ngục Tối
    "btn_khieu_chien_nhom": (963, 739),    # Nút Khiêu Chiến Nhóm Ngục Tối

    # --- Trong Ải & Thoát Về Sảnh ---
    "tap_dong_qua": (683, 720),            # Vùng tap an toàn gần đáy để tắt bảng quà/Rank S

    # --- Cửa Hàng & Mua 2 Hộp Tinh Thể Kỳ Dị ---
    "btn_cua_hang": (1155, 86),            # Cửa Hàng ở Sảnh
    "btn_doi_diem": (96, 562),             # Mục [Đổi Điểm] bên trái Cửa Hàng
    "hop_the_ky_di_1": (477, 224),         # Ô Hộp Tinh Thể 1
    "hop_the_ki_di_2": (751, 241),         # Ô Hộp Tinh Thể 2
    "btn_tang_hop_the": (1220, 662),       # Dấu [+] tăng số lượng hộp
    "btn_bam_mua_hop_the": (1118, 736),    # Nút [Mua] hộp
    "btn_xac_nhan_mua_hop": (891, 524),    # Nút [Xác Nhận] mua hộp

    # --- Đổi 8 Chìa Khóa Raid (Túi Đồ -> Mở Hộp) ---
    "mo_hop_tinh_the": (1128, 661),        # Nút [Mở Nhiều] Hộp Tinh Thể (tâm chuẩn)
    "key_l8": (425, 422),                  # Chìa L8
    "key_t8": (584, 425),                  # Chìa T8
    "key_s8": (733, 424),                  # Chìa S8
    "key_h4": (889, 425),                  # Chìa H4
    "key_k8": (1043, 425),                 # Chìa K8
    "key_d8": (428, 496),                  # Chìa D8
    "key_q8": (580, 495),                  # Chìa Q8
    "key_v8": (736, 496),                  # Chìa V8
    "btn_doi_chia": (813, 631),            # Nút [Đổi] chìa
    "btn_xac_nhan_doi_chia": (854, 528),   # Nút [Xác nhận đổi chìa]
    "xac_nhan_dung_chia": (872, 525),      # Nút [Xác nhận dùng chìa khóa]

    # --- Túi Đồ & Vật Phẩm ---
    "btn_tui_do": (807, 705),              # Nút Túi Đồ ở sảnh
    "tab_tieu_hao_bag": (1303, 72),        # Ô thứ 4: Tab Bình Thuốc (Tiêu Hao trong Túi Đồ)

    # --- Daily Chuẩn Xác 100% (TUYỆT ĐỐI BỎ TÁCH ĐỒ) ---
    # 1. Phúc Lợi Ngày (Trong Cửa Hàng)
    "tab_goi_qua": (110, 282),             # Tab Gói Quà bên trái Cửa Hàng
    "tab_goi_tuan": (735, 124),            # Tab Gói Quà Tuần ở giữa
    "btn_phuc_loi_ngay": (1007, 249),      # Nút Nhận Phúc Lợi Ngày
    # 2. Dùng Pin Thể Lực
    "btn_pin_2": (215, 87),                # Icon Pin thể lực trên thanh trạng thái
    "btn_dung_pin": (898, 429),            # Nút [Dùng] trong bảng Pin
    "btn_nut_tat": (1005, 213),            # Nút [X] tắt popup Pin
    "btn_close_x_nho": (1104, 250),        # Nút [X] tắt popup nhỏ
    # 3. Điểm Danh Hạm Đội
    "btn_ham_doi": (1234, 327),            # Mục Hạm Đội trong Menu
    "icon_check_in_ham": (316, 720),       # Icon Điểm danh góc dưới Hạm Đội
    "btn_checkin_mien_phi": (995, 601),    # Nút Điểm Danh Miễn Phí
    "btn_thoat_diem_danh": (1164, 172),    # Nút [X] thoát popup điểm danh
    # 4. Nhận Hòm Thư
    "btn_thu": (1336, 621),                # Mục Hòm Thư trong Menu
    "btn_nhan_thu": (330, 728),            # Nút [Nhận Toàn Bộ] Thư
    "btn_close_popup": (1258, 226),        # Nút tắt popup nhận thư
    # 5. Kho (Nạp Vàng & Gộp Đồ Nhanh)
    "btn_kho": (1064, 748),                # Nút Kho ở sảnh
    "btn_nap_vang": (667, 749),            # Nút Nạp Vàng trong Kho
    "btn_nap_vang_thuong": (820, 360),     # Bấm nạp vàng thường
    "btn_nap_vang_khoa": (818, 415),       # Bấm nạp vàng khóa
    "btn_cho_vao": (763, 521),             # Nút Cho Vào
    "btn_cong_don_nhanh": (1243, 749),     # Nút Gộp / Cộng Dồn Nhanh
    "btn_kho_tai_khoan": (758, 75),        # Tab Kho Tài Khoản
    "btn_tat_kho": (946, 411),             # Nút đóng kho
    # 6. Quà Sổ Tay
    "icon_so_tay": (1301, 252),            # Icon Sổ Tay ở sảnh
    "btn_tui_qua_so_tay": (1282, 325),     # Nút túi quà nhận nhanh
    "btn_qua_20": (789, 655),              # Mốc nhận quà 20
    "btn_qua_60": (1056, 655),             # Mốc nhận quà 60
    "btn_qua_80": (1186, 651),             # Mốc nhận quà 80
    "btn_qua_100": (1320, 653),            # Mốc nhận quà 100
    "btn_thoat_so": (37, 64),              # Nút thoát giao diện sổ tay
}


class SeriaEngineV2:
    """Bộ điều khiển lõi siêu tinh gọn, thực chiến 100%."""

    def __init__(self, log_callback=None):
        self.log_cb = log_callback or print
        self.game_hwnd = None
        self.is_running = False
        self.is_paused = False
        self.templates = {}
        self._load_templates()
        self.delay_multiplier = 1.0
        self.speed_mode = '⚖ Chuẩn (1.0x)'

    def log(self, text):
        self.log_cb(str(text))

    def _decode_b64_img(self, b64_str):
        if not b64_str:
            return None
        try:
            arr = np.frombuffer(base64.b64decode(b64_str), np.uint8)
            return cv2.imdecode(arr, cv2.IMREAD_COLOR)
        except Exception:
            return None

    def _load_templates(self):
        """Giải mã toàn bộ template Base64 thành ảnh OpenCV."""
        for name, b64_str in ITEM_TEMPLATES_B64.items():
            img = self._decode_b64_img(b64_str)
            if img is not None:
                self.templates[name] = img

    # --------------------------------------------------------------------------
    # THAO TÁC CỬA SỔ & PHÍM NÓNG
    # --------------------------------------------------------------------------
    def lock_game_window(self):
        """Tìm và ghim cửa sổ game về (0, 0) chuẩn 1366x768 (TUYỆT ĐỐI BỎ QUA TOOL)."""
        hwnd_found = None
        my_pid = os.getpid()

        def enum_cb(h, _):
            nonlocal hwnd_found
            try:
                if not win32gui.IsWindowVisible(h):
                    return True

                _, pid = win32process.GetWindowThreadProcessId(h)
                if pid == my_pid:
                    return True

                title = win32gui.GetWindowText(h)
                if not title:
                    return True

                t_lower = title.lower()
                if "autoclick" in t_lower or "autoseria" in t_lower:
                    return True

                is_iconic = win32gui.IsIconic(h)
                rect = win32gui.GetWindowRect(h)
                w = rect[2] - rect[0]
                h_len = rect[3] - rect[1]

                if "crystal of atlan" in t_lower or t_lower == "seria":
                    if is_iconic or (w > 400 and h_len > 300):
                        hwnd_found = h
                        return False

                import psutil
                pname = psutil.Process(pid).name().lower()
                if pname in ["seria.exe", "crystal of atlan.exe"]:
                    if is_iconic or (w > 400 and h_len > 300):
                        hwnd_found = h
                        return False
            except Exception:
                pass
            return True

        try:
            win32gui.EnumWindows(enum_cb, None)
        except Exception:
            pass

        if not hwnd_found:
            self.log("[!] Chưa tìm thấy cửa sổ game 'Crystal of Atlan'! Hãy mở game trước.")
            return None

        self.game_hwnd = hwnd_found
        try:
            if win32gui.IsIconic(hwnd_found):
                win32gui.ShowWindow(hwnd_found, win32con.SW_RESTORE)
                time.sleep(0.3)
            self.force_foreground()
            time.sleep(0.2)
            win32gui.SetWindowPos(hwnd_found, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
            self.log("[OK] Đã ghim cửa sổ game về góc (0, 0) (Kích thước gốc 1366x768).")
            return hwnd_found
        except Exception as e:
            self.log(f"[!] Lỗi ghim cửa sổ game: {e}")
            return None

    def force_foreground(self):
        if not self.game_hwnd or not win32gui.IsWindow(self.game_hwnd):
            return
        try:
            cur_fg = win32gui.GetForegroundWindow()
            if cur_fg == self.game_hwnd:
                return

            # Nhả Foreground Lock của Windows bằng cách giả lập phím ALT
            try:
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            except Exception:
                pass

            if win32gui.IsIconic(self.game_hwnd):
                win32gui.ShowWindow(self.game_hwnd, win32con.SW_RESTORE)

            win32gui.BringWindowToTop(self.game_hwnd)
            win32gui.SetForegroundWindow(self.game_hwnd)
            time.sleep(0.10)
        except Exception:
            pass

    def activate_game_input(self):
        """Kích hoạt và click mồi vào sảnh để game bắt chuột & focus 100% trước khi chạy."""
        self.force_foreground()
        time.sleep(0.25)
        # Click nhẹ vào vùng an toàn (683, 720) để bảo đảm game đã nhận focus và con trỏ chuột
        win32api.SetCursorPos((683, 720))
        pydirectinput.moveTo(683, 720)
        time.sleep(0.15)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.08)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.3)

    def check_hotkeys(self):
        if win32api.GetAsyncKeyState(win32con.VK_F11) & 0x8000:
            self.is_paused = not self.is_paused
            state = "TẠM DỪNG (PAUSED)" if self.is_paused else "TIẾP TỤC (RESUMED)"
            self.log(f"\n[HOTKEY F11] Tool {state}")
            time.sleep(0.4)

        if win32api.GetAsyncKeyState(win32con.VK_F12) & 0x8000:
            self.is_running = False
            self.log("\n[HOTKEY F12] Đã bấm dừng khẩn cấp!")
            raise KeyboardInterrupt("Stop requested via F12")

        while self.is_paused and self.is_running:
            time.sleep(0.2)
            if win32api.GetAsyncKeyState(win32con.VK_F11) & 0x8000:
                self.is_paused = False
                self.log("\n[HOTKEY F11] Tool TIẾP TỤC (RESUMED)")
                time.sleep(0.4)
                break

    # --------------------------------------------------------------------------
    # THAO TÁC CLICK & PHÍM DỨT KHOÁT
    # --------------------------------------------------------------------------
    def set_speed_mode(self, mode_str):
        """Điều chỉnh tốc độ thao tác: ⚡ Nhanh (0.75x) | ⚖ Chuẩn (1.0x) | 🛡 Chậm / An Toàn (1.30x)"""
        self.speed_mode = str(mode_str)
        if "Nhanh" in self.speed_mode or "0.75" in self.speed_mode:
            self.delay_multiplier = 0.75
            self.log(f"-> Tốc độ thao tác: ⚡ Nhanh (hệ số delay 0.75x)")
        elif "Chậm" in self.speed_mode or "1.3" in self.speed_mode:
            self.delay_multiplier = 1.30
            self.log(f"-> Tốc độ thao tác: 🛡 Chậm / An Toàn (hệ số delay 1.30x)")
        else:
            self.delay_multiplier = 1.0
            self.log(f"-> Tốc độ thao tác: ⚖ Chuẩn (hệ số delay 1.0x)")

    def click(self, x, y, delay=1.5, move_wait=0.30, label=None, clicks=1):
        """
        Di chuyển tới tọa độ -> DỪNG LẠI tại tọa độ (move_wait >= 0.28s) để game nhận hover
        -> Bấm dứt khoát (down 0.08s, up) -> Chờ delay.
        """
        self.check_hotkeys()
        self.force_foreground()

        # 1. Đưa con trỏ tới đúng tọa độ
        win32api.SetCursorPos((x, y))
        pydirectinput.moveTo(x, y)

        # 2. DỪNG LẠI TẠI TỌA ĐỘ để game nhận diện con trỏ và nút bấm (chống lướt qua)
        eff_mult = getattr(self, "delay_multiplier", 1.0)
        base_wait = max(0.20, move_wait) if move_wait > 0 else 0
        wait_time = base_wait * eff_mult if base_wait > 0 else 0
        if wait_time > 0:
            time.sleep(wait_time)

        # 3. Bấm dứt khoát (mặc định 1 lần, hoặc clicks lần nếu được chỉ định)
        num_clicks = max(1, clicks)
        lbl_text = f" [{label}]" if label else ""
        eff_delay = delay * eff_mult
        if num_clicks > 1:
            self.log(f"-> Click x{num_clicks} ({x:4d}, {y:4d}){lbl_text} (dừng {wait_time:.2f}s, chờ {eff_delay:.1f}s)")
        else:
            self.log(f"-> Click ({x:4d}, {y:4d}){lbl_text} (dừng {wait_time:.2f}s, chờ {eff_delay:.1f}s)")

        for c_idx in range(num_clicks):
            self.check_hotkeys()
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.08)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            if c_idx < num_clicks - 1:
                time.sleep(max(0.08, 0.15 * eff_mult))

        start_t = time.time()
        while time.time() - start_t < eff_delay:
            self.check_hotkeys()
            time.sleep(0.06)

    def spam_click(self, x, y, count=6, interval=0.12, label=None):
        """Spam click liên tục dứt khoát tại 1 tọa độ."""
        self.check_hotkeys()
        self.force_foreground()
        win32api.SetCursorPos((x, y))
        pydirectinput.moveTo(x, y)
        time.sleep(0.15)
        lbl_text = f" [{label}]" if label else ""
        self.log(f"-> Spam click x{count} ({x}, {y}){lbl_text}...")
        for _ in range(count):
            self.check_hotkeys()
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(interval)

    def mouse_drag(self, start_x, start_y, end_x, end_y, steps=15, step_delay=0.02, post_wait=0.4, label=None):
        """Kéo giữ chuột trái từ (start_x, start_y) tới (end_x, end_y) mượt mà để cuộn danh sách."""
        self.check_hotkeys()
        self.force_foreground()
        lbl_text = f" [{label}]" if label else ""
        self.log(f"-> Kéo giữ chuột từ ({start_x}, {start_y}) tới ({end_x}, {end_y}){lbl_text}...")
        win32api.SetCursorPos((start_x, start_y))
        pydirectinput.moveTo(start_x, start_y)
        time.sleep(0.15)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.08)
        try:
            for s in range(1, steps + 1):
                self.check_hotkeys()
                cur_x = int(start_x + (end_x - start_x) * (s / steps))
                cur_y = int(start_y + (end_y - start_y) * (s / steps))
                win32api.SetCursorPos((cur_x, cur_y))
                pydirectinput.moveTo(cur_x, cur_y)
                time.sleep(step_delay)
            time.sleep(0.08)
        finally:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(post_wait)

    def click_coord(self, coord_name, delay=1.5, move_wait=0.28, clicks=1):
        if coord_name not in COORDS:
            self.log(f"[!] Cảnh báo: Tọa độ '{coord_name}' không tồn tại!")
            return
        x, y = COORDS[coord_name]
        self.click(x, y, delay=delay, move_wait=move_wait, label=coord_name, clicks=clicks)

    def press_key(self, key_char, hold=0.18, delay=0.3):
        self.check_hotkeys()
        self.force_foreground()
        pydirectinput.keyDown(key_char)
        time.sleep(hold)
        pydirectinput.keyUp(key_char)
        eff_mult = getattr(self, "delay_multiplier", 1.0)
        if delay > 0:
            time.sleep(delay * eff_mult)

    def press_esc(self, delay=1.5):
        self.check_hotkeys()
        self.force_foreground()
        win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
        time.sleep(0.10)
        win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
        eff_mult = getattr(self, "delay_multiplier", 1.0)
        eff_delay = delay * eff_mult
        self.log(f"-> Phím ESC (chờ {eff_delay:.1f}s)")
        time.sleep(eff_delay)

    def move_forward_continuous(self, seconds=20.0, press_p_interval=0.0):
        """
        Giữ phím W di chuyển thẳng liên tục trong `seconds` giây.
        Nếu `press_p_interval > 0`, xen kẽ bấm phím P bỏ qua cutscene trong lúc giữ W.
        """
        self.check_hotkeys()
        self.force_foreground()
        self.log(f"-> Di chuyển thẳng liên tục (giữ W) trong {seconds:.1f}s...")
        pydirectinput.keyDown("w")
        try:
            start_t = time.time()
            last_p = 0.0
            while time.time() - start_t < seconds:
                if win32api.GetAsyncKeyState(win32con.VK_F11) & 0x8000:
                    pydirectinput.keyUp("w")
                    self.check_hotkeys()
                    self.force_foreground()
                    pydirectinput.keyDown("w")
                else:
                    self.check_hotkeys()
                now = time.time()
                if press_p_interval > 0 and (now - last_p) >= press_p_interval:
                    pydirectinput.keyDown("p")
                    time.sleep(0.06)
                    pydirectinput.keyUp("p")
                    last_p = now
                time.sleep(0.15)
        finally:
            try:
                pydirectinput.keyUp("w")
            except Exception:
                pass
        time.sleep(0.2)

    def move_forward(self, seconds=1.5):
        self.move_forward_continuous(seconds=seconds)

    def find_arrow_portal(self, screen=None):
        """
        Dò tìm Mũi Tên Chỉ Xuống (2 mũi tên hoặc 3 mũi tên) / Trụ sáng Ô Xanh mở ải.
        Trả về: (found, target_x, target_y, score)
        """
        if screen is None:
            screen = self.capture_screen()
        if screen is None:
            return False, 0, 0, 0.0

        h, w = screen.shape[:2]
        # Mở rộng vùng quét: từ 10% đến 95% chiều cao và 10% đến 90% chiều rộng sàn đấu
        roi_y1 = int(h * 0.10)
        roi_y2 = int(h * 0.95)
        roi_x1 = int(w * 0.10)
        roi_x2 = int(w * 0.90)
        roi = screen[roi_y1:roi_y2, roi_x1:roi_x2]

        best_score = 0.0
        best_pos = None

        # Quét lần lượt các mẫu: 2 mũi tên, 3 mũi tên, trụ sáng
        for tpl_name in ["arrow_portal_2", "arrow_portal_3", "tru_sang_mo_ai"]:
            tpl = self.templates.get(tpl_name)
            if tpl is None:
                continue
            # Dải tỷ lệ scale linh hoạt từ xa (0.35) đến gần (1.10)
            for s in [0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 1.0, 1.10]:
                tw = int(tpl.shape[1] * s)
                th = int(tpl.shape[0] * s)
                if tw > roi.shape[1] or th > roi.shape[0] or tw < 15 or th < 15:
                    continue
                resized = cv2.resize(tpl, (tw, th), interpolation=cv2.INTER_AREA)
                res = cv2.matchTemplate(roi, resized, cv2.TM_CCOEFF_NORMED)
                min_v, max_v, min_l, max_l = cv2.minMaxLoc(res)
                if max_v > best_score:
                    best_score = max_v
                    gx = roi_x1 + max_l[0] + tw // 2
                    gy = roi_y1 + max_l[1] + int(th * 0.85)  # Điểm chạm mặt sàn
                    best_pos = (gx, gy)

        if best_score >= 0.48 and best_pos:
            return True, best_pos[0], best_pos[1], best_score
        return False, 0, 0, best_score

    def release_movement_keys(self):
        """Nhả toàn bộ phím di chuyển W, A, S, D."""
        for k in ['w', 'a', 's', 'd']:
            try:
                pydirectinput.keyUp(k)
            except Exception:
                pass

    def step_into_portal(self):
        """
        Quét tìm Mũi Tên Ô Xanh chính diện và bước vào ô trong 1.5s (KHÔNG XOAY CHUỘT).
        Quét đa khung hình (tối đa 4 lần trong 1.0s) để bắt trúng khoảnh khắc phát sáng rực rỡ nhất.
        """
        self.check_hotkeys()
        self.force_foreground()
        self.log("-> Quét tìm Mũi Tên Ô Xanh chính diện (đa khung hình)...")

        found = False
        tx, ty = 0, 0
        best_score = 0.0
        last_screen = None

        for attempt in range(4):
            self.check_hotkeys()
            last_screen = self.capture_screen()
            f, x, y, score = self.find_arrow_portal(last_screen)
            if f and score > best_score:
                found = True
                tx, ty = x, y
                best_score = score
                if best_score >= 0.70:
                    break
            time.sleep(0.20)

        if found:
            w_screen = last_screen.shape[1] if last_screen is not None else 1366
            char_x = int(w_screen * 0.50)
            dx = tx - char_x
            self.log(f"-> Thấy Mũi Tên Ô Xanh tại ({tx}, {ty}), lệch dx={dx}px (score={best_score:.2f})")
            if dx < -40:
                self.log("-> Lệch trái: Bấm [W + A] 1.5s bước vào ô...")
                pydirectinput.keyDown("w")
                pydirectinput.keyDown("a")
                time.sleep(1.5)
                pydirectinput.keyUp("a")
                pydirectinput.keyUp("w")
            elif dx > 40:
                self.log("-> Lệch phải: Bấm [W + D] 1.5s bước vào ô...")
                pydirectinput.keyDown("w")
                pydirectinput.keyDown("d")
                time.sleep(1.5)
                pydirectinput.keyUp("d")
                pydirectinput.keyUp("w")
            else:
                self.log("-> Chính diện: Bấm [W] 1.5s bước thẳng vào ô...")
                self.move_forward(seconds=1.5)
            self.log("[OK] Đã bước vào Ô Xanh!")
            return True
        else:
            self.log("-> Chưa thấy rõ Mũi Tên Ô Xanh: Bấm nhẹ [W] 1.0s tiếp cận sảnh mở...")
            self.move_forward(seconds=1.0)
            return False

    def walk_into_portal(self, max_seconds=6.0):
        """
        Dò tìm Mũi Tên Ô Xanh chính diện và dùng W, A, D bước thẳng vào ô mở ải (KHÔNG XOAY CHUỘT).
        """
        self.check_hotkeys()
        self.force_foreground()
        start_t = time.time()
        w_screen, h_screen = 1366, 768

        try:
            while time.time() - start_t < max_seconds:
                self.check_hotkeys()
                screen = self.capture_screen()
                if screen is not None:
                    h_screen, w_screen = screen.shape[:2]

                found, tx, ty, score = self.find_arrow_portal(screen)

                if not found:
                    # Nếu chưa phát hiện, tiến nhẹ W 0.30s xem có vào tầm nhìn không
                    self.log(f"-> Đang quét Mũi Tên Ô Xanh chính diện (score={score:.2f})...")
                    pydirectinput.keyDown("w")
                    time.sleep(0.30)
                    pydirectinput.keyUp("w")
                    time.sleep(0.08)
                    continue

                char_x = int(w_screen * 0.50)
                char_y = int(h_screen * 0.68)
                dx = tx - char_x
                dy = ty - char_y
                dist = (dx**2 + dy**2) ** 0.5

                self.log(f"-> Thấy Mũi Tên Ô Xanh tại ({tx:4d}, {ty:4d}) | Lệch ngang dx={dx:3d}, dy={dy:3d} (score={score:.2f})")

                # ĐIỀU KIỆN ĐÃ VÀO Ô: Chân nhân vật đã chạm tâm ô
                if dist < 45 or (abs(dx) <= 25 and -35 <= dy <= 20):
                    self.release_movement_keys()
                    self.log("[OK] ĐÃ BƯỚC VÀO TRONG TÂM Ô XANH! Mở ải thành công.")
                    time.sleep(0.5)
                    return True

                # ĐIỀU KHIỂN HƯỚNG BẰNG W, A, D (KHÔNG XOAY CHUỘT)
                keys_to_press = []
                if dy < -20:
                    keys_to_press.append("w")
                elif dy > 25:
                    keys_to_press.append("s")

                if dx < -25:
                    keys_to_press.append("a")
                elif dx > 25:
                    keys_to_press.append("d")

                if not keys_to_press:
                    keys_to_press = ["w"]

                pulse_time = 0.25 if dist > 100 else 0.15
                lbl_keys = "+".join(k.upper() for k in keys_to_press)
                self.log(f"   -> Bấm [{lbl_keys}] trong {pulse_time:.2f}s...")

                for k in keys_to_press:
                    pydirectinput.keyDown(k)
                time.sleep(pulse_time)
                for k in keys_to_press:
                    pydirectinput.keyUp(k)
                time.sleep(0.05)

            self.log("-> Kết thúc thời gian dò mũi tên.")
            return False
        finally:
            self.release_movement_keys()

    def navigate_to_green_zone(self, max_seconds=6.0):
        return self.walk_into_portal(max_seconds=max_seconds)

    def capture_screen(self, bbox=(0, 0, 1366, 768)):
        try:
            self.force_foreground()
            img = ImageGrab.grab(bbox=bbox)
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception:
            return None

    def find_template(self, tpl_name, bbox=(0, 0, 1366, 768), threshold=0.68):
        if tpl_name not in self.templates:
            return False, 0, 0, 0.0

        screen = self.capture_screen(bbox=bbox)
        if screen is None:
            return False, 0, 0, 0.0

        tpl = self.templates[tpl_name]
        if screen.shape[0] < tpl.shape[0] or screen.shape[1] < tpl.shape[1]:
            return False, 0, 0, 0.0

        res = cv2.matchTemplate(screen, tpl, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            cx = bbox[0] + max_loc[0] + tpl.shape[1] // 2
            cy = bbox[1] + max_loc[1] + tpl.shape[0] // 2
            return True, cx, cy, float(max_val)
        return False, 0, 0, float(max_val)

    # --------------------------------------------------------------------------
    # QUÉT POPUP QUẢNG CÁO / THÔNG BÁO Ở SẢNH & TẮT BẰNG DẤU [X]
    # --------------------------------------------------------------------------
    def get_screen_pixel_rgb(self, x, y):
        hdc = 0
        try:
            hdc = win32gui.GetDC(0)
            color = win32gui.GetPixel(hdc, int(x), int(y))
            if color == -1:
                return (0, 0, 0)
            return (color & 0xFF, (color >> 8) & 0xFF, (color >> 16) & 0xFF)
        except Exception:
            return (0, 0, 0)
        finally:
            if hdc:
                try:
                    win32gui.ReleaseDC(0, hdc)
                except Exception:
                    pass

    @staticmethod
    def is_color_close(rgb1, rgb2, tolerance=25):
        return (
            abs(rgb1[0] - rgb2[0]) <= tolerance
            and abs(rgb1[1] - rgb2[1]) <= tolerance
            and abs(rgb1[2] - rgb2[2]) <= tolerance
        )

    def check_and_close_popups(self, max_passes=2):
        """Quét các tọa độ dấu [X] popup 2 lần liên tiếp ngay sau khi vào game thành công."""
        self.check_hotkeys()
        self.force_foreground()
        popup_targets = [
            ("btn_close_popup", [(235, 235, 236), (255, 255, 255), (200, 200, 200)]),
            ("btn_close_x_nho", [(235, 235, 236), (255, 255, 255), (200, 200, 200)]),
        ]
        closed_any = False
        for scan_idx in range(1, max_passes + 1):
            self.log(f"-> Quét Popup Sảnh lần {scan_idx}/{max_passes}...")
            closed_this_pass = False
            for btn_name, target_colors in popup_targets:
                if btn_name not in COORDS:
                    continue
                px, py = COORDS[btn_name]
                current_rgb = self.get_screen_pixel_rgb(px, py)
                if any(self.is_color_close(current_rgb, t_rgb, tolerance=25) for t_rgb in target_colors):
                    self.log(f"[Popup Sảnh] Phát hiện dấu [X] tại [{btn_name}] ({px}, {py}) RGB={current_rgb} -> Bấm tắt!")
                    self.click(px, py, delay=0.9, move_wait=0.25, label=f"Tắt Popup {btn_name}", clicks=1)
                    closed_any = True
                    closed_this_pass = True
                    break
            if not closed_this_pass and scan_idx < max_passes:
                time.sleep(0.4)
        return closed_any

    # --------------------------------------------------------------------------
    # CUỘN DANH SÁCH NHÂN VẬT (CHỈ DÙNG CHO CÁC SLOT ĐÁY >= 8)
    # --------------------------------------------------------------------------
    def scroll_char_list_to_bottom(self):
        # BỎ HOÀN TOÀN CUỘN CHUỘT THEO YÊU CẦU: Giữ nguyên vị trí cố định để tránh lệch tọa độ
        self.log("-> [Bỏ Cuộn Chuột] Giữ nguyên vị trí danh sách nhân vật cố định.")
        return

    # --------------------------------------------------------------------------
    # MỞ MENU & CHỌN NHÂN VẬT
    # --------------------------------------------------------------------------
    def open_char_select_from_lobby(self):
        self.force_foreground()
        self.click_coord("btn_menu", delay=1.5, move_wait=0.20)
        self.click_coord("btn_cai_dat_gear", delay=1.6, move_wait=0.20)
        self.click_coord("btn_doi_nhan_vat", delay=4.8, move_wait=0.24)

    def open_char_select_from_dungeon(self):
        self.force_foreground()
        self.press_esc(delay=1.4)
        self.click_coord("btn_cai_dat_gear", delay=1.6, move_wait=0.20)
        self.click_coord("btn_doi_nhan_vat", delay=4.8, move_wait=0.24)

    # --------------------------------------------------------------------------
    # CƠ CHẾ ĐỔI NHÂN VẬT CHUẨN XÁC (HỖ TRỢ >= 11 NV VÀ < 11 NV, KHÔNG CUỘN CHUỘT)
    # --------------------------------------------------------------------------
    def _resolve_slot_coord_key(self, slot_num, total_chars, is_direct_test=False):
        """
        Quy đổi (slot_num, total_chars) -> (coord_key, description) không cuộn chuột:
        - >= 11 NV: Slot 1 -> slot_1; Slot 2..7 -> slot_2 (thay thế); Slot 8..12 -> slot_8..slot_12.
        - 6..10 NV: Slot 1 -> slot_1; Slot 2..(total-4) -> slot_2 (thay thế);
                    4 slot cuối (total-3..total) -> slot_8..slot_11.
        - <= 5 NV : Bấm trực tiếp slot_1..slot_5.
        """
        if is_direct_test:
            coord_key = f"slot_{slot_num}" if f"slot_{slot_num}" in COORDS else f"slot_{min(6, max(1, slot_num))}"
            x, y = COORDS[coord_key]
            return coord_key, f"Test Trực Tiếp: Bấm ô {coord_key} ({x}, {y}) [CỐ ĐỊNH, KHÔNG CUỘN]"

        if total_chars >= 11:
            if slot_num == 1:
                return "slot_1", f"Slot 1/{total_chars}: Bấm đầu danh sách (CỐ ĐỊNH, KHÔNG CUỘN)"
            if 2 <= slot_num <= 7:
                return "slot_2", f"Slot {slot_num}/{total_chars}: Thay thế vị trí -> Bấm slot_2 (KHÔNG CUỘN)"
            idx = max(8, min(12, slot_num))
            coord_key = f"slot_{idx}"
            return coord_key, f"Slot {slot_num}/{total_chars}: Vị trí cố định -> Bấm {coord_key} (KHÔNG CUỘN)"

        if total_chars >= 6:
            if slot_num == 1:
                return "slot_1", f"Slot 1/{total_chars}: Bấm đầu danh sách (CỐ ĐỊNH, KHÔNG CUỘN)"
            bottom_start = total_chars - 3
            if slot_num < bottom_start:
                return "slot_2", f"Slot {slot_num}/{total_chars} (Acc < 11, nhóm thay thế 2..{bottom_start - 1}): Bấm slot_2 (KHÔNG CUỘN)"
            mapped_idx = max(8, min(11, 8 + (slot_num - bottom_start)))
            coord_key = f"slot_{mapped_idx}"
            return coord_key, f"Slot {slot_num}/{total_chars} (Acc < 11): Ánh xạ cố định -> Bấm {coord_key} (KHÔNG CUỘN)"

        safe_slot = max(1, min(6, slot_num))
        coord_key = f"slot_{safe_slot}"
        return coord_key, f"Slot {slot_num}/{total_chars}: Bấm trực tiếp {coord_key} (KHÔNG CUỘN)"

    def switch_to_slot(self, slot_num, total_chars=12, from_screen="lobby", is_direct_test=False):
        self.log(f"\n=== [ĐỔI NHÂN VẬT: SLOT {slot_num}/{total_chars}] ===")

        if from_screen == "lobby":
            self.open_char_select_from_lobby()
        elif from_screen == "dungeon":
            self.open_char_select_from_dungeon()
        else:
            self.log("-> Đang ở sẵn màn hình Chọn Nhân Vật.")

        coord_key, desc = self._resolve_slot_coord_key(slot_num, total_chars, is_direct_test=is_direct_test)
        x, y = COORDS[coord_key]

        self.log(f"-> Thao tác: {desc}")
        self.log("-> Giữ nguyên danh sách nhân vật cố định, TUYỆT ĐỐI KHÔNG CUỘN CHUỘT!")

        # Bấm chọn ô nhân vật
        self.click(x, y, delay=1.2, move_wait=0.28, label=f"Chọn Slot {slot_num}")

        # Bấm [VÀO GAME]
        self.click_coord("btn_vao_game", delay=7.5, move_wait=0.25, clicks=2)
        self.log(f"[OK] Đã chọn và đang tải vào nhân vật Slot {slot_num} (chờ 5.5s ổn định sảnh)...")
        time.sleep(5.5)
        self.force_foreground()
        self.click(683, 720, delay=0.40, move_wait=0.10, label="Kích hoạt chuột Sảnh", clicks=1)
        self.check_and_close_popups()

    def reload_current_char_to_lobby(self):
        """Thoát ải về sảnh bằng cách re-login trực tiếp nhân vật hiện tại (không bấm slot)."""
        self.log("\n-> Thoát về sảnh: Bấm [VÀO GAME] ngay nhân vật đang đứng sẵn (BỎ CHỌN SLOT)...")
        self.open_char_select_from_dungeon()

        # BỎ CLICK SLOT: Màn hình chọn nhân vật đã tự động chọn sẵn nhân vật này, chỉ bấm [VÀO GAME]
        self.click_coord("btn_vao_game", delay=7.5, move_wait=0.25, clicks=2)
        self.log("[OK] Đã về lại Sảnh Chính (chờ 5.5s ổn định sảnh)...")
        time.sleep(5.5)
        self.force_foreground()
        self.click(683, 720, delay=0.40, move_wait=0.10, label="Kích hoạt chuột Sảnh", clicks=1)
        self.check_and_close_popups()

    def exit_dungeon_to_lobby(self):
        """Alias tương thích."""
        return self.reload_current_char_to_lobby()

    # --------------------------------------------------------------------------
    # KIỂM TRA BẢNG GHÉP VÀ ĐẾM SỐ LƯỢNG NGƯỜI (DƯỚI 4 TỪ CHỐI, ĐỦ 4 VÀO NGAY)
    # --------------------------------------------------------------------------
    def is_match_popup_open(self, screen):
        """Kiểm tra bảng Chuẩn Bị Chiến Đấu đã nảy lên chưa bằng cách nhận diện nút [CHUẨN BỊ] màu xanh."""
        if screen is None:
            return False
        try:
            if screen.shape[1] != 1366 or screen.shape[0] != 768:
                screen = cv2.resize(screen, (1366, 768))
            # Vùng nút [CHUẨN BỊ] (x: 780..960, y: 580..650)
            btn_chuan_bi = screen[580:650, 780:960]
            b = btn_chuan_bi[:, :, 0]
            g = btn_chuan_bi[:, :, 1]
            r = btn_chuan_bi[:, :, 2]
            blue_count = np.count_nonzero((b > 170) & (b > r * 1.3) & (g > 70))
            return blue_count > 1500
        except Exception:
            return False

    def count_ready_players(self, screen):
        """
        Đếm số lượng thành viên trong bảng Chuẩn Bị Chiến Đấu:
        - Slot 1: Luôn là người chơi (1 người).
        - Slot 2, 3, 4: Quét dải màu xanh lá cây Sẵn Sàng (y: 320..450).
        Tự động chuẩn hóa kích thước về 1366x768 chuẩn xác 100%.
        """
        try:
            if screen.shape[1] != 1366 or screen.shape[0] != 768:
                screen = cv2.resize(screen, (1366, 768))

            crop = screen[320:450, 500:1050]
            hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
            green_mask = cv2.inRange(hsv, (35, 80, 80), (85, 255, 255))

            # Slot 2 (x: 570..690 -> trong crop: 70..190)
            s2 = np.count_nonzero(green_mask[:, 70:190]) >= 400
            # Slot 3 (x: 720..840 -> trong crop: 220..340)
            s3 = np.count_nonzero(green_mask[:, 220:340]) >= 400
            # Slot 4 (x: 870..990 -> trong crop: 370..490)
            s4 = np.count_nonzero(green_mask[:, 370:490]) >= 400

            total = 1 + (1 if s2 else 0) + (1 if s3 else 0) + (1 if s4 else 0)
            return total
        except Exception:
            return 1

    def handle_ready_after_matchmaking(self):
        """
        BỎ HOÀN TOÀN CẢNH BÁO ĐỎ:
        1. Chờ bảng "CHUẨN BỊ CHIẾN ĐẤU" xuất hiện (tối đa 12s, kiểm tra liên tục mỗi 0.35s).
        2. Khi bảng xuất hiện:
           - Đếm số lượng người trong phòng:
             + Nếu ĐỦ 4 NGƯỜI (1 Người + 3 Bot) -> Spam click [CHUẨN BỊ] (872, 615) 8 lần liên tiếp dứt khoát!
             + Nếu DƯỚI 4 NGƯỜI (< 4 người) -> Bấm [TỪ CHỐI] (532, 615) để hủy và ghép lại ngay!
        """
        self.log("-> Đang chờ bảng ghép [Chuẩn Bị Chiến Đấu] xuất hiện...")
        popup_found = False
        start_time = time.time()

        # Vòng lặp chờ bảng nảy lên tối đa 11s
        while time.time() - start_time < 11.0:
            self.check_hotkeys()
            screen = self.capture_screen((0, 0, 1366, 768))
            if self.is_match_popup_open(screen):
                popup_found = True
                self.log(f"-> [OK] Bảng Chuẩn Bị đã xuất hiện sau {time.time() - start_time:.1f}s!")
                break
            time.sleep(0.25)

        if not popup_found:
            self.log("[!] Hết 11s chưa thấy bảng Chuẩn Bị xuất hiện (đang tìm trận hoặc bị lag).")
            return False

        # Cho thêm 0.3s để các thẻ Bot ổn định
        time.sleep(0.3)
        screen = self.capture_screen((0, 0, 1366, 768))
        total_players = self.count_ready_players(screen)
        self.log(f"-> Quét số lượng người trong phòng: {total_players}/4 thành viên")

        # Nếu chưa đủ 4, chờ thêm 0.45s quét lại lần 2 tránh trường hợp thẻ tải chậm
        if total_players < 4:
            time.sleep(0.45)
            screen2 = self.capture_screen((0, 0, 1366, 768))
            if screen2 is not None:
                total_players = self.count_ready_players(screen2)
                self.log(f"-> Quét lại lần 2: {total_players}/4 thành viên (đã trừ hao tải chậm)")

        # TRƯỜNG HỢP 1: DƯỚI 4 NGƯỜI -> BẤM TỪ CHỐI ĐỂ GHÉP LẠI!
        if total_players < 4:
            self.log(f"-> [THIẾU NGƯỜI: Chỉ có {total_players}/4] Bấm [TỪ CHỐI] (532, 615) để ghép lại với Bot...")
            self.click(COORDS["btn_tu_choi"][0], COORDS["btn_tu_choi"][1], delay=1.4, move_wait=0.28, label="Bấm Từ Chối")
            return False

        # TRƯỜNG HỢP 2: ĐỦ 4 NGƯỜI (1 NGƯỜI + 3 BOT HOÀN HẢO) -> BẤM CHUẨN BỊ NGAY!
        self.log("-> [ĐỦ 4 NGƯỜI - 3 BOT SẴN SÀNG] Spam click [CHUẨN BỊ] (872, 615) vào trận ngay!")
        self.spam_click(COORDS["btn_chuan_bi"][0], COORDS["btn_chuan_bi"][1], count=8, interval=0.08, label="Spam Chuẩn Bị")
        time.sleep(0.35)

        # Click thêm xác nhận
        self.click(COORDS["btn_chuan_bi"][0], COORDS["btn_chuan_bi"][1], delay=2.8, move_wait=0.28, label="Xác nhận Chuẩn Bị")
        return True

    def _matchmake_stage_with_reset(self, stage_name, open_team_fn, max_cycles=4, max_declines=3):
        """
        Ghép cặp Bot 4 người với cơ chế ẩn chống văng:
        - Trong mỗi lượt vào ải, thử ghép tối đa `max_declines` (3) lần.
        - Nếu bị từ chối / ghép trượt đủ 3 lần: bấm ESC thoát ra ngoài rồi thao tác
          vào lại ải từ đầu (tránh từ chối > 3 lần bị game văng ra màn hình ngoài).
        """
        for cycle in range(1, max_cycles + 1):
            self.check_hotkeys()
            if cycle > 1:
                self.log(f"\n-> [Vào lại {stage_name} - Vòng {cycle}/{max_cycles}] Thao tác vào ải lại như bình thường...")

            open_team_fn()

            for attempt in range(1, max_declines + 1):
                self.check_hotkeys()
                if attempt > 1:
                    self.log(f"-> [Ghép lại lần {attempt}/{max_declines}] Bấm [Ghép Cặp Nhanh]...")
                self.click_coord("btn_ghep_cap_nhanh", delay=1.2, move_wait=0.28)

                if self.handle_ready_after_matchmaking():
                    return True

                if attempt < max_declines:
                    self.log(f"-> Chờ 1.2s rồi bấm [Ghép Cặp Nhanh] lại (đã trượt/từ chối {attempt}/{max_declines} lần)...")
                    time.sleep(1.2)
                else:
                    self.log(f"-> [Đã từ chối {max_declines} lần - {stage_name}] Bấm ESC 1 lần thoát ra ngoài để thao tác vào lại ải...")
                    self.press_esc(delay=1.4)
                    time.sleep(0.8)

        self.log(f"[!] Không ghép được 4 Bot {stage_name} sau {max_cycles} vòng ({max_cycles * max_declines} lần).")
        return False

    def _open_chinh_phat_team(self):
        self.click_coord("btn_menu_chien_dau", delay=1.8, move_wait=0.30)
        self.click_coord("btn_khieu_chien", delay=1.7, move_wait=0.28)
        self.click_coord("tab_chinh_phat_gioi_han", delay=1.6, move_wait=0.28)
        self.click_coord("tab_boss_3", delay=1.6, move_wait=0.28)
        self.click_coord("btn_nhan_doi_qua", delay=1.5, move_wait=0.28)
        self.click_coord("btn_lap_doi_chinh_phat", delay=2.0, move_wait=0.32)

    def _open_nguc_toi_team(self):
        self.click_coord("btn_menu_chien_dau", delay=1.8, move_wait=0.30)
        self.click_coord("tab_tham_hiem", delay=1.7, move_wait=0.28)
        self.click_coord("btn_nhan_doi_qua_nguc", delay=1.5, move_wait=0.28)
        self.click_coord("btn_khieu_chien_nhom", delay=2.0, move_wait=0.32)

    # --------------------------------------------------------------------------
    # ĐI ẢI CHINH PHẠT (QUY TRÌNH ĐẦY ĐỦ GHÉP VỚI BOT 4 NGƯỜI)
    # --------------------------------------------------------------------------
    def run_chinh_phat_once(self):
        self.log("\n=== [ĐI ẢI CHINH PHẠT: GHÉP VỚI BOT 4 NGƯỜI] ===")
        if not self._matchmake_stage_with_reset("Chinh Phạt", self._open_chinh_phat_team):
            return False

        self.log("-> Đang load vào ải Chinh Phạt (chờ 5.0s & bấm P skip cutscene)...")
        time.sleep(5.0)
        # Bấm P liên tục bỏ qua cutscene mở màn sớm
        for _ in range(8):
            self.check_hotkeys()
            self.press_key('p', hold=0.07, delay=0.15)

        # 1. Đi thẳng bằng W 2s
        self.log("-> Đi thẳng bằng W 2.0s tiếp cận sảnh đấu...")
        self.move_forward(seconds=2.0)

        # 2. Sau đó quét tìm Mũi Tên Ô Xanh và bước vào ô
        self.step_into_portal()

        # Kéo dài thời gian chờ đồng đội / Bot hạ Boss dứt điểm (chờ 24s)
        self.log("-> Đang trong ải: Dừng chạy, chờ đồng đội / Bot hạ gục Boss (24s)...")
        for _ in range(24):
            self.check_hotkeys()
            self.press_key('p', hold=0.05, delay=0.10)
            time.sleep(0.9)

        self.log("-> Spam click tắt bảng phần thưởng / Rank S nhanh dứt khoát...")
        self.spam_click(683, 720, count=25, interval=0.07, label="Spam tắt thưởng/Rank S")
        time.sleep(1.0)

        self.reload_current_char_to_lobby()
        return True

    # --------------------------------------------------------------------------
    # ĐI ẢI NGỤC TỐI (QUY TRÌNH ĐẦY ĐỦ GHÉP VỚI BOT 4 NGƯỜI)
    # --------------------------------------------------------------------------
    def run_nguc_toi_once(self):
        self.log("\n=== [ĐI ẢI NGỤC TỐI: GHÉP VỚI BOT 4 NGƯỜI] ===")
        if not self._matchmake_stage_with_reset("Ngục Tối", self._open_nguc_toi_team):
            return False

        self.log("-> Đang load vào ải Ngục Tối (chờ 9.0s ổn định màn hình)...")
        time.sleep(9.0)

        # Di chuyển W tới trước 2.5s rồi chờ đồng đội / Bot hạ Boss (giữ nguyên gốc)
        self.move_forward(seconds=2.5)

        self.log("-> Đang trong ải: Kéo dài thời gian chờ đồng đội / Bot hạ gục Boss (32s)...")
        for _ in range(32):
            self.check_hotkeys()
            time.sleep(1.0)

        self.log("-> Spam click tắt bảng phần thưởng nhanh dứt khoát...")
        self.spam_click(683, 720, count=25, interval=0.07, label="Spam tắt thưởng Ngục")
        time.sleep(1.0)

        self.reload_current_char_to_lobby()
        return True

    # --------------------------------------------------------------------------
    # TÍNH NĂNG VẬT PHẨM: MUA 2 HỘP TINH THỂ, DÙNG VÉ SẠP, VÉ MẬT, CHÌA RAID
    # --------------------------------------------------------------------------
    def open_bag_consumables(self):
        self.log("-> Mở Túi Đồ bằng phím B...")
        self.force_foreground()
        self.press_key('b', hold=0.20, delay=2.2)
        self.log("-> Chọn ô thứ 4: Tab Bình Thuốc (Tiêu Hao) tại (1285, 79)...")
        self.click_coord("tab_tieu_hao_bag", delay=1.8, move_wait=0.35, clicks=1)

    def close_bag(self):
        self.log("-> Đóng Túi Đồ về Sảnh (bấm phím B)...")
        self.press_key('b', hold=0.15, delay=1.5)

    def run_mua_hop_tinh_the(self, box_type="Hộp 1", plus_clicks=12):
        """
        Vào Cửa Hàng (1155, 86) -> Đổi Điểm (96, 562).
        box_type: 'Hộp 1', 'Hộp 2', 'Cả 2', hoặc 'Tắt'.
        Mặc định bấm [+] 12 lần.
        """
        if str(box_type).strip() in ["Tắt", "Không", "None", "0"]:
            self.log("-> Mua Hộp Tinh Thể: Đã chọn Tắt (Bỏ qua).")
            return

        self.log(f"\n=== VÀO CỬA HÀNG MUA HỘP TINH THỂ KỲ DỊ ({box_type}) ===")
        self.force_foreground()
        time.sleep(0.4)
        self.log("-> Bước 1: Mở Cửa Hàng (1155, 86)...")
        self.click_coord("btn_cua_hang", delay=2.2, move_wait=0.30)
        self.log("-> Bước 2: Bấm mục [Đổi Điểm] (96, 562)...")
        self.click_coord("btn_doi_diem", delay=1.8, move_wait=0.28)

        do_box1 = box_type in ["Hộp 1", "Cả 2", "1", "both"]
        do_box2 = box_type in ["Hộp 2", "Cả 2", "2", "both"]

        # Mua Hộp 1
        if do_box1:
            self.log("-> Chọn Hộp Tinh Thể 1 (477, 224)...")
            self.click_coord("hop_the_ky_di_1", delay=1.4, move_wait=0.25)
            self.log(f"   + Bấm [+] tăng số lượng ({plus_clicks} lần)...")
            self.spam_click(COORDS["btn_tang_hop_the"][0], COORDS["btn_tang_hop_the"][1], count=plus_clicks, interval=0.08)
            time.sleep(0.4)
            self.log("   + Bấm [Mua] (1118, 736)...")
            self.click_coord("btn_bam_mua_hop_the", delay=1.5, move_wait=0.22)
            self.log("   + Bấm [Xác Nhận] Mua Hộp 1 (891, 524)...")
            self.click_coord("btn_xac_nhan_mua_hop", delay=1.8, move_wait=0.25)
            self.log("   + Bấm ESC đóng bảng mua Hộp 1...")
            self.press_esc(delay=1.5)
            time.sleep(0.4)

        # Mua Hộp 2
        if do_box2:
            self.log("-> Chọn Hộp Tinh Thể 2 (751, 241)...")
            self.click_coord("hop_the_ki_di_2", delay=1.4, move_wait=0.25)
            self.log(f"   + Bấm [+] tăng số lượng ({plus_clicks} lần)...")
            self.spam_click(COORDS["btn_tang_hop_the"][0], COORDS["btn_tang_hop_the"][1], count=plus_clicks, interval=0.08)
            time.sleep(0.4)
            self.log("   + Bấm [Mua] (1118, 736)...")
            self.click_coord("btn_bam_mua_hop_the", delay=1.5, move_wait=0.22)
            self.log("   + Bấm [Xác Nhận] Mua Hộp 2 (891, 524)...")
            self.click_coord("btn_xac_nhan_mua_hop", delay=1.8, move_wait=0.25)
            self.log("   + Bấm ESC đóng bảng mua Hộp 2...")
            self.press_esc(delay=1.2)
            time.sleep(0.4)

        # Thoát Cửa Hàng về sảnh
        self.log(f"-> Mua xong {box_type}, bấm ESC thoát Cửa Hàng về Sảnh...")
        time.sleep(0.5)
        self.press_esc(delay=1.6)
        self.log(f"[OK] Đã hoàn thành Mua Hộp Tinh Thể ({box_type})!")

    def run_mua_2_hop_tinh_the(self, plus_clicks=12):
        self.run_mua_hop_tinh_the(box_type="Cả 2", plus_clicks=plus_clicks)

    def _click_dung_button(self, item_x, delay=1.5, label="Bấm DÙNG"):
        """
        Tìm và bấm chính xác nút xanh [DÙNG] trong tooltip vật phẩm mở ra bên trái ô item_x.
        Ưu tiên template 'btn_dung', dự phòng nhận diện vùng màu xanh dương của nút [DÙNG].
        """
        x1 = max(250, int(item_x) - 420)
        x2 = min(1360, int(item_x) + 15)
        search_bbox = (x1, 80, x2, 765)

        found_dung, dx, dy, score = self.find_template("btn_dung", bbox=search_bbox, threshold=0.65)
        if found_dung:
            self.log(f"-> Tìm thấy nút [DÙNG] tại ({dx}, {dy}) (score={score:.2f})")
            self.click(dx, dy, delay=delay, label=label)
            return True

        sub = self.capture_screen(bbox=search_bbox)
        if sub is not None:
            b, g, r = sub[:, :, 0], sub[:, :, 1], sub[:, :, 2]
            blue_mask = (b > 195) & (r < 105) & (g > 95)
            if np.count_nonzero(blue_mask) >= 450:
                ys, xs = np.where(blue_mask)
                dx = x1 + int(np.median(xs))
                dy = 80 + int(np.median(ys))
                self.log(f"-> Nhận diện màu nút [DÙNG] tại ({dx}, {dy})")
                self.click(dx, dy, delay=delay, label=label)
                return True

        self.log(f"[!] Không tìm thấy nút [DÙNG] cạnh item x={item_x} (score={score:.2f}).")
        return False

    def _find_dat_ve_button(self):
        """Tìm nút vàng [NHẤN GIỮ ĐỂ ĐẶT] trong bảng Mất Vé Mật."""
        found_dv, vx, vy, score = self.find_template("btn_dat_ve", bbox=(500, 400, 1100, 700), threshold=0.60)
        if found_dv:
            return vx, vy

        bbox = (620, 440, 1060, 680)
        sub = self.capture_screen(bbox=bbox)
        if sub is not None:
            b, g, r = sub[:, :, 0], sub[:, :, 1], sub[:, :, 2]
            gold_mask = (r > 195) & (g > 130) & (g < 225) & (b < 85)
            if np.count_nonzero(gold_mask) >= 800:
                ys, xs = np.where(gold_mask)
                return bbox[0] + int(np.median(xs)), bbox[1] + int(np.median(ys))

        return 830, 545

    def run_mo_hop_doi_chia(self, keys_map=None):
        """
        Quy trình mở Hộp Tinh Thể trong Túi Đồ để đổi 8 loại Chìa Khóa Raid:
        1. Bấm B mở Túi Đồ -> chọn Tab Tiêu Hao (1303, 72)
        2. Nhận diện ô Hộp Tinh Thể bằng template matching (hoặc tọa độ mặc định)
        3. Bấm nút [DÙNG] / [MỞ NHIỀU] (1109, 571)
        4. Trong bảng Chọn Thưởng: Bấm [+] cho từng loại chìa khóa theo cấu hình
        5. Bấm [Đổi Chìa] (813, 631) -> Bấm [Xác Nhận Đổi Chìa] (854, 528)
        6. Bấm ESC đóng bảng thưởng -> Bấm B đóng Túi Đồ về Sảnh.
        """
        self.log("\n=== MỞ HỘP TINH THỂ ĐỔI 8 CHÌA KHÓA RAID ===")
        self.open_bag_consumables()
        time.sleep(0.5)

        # 1. Tìm ô Hộp Tinh Thể trong túi đồ
        self.log("-> Quét tìm [Hộp Tinh Thể] trong Tab Tiêu Hao...")
        found, bx, by, score = self.find_template("hop_tinh_the", bbox=(960, 100, 1360, 710), threshold=0.62)
        if not found:
            self.log("-> Chưa thấy ở trang 1, cuộn nhẹ chuột tìm tiếp...")
            self.force_foreground()
            win32api.SetCursorPos((1150, 400))
            for _ in range(5):
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -120, 0)
                time.sleep(0.04)
            time.sleep(0.6)
            found, bx, by, score = self.find_template("hop_tinh_the", bbox=(960, 100, 1360, 710), threshold=0.62)

        if found:
            self.log(f"-> Tìm thấy Hộp Tinh Thể tại ({bx}, {by}) (score={score:.2f})")
            self.click(bx, by, delay=1.0, move_wait=0.25, label="Chọn Hộp Tinh Thể")
        else:
            self.log(f"-> Không khớp ảnh (score={score:.2f}), click vào ô mặc định (1239, 213)...")
            bx, by = 1239, 213
            self.click(bx, by, delay=1.0, move_wait=0.25, label="Chọn Hộp Tinh Thể mặc định")

        # 2. Bấm nút [MỞ NHIỀU] trên tooltip Hộp Tinh Thể Kỳ Dị để vào giao diện lấy chìa khóa
        time.sleep(0.6)
        self.log("-> Đang tìm và bấm nút [MỞ NHIỀU] trên bảng Hộp Tinh Thể...")
        found_mn, mx, my, score_mn = self.find_template("btn_mo_nhieu", bbox=(800, 450, 1366, 768), threshold=0.65)
        if found_mn:
            self.log(f"-> Nhận diện chính xác nút [MỞ NHIỀU] tại ({mx}, {my}) (score={score_mn:.2f})")
            self.click(mx, my, delay=2.0, move_wait=0.25, label="Bấm Mở Nhiều")
        else:
            self.log("-> Bấm nút [MỞ NHIỀU] theo tọa độ chuẩn (1128, 661)...")
            self.click(1128, 661, delay=2.0, move_wait=0.25, label="Bấm Mở Nhiều (1128, 661)", clicks=2)

        time.sleep(0.8)
        self.log("-> Bảng [CHỌN THƯỞNG] đã mở: Tiến hành đổi 8 loại chìa khóa...")

        keys_row1 = [
            ("l8", "Chìa L8", (425, 422)),
            ("t8", "Chìa T8", (584, 425)),
            ("s8", "Chìa S8", (733, 424)),
            ("h4", "Chìa H4", (889, 425)),
            ("k8", "Chìa K8", (1043, 425)),
        ]
        keys_row2 = [
            ("d8", "Chìa D8", (428, 496)),
            ("q8", "Chìa Q8", (580, 495)),
            ("v8", "Chìa V8", (736, 496)),
        ]

        # 2a. Bấm tăng số lượng các chìa Hàng 1
        self.log("-> Đổi chìa Hàng 1 (L8, T8, S8, H4, K8)...")
        for k_id, k_name, coord in keys_row1:
            self.check_hotkeys()
            cnt = 3
            if keys_map and k_id in keys_map:
                try:
                    cnt = int(keys_map[k_id])
                except Exception:
                    cnt = 3
            if cnt > 0:
                self.log(f"   + Bấm {cnt} lần nút [+] [{k_name}] ({coord[0]}, {coord[1]})...")
                self.spam_click(coord[0], coord[1], count=cnt, interval=0.10, label=f"Tăng {k_name}")
                time.sleep(0.2)

        # 2b. Nắm giữ chuột ở giữa danh sách kéo lên để hiển thị Hàng 2 (D8, Q8, V8)
        self.log("-> Nắm giữ chuột ở giữa danh sách kéo lên để hiển thị hàng chìa D8, Q8, V8...")
        self.mouse_drag(start_x=683, start_y=540, end_x=683, end_y=360, steps=15, step_delay=0.02, post_wait=0.4, label="Kéo cuộn bảng chìa khóa")
        # Cuộn nhẹ thêm con lăn để đảm bảo danh sách đã chạm đáy
        self.force_foreground()
        win32api.SetCursorPos((683, 450))
        for _ in range(3):
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -120, 0)
            time.sleep(0.04)
        time.sleep(0.4)

        # 2c. Bấm tăng số lượng các chìa Hàng 2
        self.log("-> Đổi chìa Hàng 2 (D8, Q8, V8)...")
        for k_id, k_name, coord in keys_row2:
            self.check_hotkeys()
            cnt = 3
            if keys_map and k_id in keys_map:
                try:
                    cnt = int(keys_map[k_id])
                except Exception:
                    cnt = 3
            if cnt > 0:
                self.log(f"   + Bấm {cnt} lần nút [+] [{k_name}] ({coord[0]}, {coord[1]})...")
                self.spam_click(coord[0], coord[1], count=cnt, interval=0.10, label=f"Tăng {k_name}")
                time.sleep(0.2)

        # 3. Bấm [ĐỔI CHÌA] (813, 631)
        self.log("-> Bấm nút [Đổi Chìa] (813, 631)...")
        self.click_coord("btn_doi_chia", delay=1.5, move_wait=0.25)

        # 4. Bấm [XÁC NHẬN ĐỔI CHÌA] (854, 528)
        self.log("-> Bấm nút [Xác Nhận Đổi Chìa] (854, 528)...")
        self.click_coord("btn_xac_nhan_doi_chia", delay=1.8, move_wait=0.25)

        # 5. Thoát giao diện về Sảnh
        self.log("-> Bấm ESC đóng bảng thông báo nhận chìa...")
        self.press_esc(delay=1.2)
        time.sleep(0.4)
        self.close_bag()
        self.log("[OK] Đã hoàn thành Mở Hộp Đổi 8 Chìa Khóa Raid!")
        return True

    def run_use_keys(self, keys_map=None):
        """
        Quy trình Dùng / Mở 8 loại Chìa Khóa Raid trong Túi Đồ:
        1. Bấm B mở Túi Đồ -> Chọn Tab Tiêu Hao (1303, 72).
        2. Duyệt qua 8 loại chìa: L8, T8, S8, H4, K8, D8, Q8, V8.
        3. Với mỗi chìa:
           - Quét tìm ảnh template chìa trong vùng Túi Đồ bbox=(960, 100, 1360, 710).
           - Nếu trang 1 chưa có, cuộn nhẹ chuột tìm tiếp.
           - Nếu tìm thấy: Click vào ô chìa khóa.
           - Bấm nút [DÙNG] trong bảng thông tin bên trái (mặc định 3 lần/chìa).
        4. Bấm ESC / B đóng Túi Đồ về Sảnh an toàn.
        """
        self.log("\n=== DÙNG / MỞ 8 CHÌA KHÓA RAID TRONG TÚI ĐỒ ===")
        self.open_bag_consumables()
        time.sleep(0.5)

        keys_list = [
            ("key_l8", "Chìa L8"),
            ("key_t8", "Chìa T8"),
            ("key_s8", "Chìa S8"),
            ("key_h4", "Chìa H4"),
            ("key_k8", "Chìa K8"),
            ("key_d8", "Chìa D8"),
            ("key_q8", "Chìa Q8"),
            ("key_v8", "Chìa V8"),
        ]

        for k_id, k_name in keys_list:
            self.check_hotkeys()
            cnt = 3
            if keys_map:
                short_k = k_id.replace("key_", "")
                if k_id in keys_map:
                    try:
                        cnt = int(keys_map[k_id])
                    except Exception:
                        cnt = 3
                elif short_k in keys_map:
                    try:
                        cnt = int(keys_map[short_k])
                    except Exception:
                        cnt = 3

            if cnt <= 0:
                continue

            self.log(f"\n-> Kiểm tra [{k_name}] (mục tiêu mở: {cnt} lần)...")
            # Đảm bảo danh sách ở đầu trang
            self.click_coord("tab_tieu_hao", delay=0.8, move_wait=0.20)

            # Quét tìm ô chìa khóa
            found, kx, ky, score = self.find_template(k_id, bbox=(960, 100, 1360, 710), threshold=0.65)
            if not found:
                # Cuộn nhẹ chuột xuống tìm tiếp
                self.force_foreground()
                win32api.SetCursorPos((1150, 400))
                for _ in range(5):
                    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -120, 0)
                    time.sleep(0.04)
                time.sleep(0.5)
                found, kx, ky, score = self.find_template(k_id, bbox=(960, 100, 1360, 710), threshold=0.65)

            if not found:
                self.log(f"   [!] Không thấy [{k_name}] trong Túi Đồ (score={score:.2f}). Bỏ qua loại chìa này.")
                continue

            self.log(f"   -> Tìm thấy [{k_name}] tại ({kx}, {ky}) (score={score:.2f})")

            # Mở cnt lần (màn hình Túi Đồ giữ nguyên, không đóng mở lại)
            for open_idx in range(cnt):
                self.check_hotkeys()
                self.log(f"   + Lần {open_idx + 1}/{cnt}: Chọn [{k_name}] ({kx}, {ky})...")
                self.click(kx, ky, delay=0.7, move_wait=0.20, label=f"Chọn {k_name}")

                # 1. Bấm nút [DÙNG] trong tooltip bên trái
                used = self._click_dung_button(kx, delay=1.0, label=f"Bấm DÙNG {k_name} ({open_idx+1}/{cnt})")
                if not used:
                    self.log(f"   [!] Thử click lại ô ({kx}, {ky})...")
                    self.click(kx, ky, delay=0.7, move_wait=0.20, label=f"Chọn lại {k_name}")
                    used = self._click_dung_button(kx, delay=1.0, label=f"Bấm DÙNG lại {k_name}")
                    if not used:
                        self.log(f"   [!] Không tìm thấy nút [DÙNG]. Dừng mở chìa này.")
                        break

                # 2. Bấm nút [Xác nhận dùng chìa khóa] tại tọa độ (872, 525)
                self.log(f"   + Bấm [Xác nhận dùng chìa khóa] (872, 525)...")
                self.click_coord("xac_nhan_dung_chia", delay=1.0, move_wait=0.25)

                # 3. Đợi khoảng 5s cho game hoàn thành hiệu ứng nhận thưởng
                self.log("   + Đang chờ 5s hiệu ứng nhận thưởng...")
                for _ in range(10):
                    self.check_hotkeys()
                    time.sleep(0.5)

                # 4. Tap chuột xuống cuối giữa game (683, 700) để bỏ qua/nhận thưởng
                self.log("   + Tap chuột xuống cuối giữa game (683, 700) để bỏ qua bảng thưởng...")
                self.click(683, 700, delay=1.0, move_wait=0.15, label="Tap cuối giữa game bỏ qua thưởng")

                # Túi Đồ vẫn giữ nguyên, tiếp tục lượt tiếp theo mà không bấm B hay ESC
                time.sleep(0.5)

            time.sleep(0.4)

        # Thoát Túi Đồ về Sảnh
        self.log("\n-> Đã hoàn thành mở chìa khóa, đóng Túi Đồ về Sảnh...")
        self.close_bag()
        self.log("[OK] Hoàn tất tiến trình Dùng / Mở Chìa Khóa Raid!")
        return True

    def run_use_ve_sap(self):
        self.log("\n--- DÙNG VÉ SẠP BẤT NGỜ TRONG TÚI ĐỒ ---")
        self.open_bag_consumables()
        found, x, y, score = self.find_template("ve_sap", bbox=(960, 100, 1360, 710), threshold=0.65)
        if not found:
            self.log(f"-> Không tìm thấy [Vé Sạp Bất Ngờ] trong túi (score={score:.2f}).")
            self.close_bag()
            return False

        self.log(f"-> Tìm thấy Vé Sạp tại ({x}, {y}) (score={score:.2f})")
        self.click(x, y, delay=0.8, label="Chọn Vé Sạp")

        # Bước bắt buộc: Bấm nút [DÙNG] để mở giao diện 3 lá bài Sạp Bất Ngờ
        if not self._click_dung_button(x, delay=2.0, label="Bấm Dùng Vé Sạp"):
            self.click(x, y, delay=0.8, label="Chọn lại Vé Sạp")
            if not self._click_dung_button(x, delay=2.0, label="Bấm Dùng Vé Sạp"):
                self.close_bag()
                return False

        # Chọn 1 trong 3 lá bài (mặc định lá giữa: 707, 577)
        self.log("-> Giao diện 3 lá bài Sạp Bất Ngờ: Chọn lá bài ở giữa (707, 577)...")
        self.click(707, 577, delay=1.8, move_wait=0.25, label="Chọn lá bài Sạp")

        # Kiểm tra nút [CHIA SẺ]; nếu đang chờ hoạt ảnh lật bài thì tap bỏ qua hoạt ảnh
        found_cs, sx, sy, _ = self.find_template("btn_chia_se", bbox=(700, 450, 1200, 750), threshold=0.65)
        if not found_cs:
            self.click(683, 555, delay=1.5, move_wait=0.15, label="Mở hoạt ảnh bài Sạp")
            for _ in range(4):
                found_cs, sx, sy, _ = self.find_template("btn_chia_se", bbox=(700, 450, 1200, 750), threshold=0.65)
                if found_cs:
                    break
                time.sleep(0.4)

        if not found_cs:
            sx, sy = 970, 639

        self.log(f"-> Bấm nút [CHIA SẺ] tại ({sx}, {sy})...")
        self.click(sx, sy, delay=1.5, move_wait=0.25, label="Bấm Chia Sẻ Sạp")

        # Tắt Sạp Bất Ngờ bằng ESC (xử lý popup chia sẻ nếu có rồi thoát hẳn bảng Hoạt Động)
        self.press_esc(delay=1.2)
        still_in_sap, _, _, _ = self.find_template("btn_chia_se", bbox=(700, 450, 1200, 750), threshold=0.65)
        if still_in_sap:
            self.press_esc(delay=1.2)

        bag_open, _, _, _ = self.find_template("btn_kho_bag", bbox=(950, 660, 1220, 768), threshold=0.70)
        if bag_open:
            self.close_bag()

        self.log("[OK] Đã thực hiện xong Dùng Vé Sạp Bất Ngờ!")
        return True

    def run_use_ve_mat(self, ticket_count=5):
        mode_desc = f"{ticket_count} vé (bấm từng lần)" if ticket_count > 0 else "nhấn giữ 3.5s đặt hết"
        self.log(f"\n--- DÙNG VÉ SỐ (VÉ MẬT THẤT LẠC: {mode_desc}) ---")
        self.open_bag_consumables()
        found, x, y, score = self.find_template("ve_mat", bbox=(960, 100, 1360, 710), threshold=0.65)
        if not found:
            self.log(f"-> Không tìm thấy [Vé Mật Thất Lạc] trong túi (score={score:.2f}).")
            self.close_bag()
            return False

        self.log(f"-> Tìm thấy Vé Mật tại ({x}, {y}) (score={score:.2f})")
        self.click(x, y, delay=0.8, label="Chọn Vé Mật")

        # Bước bắt buộc: Bấm nút [DÙNG] để mở bảng Mất Vé Mật
        if not self._click_dung_button(x, delay=1.8, label="Bấm Dùng Vé Mật"):
            self.click(x, y, delay=0.8, label="Chọn lại Vé Mật")
            if not self._click_dung_button(x, delay=1.8, label="Bấm Dùng Vé Mật"):
                self.close_bag()
                return False

        vx, vy = self._find_dat_ve_button()
        if ticket_count > 0:
            self.log(f"-> Bấm đúng {ticket_count} lần vào nút vàng [NHẤN GIỮ ĐỂ ĐẶT] ({vx}, {vy})...")
            self.spam_click(vx, vy, count=ticket_count, interval=0.15, label=f"Đặt {ticket_count} Vé Số")
            time.sleep(0.8)
        else:
            self.log(f"-> Nhấn giữ chuột 3.5s tại [NHẤN GIỮ ĐỂ ĐẶT] ({vx}, {vy}) để đặt hết Vé Mật...")
            self.force_foreground()
            win32api.SetCursorPos((vx, vy))
            pydirectinput.moveTo(vx, vy)
            time.sleep(0.15)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            try:
                for _ in range(7):
                    self.check_hotkeys()
                    time.sleep(0.5)
            finally:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(1.0)

        # Tắt bảng sử dụng vé bằng ESC rồi bấm B để tắt Túi Đồ / Kho Đồ
        self.log("-> Bấm ESC tắt bảng Vé Mật rồi bấm B tắt Túi Đồ...")
        self.press_esc(delay=1.2)
        self.close_bag()
        self.log("[OK] Đã hoàn tất Đặt Vé Mật Thất Lạc!")
        return True

    def run_use_raid_key(self, key_id, key_name, count=3):
        self.log(f"\n--- SỬ DỤNG CHÌA KHÓA: {key_name} ({count} lần) ---")
        self.open_bag_consumables()
        for attempt in range(1, count + 1):
            found, x, y, score = self.find_template(key_id, bbox=(960, 100, 1360, 710), threshold=0.65)
            if not found:
                self.log(f"-> Chưa có [{key_name}] trong túi (score={score:.2f}). Ngưng.")
                break

            self.log(f"-> Lần {attempt}/{count}: Click [{key_name}] tại ({x}, {y})")
            self.click(x, y, delay=0.8, label=key_name)

            if not self._click_dung_button(x, delay=1.5, label=f"Dùng {key_name}"):
                break

            self.click(683, 700, delay=1.0, label="Tắt bảng thưởng")

        self.close_bag()
        self.log(f"[OK] Đã xử lý xong {key_name}!")

    # --------------------------------------------------------------------------
    # CÁC TÁC VỤ DAILY CHUẨN XÁC 100% (TUYỆT ĐỐI BỎ TÁCH ĐỒ)
    # --------------------------------------------------------------------------
    def run_daily_phuc_loi(self):
        self.log("\n--- DAILY 1: PHÚC LỢI NGÀY ---")
        self.force_foreground()
        time.sleep(0.4)
        self.click_coord("btn_cua_hang", delay=2.2, move_wait=0.30, clicks=1)
        self.click_coord("tab_goi_qua", delay=1.8, move_wait=0.30, clicks=1)
        self.click_coord("tab_goi_tuan", delay=1.8, move_wait=0.30, clicks=1)
        self.click_coord("btn_phuc_loi_ngay", delay=1.8, move_wait=0.30, clicks=1)
        # Tap thêm 1 lần nữa vào tọa độ nhận phúc lợi ngày để tắt bảng quà trước khi bấm ESC thoát Cửa Hàng
        self.click_coord("btn_phuc_loi_ngay", delay=1.2, move_wait=0.25, clicks=1)
        # Đóng Cửa Hàng về Sảnh: Bấm ESC ĐÚNG 1 LẦN (KHÔNG bấm thừa lần 2 gây bật menu hệ thống sảnh)
        self.press_esc(delay=1.6)
        self.log("[OK] Đã nhận xong Phúc Lợi Ngày!")

    def run_daily_pin(self):
        self.log("\n--- DAILY 2: DÙNG PIN THỂ LỰC ---")
        self.force_foreground()
        time.sleep(0.4)
        self.click_coord("btn_pin_2", delay=1.8, move_wait=0.30, clicks=1)
        self.click_coord("btn_dung_pin", delay=1.4, move_wait=0.28, clicks=1)
        self.click_coord("btn_dung_pin", delay=1.4, move_wait=0.25, clicks=1)
        # Đóng popup Pin bằng nút [X] (1005, 213) để KHÔNG bấm phím ESC tại Sảnh
        self.click_coord("btn_nut_tat", delay=1.5, move_wait=0.28, clicks=1)
        self.log("[OK] Đã dùng Pin thể lực xong!")

    def run_daily_ham_doi(self):
        self.log("\n--- DAILY 3: ĐIỂM DANH HẠM ĐỘI ---")
        self.force_foreground()
        time.sleep(0.4)
        # Bước 1: Mở menu (CHỈ CLICK 1 LẦN DUY NHẤT, chờ 2.0s để menu trượt ra hoàn tất)
        self.click_coord("btn_menu", delay=2.0, move_wait=0.30, clicks=1)
        # Bước 2: Bấm Hạm Đội
        self.click_coord("btn_ham_doi", delay=2.2, move_wait=0.30, clicks=1)
        # Bước 3: Mở bảng điểm danh
        self.click_coord("icon_check_in_ham", delay=1.8, move_wait=0.28, clicks=1)
        # Bước 4: Điểm danh miễn phí
        self.click_coord("btn_checkin_mien_phi", delay=1.6, move_wait=0.28, clicks=1)
        # Bước 5: Đóng popup điểm danh bằng nút [X] (1164, 172)
        self.spam_click(COORDS["btn_thoat_diem_danh"][0], COORDS["btn_thoat_diem_danh"][1], count=3, interval=0.25, label="Thoát điểm danh")
        time.sleep(0.7)
        # Bước 6: Thoát Hạm Đội về Sảnh (bấm ESC ĐÚNG 1 LẦN)
        self.press_esc(delay=1.6)
        self.log("[OK] Đã điểm danh Hạm Đội xong!")

    def run_daily_thu(self):
        self.log("\n--- DAILY 4: NHẬN THƯ ---")
        self.force_foreground()
        time.sleep(0.4)
        # Bước 1: Mở menu (CHỈ CLICK 1 LẦN DUY NHẤT, chờ 2.0s để thanh menu trượt ra hoàn tất)
        self.click_coord("btn_menu", delay=2.0, move_wait=0.30, clicks=1)
        # Bước 2: Click btn_thu (1336, 621)
        self.click_coord("btn_thu", delay=2.0, move_wait=0.30, clicks=1)
        # Bước 3: Click btn_nhan_thu (330, 728) nhận toàn bộ thư
        self.click_coord("btn_nhan_thu", delay=1.8, move_wait=0.28, clicks=1)
        # Bước 4: Đóng popup nhận thư
        self.spam_click(COORDS["btn_close_popup"][0], COORDS["btn_close_popup"][1], count=3, interval=0.25, label="Đóng popup thư")
        time.sleep(0.7)
        # Bước 5: Thoát Hòm Thư về Sảnh (bấm ESC ĐÚNG 1 LẦN)
        self.press_esc(delay=1.6)
        self.log("[OK] Đã nhận toàn bộ Thư xong!")

    def run_daily_kho(self):
        self.log("\n--- DAILY 5: KHO (NẠP VÀNG & GỘP ĐỒ) ---")
        self.force_foreground()
        time.sleep(0.4)
        self.log("-> Bước 1: Bấm phím B để mở Túi Đồ...")
        self.press_key('b', hold=0.18, delay=2.0)
        self.log("-> Bước 2: Bấm nút [Kho] (1064, 748) trong Túi Đồ...")
        self.click_coord("btn_kho", delay=2.0, move_wait=0.30, clicks=1)
        self.log("-> Bước 3: Bấm [Nạp Vàng]...")
        self.click_coord("btn_nap_vang", delay=1.6, move_wait=0.28, clicks=1)
        self.spam_click(COORDS["btn_nap_vang_thuong"][0], COORDS["btn_nap_vang_thuong"][1], count=4, interval=0.22, label="Nạp vàng thường")
        self.spam_click(COORDS["btn_nap_vang_khoa"][0], COORDS["btn_nap_vang_khoa"][1], count=4, interval=0.22, label="Nạp vàng khóa")
        self.click_coord("btn_cho_vao", delay=1.6, move_wait=0.28, clicks=1)
        self.click_coord("btn_cong_don_nhanh", delay=1.6, move_wait=0.28, clicks=1)
        self.click_coord("btn_kho_tai_khoan", delay=1.6, move_wait=0.28, clicks=1)
        self.click_coord("btn_cong_don_nhanh", delay=1.6, move_wait=0.28, clicks=1)
        # Sau khi nạp xong thì bấm B 1 lần để thoát khỏi túi đồ và kho đồ về sảnh
        time.sleep(0.5)
        self.log("-> Bấm phím B 1 lần để thoát khỏi Túi Đồ & Kho Đồ về Sảnh...")
        self.press_key('b', hold=0.18, delay=1.8)
        self.log("[OK] Đã Nạp Vàng & Gộp Kho xong!")

    def run_daily_so_tay(self):
        self.log("\n--- DAILY 6: QUÀ SỔ TAY TIẾN ĐỘ ---")
        self.force_foreground()
        time.sleep(0.4)
        self.click_coord("icon_so_tay", delay=2.0, move_wait=0.30, clicks=1)
        self.spam_click(COORDS["btn_tui_qua_so_tay"][0], COORDS["btn_tui_qua_so_tay"][1], count=12, interval=0.16, label="Túi quà Sổ tay")
        time.sleep(0.6)
        # Bỏ mục nhận quà 100 theo yêu cầu: Chỉ nhận mốc 20, 60, 80
        for moc in ["btn_qua_20", "btn_qua_60", "btn_qua_80"]:
            self.click_coord(moc, delay=1.2, move_wait=0.28, clicks=1)
        time.sleep(0.6)
        # Sau khi nhận xong thì tắt sổ bằng nút "btn_thoat_so": (37, 64)
        self.log("-> Tắt Sổ Tay bằng nút [btn_thoat_so] (37, 64)...")
        self.click_coord("btn_thoat_so", delay=1.5, move_wait=0.28, clicks=1)
        time.sleep(0.4)
        # Bấm thêm 1 lần dự phòng để đảm bảo thoát hẳn về sảnh
        self.click_coord("btn_thoat_so", delay=1.6, move_wait=0.25, clicks=1)
        self.log("[OK] Đã nhận Quà Sổ Tay và tắt sổ về sảnh thành công!")


# ==============================================================================
# GIAO DIỆN ĐIỀU KHIỂN TINH GỌN (TKINTER GUI V2)
# ==============================================================================
class AutoSeriaV2App:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoSeria V2 Stable - Bản Ổn Định 100% (Hộp & Chìa)")
        # Giao diện hình chữ nhật đứng gọn gàng, tự đặt lệch phải nếu màn hình đủ rộng để không che game (0,0 -> 1366x768)
        win_w, win_h = 580, 820
        try:
            scr_w = self.root.winfo_screenwidth()
            pos_x = 1376 if scr_w >= 1376 + win_w else max(0, scr_w - win_w - 10)
            self.root.geometry(f"{win_w}x{win_h}+{pos_x}+20")
        except Exception:
            self.root.geometry(f"{win_w}x{win_h}")
        self.root.minsize(540, 720)

        self.engine = SeriaEngineV2(log_callback=self.append_log)
        self.worker_thread = None

        self.init_variables()
        self.build_ui()
        self.load_config()
        self.sync_header_checks()
        self.sync_bk_header_checks()

    def init_variables(self):
        self.total_chars_var = tk.IntVar(value=7)
        self.start_slot_var = tk.IntVar(value=1)
        self.already_in_lobby_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Sẵn sàng")

        self.slot_vars = {}
        for s in range(1, 13):
            self.slot_vars[s] = {
                "enabled": tk.BooleanVar(value=(s <= 7)),
                "do_cp": tk.BooleanVar(value=True),
                "cp_times": tk.IntVar(value=1),
                "do_nt": tk.BooleanVar(value=True),
                "nt_times": tk.IntVar(value=2),
                "do_daily": tk.BooleanVar(value=True),
                "do_ve_sap": tk.BooleanVar(value=False),
                "do_ve_so": tk.BooleanVar(value=False),
                "do_open_keys": tk.BooleanVar(value=False),
            }

        self.daily_opts = {
            "phuc_loi": tk.BooleanVar(value=True),
            "pin": tk.BooleanVar(value=True),
            "ham_doi": tk.BooleanVar(value=True),
            "thu": tk.BooleanVar(value=True),
            "kho": tk.BooleanVar(value=True),
            "so_tay": tk.BooleanVar(value=True),
        }

        self.test_slot_var = tk.IntVar(value=2)

        # Biến Tích All cho từng cột
        self.all_enabled_var = tk.BooleanVar(value=False)
        self.all_cp_var = tk.BooleanVar(value=True)
        self.all_nt_var = tk.BooleanVar(value=True)
        self.speed_mode_var = tk.StringVar(value="⚖ Chuẩn (1.0x)")
        self.all_daily_var = tk.BooleanVar(value=True)
        self.all_ve_sap_var = tk.BooleanVar(value=False)
        self.all_ve_so_var = tk.BooleanVar(value=False)
        self.all_open_keys_var = tk.BooleanVar(value=False)

        # Biến Hộp Tinh Thể & Chìa Khóa theo từng nhân vật (12 Slot)
        self.box_key_slots = {}
        for s in range(1, 13):
            self.box_key_slots[s] = {
                "enabled": tk.BooleanVar(value=(s <= 7)),
                "buy_box_type": tk.StringVar(value="Hộp 1"),
                "do_exchange": tk.BooleanVar(value=True),
                "use_l8": tk.IntVar(value=3),
                "use_t8": tk.IntVar(value=3),
                "use_s8": tk.IntVar(value=3),
                "use_h4": tk.IntVar(value=3),
                "use_k8": tk.IntVar(value=3),
                "use_d8": tk.IntVar(value=3),
                "use_q8": tk.IntVar(value=3),
                "use_v8": tk.IntVar(value=3),
            }

        self.all_bk_enabled_var = tk.BooleanVar(value=False)
        self.all_bk_exchange_var = tk.BooleanVar(value=True)

    def build_ui(self):
        self.style = ttk.Style()
        self.style.configure("Header.TCheckbutton", font=("Segoe UI", 8, "bold"))

        header = tk.Frame(self.root, bg="#1e293b", height=44)
        header.pack(fill="x", side="top")
        tk.Label(
            header,
            text="AUTOSERIA V2",
            font=("Segoe UI", 11, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
        ).pack(side="left", padx=12, pady=8)

        status_lbl = tk.Label(
            header,
            textvariable=self.status_var,
            font=("Segoe UI", 9, "italic"),
            fg="#facc15",
            bg="#1e293b",
        )
        status_lbl.pack(side="right", padx=12, pady=8)

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=6, pady=6)

        tab_main = ttk.Frame(nb)
        tab_daily = ttk.Frame(nb)
        tab_box = ttk.Frame(nb)
        nb.add(tab_main, text="  ⚙ Cấu Hình & Chạy  ")
        nb.add(tab_daily, text="  🎁 Tùy Chọn Daily  ")
        nb.add(tab_box, text="  💎 Hộp Tinh Thể & Chìa  ")

        # TAB 1: CÀI ĐẶT CHUNG (2 DÒNG GỌN)
        top_bar = ttk.LabelFrame(tab_main, text=" Cài đặt chung & Phím tắt ")
        top_bar.pack(fill="x", padx=8, pady=4)

        top_r1 = ttk.Frame(top_bar)
        top_r1.pack(fill="x", padx=6, pady=(4, 2))
        ttk.Label(top_r1, text="Tổng NV:").pack(side="left", padx=(2, 2))
        ttk.Spinbox(top_r1, from_=1, to=12, textvariable=self.total_chars_var, width=4).pack(side="left", padx=2)
        ttk.Label(top_r1, text="Từ NV:").pack(side="left", padx=(8, 2))
        ttk.Spinbox(top_r1, from_=1, to=12, textvariable=self.start_slot_var, width=4).pack(side="left", padx=2)
        ttk.Button(top_r1, text="📌 Ghim Game", command=self.engine.lock_game_window).pack(side="left", padx=(6, 4))
        ttk.Label(top_r1, text="Tốc độ:").pack(side="left", padx=(4, 2))
        cbo_speed = ttk.Combobox(
            top_r1,
            values=["⚖ Chuẩn (1.0x)", "⚡ Nhanh (0.75x)", "🛡 Chậm (1.30x)"],
            textvariable=self.speed_mode_var,
            width=13,
            state="readonly"
        )
        cbo_speed.pack(side="left", padx=2)
        cbo_speed.bind("<<ComboboxSelected>>", lambda e: self.engine.set_speed_mode(self.speed_mode_var.get()))
        tk.Label(top_r1, text="[F11: Pause | F12: Dừng]", fg="#ef4444", font=("Segoe UI", 8, "bold")).pack(side="right", padx=2)

        top_r2 = ttk.Frame(top_bar)
        top_r2.pack(fill="x", padx=6, pady=(2, 4))
        ttk.Checkbutton(
            top_r2,
            text="Đang ở sẵn Sảnh con này (Không đổi ở con đầu)",
            variable=self.already_in_lobby_var,
        ).pack(side="left", padx=2)

        # BẢNG 12 SLOT DẠNG LƯỚI CĂN THẲNG CỘT
        slots_frame = ttk.LabelFrame(tab_main, text=" Cấu hình từng nhân vật ")
        slots_frame.pack(fill="both", expand=True, padx=8, pady=4)

        hdr = ttk.Frame(slots_frame)
        hdr.pack(fill="x", padx=4, pady=(3, 1))
        col_specs = [
            (0, 50), (1, 54), (2, 48), (3, 40), (4, 58), (5, 40), (6, 62), (7, 68), (8, 64), (9, 64)
        ]
        for col_i, min_w in col_specs:
            hdr.columnconfigure(col_i, minsize=min_w)

        ttk.Checkbutton(hdr, text="Bật", variable=self.all_enabled_var, command=self.toggle_all_enabled, style="Header.TCheckbutton").grid(row=0, column=0, sticky="w", padx=3)
        ttk.Label(hdr, text="Slot", font=("Segoe UI", 8, "bold")).grid(row=0, column=1, sticky="w", padx=2)
        ttk.Checkbutton(hdr, text="CP", variable=self.all_cp_var, command=self.toggle_all_cp, style="Header.TCheckbutton").grid(row=0, column=2, sticky="w", padx=2)
        ttk.Label(hdr, text="SL", font=("Segoe UI", 8, "bold")).grid(row=0, column=3, sticky="w", padx=2)
        ttk.Checkbutton(hdr, text="Ngục", variable=self.all_nt_var, command=self.toggle_all_nt, style="Header.TCheckbutton").grid(row=0, column=4, sticky="w", padx=2)
        ttk.Label(hdr, text="SL", font=("Segoe UI", 8, "bold")).grid(row=0, column=5, sticky="w", padx=2)
        ttk.Checkbutton(hdr, text="Daily", variable=self.all_daily_var, command=self.toggle_all_daily, style="Header.TCheckbutton").grid(row=0, column=6, sticky="w", padx=2)
        ttk.Checkbutton(hdr, text="Vé Sạp", variable=self.all_ve_sap_var, command=self.toggle_all_ve_sap, style="Header.TCheckbutton").grid(row=0, column=7, sticky="w", padx=2)
        ttk.Checkbutton(hdr, text="Vé Số", variable=self.all_ve_so_var, command=self.toggle_all_ve_so, style="Header.TCheckbutton").grid(row=0, column=8, sticky="w", padx=2)
        ttk.Checkbutton(hdr, text="Chìa", variable=self.all_open_keys_var, command=self.toggle_all_open_keys, style="Header.TCheckbutton").grid(row=0, column=9, sticky="w", padx=2)

        canvas = tk.Canvas(slots_frame, height=210, highlightthickness=0)
        scrollbar = ttk.Scrollbar(slots_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=4, pady=2)
        scrollbar.pack(side="right", fill="y", pady=2)

        for col_i, min_w in col_specs:
            scrollable_frame.columnconfigure(col_i, minsize=min_w)

        for s in range(1, 13):
            r_idx = s - 1
            vars_s = self.slot_vars[s]
            ttk.Checkbutton(scrollable_frame, variable=vars_s["enabled"], command=self.sync_header_checks).grid(row=r_idx, column=0, sticky="w", padx=3, pady=2)
            ttk.Label(scrollable_frame, text=f"Slot {s:2d}:").grid(row=r_idx, column=1, sticky="w", padx=2, pady=2)
            ttk.Checkbutton(scrollable_frame, text="CP", variable=vars_s["do_cp"], command=self.sync_header_checks).grid(row=r_idx, column=2, sticky="w", padx=2, pady=2)
            ttk.Spinbox(scrollable_frame, from_=0, to=10, textvariable=vars_s["cp_times"], width=3).grid(row=r_idx, column=3, sticky="w", padx=2, pady=2)
            ttk.Checkbutton(scrollable_frame, text="Ngục", variable=vars_s["do_nt"], command=self.sync_header_checks).grid(row=r_idx, column=4, sticky="w", padx=2, pady=2)
            ttk.Spinbox(scrollable_frame, from_=0, to=10, textvariable=vars_s["nt_times"], width=3).grid(row=r_idx, column=5, sticky="w", padx=2, pady=2)
            ttk.Checkbutton(scrollable_frame, text="Daily", variable=vars_s["do_daily"], command=self.sync_header_checks).grid(row=r_idx, column=6, sticky="w", padx=2, pady=2)
            ttk.Checkbutton(scrollable_frame, text="V.Sạp", variable=vars_s["do_ve_sap"], command=self.sync_header_checks).grid(row=r_idx, column=7, sticky="w", padx=2, pady=2)
            ttk.Checkbutton(scrollable_frame, text="V.Số", variable=vars_s["do_ve_so"], command=self.sync_header_checks).grid(row=r_idx, column=8, sticky="w", padx=2, pady=2)
            ttk.Checkbutton(scrollable_frame, text="Mở", variable=vars_s["do_open_keys"], command=self.sync_header_checks).grid(row=r_idx, column=9, sticky="w", padx=2, pady=2)

        # KHU VỰC THỬ NGHIỆM (CHIA 3 HÀNG GỌN TRONG KHUNG ĐỨNG)
        test_frame = ttk.LabelFrame(tab_main, text=" Khu vực thử nghiệm ")
        test_frame.pack(fill="x", padx=8, pady=4)

        test_row1 = ttk.Frame(test_frame)
        test_row1.pack(fill="x", padx=5, pady=3)
        ttk.Label(test_row1, text="Slot test:", font=("Segoe UI", 8, "bold")).pack(side="left", padx=3)
        ttk.Spinbox(test_row1, from_=1, to=12, textvariable=self.test_slot_var, width=4).pack(side="left", padx=3)
        ttk.Button(test_row1, text="▶ Đổi NV (Thay Thế)", command=lambda: self.run_test_switch(is_direct=False)).pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(test_row1, text="🎯 Bấm Trực Tiếp Ô Này", command=lambda: self.run_test_switch(is_direct=True)).pack(side="left", padx=4, fill="x", expand=True)

        test_row2 = ttk.Frame(test_frame)
        test_row2.pack(fill="x", padx=5, pady=3)
        ttk.Button(test_row2, text="🚪 Thoát Ải (Giữ NV)", command=self.run_test_relogin).pack(side="left", padx=3, fill="x", expand=True)
        ttk.Button(test_row2, text="▶ Test 1 Chinh Phạt", command=self.run_test_cp).pack(side="left", padx=3, fill="x", expand=True)
        ttk.Button(test_row2, text="▶ Test 1 Ngục Tối", command=self.run_test_nt).pack(side="left", padx=3, fill="x", expand=True)

        test_row3 = ttk.Frame(test_frame)
        test_row3.pack(fill="x", padx=5, pady=3)
        ttk.Button(test_row3, text="▶ Test Daily", command=self.run_test_daily).pack(side="left", padx=3, fill="x", expand=True)
        ttk.Button(test_row3, text="🎟 Test Vé Sạp", command=self.run_test_ve_sap).pack(side="left", padx=3, fill="x", expand=True)
        ttk.Button(test_row3, text="🗺 Test Vé Số", command=self.run_test_ve_mat).pack(side="left", padx=3, fill="x", expand=True)

        test_row4 = ttk.Frame(test_frame)
        test_row4.pack(fill="x", padx=4, pady=(2, 3))
        ttk.Button(test_row4, text="🧭 TEST CHẠY VÀO Ô XANH (MỞ ẢI)", command=self.run_test_navigate_green_zone).pack(side="left", padx=3, fill="x", expand=True)

        # THANH NÚT CHẠY CHÍNH
        ctrl_bar = ttk.Frame(tab_main)
        ctrl_bar.pack(fill="x", padx=8, pady=6)

        btn_start = tk.Button(
            ctrl_bar,
            text="🚀 BẮT ĐẦU",
            font=("Segoe UI", 10, "bold"),
            bg="#16a34a",
            fg="white",
            padx=12,
            pady=6,
            command=self.start_full_auto,
        )
        btn_start.pack(side="left", padx=3, fill="x", expand=True)

        btn_run_current = tk.Button(
            ctrl_bar,
            text="⚡ CHẠY NV HIỆN TẠI",
            font=("Segoe UI", 9, "bold"),
            bg="#2563eb",
            fg="white",
            padx=10,
            pady=6,
            command=self.start_current_character_only,
        )
        btn_run_current.pack(side="left", padx=3, fill="x", expand=True)

        btn_stop = tk.Button(
            ctrl_bar,
            text="⏹ DỪNG (F12)",
            font=("Segoe UI", 10, "bold"),
            bg="#dc2626",
            fg="white",
            padx=10,
            pady=6,
            command=self.stop_auto,
        )
        btn_stop.pack(side="right", padx=3, fill="x", expand=True)

        # TAB 2: TÙY CHỌN DAILY
        daily_card = ttk.LabelFrame(tab_daily, text=" Các mục Daily cần thực hiện (Đã bỏ tách đồ) ")
        daily_card.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Checkbutton(daily_card, text="1. Nhận Phúc Lợi Ngày (Cửa Hàng -> Gói Tuần -> Phúc Lợi)", variable=self.daily_opts["phuc_loi"]).pack(anchor="w", padx=14, pady=7)
        ttk.Checkbutton(daily_card, text="2. Dùng Pin Thể Lực (Icon Pin -> Dùng)", variable=self.daily_opts["pin"]).pack(anchor="w", padx=14, pady=7)
        ttk.Checkbutton(daily_card, text="3. Điểm danh Hạm Đội (Menu -> Hạm Đội -> Điểm Danh)", variable=self.daily_opts["ham_doi"]).pack(anchor="w", padx=14, pady=7)
        ttk.Checkbutton(daily_card, text="4. Nhận Hòm Thư Toàn Bộ (Menu -> Hòm Thư)", variable=self.daily_opts["thu"]).pack(anchor="w", padx=14, pady=7)
        ttk.Checkbutton(daily_card, text="5. Kho (Nạp Vàng & Gộp Đồ -> Phím B thoát)", variable=self.daily_opts["kho"]).pack(anchor="w", padx=14, pady=7)
        ttk.Checkbutton(daily_card, text="6. Nhận Quà Sổ Tay (Mốc 20, 60, 80 -> Tắt sổ)", variable=self.daily_opts["so_tay"]).pack(anchor="w", padx=14, pady=7)

        tk.Label(
            daily_card,
            text="[Ghi chú]: Tính năng Tách Đồ đã được gỡ bỏ 100%.",
            fg="#16a34a",
            font=("Segoe UI", 9, "italic"),
        ).pack(anchor="w", padx=14, pady=12)

        # TAB 3: HỘP TINH THỂ & CHÌA KHÓA RAID (CẤU HÌNH TỪNG NHÂN VẬT 1..12)
        top_box_frame = ttk.LabelFrame(tab_box, text=" Điều khiển tác vụ Hộp & Chìa ")
        top_box_frame.pack(fill="x", padx=8, pady=4)

        top_bk_r1 = ttk.Frame(top_box_frame)
        top_bk_r1.pack(fill="x", padx=6, pady=(4, 2))

        btn_run_bk_all = tk.Button(
            top_bk_r1,
            text="▶ CHẠY 12 NV (HỘP & CHÌA)",
            font=("Segoe UI", 9, "bold"),
            bg="#16a34a",
            fg="white",
            padx=8,
            pady=4,
            command=self.run_box_key_all,
        )
        btn_run_bk_all.pack(side="left", padx=3, fill="x", expand=True)

        btn_run_bk_curr = tk.Button(
            top_bk_r1,
            text="⚡ CHẠY NV HIỆN TẠI",
            font=("Segoe UI", 9, "bold"),
            bg="#2563eb",
            fg="white",
            padx=8,
            pady=4,
            command=self.run_box_key_current_slot,
        )
        btn_run_bk_curr.pack(side="left", padx=3, fill="x", expand=True)

        top_bk_r2 = ttk.Frame(top_box_frame)
        top_bk_r2.pack(fill="x", padx=6, pady=(3, 4))
        ttk.Label(top_bk_r2, text="Slot test:", font=("Segoe UI", 8, "bold")).pack(side="left", padx=(2, 2))
        ttk.Spinbox(top_bk_r2, from_=1, to=12, textvariable=self.test_slot_var, width=3).pack(side="left", padx=2)

        ttk.Label(top_bk_r2, text="Mua Hộp (All):", font=("Segoe UI", 8)).pack(side="left", padx=(6, 2))
        cbo_all_box = ttk.Combobox(top_bk_r2, values=["Hộp 1", "Hộp 2", "Cả 2", "Tắt"], width=6, state="readonly")
        cbo_all_box.set("Hộp 1")
        cbo_all_box.bind("<<ComboboxSelected>>", lambda e: self.apply_all_bk_buy_type(cbo_all_box.get()))
        cbo_all_box.pack(side="left", padx=2)

        ttk.Button(top_bk_r2, text="🛒 Test Mua", command=self.run_test_mua_hop).pack(side="left", padx=3, fill="x", expand=True)
        ttk.Button(top_bk_r2, text="🗝 Test Đổi", command=self.run_test_mo_hop_doi_chia).pack(side="left", padx=3, fill="x", expand=True)
        ttk.Button(top_bk_r2, text="🔓 Test Mở", command=self.run_test_use_keys).pack(side="left", padx=3, fill="x", expand=True)

        # BẢNG 12 SLOT HỘP & CHÌA (DẠNG LƯỚI GIỐNG TAB 1)
        bk_slots_frame = ttk.LabelFrame(tab_box, text=" Cấu hình Hộp & Chìa từng nhân vật ")
        bk_slots_frame.pack(fill="both", expand=True, padx=8, pady=4)

        hdr_bk = ttk.Frame(bk_slots_frame)
        hdr_bk.pack(fill="x", padx=4, pady=(3, 1))

        col_specs_bk = [
            (0, 40), (1, 46), (2, 66), (3, 38),
            (4, 36), (5, 36), (6, 36), (7, 36),
            (8, 36), (9, 36), (10, 36), (11, 36)
        ]
        for col_i, min_w in col_specs_bk:
            hdr_bk.columnconfigure(col_i, minsize=min_w)

        ttk.Checkbutton(hdr_bk, text="Bật", variable=self.all_bk_enabled_var, command=self.toggle_all_bk_enabled, style="Header.TCheckbutton").grid(row=0, column=0, sticky="w", padx=2)
        ttk.Label(hdr_bk, text="Slot", font=("Segoe UI", 8, "bold")).grid(row=0, column=1, sticky="w", padx=2)
        ttk.Label(hdr_bk, text="Mua Hộp", font=("Segoe UI", 8, "bold")).grid(row=0, column=2, sticky="w", padx=2)
        ttk.Checkbutton(hdr_bk, text="Đổi", variable=self.all_bk_exchange_var, command=self.toggle_all_bk_exchange, style="Header.TCheckbutton").grid(row=0, column=3, sticky="w", padx=2)

        key_labels = ["L8", "T8", "S8", "H4", "K8", "D8", "Q8", "V8"]
        for idx, k_txt in enumerate(key_labels):
            ttk.Label(hdr_bk, text=k_txt, font=("Segoe UI", 8, "bold")).grid(row=0, column=4 + idx, sticky="w", padx=2)

        canvas_bk = tk.Canvas(bk_slots_frame, height=220, highlightthickness=0)
        scrollbar_bk = ttk.Scrollbar(bk_slots_frame, orient="vertical", command=canvas_bk.yview)
        scrollable_frame_bk = ttk.Frame(canvas_bk)

        scrollable_frame_bk.bind("<Configure>", lambda e: canvas_bk.configure(scrollregion=canvas_bk.bbox("all")))
        canvas_bk.create_window((0, 0), window=scrollable_frame_bk, anchor="nw")
        canvas_bk.configure(yscrollcommand=scrollbar_bk.set)

        canvas_bk.pack(side="left", fill="both", expand=True, padx=4, pady=2)
        scrollbar_bk.pack(side="right", fill="y", pady=2)

        for col_i, min_w in col_specs_bk:
            scrollable_frame_bk.columnconfigure(col_i, minsize=min_w)

        for s in range(1, 13):
            r_idx = s - 1
            vars_bk = self.box_key_slots[s]
            ttk.Checkbutton(scrollable_frame_bk, variable=vars_bk["enabled"], command=self.sync_bk_header_checks).grid(row=r_idx, column=0, sticky="w", padx=2, pady=2)
            ttk.Label(scrollable_frame_bk, text=f"Slot {s:2d}:").grid(row=r_idx, column=1, sticky="w", padx=2, pady=2)
            
            cbo_box = ttk.Combobox(
                scrollable_frame_bk,
                values=["Hộp 1", "Hộp 2", "Cả 2", "Tắt"],
                textvariable=vars_bk["buy_box_type"],
                width=6,
                state="readonly"
            )
            cbo_box.grid(row=r_idx, column=2, sticky="w", padx=2, pady=2)

            ttk.Checkbutton(scrollable_frame_bk, variable=vars_bk["do_exchange"], command=self.sync_bk_header_checks).grid(row=r_idx, column=3, sticky="w", padx=2, pady=2)

            for idx, k_id in enumerate(["l8", "t8", "s8", "h4", "k8", "d8", "q8", "v8"]):
                ttk.Spinbox(scrollable_frame_bk, from_=0, to=99, textvariable=vars_bk[f"use_{k_id}"], width=3).grid(row=r_idx, column=4 + idx, sticky="w", padx=2, pady=2)

        note_bk = tk.Label(
            tab_box,
            text="• Mua Hộp: Chọn Hộp 1 hoặc Hộp 2 (mặc định 12 lần [+], có thể chọn Cả 2 hoặc Tắt).\n"
                 "• Đổi: Mở Hộp Tinh Thể trong Túi Đồ, bấm [MỞ NHIỀU] đổi các chìa có SL > 0.\n"
                 "• L8, T8, S8, H4, K8, D8, Q8, V8: Số lần mở mỗi chìa (0 = bỏ qua, mặc định 3 lần/chìa).",
            fg="#0369a1",
            font=("Segoe UI", 8),
            justify="left",
        )
        note_bk.pack(anchor="w", padx=12, pady=(2, 6))

        # LOG FRAME
        log_frame = ttk.LabelFrame(self.root, text=" Nhật Ký Hoạt Động ")
        log_frame.pack(fill="both", expand=True, padx=6, pady=4)

        self.log_txt = scrolledtext.ScrolledText(log_frame, height=10, bg="#0f172a", fg="#f8fafc", font=("Consolas", 8))
        self.log_txt.pack(fill="both", expand=True, padx=4, pady=4)

    def append_log(self, text):
        def _append():
            self.log_txt.insert(tk.END, text + "\n")
            self.log_txt.see(tk.END)
        self.root.after(0, _append)

    @staticmethod
    def _safe_int(var, default=0):
        try:
            return int(var.get())
        except Exception:
            return default

    def save_config(self):
        data = {
            "total_chars": self._safe_int(self.total_chars_var, 7),
            "start_slot": self._safe_int(self.start_slot_var, 1),
            "already_in_lobby": self.already_in_lobby_var.get(),
            "speed_mode": self.speed_mode_var.get(),
            "slots": {},
            "box_key_slots": {},
            "daily_opts": {k: v.get() for k, v in self.daily_opts.items()},
        }
        for s in range(1, 13):
            data["slots"][str(s)] = {
                "enabled": self.slot_vars[s]["enabled"].get(),
                "do_cp": self.slot_vars[s]["do_cp"].get(),
                "cp_times": self._safe_int(self.slot_vars[s]["cp_times"], 1),
                "do_nt": self.slot_vars[s]["do_nt"].get(),
                "nt_times": self._safe_int(self.slot_vars[s]["nt_times"], 2),
                "do_daily": self.slot_vars[s]["do_daily"].get(),
                "do_ve_sap": self.slot_vars[s]["do_ve_sap"].get(),
                "do_ve_so": self.slot_vars[s]["do_ve_so"].get(),
                "do_open_keys": self.slot_vars[s]["do_open_keys"].get(),
            }
            bk = self.box_key_slots[s]
            data["box_key_slots"][str(s)] = {
                "enabled": bk["enabled"].get(),
                "buy_box_type": bk["buy_box_type"].get(),
                "do_exchange": bk["do_exchange"].get(),
                "use_l8": self._safe_int(bk["use_l8"], 3),
                "use_t8": self._safe_int(bk["use_t8"], 3),
                "use_s8": self._safe_int(bk["use_s8"], 3),
                "use_h4": self._safe_int(bk["use_h4"], 3),
                "use_k8": self._safe_int(bk["use_k8"], 3),
                "use_d8": self._safe_int(bk["use_d8"], 3),
                "use_q8": self._safe_int(bk["use_q8"], 3),
                "use_v8": self._safe_int(bk["use_v8"], 3),
            }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.append_log(f"[!] Lỗi lưu file cấu hình: {e}")

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.total_chars_var.set(data.get("total_chars", 7))
            self.start_slot_var.set(data.get("start_slot", 1))
            self.already_in_lobby_var.set(data.get("already_in_lobby", True))
            saved_speed = data.get("speed_mode", "⚖ Chuẩn (1.0x)")
            self.speed_mode_var.set(saved_speed)
            self.engine.set_speed_mode(saved_speed)
            slots = data.get("slots", {})
            for s_str, cfg in slots.items():
                try:
                    s = int(s_str)
                    if s in self.slot_vars:
                        self.slot_vars[s]["enabled"].set(cfg.get("enabled", s <= 7))
                        self.slot_vars[s]["do_cp"].set(cfg.get("do_cp", True))
                        self.slot_vars[s]["cp_times"].set(cfg.get("cp_times", 1))
                        self.slot_vars[s]["do_nt"].set(cfg.get("do_nt", True))
                        self.slot_vars[s]["nt_times"].set(cfg.get("nt_times", 2))
                        self.slot_vars[s]["do_daily"].set(cfg.get("do_daily", True))
                        self.slot_vars[s]["do_ve_sap"].set(cfg.get("do_ve_sap", False))
                        self.slot_vars[s]["do_ve_so"].set(cfg.get("do_ve_so", False))
                        self.slot_vars[s]["do_open_keys"].set(cfg.get("do_open_keys", False))
                except Exception:
                    pass

            bk_slots = data.get("box_key_slots", {})
            for s_str, b_cfg in bk_slots.items():
                try:
                    s = int(s_str)
                    if s in self.box_key_slots:
                        target = self.box_key_slots[s]
                        target["enabled"].set(b_cfg.get("enabled", s <= 7))
                        if "buy_box_type" in b_cfg:
                            target["buy_box_type"].set(b_cfg["buy_box_type"])
                        elif b_cfg.get("do_buy_box", True) is False:
                            target["buy_box_type"].set("Tắt")
                        else:
                            target["buy_box_type"].set("Hộp 1")
                        target["do_exchange"].set(b_cfg.get("do_exchange", True))
                        for k in ["l8", "t8", "s8", "h4", "k8", "d8", "q8", "v8"]:
                            target[f"use_{k}"].set(b_cfg.get(f"use_{k}", 3))
                except Exception:
                    pass

            daily = data.get("daily_opts", {})
            for k, val in daily.items():
                if k in self.daily_opts:
                    self.daily_opts[k].set(val)
        except Exception as e:
            self.append_log(f"[!] Không đọc được file cấu hình cũ: {e}")
        self.sync_header_checks()
        self.sync_bk_header_checks()

    def sync_header_checks(self):
        """Đồng bộ trạng thái của các ô Tích All ở tiêu đề bảng theo trạng thái của 12 slot."""
        self.all_enabled_var.set(all(self.slot_vars[s]["enabled"].get() for s in range(1, 13)))
        self.all_cp_var.set(all(self.slot_vars[s]["do_cp"].get() for s in range(1, 13)))
        self.all_nt_var.set(all(self.slot_vars[s]["do_nt"].get() for s in range(1, 13)))
        self.all_daily_var.set(all(self.slot_vars[s]["do_daily"].get() for s in range(1, 13)))
        self.all_ve_sap_var.set(all(self.slot_vars[s]["do_ve_sap"].get() for s in range(1, 13)))
        self.all_ve_so_var.set(all(self.slot_vars[s]["do_ve_so"].get() for s in range(1, 13)))
        self.all_open_keys_var.set(all(self.slot_vars[s]["do_open_keys"].get() for s in range(1, 13)))

    def toggle_all_enabled(self):
        val = self.all_enabled_var.get()
        for s in range(1, 13):
            self.slot_vars[s]["enabled"].set(val)

    def toggle_all_cp(self):
        val = self.all_cp_var.get()
        for s in range(1, 13):
            self.slot_vars[s]["do_cp"].set(val)

    def toggle_all_nt(self):
        val = self.all_nt_var.get()
        for s in range(1, 13):
            self.slot_vars[s]["do_nt"].set(val)

    def toggle_all_daily(self):
        val = self.all_daily_var.get()
        for s in range(1, 13):
            self.slot_vars[s]["do_daily"].set(val)

    def toggle_all_ve_sap(self):
        val = self.all_ve_sap_var.get()
        for s in range(1, 13):
            self.slot_vars[s]["do_ve_sap"].set(val)

    def toggle_all_ve_so(self):
        val = self.all_ve_so_var.get()
        for s in range(1, 13):
            self.slot_vars[s]["do_ve_so"].set(val)

    def toggle_all_open_keys(self):
        val = self.all_open_keys_var.get()
        for s in range(1, 13):
            self.slot_vars[s]["do_open_keys"].set(val)

    def sync_bk_header_checks(self):
        """Đồng bộ trạng thái ô Tích All ở tiêu đề bảng Hộp & Chìa."""
        self.all_bk_enabled_var.set(all(self.box_key_slots[s]["enabled"].get() for s in range(1, 13)))
        self.all_bk_exchange_var.set(all(self.box_key_slots[s]["do_exchange"].get() for s in range(1, 13)))

    def toggle_all_bk_enabled(self):
        val = self.all_bk_enabled_var.get()
        for s in range(1, 13):
            self.box_key_slots[s]["enabled"].set(val)

    def toggle_all_bk_exchange(self):
        val = self.all_bk_exchange_var.get()
        for s in range(1, 13):
            self.box_key_slots[s]["do_exchange"].set(val)

    def apply_all_bk_buy_type(self, val):
        for s in range(1, 13):
            self.box_key_slots[s]["buy_box_type"].set(val)

    def _execute_character_box_key(self, slot_num, slot_label):
        """Thực thi chuỗi Hộp & Chìa riêng cho 1 nhân vật (Mua Hộp -> Đổi Chìa -> Mở Chìa)."""
        if not self.engine.is_running:
            return
        bk_cfg = self.box_key_slots.get(slot_num)
        if not bk_cfg or not bk_cfg["enabled"].get():
            self.append_log(f"-> {slot_label}: Hộp & Chìa tắt (Bỏ qua).")
            return

        # 1. Mua Hộp Tinh Thể (Hộp 1, Hộp 2, Cả 2, hoặc Tắt) - mặc định 12 lần [+]
        box_choice = bk_cfg["buy_box_type"].get()
        if box_choice != "Tắt":
            if not self.engine.is_running:
                return
            self.append_log(f"-> {slot_label}: Mua Hộp Tinh Thể ({box_choice}, mặc định 12 lần [+])...")
            self.engine.run_mua_hop_tinh_the(box_type=box_choice, plus_clicks=12)

        # 2. Đổi Chìa từ Hộp Tinh Thể nếu được bật
        if bk_cfg["do_exchange"].get():
            if not self.engine.is_running:
                return
            k_map = {k: self._safe_int(bk_cfg[f"use_{k}"], 3) for k in ["l8", "t8", "s8", "h4", "k8", "d8", "q8", "v8"]}
            self.append_log(f"-> {slot_label}: Đổi chìa khóa từ Hộp Tinh Thể...")
            self.engine.run_mo_hop_doi_chia(keys_map=k_map)

        # 3. Dùng / Mở Chìa Khóa Raid trong Túi Đồ
        k_map_use = {k: self._safe_int(bk_cfg[f"use_{k}"], 3) for k in ["l8", "t8", "s8", "h4", "k8", "d8", "q8", "v8"]}
        has_keys = any(v > 0 for v in k_map_use.values())
        if has_keys:
            if not self.engine.is_running:
                return
            self.append_log(f"-> {slot_label}: Mở các Chìa Khóa Raid trong Túi Đồ...")
            self.engine.run_use_keys(keys_map=k_map_use)

    def run_box_key_all(self):
        """Chạy quy trình Hộp & Chìa cho tất cả các nhân vật được bật trong Tab Hộp & Chìa."""
        if self.engine.is_running:
            messagebox.showinfo("Đang chạy", "Tool đang chạy!")
            return

        self.save_config()
        self.engine.lock_game_window()
        self.engine.is_running = True
        self.status_var.set("Đang chạy Hộp & Chìa 12 NV...")
        self.engine.set_speed_mode(self.speed_mode_var.get())

        def _worker():
            try:
                self.engine.activate_game_input()
                start_slot = max(1, self._safe_int(self.start_slot_var, 1))
                total_chars = self._safe_int(self.total_chars_var, 7)
                already_in_lobby = self.already_in_lobby_var.get()

                self.append_log("\n==============================================")
                self.append_log(f"   BẮT ĐẦU CHẠY HỘP & CHÌA TỪ SLOT {start_slot} ĐẾN {total_chars}   ")
                self.append_log("==============================================")

                is_first_character = already_in_lobby

                for slot_num in range(start_slot, total_chars + 1):
                    if not self.engine.is_running:
                        break

                    bk_cfg = self.box_key_slots.get(slot_num)
                    if not bk_cfg or not bk_cfg["enabled"].get():
                        self.append_log(f"-> Slot {slot_num}: Tắt Hộp & Chìa (Bỏ qua).")
                        continue

                    self.status_var.set(f"Hộp & Chìa Slot {slot_num}/{total_chars}")
                    self.append_log(f"\n>>>>>>>> HỘP & CHÌA: NHÂN VẬT SLOT {slot_num} <<<<<<<<")

                    if is_first_character:
                        self.append_log(f"-> Nhân vật Slot {slot_num} đang ở sẵn tại Sảnh (Không đổi NV)!")
                        is_first_character = False
                    else:
                        self.engine.switch_to_slot(slot_num, total_chars=total_chars, from_screen="lobby", is_direct_test=False)

                    self._execute_character_box_key(slot_num, f"Slot {slot_num}")
                    self.append_log(f"[OK] Xong Hộp & Chìa cho Slot {slot_num}!")

                self.append_log("\n==============================================")
                self.append_log("   HOÀN THÀNH HỘP & CHÌA CHO TẤT CẢ NHÂN VẬT! ")
                self.append_log("==============================================")
                messagebox.showinfo("Hoàn tất", "Đã chạy xong quy trình Hộp & Chìa cho các nhân vật được chọn!")
            except KeyboardInterrupt:
                self.append_log("\n[!] Đã dừng chương trình theo yêu cầu của bạn.")
            except Exception as e:
                self.append_log(f"\n[!] Lỗi phát sinh: {e}")
            finally:
                self.engine.is_running = False
                self.status_var.set("Sẵn sàng")

        self.worker_thread = threading.Thread(target=_worker, daemon=True)
        self.worker_thread.start()

    def run_box_key_current_slot(self):
        """Chạy quy trình Hộp & Chìa cho DUY NHẤT nhân vật hiện tại ở sảnh (theo slot test)."""
        if self.engine.is_running:
            messagebox.showinfo("Đang chạy", "Tool đang chạy!")
            return

        self.save_config()
        self.engine.lock_game_window()
        self.engine.is_running = True
        slot_ref = self._safe_int(self.test_slot_var, 1)
        self.status_var.set(f"Hộp & Chìa NV Hiện Tại (Slot {slot_ref})...")

        def _worker():
            try:
                self.engine.activate_game_input()
                self.append_log("\n==============================================")
                self.append_log(f"   CHẠY HỘP & CHÌA NV HIỆN TẠI (SLOT {slot_ref})  ")
                self.append_log("==============================================")
                self._execute_character_box_key(slot_ref, f"Slot {slot_ref} (Hiện tại)")
                self.append_log("\n[OK] Hoàn tất Hộp & Chìa cho nhân vật hiện tại!")
                messagebox.showinfo("Hoàn tất", f"Đã chạy xong Hộp & Chìa theo cấu hình Slot {slot_ref}!")
            except KeyboardInterrupt:
                self.append_log("\n[!] Đã dừng chương trình theo yêu cầu của bạn.")
            except Exception as e:
                self.append_log(f"\n[!] Lỗi phát sinh: {e}")
            finally:
                self.engine.is_running = False
                self.status_var.set("Sẵn sàng")

        self.worker_thread = threading.Thread(target=_worker, daemon=True)
        self.worker_thread.start()

    def _run_in_worker(self, target_fn, name="Task"):
        if self.engine.is_running:
            messagebox.showinfo("Đang chạy", "Một tác vụ khác đang chạy. Hãy chờ hoặc bấm Dừng.")
            return

        self.save_config()
        self.engine.lock_game_window()
        self.engine.is_running = True
        self.status_var.set(f"Đang chạy: {name}")
        self.engine.set_speed_mode(self.speed_mode_var.get())

        def _w():
            try:
                self.engine.activate_game_input()
                target_fn()
            except KeyboardInterrupt:
                self.append_log(f"\n[!] Đã dừng {name}.")
            except Exception as e:
                self.append_log(f"\n[!] Lỗi khi chạy {name}: {e}")
            finally:
                self.engine.is_running = False
                self.status_var.set("Sẵn sàng")

        self.worker_thread = threading.Thread(target=_w, daemon=True)
        self.worker_thread.start()

    def run_test_switch(self, is_direct=False):
        slot = self.test_slot_var.get()
        total = self.total_chars_var.get()
        mode_str = "Trực Tiếp" if is_direct else "Thay Thế Vị Trí"
        self._run_in_worker(
            lambda: self.engine.switch_to_slot(slot, total_chars=total, from_screen="lobby", is_direct_test=is_direct),
            f"Test Đổi Slot {slot} ({mode_str})"
        )

    def run_test_relogin(self):
        self._run_in_worker(self.engine.exit_dungeon_to_lobby, "Thoát Ải Về Sảnh (Giữ Đúng NV Hiện Tại)")

    def run_test_mua_hop(self):
        slot_ref = self._safe_int(self.test_slot_var, 1)
        bk_cfg = self.box_key_slots.get(slot_ref, self.box_key_slots[1])
        box_choice = bk_cfg["buy_box_type"].get()
        if box_choice == "Tắt":
            box_choice = "Hộp 1"
        self._run_in_worker(
            lambda: self.engine.run_mua_hop_tinh_the(box_type=box_choice, plus_clicks=12),
            f"Test Mua Hộp Tinh Thể (Slot {slot_ref}: {box_choice})"
        )

    def run_test_mo_hop_doi_chia(self):
        slot_ref = self._safe_int(self.test_slot_var, 1)
        bk_cfg = self.box_key_slots.get(slot_ref, self.box_key_slots[1])
        k_map = {k: self._safe_int(bk_cfg[f"use_{k}"], 3) for k in ["l8", "t8", "s8", "h4", "k8", "d8", "q8", "v8"]}
        self._run_in_worker(
            lambda: self.engine.run_mo_hop_doi_chia(keys_map=k_map),
            f"Test Mở Hộp Đổi 8 Chìa Khóa (Slot {slot_ref})"
        )

    def run_test_use_keys(self):
        slot_ref = self._safe_int(self.test_slot_var, 1)
        bk_cfg = self.box_key_slots.get(slot_ref, self.box_key_slots[1])
        k_map = {k: self._safe_int(bk_cfg[f"use_{k}"], 3) for k in ["l8", "t8", "s8", "h4", "k8", "d8", "q8", "v8"]}
        self._run_in_worker(
            lambda: self.engine.run_use_keys(keys_map=k_map),
            f"Test Dùng / Mở 8 Chìa Khóa Raid (Slot {slot_ref})"
        )

    def run_test_ve_sap(self):
        self._run_in_worker(self.engine.run_use_ve_sap, "Test Dùng Vé Sạp")

    def run_test_ve_mat(self):
        self._run_in_worker(lambda: self.engine.run_use_ve_mat(ticket_count=5), "Test Dùng Vé Số (5 vé)")

    def run_test_navigate_green_zone(self):
        def _test_flow():
            self.engine.log("-> Test: Đi thẳng W 2.0s...")
            self.engine.move_forward(seconds=2.0)
            self.engine.step_into_portal()
        self._run_in_worker(_test_flow, "Test Đi Thẳng 2s + Quét Vào Ô Xanh")

    def run_test_cp(self):
        self._run_in_worker(self.engine.run_chinh_phat_once, "Test Đi 1 Chinh Phạt (Bot 4 Người)")

    def run_test_nt(self):
        self._run_in_worker(self.engine.run_nguc_toi_once, "Test Đi 1 Ngục Tối (Bot 4 Người)")

    def run_test_daily(self):
        def _do_daily():
            if self.daily_opts["phuc_loi"].get(): self.engine.run_daily_phuc_loi()
            if self.daily_opts["pin"].get(): self.engine.run_daily_pin()
            if self.daily_opts["ham_doi"].get(): self.engine.run_daily_ham_doi()
            if self.daily_opts["thu"].get(): self.engine.run_daily_thu()
            if self.daily_opts["kho"].get(): self.engine.run_daily_kho()
            if self.daily_opts["so_tay"].get(): self.engine.run_daily_so_tay()
        self._run_in_worker(_do_daily, "Test Daily")

    def _run_stage_turns(self, slot_label, stage_label, total_turns, run_once_fn):
        """Chạy đủ số lượt ải; chỉ tính xong và sang lượt mới khi lượt hiện tại thành công."""
        completed = 0
        while completed < total_turns and self.engine.is_running:
            current_turn = completed + 1
            self.append_log(f"-> {slot_label}: {stage_label} Bot 4 Người ({current_turn}/{total_turns})...")
            if run_once_fn():
                completed += 1
            else:
                self.append_log(f"-> [Giữ nguyên lượt {current_turn}/{total_turns}] Chưa ghép được 4 Bot, vào lại lượt này...")
                time.sleep(1.0)

    def _execute_character_plan(self, slot_label, cfg, slot_num=None):
        """Thực thi toàn bộ tác vụ đã bật cho 1 nhân vật: Chinh Phạt, Ngục Tối, Daily, Vé Sạp, Vé Số, Hộp & Chìa."""
        # 1. Đi Chinh Phạt (nếu tick chọn)
        if cfg["do_cp"].get():
            cp_times = self._safe_int(cfg["cp_times"], 0)
            self._run_stage_turns(slot_label, "Chinh Phạt", cp_times, self.engine.run_chinh_phat_once)

        # 2. Đi Ngục Tối (nếu tick chọn)
        if cfg["do_nt"].get():
            nt_times = self._safe_int(cfg["nt_times"], 0)
            self._run_stage_turns(slot_label, "Ngục Tối", nt_times, self.engine.run_nguc_toi_once)

        # 3. Làm Daily (nếu tick chọn)
        if cfg["do_daily"].get():
            if not self.engine.is_running:
                return
            self.append_log(f"-> {slot_label}: Thực hiện Daily...")
            if self.daily_opts["phuc_loi"].get(): self.engine.run_daily_phuc_loi()
            if self.daily_opts["pin"].get(): self.engine.run_daily_pin()
            if self.daily_opts["ham_doi"].get(): self.engine.run_daily_ham_doi()
            if self.daily_opts["thu"].get(): self.engine.run_daily_thu()
            if self.daily_opts["kho"].get(): self.engine.run_daily_kho()
            if self.daily_opts["so_tay"].get(): self.engine.run_daily_so_tay()

        # 4. Dùng Vé Sạp (nếu tick chọn)
        if cfg["do_ve_sap"].get():
            if not self.engine.is_running:
                return
            self.append_log(f"-> {slot_label}: Dùng Vé Sạp...")
            self.engine.run_use_ve_sap()

        # 5. Dùng Vé Số / Vé Mật Thất Lạc mặc định 5 vé (5 lần click nút đặt vé)
        if cfg["do_ve_so"].get():
            if not self.engine.is_running:
                return
            self.append_log(f"-> {slot_label}: Dùng 5 Vé Số (Vé Mật Thất)...")
            self.engine.run_use_ve_mat(ticket_count=5)

        # 6. Dùng / Mở Chìa Khóa Raid (nếu tick chọn)
        if cfg.get("do_open_keys", None) and cfg["do_open_keys"].get():
            if not self.engine.is_running:
                return
            s_num = slot_num if slot_num is not None else 1
            self._execute_character_box_key(s_num, slot_label)

    # --------------------------------------------------------------------------
    # CHẠY RIÊNG NHÂN VẬT HIỆN TẠI (ĐANG Ở SẴN SẢNH - KHÔNG ĐỔI SLOT)
    # --------------------------------------------------------------------------
    def start_current_character_only(self):
        """
        Chạy toàn bộ tiến trình (Chinh Phạt, Ngục Tối, Daily, Vé Sạp, Vé Số) cho DUY NHẤT
        nhân vật hiện tại đang ở sẵn trong Sảnh Chính (TUYỆT ĐỐI KHÔNG ĐỔI NHÂN VẬT).
        """
        if self.engine.is_running:
            messagebox.showinfo("Đang chạy", "Tool đang chạy!")
            return

        self.save_config()
        self.engine.lock_game_window()
        self.engine.is_running = True
        self.status_var.set("Đang chạy NV hiện tại...")

        def _current_worker():
            try:
                self.engine.activate_game_input()
                self.append_log("\n==============================================")
                self.append_log("   CHẠY RIÊNG NHÂN VẬT HIỆN TẠI (ĐANG Ở SẢNH) ")
                self.append_log("==============================================")

                slot_ref = self._safe_int(self.test_slot_var, 1)
                cfg = self.slot_vars.get(slot_ref, self.slot_vars[1])
                self.append_log(
                    f"-> Áp dụng cấu hình theo Slot {slot_ref}: "
                    f"CP={self._safe_int(cfg['cp_times'], 0)}, "
                    f"NT={self._safe_int(cfg['nt_times'], 0)}, "
                    f"Daily={cfg['do_daily'].get()}, "
                    f"Vé Sạp={cfg['do_ve_sap'].get()}, "
                    f"Vé Số={cfg['do_ve_so'].get()}, "
                    f"Mở Chìa={cfg['do_open_keys'].get()}..."
                )

                self._execute_character_plan(f"Slot {slot_ref} (Hiện tại)", cfg, slot_num=slot_ref)

                self.append_log("\n==============================================")
                self.append_log("   HOÀN THÀNH TIẾN TRÌNH NHÂN VẬT HIỆN TẠI!   ")
                self.append_log("==============================================")
                messagebox.showinfo("Hoàn tất", "Đã hoàn thành toàn bộ tiến trình cho nhân vật hiện tại!")

            except KeyboardInterrupt:
                self.append_log("\n[!] Đã dừng chương trình theo yêu cầu của bạn.")
            except Exception as e:
                self.append_log(f"\n[!] Lỗi phát sinh: {e}")
            finally:
                self.engine.is_running = False
                self.status_var.set("Sẵn sàng")

        self.worker_thread = threading.Thread(target=_current_worker, daemon=True)
        self.worker_thread.start()

    # --------------------------------------------------------------------------
    # CHUỖI FULL AUTO HOÀN CHỈNH CHO TỪNG NHÂN VẬT
    # --------------------------------------------------------------------------
    def start_full_auto(self):
        if self.engine.is_running:
            messagebox.showinfo("Đang chạy", "Tool đang chạy!")
            return

        self.save_config()
        self.engine.lock_game_window()
        self.engine.is_running = True
        self.status_var.set("Đang chạy Full Auto...")

        def _full_worker():
            try:
                self.engine.activate_game_input()
                start_slot = max(1, self._safe_int(self.start_slot_var, 1))
                total_chars = self._safe_int(self.total_chars_var, 7)
                already_in_lobby = self.already_in_lobby_var.get()

                self.append_log("\n==============================================")
                self.append_log(f"   BẮT ĐẦU CHẠY TỪ NHÂN VẬT SLOT {start_slot} ĐẾN {total_chars}   ")
                if already_in_lobby:
                    self.append_log(f"   -> Đang ở sẵn NV Slot {start_slot} tại Sảnh (Không đổi ở con đầu)")
                self.append_log("==============================================")

                is_first_character = already_in_lobby

                for slot_num in range(start_slot, total_chars + 1):
                    if not self.engine.is_running:
                        break

                    cfg = self.slot_vars.get(slot_num)
                    if not cfg or not cfg["enabled"].get():
                        self.append_log(f"-> Slot {slot_num}: Tắt (Bỏ qua).")
                        continue

                    self.status_var.set(f"Đang làm NV Slot {slot_num}/{total_chars}")
                    self.append_log(f"\n>>>>>>>> BẮT ĐẦU NHÂN VẬT SLOT {slot_num} <<<<<<<<")

                    # 1. Đổi sang nhân vật này (nếu không phải con đang đứng sẵn ở sảnh)
                    if is_first_character:
                        self.append_log(f"-> Nhân vật Slot {slot_num} đang ở sẵn tại Sảnh. Bắt đầu chạy ngay (không đổi NV)!")
                        is_first_character = False
                    else:
                        self.engine.switch_to_slot(slot_num, total_chars=total_chars, from_screen="lobby", is_direct_test=False)

                    # 2. Thực thi Chinh Phạt, Ngục Tối, Daily, Vé Sạp, Vé Số, Hộp & Chìa
                    self._execute_character_plan(f"Slot {slot_num}", cfg, slot_num=slot_num)

                    self.append_log(f"[OK] XONG TOÀN BỘ CÁC TIẾN TRÌNH CỦA NHÂN VẬT SLOT {slot_num}!")

                self.append_log("\n==============================================")
                self.append_log("       HOÀN TẤT TẤT CẢ CÁC NHÂN VẬT!          ")
                self.append_log("==============================================")
                messagebox.showinfo("Hoàn tất", "Đã chạy xong tất cả các nhân vật được chọn!")

            except KeyboardInterrupt:
                self.append_log("\n[!] Đã dừng chương trình theo yêu cầu của bạn.")
            except Exception as e:
                self.append_log(f"\n[!] Lỗi ngoài dự tính: {e}")
            finally:
                self.engine.is_running = False
                self.status_var.set("Sẵn sàng")

        self.worker_thread = threading.Thread(target=_full_worker, daemon=True)
        self.worker_thread.start()

    def stop_auto(self):
        self.engine.is_running = False
        self.engine.is_paused = False
        self.status_var.set("Đã dừng")
        self.append_log("\n[!] Bấm dừng khẩn cấp.")


def start_gui():
    root = tk.Tk()
    app = AutoSeriaV2App(root)
    root.mainloop()

if __name__ == "__main__":
    start_gui()
