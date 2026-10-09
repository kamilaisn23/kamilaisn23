"""Draw the pink curiosity cards, growth path, and contact buttons."""
from pathlib import Path
import html
import resvg_py

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

def svg(body, height, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-label="{html.escape(title)}">
    <defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#fff9fc"/><stop offset="1" stop-color="#fbe7f0"/></linearGradient></defs>
    <g font-family="Arial, sans-serif" fill="#8c4368">{body}</g></svg>'''

icons = {
    'code': '<path d="m-9-13-16 13 16 13m18-26 16 13-16 13m-5-32-8 38"/>',
    'design': '<rect x="-23" y="-23" width="46" height="46" rx="10"/><path d="m-14 14 5-14 18-18 9 9L0 9Z"/><path d="m9-18 9 9"/>',
    'data': '<ellipse cy="-19" rx="23" ry="9"/><path d="M-23-19v38c0 12 46 12 46 0v-38m-46 19c0 12 46 12 46 0"/>',
    'ai': '<rect x="-24" y="-18" width="48" height="38" rx="12"/><path d="M0-18v-10m-30 20h6m48 0h6m-42 16h24"/><circle cy="-31" r="4"/><circle cx="-10" cy="-3" r="3"/><circle cx="10" cy="-3" r="3"/>',
    'systems': '<rect x="-26" y="-22" width="52" height="15" rx="5"/><rect x="-26" y="3" width="52" height="15" rx="5"/><path d="M-15-15h1m9 0h16m-26 25h1m9 0h16m-10 8v9m-15 0h30"/>',
    'ideas': '<path d="M-12 9C-34-10-12-35 5-27c19 5 24 24 7 36v8h-24Zm0 8h24m-22 8h20m-15 6h10m-33-61-8-7m64 7 8-7m-38-4v-10"/>',
}
topics = [
    ('code', 'Code & applications', 'Web, mobile & useful little tools'),
    ('design', 'Design & experiences', 'Thoughtful interfaces & creative ideas'),
    ('data', 'Data & problem solving', 'Finding patterns, asking better questions'),
    ('ai', 'AI & automation', 'Curious about smarter ways to build'),
    ('systems', 'Systems & technology', 'How software, networks & tools connect'),
    ('ideas', 'Whatever sparks curiosity', 'Always room for something new'),
]
body = '<rect x="1" y="1" width="1198" height="428" rx="26" fill="url(#bg)" stroke="#efc1d6" stroke-width="2"/>'
body += '<text x="40" y="47" font-size="17" font-weight="700" letter-spacing="2.5" fill="#b16a8d">MY CURIOSITY CORNER</text><text x="40" y="79" font-size="17" fill="#aa7391">Things I enjoy exploring — with plenty of room to grow.</text>'
for i, (icon, title, subtitle) in enumerate(topics):
    title, subtitle = html.escape(title), html.escape(subtitle)
    x = 30 + (i % 3) * 386
    y = 108 + (i // 3) * 152
    body += f'''<g transform="translate({x} {y})"><rect width="368" height="134" rx="20" fill="#fffdfd" stroke="#f1cbde"/><circle cx="47" cy="49" r="29" fill="#fbe7f0"/><g transform="translate(47 49) scale(.68)" fill="none" stroke="#ba799b" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">{icons[icon]}</g><text x="88" y="45" font-size="18" font-weight="700">{title}</text><text x="20" y="104" font-size="15" fill="#a66f8c">{subtitle}</text><path d="m335 25 3 6 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1Z" fill="#efd1df"/></g>'''
map_svg = svg(body, 430, 'My interests: code, design, data, AI, systems, and new ideas. These are areas to explore and learn.')
(OUT / 'curiosity-corner.svg').write_text(map_svg, encoding='utf-8', newline='\n')

body = '<rect x="1" y="1" width="1198" height="188" rx="26" fill="url(#bg)" stroke="#efc1d6" stroke-width="2"/><path d="M148 71H1052" stroke="#edbed5" stroke-width="3" stroke-dasharray="5 9"/>'
for x, number, title, sub in [(150,'01','Learn','Stay curious'), (450,'02','Build','Turn ideas into something useful'), (750,'03','Share','Connect & learn together'), (1050,'04','Grow','Keep moving toward my dreams')]:
    title, sub = html.escape(title), html.escape(sub)
    body += f'<circle cx="{x}" cy="71" r="31" fill="#fffdfd" stroke="#dda2be" stroke-width="2"/><text x="{x}" y="78" text-anchor="middle" font-size="21" font-weight="700">{number}</text><text x="{x}" y="129" text-anchor="middle" font-size="20" font-weight="700">{title}</text><text x="{x}" y="158" text-anchor="middle" font-size="14" fill="#a66f8c">{sub}</text>'
journey = svg(body, 190, 'My goals: learn, build, share, and grow. One small step at a time.')
(OUT / 'little-steps.svg').write_text(journey, encoding='utf-8', newline='\n')

for name, label, width in [('contact-linkedin','LinkedIn',180), ('contact-email', 'Say hello',180)]:
    button=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="42" viewBox="0 0 {width} 42" role="img" aria-label="{label}"><rect x="1" y="1" width="{width-2}" height="40" rx="20" fill="#fff0f7" stroke="#e9b1cd"/><path d="M28 17c-7-8-16 2-7 9l7 6 7-6c9-7 0-17-7-9Z" fill="#d391b2" transform="translate(0 -5) scale(.95)"/><text x="98" y="27" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#944b72">{label}</text></svg>'''
    (OUT / f'{name}.svg').write_text(button, encoding='utf-8', newline='\n')

