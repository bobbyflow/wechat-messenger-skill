---
name: wechat-messenger
description: Send results and images to your local WeChat account via a robust Python bridge. Use when you need to output data to WeChat contacts (like "Bobby Choi") or "油品组会群 Oil" without UI interference.
---

# WeChat Messenger (OpenClaw Edition)

This skill allows OpenClaw agents to send text output and images directly to your local WeChat desktop client using a surgical Python bridge.

## Key Features
- **Atomic Delivery:** Uses high-speed clipboard pasting to bypass hardware interference.
- **Auto-Launch:** Automatically wakes up WeChat from the system tray or launches it if closed.
- **Context Awareness:** Automatically follows focus if a chat is popped out into a small window.

## Tools

### send_to_wechat
Sends a message or image to a specific WeChat contact.

- **Arguments**:
  - `contact`: The name of the contact or group (e.g., "Bobby Choi").
  - `message` (optional): The text to send.
  - `image` (optional): The absolute local path to an image file.
  - `send` (optional): Set to true to actually transmit (default: false / Halt mode).

- **Command**:
  `python C:\Users\choib\.openclaw\skills\wechat-messenger\scripts\wechat_bridge.py "<contact>" [--message "<message>"] [--image "<image_path>"] [--send]`

## Context & Aliases
- **"Oil"**: Target full name "油品组会群 Oil".

## Workflow
1.  Identify the target contact and content (text or image).
2.  Use the `send_to_wechat` command to deliver.
3.  By default, the script stays in **Halt Mode** (types/pastes but doesn't send). Include `--send` for full automation.
