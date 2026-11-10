from pathlib import Path
import textwrap

OUT = Path('output/pdf/dummy_company_handbook.pdf')
OUT.parent.mkdir(parents=True, exist_ok=True)

PAGES = [
    ('Company overview and teams', '''Apex Demo Works is a fictional company created only to test document upload, indexing, retrieval, citations, and source excerpts in the Apex Enterprise AI demo. It has no connection to a real company and these sample rules are not intended for actual workplace use.

The company builds inventory planning software for small retailers. Its three demonstration teams are Product Engineering, Customer Support, and Operations. Product Engineering maintains the web application and releases approved changes. Customer Support answers customer questions from the shared help desk. Operations maintains the sample inventory catalog and coordinates internal requests.

The main office is called Cedar House and is located in the fictional city of Sampleton. The company also has remote employees. Each team has a team lead who assigns work, reviews schedules, and helps resolve routine blockers. The People Desk handles general workplace questions. The IT Desk handles account access, laptop setup, and security incidents.

For this sample handbook, normal internal announcements are posted in the Apex Bulletin channel. Urgent service interruptions are posted in the Incident Room channel. Employees should use the help desk for customer issues and should not post customer personal information in public channels. These channel names, departments, and processes exist only for this testing document.'''),
    ('Working hours and time off', '''The standard schedule at Apex Demo Works is Monday through Friday, 9:00 AM to 5:30 PM Sampleton Time. The schedule includes a 30-minute meal break. The office opens at 8:30 AM and closes at 6:00 PM. Remote employees follow the same core hours unless their team lead approves a different schedule in writing.

Employees should keep their team calendar accurate and mark planned appointments as unavailable. If an employee will be late or absent unexpectedly, they should notify their team lead in the Incident Room channel before 9:00 AM when practical. The team lead records the schedule change in the weekly roster. A calendar entry by itself does not count as approval for planned leave.

The fictional sample leave allowance is 18 paid days per calendar year, plus 6 personal days. Planned leave requests should be submitted in the People Desk portal at least 5 business days before the first day away. The team lead responds within 2 business days. If the request is urgent, the employee should contact the People Desk directly and explain the timing.

Unused sample leave expires at the end of the calendar year and is not paid out. This rule is invented for the sample document. It should not be treated as legal or real employer guidance. Questions about the sample process go to people@apex-demo.example.'''),
    ('Information security practices', '''Apex Demo Works employees must use multi-factor authentication on company accounts. Passwords must be unique to the company account and must not be shared with coworkers, customers, or family members. A password manager approved by the fictional IT Desk may be used to store credentials.

Company laptops must use full-disk encryption, automatic screen locking after 5 minutes of inactivity, and current operating-system security updates. Employees should lock their screen whenever they step away. Sensitive files should be stored in the approved company drive rather than copied to personal storage, personal email, or removable media.

Unexpected login prompts, suspicious attachments, or suspected account compromise should be reported to security@apex-demo.example within 30 minutes of discovery. Employees should not investigate suspicious links themselves or forward suspicious attachments to other people. The IT Desk will confirm receipt within 1 business hour during normal office hours.

Customer records in this fictional example may be accessed only when needed for assigned work. Do not include customer names, account numbers, or private support content in public chat channels. These controls are test content for a demo system, not real security policy.'''),
    ('Equipment and remote work', '''The fictional company issues a laptop, power adapter, and security key to each full-time employee. The employee is responsible for keeping issued equipment in a secure place and using it for assigned work. Equipment should not be lent to friends or family. The IT Desk keeps the equipment inventory and records each handoff.

Remote employees should work from a private location and use a trusted network. Public Wi-Fi may be used only with the company virtual private network enabled. Company files should not be downloaded to a shared computer. When a household member needs to use the desk, the employee should lock the laptop and put away printed company material.

A lost laptop or security key must be reported to it@apex-demo.example within 30 minutes. The employee should provide the last known location and the approximate time it went missing. The IT Desk disables the affected access key and arranges a replacement. Damaged equipment should be reported within 1 business day; employees should not attempt hardware repairs themselves.

At the end of employment, the laptop, adapter, and security key should be returned to the IT Desk within 3 business days. This is fictional sample content for testing retrieval and citation behavior.'''),
    ('Purchases, travel, and support contacts', '''Apex Demo Works uses fictional sample purchase limits for this handbook. A team lead may approve routine software or office purchases up to 250 Demo Credits. Purchases above 250 Demo Credits require written approval from both the team lead and Operations. No employee may split one purchase into smaller orders to avoid the approval limit.

Travel should be requested in the People Desk portal at least 10 business days before departure. The request must include the business purpose, destination, dates, and estimated cost. Operations responds within 3 business days. Air travel is limited to standard economy class in this fictional example. Receipts should be submitted within 5 business days after returning.

For sample reimbursement questions, contact expenses@apex-demo.example. For schedule or leave questions, contact people@apex-demo.example. For account access, lost devices, or suspicious activity, contact it@apex-demo.example. For a customer support issue, use the shared help desk and include the ticket number rather than personal customer details.

If this sample handbook does not answer a question, employees should ask their team lead and then the relevant support desk. These departments, Demo Credits, contacts, and procedures are invented solely for testing a demo knowledge assistant.'''),
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
    commands = ['BT', '/F1 17 Tf', '54 748 Td', f'({title}) Tj', '/F1 9 Tf', '0 -24 Td', '(APEX DEMO WORKS | FICTIONAL TEST HANDBOOK) Tj', '0 -24 Td', '/F1 10 Tf', '14 TL']
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
