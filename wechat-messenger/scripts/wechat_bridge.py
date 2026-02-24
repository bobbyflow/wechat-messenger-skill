import win32gui
import win32con
import win32api
import time
import sys
import os
import subprocess
import uiautomation as auto
import pyperclip
import json

# --- Configuration ---
WECHAT_PATH = r"C:\Program Files\Tencent\WeChat\WeChat.exe"
RETRY_COUNT = 3
TIMEOUT = 5  # Seconds for UI element discovery

def output_result(success, message, data=None):
    """Structured JSON output for Gemini CLI."""
    print(json.dumps({
        "success": success,
        "message": message,
        "data": data or {}
    }, ensure_ascii=False))

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
                return hwnd
    return hwnd

def is_wechat_window(hwnd):
    try:
        class_name = win32gui.GetClassName(hwnd)
        return "ChatWnd" in class_name or class_name == "WeChatMainWndForPC"
    except:
        return False

def get_target_msg_box(win_ctrl):
    """Robust discovery of the message edit box using heuristics."""
    try:
        # We look for the largest EditControl in the bottom half of the window
        win_rect = win_ctrl.BoundingRectangle
        win_height = win_rect.bottom - win_rect.top
        
        candidates = []
        for ctrl, _ in auto.WalkControl(win_ctrl, maxDepth=10):
            if ctrl.ControlTypeName == "EditControl" and ctrl.Name != "Search":
                rect = ctrl.BoundingRectangle
                if rect.top > (win_rect.top + win_height * 0.4): # Bottom 60%
                    area = (rect.right - rect.left) * (rect.bottom - rect.top)
                    candidates.append((area, ctrl))
        
        if candidates:
            # Return the one with the largest area (most likely the message box)
            return sorted(candidates, key=lambda x: x[0], reverse=True)[0][1]
    except Exception as e:
        pass
    return None

def verify_chat_header(win_ctrl, contact):
    """Verify that the current chat window matches the target contact."""
    try:
        # The chat header is usually a TextControl or ButtonControl at the top
        win_rect = win_ctrl.BoundingRectangle
        header_boundary = win_rect.top + (win_rect.bottom - win_rect.top) * 0.2
        
        for ctrl, _ in auto.WalkControl(win_ctrl, maxDepth=10):
            if ctrl.ControlTypeName in ["TextControl", "ButtonControl"]:
                rect = ctrl.BoundingRectangle
                if rect.bottom < header_boundary:
                    if contact.lower() in ctrl.Name.lower():
                        return True
    except:
        pass
    return False

def atomic_paste(with_enter=False):
    """Simulate Ctrl+V and optionally Enter with low-level key events."""
    win32api.keybd_event(0x11, 0, 0, 0) # Ctrl down
    win32api.keybd_event(0x56, 0, 0, 0) # V down
    time.sleep(0.05)
    win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0) # V up
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0) # Ctrl up
    
    if with_enter:
        time.sleep(0.1)
        win32api.keybd_event(0x0D, 0, 0, 0) # Enter down
        win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0) # Enter up

def send_wechat_message(contact, message=None, image_path=None, auto_send=False, mute=False):
    if not contact or not contact.strip():
        output_result(False, "Contact name cannot be empty.")
        return False
        
    main_hwnd = ensure_wechat_open()
    if not main_hwnd:
        output_result(False, "WeChat is not running and could not be started.")
        return False

    try:
        # Try to use existing window focus first to avoid aggressive focus stealing
        current_hwnd = win32gui.GetForegroundWindow()
        if not is_wechat_window(current_hwnd):
            try:
                win32gui.ShowWindow(main_hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(main_hwnd)
            except: pass
        
        main_win = auto.ControlFromHandle(main_hwnd)
        
        # 1. Search for contact
        search_box = main_win.EditControl(Name="Search")
        if not search_box.Exists(0.5):
            # Try Ctrl+F if search box isn't immediately visible
            win32api.keybd_event(0x11, 0, 0, 0)
            win32api.keybd_event(0x46, 0, 0, 0) # F
            time.sleep(0.05)
            win32api.keybd_event(0x46, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
            
        if not search_box.Exists(2):
            output_result(False, "Could not find Search box in WeChat.")
            return False

        # Atomic Search Execution
        pyperclip.copy(contact)
        search_box.Click(simulateMove=False)
        time.sleep(0.1)
        
        # Select all and delete to clear previous search
        win32api.keybd_event(0x11, 0, 0, 0)
        win32api.keybd_event(0x41, 0, 0, 0) # Ctrl+A
        win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x08, 0, 0, 0) # Backspace
        win32api.keybd_event(0x08, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        atomic_paste(with_enter=True)
        
        # Wait for search results and selection
        time.sleep(1.0)
        
        # Get the active chat window handle (might be main or a separate window)
        active_hwnd = win32gui.GetForegroundWindow()
        target_hwnd = active_hwnd if is_wechat_window(active_hwnd) else main_hwnd
        target_win = auto.ControlFromHandle(target_hwnd)
        
        # 2. Identity Verification
        if not verify_chat_header(target_win, contact):
             # Fallback: maybe it's "File Transfer" vs "文件传输助手"
             if contact == "File Transfer" and verify_chat_header(target_win, "文件传输助手"):
                 pass
             else:
                 output_result(False, f"Identity Lock failed for '{contact}'. Current chat header mismatch.")
                 return False

        # 3. Message Delivery
        msg_box = get_target_msg_box(target_win)
        if not msg_box:
            output_result(False, "Could not locate the message input box.")
            return False

        msg_box.SetFocus()
        
        # MUTE CHECK (Dry Run)
        if mute:
            output_result(True, f"Mute Mode: Target verified for {contact}. Execution halted.")
            return True

        # Handle Image/File first if provided
        if image_path and os.path.exists(image_path):
            p_path = os.path.abspath(image_path).replace("'", "''")
            # Use PowerShell to put file on clipboard in a way WeChat understands
            subprocess.run(["powershell.exe", "-NoProfile", "-Command", f"Set-Clipboard -Path '{p_path}'"], capture_output=True)
            time.sleep(0.8)
            atomic_paste(with_enter=False)
            time.sleep(1.2) # Wait for file to 'attach'

        if message:
            pyperclip.copy(message)
            msg_box.SetFocus()
            atomic_paste(with_enter=False)
        
        # 4. Final Send
        if auto_send:
            time.sleep(0.3)
            win32api.keybd_event(0x0D, 0, 0, 0) # Enter
            win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)
            output_result(True, f"Message successfully sent to {contact}")
        else:
            output_result(True, f"Message prepared for {contact} (Manual send required)")
            
        return True

    except Exception as e:
        output_result(False, f"Bridge Error: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Robust WeChat Messenger Bridge")
    parser.add_argument("contact", help="Name of the contact or group")
    parser.add_argument("--message", help="Text message to send")
    parser.add_argument("--image", help="Path to image or file to attach")
    parser.add_argument("--send", action="store_true", help="Automatically press Enter to send")
    parser.add_argument("--mute", action="store_true", help="Dry-run mode: Find the box but don't paste or send")
    
    args = parser.parse_args()
    
    if not args.message and not args.image:
        output_result(False, "No message or image provided.")
        sys.exit(1)
        
    send_wechat_message(args.contact, args.message, args.image, auto_send=args.send, mute=args.mute)
