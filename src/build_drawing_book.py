import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas

PAGE_WIDTH, PAGE_HEIGHT = letter  # 8.5 x 11 inches
BASE_DIR = Path(__file__).resolve().parent.parent


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, page_count):
        page_num = self._pageNumber
        if page_num <= 2 or page_num == page_count:
            return
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        self.drawCentredString(
            PAGE_WIDTH / 2.0,
            0.35 * inch,
            f"Learn to Draw: English & French  •  Page {page_num}"
        )
        self.restoreState()


def get_margins(page_num):
    if page_num % 2 == 1:
        return 0.625 * inch, 0.5 * inch
    return 0.5 * inch, 0.625 * inch


def draw_tracing_line(c, x, y, width, word_text):
    c.saveState()
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(x, y + 0.45 * inch, x + width, y + 0.45 * inch)
    c.line(x, y, x + width, y)

    c.setDash(4, 4)
    c.setStrokeColor(colors.grey)
    c.line(x, y + 0.225 * inch, x + width, y + 0.225 * inch)
    c.setDash()

    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.Color(0.78, 0.78, 0.78))
    c.drawString(x + 0.2 * inch, y + 0.08 * inch, word_text)
    c.drawString(x + width * 0.52, y + 0.08 * inch, word_text)
    c.restoreState()


def draw_front_matter(c):
    left, right = get_margins(1)
    center_x = (left + (PAGE_WIDTH - right)) / 2

    c.setLineWidth(2)
    c.roundRect(left, 0.6 * inch, PAGE_WIDTH - left - right, PAGE_HEIGHT - 1.2 * inch, 16)

    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(center_x, PAGE_HEIGHT - 2.0 * inch, "LEARN TO DRAW:")
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(center_x, PAGE_HEIGHT - 2.55 * inch, "ENGLISH & FRENCH")

    c.setFont("Helvetica", 15)
    c.drawCentredString(center_x, PAGE_HEIGHT - 3.2 * inch, "30 Step-by-Step Animals, Food & Everyday Objects")
    c.drawCentredString(center_x, PAGE_HEIGHT - 3.5 * inch, "for Kids Ages 4–8")

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(center_x, PAGE_HEIGHT - 5.2 * inch, "This Drawing Book Belongs To / Ce livre appartient à :")
    c.line(left + 1.0 * inch, PAGE_HEIGHT - 5.9 * inch, PAGE_WIDTH - right - 1.0 * inch, PAGE_HEIGHT - 5.9 * inch)

    c.setFont("Helvetica", 11)
    c.drawCentredString(center_x, 1.3 * inch, "By Olanrewaju Michael Akinbode")
    c.showPage()

    left, right = get_margins(2)
    center_x = (left + (PAGE_WIDTH - right)) / 2

    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(center_x, PAGE_HEIGHT - 1.4 * inch, "How to Use This Book / Comment utiliser ce livre")

    steps = [
        ("1. Look & Say / Regarde et dis", "Say the English and French words out loud using the easy pronunciation guide."),
        ("2. Follow the Shapes / Suis les formes", "Look at the step-by-step shapes on the left page to see how each picture is built."),
        ("3. Trace the Words / Trace les mots", "Practice your handwriting by tracing both the English and French names."),
        ("4. Draw & Color / Dessine et colorie", "Draw your own picture in the big frame on the right page, then color it in!")
    ]

    y_pos = PAGE_HEIGHT - 2.4 * inch
    for title, desc in steps:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left + 0.3 * inch, y_pos, title)
        c.setFont("Helvetica", 12)
        c.drawString(left + 0.3 * inch, y_pos - 0.3 * inch, desc)
        y_pos -= 1.2 * inch

    c.showPage()


def draw_word_spread(c, item, left_page_num):
    left, right = get_margins(left_page_num)
    usable_w = PAGE_WIDTH - left - right
    center_x = left + usable_w / 2

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.darkgrey)
    c.drawString(left, PAGE_HEIGHT - 0.65 * inch, item["unit"].upper())
    c.setFillColor(colors.black)

    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(center_x, PAGE_HEIGHT - 1.15 * inch, f"{item['en']}  /  {item['fr']}")

    c.setFont("Helvetica-Oblique", 13)
    c.drawCentredString(center_x, PAGE_HEIGHT - 1.48 * inch, f"French Pronunciation: ({item['phonetic']})")

    box_top = PAGE_HEIGHT - 1.75 * inch
    box_h = 5.4 * inch
    box_y = box_top - box_h
    c.setLineWidth(1.5)
    c.roundRect(left, box_y, usable_w, box_h, 12)

    rel_img = item.get("image_path", "")
    img_path = BASE_DIR / rel_img if rel_img else None

    if img_path and img_path.exists():
        c.drawImage(
            str(img_path),
            left + 0.15 * inch,
            box_y + 0.15 * inch,
            width=usable_w - 0.3 * inch,
            height=box_h - 0.3 * inch,
            preserveAspectRatio=True,
            anchor="c"
        )
    else:
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(center_x, box_y + box_h - 0.5 * inch, "Step-by-Step Shape Guide:")
        c.setFont("Helvetica", 12)
        c.drawCentredString(center_x, box_y + box_h / 2, item["shapes"])
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.grey)
        c.drawCentredString(center_x, box_y + 0.35 * inch, f"[Place 4-step line art image at: {rel_img}]")
        c.setFillColor(colors.black)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, box_y - 0.35 * inch, "Trace the Words / Trace les mots :")
    draw_tracing_line(c, left, box_y - 1.0 * inch, usable_w, item["en"])
    draw_tracing_line(c, left, box_y - 1.75 * inch, usable_w, item["fr"])

    c.showPage()

    right_page_num = left_page_num + 1
    left, right = get_margins(right_page_num)
    usable_w = PAGE_WIDTH - left - right
    center_x = left + usable_w / 2

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(center_x, PAGE_HEIGHT - 0.85 * inch, f"My Drawing / Mon Dessin : {item['fr']}")

    frame_top = PAGE_HEIGHT - 1.15 * inch
    frame_h = 8.1 * inch
    frame_y = frame_top - frame_h
    c.setLineWidth(2)
    c.roundRect(left, frame_y, usable_w, frame_h, 14)

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(center_x, frame_y - 0.38 * inch, f"★ {item['prompt_en']}")
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(center_x, frame_y - 0.65 * inch, f"★ {item['prompt_fr']}")

    c.showPage()


def draw_certificate(c, page_num):
    left, right = get_margins(page_num)
    usable_w = PAGE_WIDTH - left - right
    center_x = left + usable_w / 2

    c.setLineWidth(3)
    c.roundRect(left, 0.7 * inch, usable_w, PAGE_HEIGHT - 1.4 * inch, 18)

    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(center_x, PAGE_HEIGHT - 2.0 * inch, "CERTIFICATE OF ACHIEVEMENT")
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(center_x, PAGE_HEIGHT - 2.5 * inch, "CERTIFICAT DE RÉUSSITE")

    c.setFont("Helvetica", 14)
    c.drawCentredString(center_x, PAGE_HEIGHT - 3.5 * inch, "Awarded to / Décerné à :")
    c.line(left + 1.0 * inch, PAGE_HEIGHT - 4.3 * inch, PAGE_WIDTH - right - 1.0 * inch, PAGE_HEIGHT - 4.3 * inch)

    c.setFont("Helvetica", 13)
    c.drawCentredString(center_x, PAGE_HEIGHT - 5.2 * inch, "For learning to draw and spell 30 words in English and French!")
    c.drawCentredString(center_x, PAGE_HEIGHT - 5.55 * inch, "Pour avoir appris à dessiner et écrire 30 mots en anglais et en français !")

    c.setFont("Helvetica-Bold", 13)
    c.drawString(left + 0.8 * inch, 2.0 * inch, "Date: ___________________")
    c.drawRightString(PAGE_WIDTH - right - 0.8 * inch, 2.0 * inch, "Signed: Olanrewaju M. Akinbode")
    c.showPage()


def build_pdf(
    json_file=BASE_DIR / "data" / "drawing_vocab.json",
    output_pdf=BASE_DIR / "output" / "Learn_to_Draw_English_French_Ages_4_8.pdf"
):
    json_path = Path(json_file)
    out_path = Path(output_pdf)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        vocab_list = json.load(f)

    c = NumberedCanvas(str(out_path), pagesize=letter)
    draw_front_matter(c)

    current_page = 3
    for item in vocab_list:
        draw_word_spread(c, item, current_page)
        current_page += 2

    draw_certificate(c, current_page)
    c.save()
    print(f"Successfully generated {out_path} ({current_page} pages)!")


if __name__ == "__main__":
    build_pdf()
