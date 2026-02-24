# 🚀 WeChat Messenger Skill for OpenClaw

A surgical, hardware-resilient bridge for automating WeChat Desktop from AI agents (OpenClaw, Gemini CLI, etc.).

## 🌟 Key Features

- **⚡ Atomic Blast Search**: Uses high-speed clipboard injection and hardware-level key events to clear and search contacts in <100ms, effectively bypassing physical keyboard interference.
- **🥷 Stealth Injection**: Delivers messages via high-speed atomic pasting, minimizing the "focus window" and allowing you to keep typing in your browser while the agent works.
- **🛡️ Identity Lock**: Real-time verification of the active chat header before any data is sent, preventing accidental mis-delivery.
- **🔄 Follow-the-Focus**: Automatically detects if a chat is popped out into a separate window and re-binds the automation to that window.
- **🛠️ Self-Healing Launch**: Automatically wakes up WeChat from the system tray or launches the executable if it's closed.

## 📦 Installation

1. **Prerequisites**:
   - Windows OS
   - Python 3.x
   - WeChat Windows Desktop Client installed

2. **Install Dependencies**:
   ```bash
   pip install pypiwin32 uiautomation pyperclip
   ```

3. **Install Skill**:
   ```bash
   gemini skills install https://github.com/bobbyflow/wechat-messenger-skill
   ```

## 🛠 Usage

Once installed, your agent can invoke the bridge using the following command structure:

```bash
python scripts/wechat_bridge.py "Contact Name" --message "Your message here" [--image "path/to/image.png"] [--send]
```

- **Halt Mode (Default)**: Types the message but waits for you to press Enter.
- **Send Mode**: Add the `--send` flag for 100% autonomous transmission.

### Aliases
The skill includes a pre-configured mapping for **"Oil"** which targets the full group name: `油品组会群 Oil`.

## 🔒 Security & Safety
This tool uses local UI Automation. It does **not** hook into WeChat's network protocols or servers, making it significantly safer from account flagging than traditional web-based bots.

---
Engineered by Opal | Systems Architect
