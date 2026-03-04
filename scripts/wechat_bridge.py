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
import ctypes

user32 = ctypes.windll.user32

# --- PORTABLE PATH DISCOVERY ---
def find_wechat_path():
    possible_paths = [
        r"C:\Program Files\Tencent\WeChat\WeChat.exe",
        r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Tencent\\WeChat\\WeChat.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Tencent\\WeChat\\WeChat.exe")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return "WeChat.exe" # Fallback to PATH

WECHAT_PATH = find_wechat_path()

def block_input(block=True):
    """Freezes hardware input (Keyboard/Mouse). Requires Admin."""
    try:
        user32.BlockInput(block)
    except:
        pass

def set_topmost(hwnd, is_topmost=True):
    """Forces window to absolute Z-order priority (Always on Top)."""
    if not hwnd or not win32gui.IsWindow(hwnd): return
    z_order = win32con.HWND_TOPMOST if is_topmost else win32con.HWND_NOTOPMOST
    win32gui.SetWindowPos(hwnd, z_order, 0, 0, 0, 0, 
                         win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

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

def force_focus(hwnd, fast=False):
    """Hostile Focus: Uses Thread Attachment and Alt-key bypass to force WeChat to front."""
    if not hwnd or not win32gui.IsWindow(hwnd):
        return False
        
    try:
        # 1. Show and Restore
        if not fast: win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        # 2. Link Threads (The "Input Attachment" Hack)
        foreground_thread_id = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[0]
        current_thread_id = win32api.GetCurrentThreadId()
        
        if foreground_thread_id != current_thread_id:
            win32process.AttachThreadInput(current_thread_id, foreground_thread_id, True)
            
            # 3. The "Alt" Tap Bypass
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            win32gui.SetForegroundWindow(hwnd)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            win32process.AttachThreadInput(current_thread_id, foreground_thread_id, False)
        else:
            win32gui.SetForegroundWindow(hwnd)
            
        # 4. Persistence Loop (Fast vs Thorough)
        iterations = 3 if fast else 15
        for _ in range(iterations):
            if win32gui.GetForegroundWindow() == hwnd:
                if not fast: time.sleep(0.3) # Render wait
                return True
            time.sleep(0.1 if fast else 0.2)
            win32gui.SetForegroundWindow(hwnd)
            
    except Exception as e:
        print(f"Force Focus Error: {e}")
    return False

def send_wechat_message(contact, message=None, image_path=None, auto_send=False):
    main_hwnd = ensure_wechat_open()
    if not main_hwnd: return False

    print("--- INITIATING AGGRESSIVE BRIDGE ---")
    block_input(True)
    set_topmost(main_hwnd, True)
    
    try:
        if not force_focus(main_hwnd):
            print("ABORT: Could not seize focus from previous application.")
            return False
            
        time.sleep(0.2)
        main_win = auto.ControlFromHandle(main_hwnd)
        search_box = main_win.EditControl(Name="Search")
        if not search_box.Exists(0):
            # Try JIT search trigger
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
            time.sleep(1.5) # Wait for search results and UI re-draw
            
            active_hwnd = win32gui.GetForegroundWindow()
            target_hwnd = active_hwnd if is_wechat_window(active_hwnd) else main_hwnd
            target_win = auto.ControlFromHandle(target_hwnd)
            
            # Re-assert dominance on target chat window if it popped out
            set_topmost(target_hwnd, True)
            force_focus(target_hwnd, fast=True)

            msg_box = get_target_msg_box(target_win)
            if msg_box:
                msg_box.SetFocus()
                time.sleep(0.2)
                
                if image_path and os.path.exists(image_path):
                    p_path = image_path.replace("'", "''")
                    subprocess.run(["powershell.exe", "-NoProfile", "-Command", f"Set-Clipboard -Path '{p_path}'"])
                    time.sleep(1.0)
                    force_focus(target_hwnd, fast=True) # JIT Focus
                    atomic_paste(with_enter=False)
                    time.sleep(1.5)

                if message:
                    print("Pasting message via Atomic Paste...")
                    pyperclip.copy(message)
                    msg_box.SetFocus()
                    force_focus(target_hwnd, fast=True) # JIT Focus
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
    finally:
        # ABSOLUTE SAFETY: Unblock user and release Z-order
        set_topmost(main_hwnd, False)
        # Try to find target hwnd again to release it if it popped out
        try:
            active_hwnd = win32gui.GetForegroundWindow()
            if is_wechat_window(active_hwnd):
                set_topmost(active_hwnd, False)
        except: pass
        block_input(False)
        print("--- AGGRESSIVE BRIDGE COMPLETE (Input Released) ---")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("contact")
    parser.add_argument("--message", default=None)
    parser.add_argument("--image", default=None)
    parser.add_argument("--send", action="store_true")
    args = parser.parse_args()
    send_wechat_message(args.contact, args.message, args.image, auto_send=args.send)
