---
name: wechat-messenger
description: Send results and messages to your local WeChat account. Use when you need to output the final answer or specific data to your logged-in WeChat client (e.g., to "File Transfer" or a specific contact).
---

# WeChat Messenger

This skill allows you to send text output directly to your local WeChat desktop client. It works by automating the UI to search for a contact and send a message.

## Tools

### send_to_wechat

Sends a message to a specific WeChat contact (defaults to "File Transfer").

- **Arguments**:
  - `message`: The text to send.
  - `contact` (optional): The name of the contact or group to search for (default: "File Transfer").

## Workflow

1.  Ask the user for their preferred contact name if not sending to "File Transfer".
2.  Use the `send_to_wechat` tool to deliver the message.
3.  Confirm with the user that the message was sent.

### Example

"Send the summary of my codebase to my WeChat."
-> Call `send_to_wechat(message: [summary text], contact: "File Transfer")`

## Troubleshooting

-   **WeChat must be running** and logged in for this skill to work.
-   The script uses standard UI automation. If the WeChat window is minimized to the system tray (without a window), it might fail to bring it to the foreground. Ensure the main window is at least open in the background.
-   If the search for "File Transfer" fails, you can try providing the Chinese name "文件传输助手".
