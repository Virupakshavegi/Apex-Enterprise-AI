from pathlib import Path
import textwrap

OUT = Path('output/pdf/juniper_trail_customer_playbook.pdf')
OUT.parent.mkdir(parents=True, exist_ok=True)
PAGES = [
    ('Juniper Trail Gear - company overview', '''Juniper Trail Gear is a fictional outdoor equipment company created only to test a document search application. It is not a real business, and the sample policies in this playbook are not real customer or legal guidance.

The company makes hiking backpacks, insulated bottles, and lightweight travel organizers. Its fictional teams are Customer Care, Repairs, Warehouse, and Product Design. Customer Care answers order questions. Repairs handles eligible product repairs. Warehouse packs orders from the Cedar Bay distribution center. Product Design reviews product feedback once each month.

The sample help desk is open Monday through Friday from 8:30 AM to 4:30 PM Cedar Bay Time. Customers can contact help@junipertrail.example. The repair desk uses repairs@junipertrail.example. These reserved example addresses are fictional. The company does not accept phone orders in this test scenario.'''),
    ('Orders and shipping', '''Standard orders are packed within 3 business days after payment is confirmed. Orders placed after 1:00 PM Cedar Bay Time begin processing on the next business day. Standard delivery usually takes 5 to 7 business days after the package leaves the warehouse. These times are sample estimates for this fictional company.

Express orders placed before 1:00 PM Cedar Bay Time are packed the same business day when the item is in stock. Express delivery is estimated at 2 business days after dispatch. Express shipping is unavailable on weekends and on the fictional Cedar Bay public holidays listed in the monthly service notice.

Customers receive a tracking email after the carrier scans the parcel. If tracking has not changed for 4 business days, Customer Care should open a carrier inquiry. Customers should provide the order number, but should not send payment card details by email. A changed delivery address can be requested before the parcel is packed; after dispatch, the carrier controls address changes.'''),
    ('Returns and refunds', '''Unused products in their original packaging may be returned within 30 calendar days of delivery. The customer must request a return label from Customer Care and include the order number. The Warehouse team checks the returned item after it arrives. A refund is issued to the original payment method within 5 business days after inspection.

Products marked Final Sale cannot be returned for a change of mind. A defective product may be reported within 90 calendar days of delivery, including a clear description of the issue and the order number. Customer Care may offer a replacement or refund after the Repairs team confirms the defect. Customers should not mail a product before receiving a return authorization.

Original shipping charges are not refunded for a change-of-mind return. If Juniper Trail Gear shipped the wrong item, Customer Care provides a prepaid return label. Refund timing can vary by the customer's bank after the company submits it. This is fictional sample policy content for search testing only.'''),
    ('Repairs and product care', '''Eligible backpacks have a fictional 2-year warranty covering stitching or buckle defects under normal use. Damage from ordinary wear, accidental cuts, unauthorized alterations, or exposure to open flame is not covered by the sample warranty. Insulated bottles have a 1-year warranty for manufacturing defects, including a lid that fails to seal when assembled as instructed.

To request a repair, customers email repairs@junipertrail.example with the order number, product name, purchase date, and a photo of the issue. The repair desk responds within 3 business days. Once an approved item reaches the workshop, inspection and repair take up to 10 business days. The desk contacts the customer before performing any paid repair.

For routine care, wash backpacks by hand with mild soap and cool water, then air dry away from direct heat. Do not put insulated bottles in a microwave or freezer. Replacement bottle lids are sold separately through the fictional website. This playbook exists solely as a safe, invented document for testing upload, chunking, citations, and retrieval.'''),
]

objects = []
def add_obj(data):
    objects.append(data if isinstance(data, bytes) else data.encode('latin-1'))
    return len(objects)

catalog = add_obj(b'')
pages_root = add_obj(b'')
font = add_obj(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
page_ids, content_ids = [], []
for page_no, (title, body) in enumerate(PAGES, 1):
    lines = []
    for paragraph in body.splitlines():
        lines.extend(textwrap.wrap(paragraph, 96, break_long_words=False, break_on_hyphens=False) if paragraph.strip() else [''])
    commands = ['BT', '/F1 17 Tf', '54 748 Td', f'({title}) Tj', '/F1 9 Tf', '0 -24 Td', '(JUNIPER TRAIL GEAR | FICTIONAL TEST PLAYBOOK) Tj', '0 -24 Td', '/F1 10 Tf', '14 TL']
    for line in lines:
        if line:
            line = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
            commands.append(f'({line}) Tj')
        commands.append('T*')
    commands += ['ET', 'BT', '/F1 8 Tf', '54 30 Td', f'(Fictional sample - page {page_no} of {len(PAGES)}) Tj', 'ET']
    stream = '\n'.join(commands).encode('latin-1')
    content_ids.append(add_obj(b'<< /Length ' + str(len(stream)).encode() + b' >>\nstream\n' + stream + b'\nendstream'))
    page_ids.append(add_obj(b''))

objects[catalog-1] = f'<< /Type /Catalog /Pages {pages_root} 0 R >>'.encode()
objects[pages_root-1] = ('<< /Type /Pages /Kids [' + ' '.join(f'{p} 0 R' for p in page_ids) + f'] /Count {len(page_ids)} >>').encode()
for page_id, content_id in zip(page_ids, content_ids):
    objects[page_id-1] = f'<< /Type /Page /Parent {pages_root} 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 {font} 0 R >> >> /Contents {content_id} 0 R >>'.encode()

pdf = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
offsets = [0]
for n, data in enumerate(objects, 1):
    offsets.append(len(pdf))
    pdf.extend(f'{n} 0 obj\n'.encode() + data + b'\nendobj\n')
xref = len(pdf)
pdf.extend(f'xref\n0 {len(objects)+1}\n'.encode() + b'0000000000 65535 f \n')
for offset in offsets[1:]:
    pdf.extend(f'{offset:010d} 00000 n \n'.encode())
pdf.extend(f'trailer\n<< /Size {len(objects)+1} /Root {catalog} 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
OUT.write_bytes(pdf)
print(f'Created {OUT.resolve()} ({len(pdf)} bytes)')
