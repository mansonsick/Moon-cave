"""Build the three A4 worksheets and a separate answer key.

Chinese is rasterized from the privately supplied font; no font is embedded.
Requires reportlab and Pillow. Output geometry is recorded for future scanning.
"""

import argparse
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
PAGE_W, PAGE_H = A4
FONT_PIXELS = 240
BOX_X = 158
BOX_SIZE = 28
ROW_TOP = 77
ROW_STEP = 29


def answer(q):
    return q['a'] + q['b'] if q['op'] == '+' else q['a'] - q['b']


class PrintSheet:
    def __init__(self, path, font, title):
        self.c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1, invariant=1)
        self.c.setTitle(title)
        self.c.setAuthor('阿通的冒險世界')
        self.font = font
        self.images = {}

    def zh(self, text, x, top, size=14, max_width=None):
        """Place cropped high-resolution Chinese text; x/top are millimetres."""
        if text not in self.images:
            left, upper, right, lower = self.font.getbbox(text)
            pad = 12
            image = Image.new('RGBA', (right-left+2*pad, lower-upper+2*pad), (0, 0, 0, 0))
            ImageDraw.Draw(image).text((pad-left, pad-upper), text, font=self.font, fill='black')
            bounds = image.getbbox()
            assert bounds and bounds[0] > 0 and bounds[1] > 0
            assert bounds[2] < image.width and bounds[3] < image.height
            output = io.BytesIO()
            image.save(output, format='PNG')
            output.seek(0)
            self.images[text] = (ImageReader(output), image.width, image.height)
        image, pxw, pxh = self.images[text]
        width, height = pxw * size / FONT_PIXELS, pxh * size / FONT_PIXELS
        if max_width is not None and width > max_width * mm:
            scale = max_width * mm / width
            width, height = width * scale, height * scale
        assert x * mm + width <= PAGE_W - 10 * mm, (text, width / mm)
        assert (top * mm + height) <= PAGE_H - 7 * mm, text
        self.c.drawImage(image, x*mm, PAGE_H-top*mm-height, width, height, mask='auto')
        return height / mm

    def text(self, text, x, baseline, size=12, font='Helvetica', align='left'):
        self.c.setFillGray(0)
        self.c.setFont(font, size)
        method = {'left': self.c.drawString, 'center': self.c.drawCentredString, 'right': self.c.drawRightString}[align]
        method(x*mm, PAGE_H-baseline*mm, str(text))

    def line(self, x1, top1, x2, top2, width=0.7):
        self.c.setStrokeGray(0)
        self.c.setLineWidth(width)
        self.c.line(x1*mm, PAGE_H-top1*mm, x2*mm, PAGE_H-top2*mm)

    def rect(self, x, top, w, h, fill=False, width=1):
        self.c.setStrokeGray(0)
        self.c.setFillGray(0)
        self.c.setLineWidth(width)
        self.c.rect(x*mm, PAGE_H-(top+h)*mm, w*mm, h*mm, stroke=1, fill=int(fill))

    def dots(self, count, x, top, crossed=0):
        for i in range(count):
            cx, cy = x + (i % 5)*4.6, top + (i // 5)*4.5
            self.c.setLineWidth(0.65)
            self.c.circle(cx*mm, PAGE_H-cy*mm, 1.35*mm, stroke=1, fill=0)
            if i >= count-crossed:
                self.line(cx-1.6, cy+1.6, cx+1.6, cy-1.6, 0.75)

    def symbol(self, kind, x, baseline):
        y = baseline - 3.5
        self.line(x-2.6, y, x+2.6, y, 1.4)
        if kind == '+':
            self.line(x, y-2.6, x, y+2.6, 1.4)
        elif kind == '=':
            self.line(x-2.6, y+2.4, x+2.6, y+2.4, 1.4)

    def qr(self, content, x, top, size=20):
        widget = QrCodeWidget(content, barLevel='M')
        bounds = widget.getBounds()
        side = size * mm
        drawing = Drawing(side, side, transform=[side/(bounds[2]-bounds[0]), 0, 0,
                                                side/(bounds[3]-bounds[1]), 0, 0])
        drawing.add(widget)
        renderPDF.draw(drawing, self.c, x*mm, PAGE_H-(top+size)*mm)


def validate(data):
    questions = [q for gate in data['gates'] for q in gate['questions']]
    assert [len(g['questions']) for g in data['gates']] == [6, 7, 7]
    assert [q['id'] for q in questions] == list(range(1, 21))
    assert sum(q['op'] == '+' for q in questions) == 10
    for q in questions:
        assert q['op'] in ('+', '-') and 0 <= q['a'] <= 10 and 0 <= q['b'] <= 10
        assert 0 <= answer(q) <= 9
    assert [''.join(str(answer(q)) for q in g['questions']) for g in data['gates']] == [
        '637542', '8356917', '7480635']


def student_pdf(data, font, out):
    sheet = PrintSheet(out, font, '阿通與星光寶箱 - 三道門數學探險紙')
    layout = {'story_id': data['story_id'], 'worksheet_id': data['worksheet_id'],
              'layout_version': 1, 'page_mm': [210, 297],
              'coordinate_origin': 'top-left', 'units': 'mm', 'pages': []}
    for page, gate in enumerate(data['gates'], 1):
        sheet.zh(data['title'], 16, 13, 15)
        sheet.zh(gate['label'] + '　' + gate['title'], 16, 25, 24, max_width=153)
        sheet.zh('算一算，把答案寫進右邊的格子。', 16, 44, 14, max_width=177)
        sheet.zh('從上往下，一格寫一個數字。', 16, 53, 13, max_width=177)
        sheet.zh('圓點可用來算題，劃掉的表示拿走。', 16, 62, 11.5, max_width=132)
        sheet.zh('密碼格', 160, 64, 13, max_width=28)
        qr_payload = '|'.join(['aton', data['story_id'], data['worksheet_id'], gate['id']])
        sheet.qr(qr_payload, 174, 12, 21)
        sheet.text(f'G{page}', 184.5, 37, 10, align='center')

        n = len(gate['questions'])
        end = ROW_TOP + (n-1)*ROW_STEP + BOX_SIZE
        markers = [[152, ROW_TOP-4, 3, 3], [191, ROW_TOP-4, 3, 3],
                   [152, end+1, 3, 3], [191, end+1, 3, 3]]
        for marker in markers:
            sheet.rect(*marker, fill=True, width=0)
        page_meta = {'page': page, 'gate_id': gate['id'], 'qr_payload': qr_payload,
                     'marker_rects_mm': markers, 'answer_region_mm': [152, ROW_TOP-4, 42, end-ROW_TOP+8],
                     'slots': []}
        for i, q in enumerate(gate['questions']):
            top = ROW_TOP + i*ROW_STEP
            baseline = top + 12.3
            sheet.text(f'{q["id"]:02d}', 21, baseline-1, 12, font='Helvetica-Bold', align='center')
            sheet.text(q['a'], 49, baseline, 29, align='center')
            sheet.symbol(q['op'], 73, baseline)
            sheet.text(q['b'], 98, baseline, 29, align='center')
            sheet.symbol('=', 123, baseline)
            if q['op'] == '+':
                sheet.dots(q['a'], 39, top+20)
                sheet.dots(q['b'], 87, top+20)
            else:
                sheet.dots(q['a'], 39, top+20, crossed=q['b'])
            sheet.rect(BOX_X, top, BOX_SIZE, BOX_SIZE, width=1.15)
            page_meta['slots'].append({'question_id': q['id'], 'position': i+1,
                'box_mm': [BOX_X, top, BOX_SIZE, BOX_SIZE],
                'inner_crop_mm': [BOX_X+2, top+2, BOX_SIZE-4, BOX_SIZE-4]})
        if n == 6:
            sheet.zh('做完這張，就能開第一道門！', 16, 262, 13, max_width=130)
        sheet.text(f'S03 / M10-v1 / G{page}', 16, 288, 9)
        sheet.text(f'{page} / 3', 194, 288, 9, align='right')
        sheet.c.showPage()
        layout['pages'].append(page_meta)
    sheet.c.save()
    return layout


def answer_pdf(data, font, out):
    sheet = PrintSheet(out, font, '阿通與星光寶箱 - 家長解答')
    sheet.zh('阿通與星光寶箱', 16, 14, 17)
    sheet.zh('解答與列印說明', 16, 28, 27)
    sheet.zh('請與孩子的練習紙分開。', 16, 45, 13)
    for gi, gate in enumerate(data['gates']):
        top = 63 + gi*62
        sheet.line(16, top, 194, top, 0.6)
        sheet.zh(gate['label'] + '　' + gate['title'], 16, top+4, 17, max_width=108)
        sheet.zh('密碼', 143, top+4, 12)
        code = ''.join(str(answer(q)) for q in gate['questions'])
        sheet.text(code, 193, top+19, 21, 'Courier-Bold', align='right')
        for i, q in enumerate(gate['questions']):
            col, row = i//4, i%4
            x = 18 + col*88
            line = f'{q["id"]:02d})   {q["a"]} {q["op"]} {q["b"]} = {answer(q)}'
            sheet.text(line, x, top+29+row*7.8, 14)
    sheet.zh('列印：A4 直向、實際大小、單面。', 16, 255, 13, max_width=177)
    sheet.zh('每題的答案格就是密碼格，不用另外抄寫。', 16, 266, 12, max_width=177)
    sheet.zh('沒有剩下時寫零；空白不代表零。', 16, 276, 12, max_width=177)
    sheet.text('S03 / M10-v1 / ANSWERS', 16, 290, 8.5)
    sheet.text('1 / 1', 194, 290, 8.5, align='right')
    sheet.c.save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--source', type=Path, default=ROOT/'stories/story-03/worksheets/math10-v1.json')
    parser.add_argument('--out', type=Path, default=ROOT.parent/'output/pdf')
    args = parser.parse_args()
    data = json.loads(args.source.read_text(encoding='utf-8'))
    validate(data)
    font = ImageFont.truetype(str(args.font), FONT_PIXELS)
    if font.getname() != ('Bpmf GenRyu Min', 'H'):
        raise ValueError('Use the privately supplied BpmfGenRyuMin-H.ttf.')
    args.out.mkdir(parents=True, exist_ok=True)
    layout = student_pdf(data, font, args.out/'math10-v1.pdf')
    answer_pdf(data, font, args.out/'math10-v1-answers.pdf')
    (args.out/'math10-v1-layout.json').write_text(json.dumps(layout, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Built 3 student pages, 1 answer page and scan geometry. No font file embedded.')


if __name__ == '__main__':
    main()
