
import win32gui
import win32con
import win32api
import win32process
import time
import sys
import os
import uiautomation as auto
import pyperclip
import ctypes
from PIL import ImageGrab

user32 = ctypes.windll.user32

def force_focus(hwnd):
    if not hwnd or not win32gui.IsWindow(hwnd): return False
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        foreground_thread_id = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[0]
        current_thread_id = win32api.GetCurrentThreadId()
        if foreground_thread_id != current_thread_id:
            win32process.AttachThreadInput(current_thread_id, foreground_thread_id, True)
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            win32gui.SetForegroundWindow(hwnd)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32process.AttachThreadInput(current_thread_id, foreground_thread_id, False)
        else:
            win32gui.SetForegroundWindow(hwnd)
        for _ in range(10):
            if win32gui.GetForegroundWindow() == hwnd: return True
            time.sleep(0.1)
    except: pass
    return False

def capture_element(rect, output_path):
    """Takes a surgical screenshot of specific coordinates."""
    try:
        # rect is (left, top, right, bottom)
        img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
        img.save(output_path)
        return True
    except Exception as e:
        print(f"Capture Error: {e}")
        return False

def read_universal_context(target_chat, message_count=30, capture_images=True):
    hwnd = win32gui.FindWindow("WeChatMainWndForPC", None)
    if not hwnd:
        print("ERROR: WeChat not running")
        return
    
    force_focus(hwnd)
    main_win = auto.ControlFromHandle(hwnd)
    
    # --- ATOMIC SEARCH ---
    search_box = main_win.EditControl(Name="Search")
    if not search_box.Exists(0):
        win32api.keybd_event(0x11, 0, 0, 0)
        win32api.keybd_event(0x46, 0, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(0x46, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        search_box = main_win.EditControl(Name="Search")

    if search_box.Exists(0):
        search_box.Click(simulateMove=False)
        pyperclip.copy(target_chat)
        # Clear & Paste
        win32api.keybd_event(0x11, 0, 0, 0)
        win32api.keybd_event(0x41, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x08, 0, 0, 0)
        win32api.keybd_event(0x08, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        win32api.keybd_event(0x11, 0, 0, 0)
        win32api.keybd_event(0x56, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        win32api.keybd_event(0x0D, 0, 0, 0)
        win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        time.sleep(1.5) # UI Sync
        
        messages_list = main_win.ListControl(Name="消息")
        if not messages_list.Exists(0):
            messages_list = main_win.ListControl(Name="Messages")
            
        if messages_list.Exists(0):
            all_msgs = messages_list.GetChildren()
            slice_msgs = all_msgs[-message_count:]
            
            print(f"--- CONTEXT PACKAGE: {target_chat} ---")
            img_count = 0
            for i, msg in enumerate(slice_msgs):
                msg_text = msg.Name
                print(f"MSG_{i}: {msg_text}")
                
                # --- CHART-EYE TRIGGER ---
                if capture_images and "[图片]" in msg_text or "[Photo]" in msg_text:
                    # Look for the actual image control inside the list item
                    # In WeChat, the image is often a button or child control
                    img_ctrl = msg.ButtonControl(searchDepth=2)
                    if img_ctrl.Exists(0):
                        rect = img_ctrl.BoundingRectangle
                        output_path = os.path.join(os.environ["TEMP"], f"wechat_crop_{img_count}.png")
                        if capture_element(rect, output_path):
                            print(f"CHART_EYE_CROP: {output_path}")
                            img_count += 1
            print("--- END PACKAGE ---")
        else:
            print("ERROR: Messages list not found")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("chat_name")
    parser.add_argument("--count", type=int, default=30)
    args = parser.parse_args()
    read_universal_context(args.chat_name, args.count)
