---
name: wechat-messenger
description: Send results and messages to your local WeChat account via a robust Python bridge. Use when you need to output data to WeChat contacts (like "Bobby Choi") or "File Transfer" without UI interference.
---

# WeChat Messenger (Headless Bridge)

This skill allows you to send text output directly to your local WeChat desktop client using a surgical Python bridge (`uiautomation`). 

## ðŸŒŸ Key Features
- **âš¡ Atomic Delivery**: Uses high-speed clipboard injection to bypass physical keyboard interference.
- **ðŸ›¡ï¸ Absolute Zero Aggression**: Forces WeChat to front and locks hardware input (Requires Admin).
- **ðŸ‘ï¸ Chart-Eye Visuals**: Automatically captures and analyzes screenshots of charts posted in chats.
- **ðŸ§  Universal Intelligence**: Dynamic 4-way research synthesis for professional replies.

## Tools

### send_to_wechat
Sends a message to a specific WeChat contact.
- **Arguments**: `message`, `contact` (default: "File Transfer").

### help_me_reply
Performs deep context extraction and intelligence synthesis to draft a reply.
- **Arguments**:
  - `chat_name`: The name of the group or contact.
  - `intensity`: `quick` (1 search), `standard` (2 searches), `deep` (4 searches + research skill).
- **Workflow**: 
  1. Scrapes last 30 messages.
  2. Captures visual data from recent photos.
  3. Fuses 4-way parallel research with internal reasoning.
  4. Pastes draft into chat (Halt Mode).

## Setup Requirements
1.  **WeChat must be running** and logged in.
2.  **Python 3.x** with `uiautomation`, `pyperclip`, and `Pillow`.

---
Bobby Choi, Sovereign | Opal, Architect
