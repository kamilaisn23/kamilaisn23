"""Render real GitHub contribution data as a pink calendar with a hopping bunny."""
import argparse
from datetime import date
import html
from io import BytesIO
import json
import math
import os
from pathlib import Path
import urllib.request

import resvg_py
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
COLORS = ['#f6e0eb', '#efbad1', '#e895b9', '#d673a3', '#b84a82']
LEVELS = {'NONE': 0, 'FIRST_QUARTILE': 1, 'SECOND_QUARTILE': 2, 'THIRD_QUARTILE': 3, 'FOURTH_QUARTILE': 4}
FRAMES = 96
WIDTH, HEIGHT = 1200, 328
FONT = 'DejaVu Sans, Arial, sans-serif'

def fetch_calendar(username):
    token = os.environ.get('GH_TOKEN')
    if not token:
        raise RuntimeError('GH_TOKEN is required to fetch the contribution calendar.')
    query = '''query($login: String!) { user(login: $login) { contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays {
        contributionCount contributionLevel date weekday
      } } }
    } } }'''
    request = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': query, 'variables': {'login': username}}).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'User-Agent': 'pink-bunny-garden'},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        result = json.load(response)
    if result.get('errors'):
        raise RuntimeError('; '.join(e['message'] for e in result['errors']))
    user = result['data']['user']
    if not user:
        raise RuntimeError('GitHub profile was not found.')
    return user['contributionsCollection']['contributionCalendar']

def heart(x, y, scale=.4):
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({scale})"><path d="M0 4C-9-5-17 3-12 10L0 21 12 10C17 3 9-5 0 4Z" fill="#e091b3"/></g>'

def bunny(frame):
    jump = abs(math.sin(frame * math.pi / 8))
    blink = frame % 48 in (34, 35)
    eyes = '<path d="M-7-1q2 2 4 0m6 0q2 2 4 0" fill="none" stroke="#87405f" stroke-width="1.4" stroke-linecap="round"/>' if blink else '<circle cx="-5" cy="-1" r="1.5" fill="#87405f"/><circle cx="5" cy="-1" r="1.5" fill="#87405f"/>'
    return f'''<g stroke="#bc7497" stroke-width="1.5" fill="#fff9fc">
      <ellipse cy="15" rx="10" ry="14"/>
      <ellipse cx="{-7-jump*2}" cy="26" rx="6" ry="3.5" transform="rotate({-jump*18} -7 26)"/>
      <ellipse cx="{7+jump*2}" cy="26" rx="6" ry="3.5" transform="rotate({jump*18} 7 26)"/>
      <ellipse cx="-12" cy="14" rx="3" ry="7" transform="rotate({-20-jump*30} -12 14)"/>
      <ellipse cx="12" cy="14" rx="3" ry="7" transform="rotate({20+jump*30} 12 14)"/>
      <ellipse cx="-7" cy="-19" rx="5" ry="15" transform="rotate(-12 -7 -19)"/>
      <ellipse cx="7" cy="-19" rx="5" ry="15" transform="rotate(12 7 -19)"/>
      <ellipse cx="-7" cy="-20" rx="2.2" ry="10" transform="rotate(-12 -7 -20)" fill="#f2b8ce" stroke="none"/>
      <ellipse cx="7" cy="-20" rx="2.2" ry="10" transform="rotate(12 7 -20)" fill="#f2b8ce" stroke="none"/>
      <ellipse rx="17" ry="13"/>
    </g>
    <ellipse cx="-10" cy="4" rx="3.5" ry="2" fill="#f1acc7"/><ellipse cx="10" cy="4" rx="3.5" ry="2" fill="#f1acc7"/>
    {eyes}<path d="M-1.8 2q1.8-2 3.6 0L0 5Z" fill="#b57192"/>
    <path d="M0 5v2m0 0q-3 3-5 0m5 0q3 3 5 0" fill="none" stroke="#87405f" stroke-width="1" stroke-linecap="round"/>
    <g transform="translate(13 -11) rotate(10)" fill="#df87ab"><path d="M0 0-7-4v8ZM0 0 7-4v8Z"/><circle r="2.4" fill="#f9d3e3"/></g>
    <path d="M-8 12q8 5 16 0v4q-8 5-16 0Z" fill="#eda5c3"/>'''

def render_svg(calendar, frame):
    days = [day for week in calendar['weeks'] for day in week['contributionDays']]
    latest = max(day['date'] for day in days)
    month_labels, cells = [], []
    seen = set()
    for col, week in enumerate(calendar['weeks']):
        for day in week['contributionDays']:
            current = date.fromisoformat(day['date'])
            x, y = 96 + col * 19, 143 + day['weekday'] * 19
            level = LEVELS[day['contributionLevel']]
            label = f"{day['date']}: {day['contributionCount']} contributions"
            cells.append(f'<rect x="{x}" y="{y}" width="15" height="15" rx="4" fill="{COLORS[level]}"><title>{html.escape(label)}</title></rect>')
            key = (current.year, current.month)
            if key not in seen and (current.day <= 7 or not seen):
                seen.add(key)
                if col < len(calendar['weeks']) - 2:
                    month_labels.append(f'<text x="{x}" y="126" fill="#ad7390" font-size="12">{current.strftime("%b")}</text>')
    progress = frame / FRAMES
    x = 70 + progress * 1068
    hop = abs(math.sin(frame * math.pi / 8)) * 29
    legend = ''.join(f'<rect x="{956+i*22}" y="291" width="15" height="15" rx="4" fill="{c}"/>' for i, c in enumerate(COLORS))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
      <title id="title">Kamila's pink contribution garden</title>
      <desc id="desc">{calendar['totalContributions']} GitHub contributions in the rolling year ending {latest}. A pink bunny hops across a calendar; cell colors reflect real contribution levels.</desc>
      <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff4f9"/><stop offset="1" stop-color="#f9dfeb"/></linearGradient><pattern id="dots" width="27" height="27" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#d999b6" opacity=".15"/></pattern></defs>
      <rect width="1200" height="328" rx="22" fill="url(#bg)"/><rect width="1200" height="328" rx="22" fill="url(#dots)"/>
      <g font-family="{FONT}">
        <text x="52" y="51" font-size="28" font-weight="700" fill="#91466b">my little contribution garden</text>
        <text x="54" y="81" font-size="15" fill="#b16e90">{calendar['totalContributions']} contributions in the last year</text>
        <text x="1117" y="53" text-anchor="end" font-size="13" fill="#b16e90">little hops, little progress</text>
        <rect x="44" y="100" width="1112" height="174" rx="16" fill="#fffafb" stroke="#edbed3"/>
        {''.join(month_labels)}{''.join(cells)}
        <g fill="#ad7390" font-size="11"><text x="59" y="175">Mon</text><text x="60" y="213">Wed</text><text x="65" y="251">Fri</text></g>
        <text x="54" y="302" font-size="12" fill="#ac6f8d">GitHub calendar · updated {latest}</text>
        <text x="914" y="303" font-size="12" fill="#ac6f8d">Less</text>{legend}<text x="1080" y="303" font-size="12" fill="#ac6f8d">More</text>
      </g>
      {heart(1142,41,.5)}
      <ellipse cx="{x:.2f}" cy="241" rx="{15-hop*.15:.2f}" ry="3.5" fill="#c781a1" opacity=".18"/>
      <g transform="translate({x:.2f} {207-hop:.2f}) scale(1.15)">{bunny(frame)}</g>
    </svg>'''

def build(calendar):
    days = [d for w in calendar['weeks'] for d in w['contributionDays']]
    if not 50 <= len(calendar['weeks']) <= 54 or not days:
        raise ValueError('Expected a rolling-year contribution calendar.')
    if sum(d['contributionCount'] for d in days) != calendar['totalContributions']:
        raise ValueError('Contribution total does not match the daily data.')
    ASSETS.mkdir(exist_ok=True)
    reference = Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=render_svg(calendar, 48)))).convert('RGB').quantize(colors=128)
    frames = [Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=render_svg(calendar, n)))).convert('RGB').quantize(palette=reference, dither=Image.Dither.NONE) for n in range(FRAMES)]
    transparent = frames[0].getpixel((0, 0))
    frames[0].save(ASSETS / 'bunny-contributions.gif', save_all=True, append_images=frames[1:], duration=90, loop=0, disposal=1, optimize=True, transparency=transparent)
    (ASSETS / 'bunny-contributions.svg').write_text(render_svg(calendar, 48), encoding='utf-8')
    result = Image.open(ASSETS / 'bunny-contributions.gif')
    assert result.n_frames == FRAMES and result.info.get('loop') == 0
    assert result.convert('RGBA').getpixel((0, 0))[3] == 0
    print(f"Rendered {calendar['totalContributions']} contributions across {len(calendar['weeks'])} weeks; {result.n_frames} animation frames.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--calendar', type=Path, help='Use a local GitHub calendar response for previewing.')
    args = parser.parse_args()
    data = json.loads(args.calendar.read_text(encoding='utf-8-sig')) if args.calendar else fetch_calendar(os.environ.get('PROFILE_USERNAME', 'kamilaisn23'))
    build(data)
