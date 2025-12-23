# notes_ocr.py
from __future__ import annotations

import base64
from typing import List

try:
    from generator.openai_client import get_client
except ImportError:
    # helper if needed, but usually generator is available
    from openai import OpenAI
    def get_client():
        return OpenAI()

# _client is now retrieved lazily



def _image_to_data_url(file_obj) -> str:
    """Convert a Streamlit UploadedFile (or file-like) to a data: URL for vision."""
    file_bytes = file_obj.read()
    mime_type = getattr(file_obj, "type", "image/png") or "image/png"
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


def extract_text_from_note_images(images: List) -> str:
    """
    Extract and lightly clean text from handwritten note images.

    `images` should be a list of Streamlit UploadedFile objects.
    Returns one combined text block.
    """
    if not images:
        return ""

    all_chunks: list[str] = []

    for idx, img_file in enumerate(images, start=1):
        # Important: reset file pointer in case it was read before
        try:
            img_file.seek(0)
        except Exception:
            pass

        data_url = _image_to_data_url(img_file)
        label = getattr(img_file, "name", f"Image {idx}")

        try:
            client = get_client()
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Transcribe the handwritten notes in this image as clean, plain text. "
                                    "Fix obvious spelling mistakes, but do not add new ideas or explanations. "
                                    "Use short bullet points where it helps readability."
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url},
                            },
                        ],
                    }
                ],
                temperature=0.1,
            )

            text = (resp.choices[0].message.content or "").strip()
            chunk = f"=== Notes from {label} ===\n{text}"
        except Exception as e:
            chunk = f"=== Notes from {label} ===\n[Error reading this image: {e}]"

        all_chunks.append(chunk)

    return "\n\n".join(all_chunks).strip()
