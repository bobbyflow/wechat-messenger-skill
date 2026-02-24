import win32gui
import win32con
import win32api
import win32process
import time
import sys
import os
import subprocess
import uiautomation as auto
import pyperclip

WECHAT_PATH = r"C:\Program Files\Tencent\WeChat\WeChat.exe"

def ensure_wechat_open():
    hwnd = win32gui.FindWindow("WeChatMainWndForPC", None)
    if hwnd and win32gui.IsWindowVisible(hwnd):
        return hwnd
    if os.path.exists(WECHAT_PATH):
        subprocess.Popen([WECHAT_PATH])
        for _ in range(20):
            time.sleep(1)
            hwnd = win32gui.FindWindow("WeChatMainWndForPC", None)
            if hwnd and win32gui.IsWindowVisible(hwnd):
                time.sleep(1)
                return hwnd
    return hwnd

def is_wechat_window(hwnd):
    try:
        class_name = win32gui.GetClassName(hwnd)
        return "ChatWnd" in class_name or class_name == "WeChatMainWndForPC"
    except:
        return False

def get_target_msg_box(win_ctrl):
    max_area = 0
    target = None
    try:
        win_rect = win_ctrl.BoundingRectangle
        win_height = win_rect.bottom - win_rect.top
        for ctrl, _ in auto.WalkControl(win_ctrl, maxDepth=15):
            if ctrl.ControlTypeName == "EditControl" and ctrl.Name != "Search":
                rect = ctrl.BoundingRectangle
                if rect.top > (win_rect.top + win_height * 0.5):
                    area = (rect.right - rect.left) * (rect.bottom - rect.top)
                    if area > max_area:
                        max_area = area
                        target = ctrl
    except:
        pass
    return target

def verify_chat_header(win_ctrl, contact):
    try:
        win_rect = win_ctrl.BoundingRectangle
        top_boundary = win_rect.top + (win_rect.bottom - win_rect.top) * 0.3
        for ctrl, _ in auto.WalkControl(win_ctrl, maxDepth=15):
            if (ctrl.ControlTypeName in ["TextControl", "ButtonControl"]):
                if ctrl.BoundingRectangle.bottom < top_boundary:
                    if contact.lower() in ctrl.Name.lower():
                        return True
    except:
        pass
    return False

def atomic_paste(with_enter=False):
    """Ultra-fast Ctrl+V."""
    win32api.keybd_event(0x11, 0, 0, 0) # Ctrl
    win32api.keybd_event(0x56, 0, 0, 0) # V
    time.sleep(0.05)
    win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    if with_enter:
        time.sleep(0.1)
        win32api.keybd_event(0x0D, 0, 0, 0) # Enter
        win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)

def send_wechat_message(contact, message=None, image_path=None, auto_send=False):
    main_hwnd = ensure_wechat_open()
    if not main_hwnd: return False

    try:
        try:
            win32gui.ShowWindow(main_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(main_hwnd)
        except: pass
        
        time.sleep(0.5)
        main_win = auto.ControlFromHandle(main_hwnd)
        search_box = main_win.EditControl(Name="Search")
        if not search_box.Exists(0):
            win32api.keybd_event(0x11, 0, 0, 0)
            win32api.keybd_event(0x46, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(0x46, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.3)
            search_box = main_win.EditControl(Name="Search")

        if search_box.Exists(0):
            # --- ATOMIC BLAST SEARCH ---
            print("Executing Atomic Blast Search...")
            pyperclip.copy(contact)
            search_box.Click(simulateMove=False)
            time.sleep(0.1)
            
            # Atomic Clear
            win32api.keybd_event(0x11, 0, 0, 0)
            win32api.keybd_event(0x41, 0, 0, 0) # Ctrl+A
            time.sleep(0.05)
            win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(0x08, 0, 0, 0) # Backspace
            win32api.keybd_event(0x08, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            atomic_paste(with_enter=True)
            time.sleep(1.2)
            
            active_hwnd = win32gui.GetForegroundWindow()
            target_hwnd = active_hwnd if is_wechat_window(active_hwnd) else main_hwnd
            target_win = auto.ControlFromHandle(target_hwnd)
            
            # Header Verification (No Escape)
            if not verify_chat_header(target_win, contact):
                print(f"ABORT: Identity Lock failed for '{contact}'.")
                return False

            msg_box = get_target_msg_box(target_win)
            if msg_box:
                msg_box.SetFocus()
                time.sleep(0.2)
                
                if image_path and os.path.exists(image_path):
                    p_path = image_path.replace("'", "''")
                    subprocess.run(["powershell.exe", "-NoProfile", "-Command", f"Set-Clipboard -Path '{p_path}'"])
                    time.sleep(1.0)
                    atomic_paste(with_enter=False)
                    time.sleep(1.5)

                if message:
                    print("Pasting message via Atomic Paste...")
                    pyperclip.copy(message)
                    msg_box.SetFocus()
                    atomic_paste(with_enter=False)
                
                if auto_send:
                    time.sleep(0.5)
                    win32api.keybd_event(0x0D, 0, 0, 0)
                    win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)
                    print(f"Successfully SENT to {contact}")
                else:
                    print(f"DONE: Message ready for {contact}. (Halt mode)")
                return True
        return False
    except Exception as e:
        print(f"Atomic Bridge Error: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("contact")
    parser.add_argument("--message", default=None)
    parser.add_argument("--image", default=None)
    parser.add_argument("--send", action="store_true")
    args = parser.parse_args()
    send_wechat_message(args.contact, args.message, args.image, auto_send=args.send)
