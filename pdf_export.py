import re
from fpdf import FPDF


def remove_emojis(text: str) -> str:
    """Strip emoji and non-Latin characters that Helvetica can't render."""
    # Remove emoji unicode ranges
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F700-\U0001F77F"  # alchemical symbols
        u"\U0001F780-\U0001F7FF"  # geometric shapes extended
        u"\U0001F800-\U0001F8FF"  # supplemental arrows
        u"\U0001F900-\U0001F9FF"  # supplemental symbols & pictographs
        u"\U0001FA00-\U0001FA6F"  # chess symbols
        u"\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
        u"\U00002702-\U000027B0"  # dingbats
        u"\U000024C2-\U0001F251"  # enclosed characters
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub("", text)
    # Keep only printable Latin-1 characters (safe for Helvetica)
    text = "".join(c for c in text if ord(c) < 256)
    return text.strip()


def markdown_to_pdf_bytes(report_text: str, title: str = "Research Report") -> bytes:
    """
    Converts a markdown research report to a PDF and returns the bytes.
    Handles: # headings, ## headings, ### headings, bold (**text**),
    bullet lists (- item), numbered lists, horizontal rules (---), and plain paragraphs.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # --- Fonts (using built-in fonts for portability) ---
    FONT = "Helvetica"

    def set_h1():
        pdf.set_font(FONT, "B", 20)
        pdf.set_text_color(30, 30, 30)

    def set_h2():
        pdf.set_font(FONT, "B", 15)
        pdf.set_text_color(40, 40, 40)

    def set_h3():
        pdf.set_font(FONT, "B", 12)
        pdf.set_text_color(60, 60, 60)

    def set_body():
        pdf.set_font(FONT, "", 10)
        pdf.set_text_color(50, 50, 50)

    def set_bold_body():
        pdf.set_font(FONT, "B", 10)
        pdf.set_text_color(50, 50, 50)

    def clean_inline(text: str) -> str:
        """Strip markdown bold/italic markers for plain rendering."""
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        text = re.sub(r"`(.+?)`", r"\1", text)
        # Remove markdown links [text](url) -> text
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        return remove_emojis(text)

    lines = report_text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        i += 1

        # Skip empty lines (add small spacing)
        if not stripped:
            pdf.ln(2)
            continue

        # Horizontal rule ---
        if re.match(r"^-{3,}$", stripped):
            pdf.set_draw_color(180, 180, 180)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
            pdf.ln(4)
            continue

        # H1 heading
        if stripped.startswith("# ") and not stripped.startswith("## "):
            set_h1()
            text = clean_inline(stripped[2:])
            pdf.multi_cell(0, 10, text)
            pdf.ln(3)
            continue

        # H2 heading
        if stripped.startswith("## "):
            set_h2()
            text = clean_inline(stripped[3:])
            pdf.ln(2)
            pdf.multi_cell(0, 8, text)
            # Underline effect
            pdf.set_draw_color(100, 100, 100)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(3)
            continue

        # H3 heading
        if stripped.startswith("### "):
            set_h3()
            text = clean_inline(stripped[4:])
            pdf.multi_cell(0, 7, text)
            pdf.ln(1)
            continue

        # Bullet list item
        if stripped.startswith("- ") or stripped.startswith("* "):
            set_body()
            text = clean_inline(stripped[2:])
            pdf.set_x(25)
            pdf.multi_cell(0, 6, f"\u2022  {text}")
            continue

        # Numbered list item  (e.g. "1. something")
        num_match = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if num_match:
            set_body()
            num = num_match.group(1)
            text = clean_inline(num_match.group(2))
            pdf.set_x(25)
            pdf.multi_cell(0, 6, f"{num}. {text}")
            continue

        # Regular paragraph (may contain **bold** inline)
        # Simple approach: render whole line, stripping markdown
        set_body()
        text = clean_inline(stripped)
        pdf.multi_cell(0, 6, text)
        pdf.ln(1)

    return bytes(pdf.output())
