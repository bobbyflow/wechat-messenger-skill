---
name: wechat-messenger
description: Send results and messages to your local WeChat account via a robust Python bridge. Use when you need to output data to WeChat contacts (like "Bobby Choi") or "File Transfer" without UI interference.
---

# WeChat Messenger (Headless Bridge)

This skill allows you to send text output directly to your local WeChat desktop client using a surgical Python bridge (`uiautomation`). 

## Key Features
- **Group Chat Bypass:** Automatically identifies individual contacts in search results, avoiding the common issue of landing in group chats.
- **Background Mode:** Can send messages without stealing focus from your browser (works best if the target contact is **Pinned**).
- **Zero Interruption:** Uses the clipboard to handle large code blocks and complex text instantly.
- **🛡️ Absolute Zero Aggression**: Forces WeChat to front and locks hardware input (Requires Admin).

## Tools

### send_to_wechat
Sends a message to a specific WeChat contact.

- **Arguments**:
  - `message`: The text to send.
  - `contact` (optional): The name of the contact (default: "File Transfer").

- **Command**:
  `python "%USERPROFILE%\.gemini\skills\wechat-messenger\scripts\wechat_bridge.py" "<contact>" "<message>"`

## Setup Requirements
1.  **WeChat must be running** and logged in.
2.  **Pin your favorite contacts:** For the most reliable, "zero-popup" experience, pin the contacts you message frequently (like "Bobby Choi" or "File Transfer").
3.  **Python 3.x** must be installed with `uiautomation` and `pyperclip` (already set up on this system).

## Workflow
1.  Identify the content to be sent.
2.  Call `send_to_wechat` with the message and target name.
3.  **Default (HALT Mode):** The bridge will paste the message into the chat box but MUST NOT transmit it.
4.  **Bypass Rule:** The AI Agent is STRICTLY FORBIDDEN from including the `--send` flag in the command unless the user explicitly uses the phrase **"BYPASS HALT"**.

---
Bobby Choi, Sovereign | Opal, Architect
