import io
import os
import re
import xml.etree.ElementTree as ET
from typing import Any

import requests
from dotenv import load_dotenv
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters


def _kebab_to_camel(s: str) -> str:
    s = s.replace(":", "-")
    parts = s.split("-")
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:] if p)


def _jsx_attr_name(name: str) -> str:
    if name == "class":
        return "className"
    if name == "for":
        return "htmlFor"
    return _kebab_to_camel(name)


def _parse_style(style_str: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for chunk in style_str.split(";"):
        chunk = chunk.strip()
        if not chunk or ":" not in chunk:
            continue
        k, v = chunk.split(":", 1)
        k = _kebab_to_camel(k.strip())
        v = v.strip()
        if k:
            out[k] = v
    return out


def _pyobj_to_js(obj: Any) -> str:
    if isinstance(obj, dict):
        items = []
        for k, v in obj.items():
            if re.match(r"^[A-Za-z_$][A-Za-z0-9_$]*$", k):
                key = k
            else:
                key = f'"{k}"'
            items.append(f"{key}: {_pyobj_to_js(v)}")
        return "{ " + ", ".join(items) + " }"
    s = str(obj).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _render_node(el: ET.Element, indent: int = 6) -> str:
    pad = " " * indent
    tag = _strip_ns(el.tag)

    attrs = []
    for k, v in (el.attrib or {}).items():
        k2 = _jsx_attr_name(_strip_ns(k))
        if k2 == "style":
            style_obj = _parse_style(v)
            attrs.append(f'style={{{_pyobj_to_js(style_obj)}}}')
        else:
            v2 = str(v).replace("{", "{{").replace("}", "}}")
            v2 = v2.replace('"', "&quot;")  # safe inside quotes
            attrs.append(f'{k2}="{v2}"')

    children = list(el)
    text = (el.text or "").strip()

    if not children and not text:
        if attrs:
            return f"{pad}<{tag} " + " ".join(attrs) + " />"
        return f"{pad}<{tag} />"

    open_tag = f"{pad}<{tag}"
    if attrs:
        open_tag += " " + " ".join(attrs)
    open_tag += ">"

    lines = [open_tag]

    if text:
        lines.append(pad + "  " + text)

    for child in children:
        lines.append(_render_node(child, indent=indent + 2))
        tail = (child.tail or "").strip()
        if tail:
            lines.append(pad + "  " + tail)

    lines.append(f"{pad}</{tag}>")
    return "\n".join(lines)


def svg_bytes_to_react_component(svg_bytes: bytes, component_name: str = "SvgIcon") -> str:
    svg_str = svg_bytes.decode("utf-8", errors="replace").strip()

    root = ET.fromstring(svg_str)
    root.attrib["__PROPS_SPREAD__"] = "1"
    jsx_svg = _render_node(root, indent=4)
    jsx_svg = jsx_svg.replace('__PROPS_SPREAD__="1"', "{...props}")

    return f"""import React from "react";

export default function {component_name}(props) {{
  return (
{jsx_svg}
  );
}}
"""


load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь мне картинку — я превращу её в SVG.")


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = file.file_path
    file_bytes = requests.get(file_path).content
    response = requests.post(
        API_URL,
        files={"file": ("photo.jpg", file_bytes, "image/jpeg")}
    )
    data = response.json()

    if data.get("status") != "success":
        await update.message.reply_text("❌ Ошибка обработки изображения.")
        return

    svg_url = data.get("svg_url")

    read = requests.get(svg_url)

    await update.message.reply_text(f"🔗 SVG ссылка:\n{svg_url}")
    temp_buffer = io.StringIO()

    jsx_code = svg_bytes_to_react_component(read.content)

    out = io.BytesIO(jsx_code.encode("utf-8"))
    out.name = "SvgIcon.jsx"
    out.seek(0)

    await update.message.reply_document(document=InputFile(out, filename="SvgIcon.jsx"))


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    print(API_URL)
    print("Telegram bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
