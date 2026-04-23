from re import sub

import fitz


def remove_repeated_new_lines(text: str) -> str:
    return sub(r"\n(?:\s*\n)+", "\n", text)


def remove_repeated_whitespaces(text: str) -> str:
    return sub(r" {2,}", " ", text)


def get_pdf_text_from_stream(stream: bytes) -> str:
    with fitz.open(stream=stream, filetype="pdf") as doc:
        cumulative = ""
        for page in doc:
            text = page.get_text()
            if isinstance(text, str):
                cumulative += text

    result = remove_repeated_new_lines(cumulative)
    result = remove_repeated_whitespaces(result)
    return result.strip()
