"""Render real GitHub contribution data as a pink calendar with a hopping bunny."""
import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import html
from io import BytesIO
import json
import math
import os
from pathlib import Path
import re
import urllib.request

import resvg_py
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
STATE_PATH = ROOT / '.github/bunny-calendar-state.json'
COLORS = ['#f6e0eb', '#efbad1', '#e895b9', '#d673a3', '#b84a82']
LEVELS = {'NONE': 0, 'FIRST_QUARTILE': 1, 'SECOND_QUARTILE': 2, 'THIRD_QUARTILE': 3, 'FOURTH_QUARTILE': 4}
FRAMES = 96
WIDTH, HEIGHT = 1200, 328
FONT = 'DejaVu Sans, Arial, sans-serif'
PROFILE_TIMEZONE = timezone(timedelta(hours=7), 'Asia/Jakarta')

def fetch_calendar(username, year=None):
    token = os.environ.get('GH_TOKEN')
    if not token:
        raise RuntimeError('GH_TOKEN is required to fetch the contribution calendar.')
    query = '''query($login: String!, $from: DateTime, $to: DateTime) { user(login: $login) { createdAt contributionsCollection(from: $from, to: $to) {
      contributionCalendar { totalContributions weeks { contributionDays {
        contributionCount contributionLevel date weekday
      } } }
    } } }'''
    variables = {'login': username}
    if year is not None:
        variables.update({'from': f'{year}-01-01T00:00:00Z', 'to': f'{year}-12-31T23:59:59Z'})
    request = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': query, 'variables': variables}).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'User-Agent': 'pink-bunny-garden'},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        result = json.load(response)
    if result.get('errors'):
        raise RuntimeError('; '.join(e['message'] for e in result['errors']))
    user = result['data']['user']
    if not user:
        raise RuntimeError('GitHub profile was not found.')
    calendar = user['contributionsCollection']['contributionCalendar']
    calendar['accountCreatedAt'] = user['createdAt']
    return calendar

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

def render_svg(calendar, frame, year=None, updated_at=None):
    days = [day for week in calendar['weeks'] for day in week['contributionDays']]
    today = datetime.now(PROFILE_TIMEZONE).date()
    updated = updated_at or datetime.now(PROFILE_TIMEZONE).strftime('%d %b %Y · %H:%M WIB')
    caption = f"{calendar['totalContributions']} contributions in {year}" if year else f"{calendar['totalContributions']} contributions in the last year"
    month_labels, cells = [], []
    seen = set()
    for col, week in enumerate(calendar['weeks']):
        for day in week['contributionDays']:
            current = date.fromisoformat(day['date'])
            if year is not None and current.year != year:
                continue
            x, y = 96 + col * 19, 143 + day['weekday'] * 19
            level = LEVELS[day['contributionLevel']]
            label = f"{day['date']}: {day['contributionCount']} contributions"
            fill = '#fdf5f9' if current > today else COLORS[level]
            cells.append(f'<rect x="{x}" y="{y}" width="15" height="15" rx="4" fill="{fill}"><title>{html.escape(label)}</title></rect>')
            key = (current.year, current.month)
            if key not in seen and (current.day <= 7 or not seen):
                seen.add(key)
                if col < len(calendar['weeks']) - 2:
                    month_labels.append(f'<text x="{x}" y="126" fill="#ad7390" font-size="12">{current.strftime("%b")}</text>')
    progress = frame / FRAMES
    last_active_column = max(i for i, week in enumerate(calendar['weeks']) if any(date.fromisoformat(day['date']) <= today for day in week['contributionDays']))
    x = 70 + progress * (60 + last_active_column * 19)
    hop = abs(math.sin(frame * math.pi / 8)) * 29
    legend = ''.join(f'<rect x="{956+i*22}" y="291" width="15" height="15" rx="4" fill="{c}"/>' for i, c in enumerate(COLORS))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
      <title id="title">Kamila's pink contribution garden</title>
      <desc id="desc">{html.escape(caption)}. A pink bunny hops across a calendar; cell colors reflect real contribution levels. Updated {updated}.</desc>
      <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff4f9"/><stop offset="1" stop-color="#f9dfeb"/></linearGradient><pattern id="dots" width="27" height="27" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#d999b6" opacity=".15"/></pattern></defs>
      <rect width="1200" height="328" rx="22" fill="url(#bg)"/><rect width="1200" height="328" rx="22" fill="url(#dots)"/>
      <g font-family="{FONT}">
        <text x="52" y="51" font-size="28" font-weight="700" fill="#91466b">my little contribution garden</text>
        <text x="54" y="81" font-size="15" fill="#b16e90">{html.escape(caption)}</text>
        <text x="1117" y="53" text-anchor="end" font-size="13" fill="#b16e90">little hops, little progress</text>
        <rect x="44" y="100" width="1112" height="174" rx="16" fill="#fffafb" stroke="#edbed3"/>
        {''.join(month_labels)}{''.join(cells)}
        <g fill="#ad7390" font-size="11"><text x="59" y="175">Mon</text><text x="60" y="213">Wed</text><text x="65" y="251">Fri</text></g>
        <text x="54" y="302" font-size="12" fill="#ac6f8d">GitHub calendar · updated {updated}</text>
        <text x="914" y="303" font-size="12" fill="#ac6f8d">Less</text>{legend}<text x="1080" y="303" font-size="12" fill="#ac6f8d">More</text>
      </g>
      {heart(1142,41,.5)}
      <ellipse cx="{x:.2f}" cy="241" rx="{15-hop*.15:.2f}" ry="3.5" fill="#c781a1" opacity=".18"/>
      <g transform="translate({x:.2f} {207-hop:.2f}) scale(1.15)">{bunny(frame)}</g>
    </svg>'''

def build(calendar, year=None, updated_at=None):
    days = [d for w in calendar['weeks'] for d in w['contributionDays']]
    if not 50 <= len(calendar['weeks']) <= 54 or not days:
        raise ValueError('Expected a rolling-year contribution calendar.')
    if sum(d['contributionCount'] for d in days) != calendar['totalContributions']:
        raise ValueError('Contribution total does not match the daily data.')
    ASSETS.mkdir(exist_ok=True)
    suffix = f'-{year}' if year else ''
    updated_at = updated_at or datetime.now(PROFILE_TIMEZONE).strftime('%d %b %Y · %H:%M WIB')
    reference = Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=render_svg(calendar, 48, year, updated_at)))).convert('RGB').quantize(colors=128)
    frames = [Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=render_svg(calendar, n, year, updated_at)))).convert('RGB').quantize(palette=reference, dither=Image.Dither.NONE) for n in range(FRAMES)]
    transparent = frames[0].getpixel((0, 0))
    frames[0].save(ASSETS / f'bunny-contributions{suffix}.gif', save_all=True, append_images=frames[1:], duration=90, loop=0, disposal=1, optimize=True, transparency=transparent)
    (ASSETS / f'bunny-contributions{suffix}.svg').write_text(render_svg(calendar, 48, year, updated_at), encoding='utf-8')
    result = Image.open(ASSETS / f'bunny-contributions{suffix}.gif')
    assert result.n_frames == FRAMES and result.info.get('loop') == 0
    assert result.convert('RGBA').getpixel((0, 0))[3] == 0
    print(f"Rendered {calendar['totalContributions']} contributions across {len(calendar['weeks'])} weeks; {result.n_frames} animation frames.")

def refresh_calendar(calendar, year, state):
    key = str(year) if year is not None else 'latest'
    today = datetime.now(PROFILE_TIMEZONE).date()
    payload = {
        'calendar': calendar,
        'renderer': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'date': today.isoformat() if year is None or year >= today.year else None,
    }
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    previous = state.get(key, {})
    suffix = f'-{year}' if year else ''
    assets_exist = all((ASSETS / f'bunny-contributions{suffix}.{extension}').exists() for extension in ('gif', 'svg'))
    if previous.get('fingerprint') == fingerprint and assets_exist:
        print(f"Unchanged {key}: {calendar['totalContributions']} contributions; reused existing animation.")
        return fingerprint[:12]
    updated_at = datetime.now(PROFILE_TIMEZONE).strftime('%d %b %Y · %H:%M WIB')
    build(calendar, year, updated_at)
    state[key] = {'fingerprint': fingerprint, 'updated_at': updated_at}
    return fingerprint[:12]

def update_year_choices(years, versions):
    readme_path = ROOT / 'README.md'
    if not readme_path.exists():
        return
    start, end = '<!-- bunny-years-start -->', '<!-- bunny-years-end -->'
    readme = readme_path.read_text(encoding='utf-8')
    if start not in readme or end not in readme:
        return
    panels = []
    for year in sorted(years, reverse=True):
        panels.append(f'''<details>
<summary><strong>🎀 {year} · click to view</strong></summary>

<p align="center"><img src="assets/bunny-contributions-{year}.gif?v={versions[str(year)]}" alt="Pink bunny contribution calendar for {year}" width="100%" /></p>

<p align="center"><a href="https://github.com/kamilaisn23?tab=overview&amp;from={year}-01-01&amp;to={year}-12-31">View {year} on GitHub</a></p>

</details>''')
    updated = readme.split(start, 1)[0] + start + '\n\n' + '\n\n'.join(panels) + '\n\n' + end + readme.split(end, 1)[1]
    updated = re.sub(r'(src="assets/bunny-contributions\.gif)(?:\?v=[^"]*)?(\")', lambda match: match[1] + '?v=' + versions['latest'] + match[2], updated, count=1)
    if updated != readme:
        readme_path.write_text(updated, encoding='utf-8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--calendar', type=Path, help='Use a local GitHub calendar response for previewing.')
    parser.add_argument('--year', type=int, help='Render a specific calendar year.')
    args = parser.parse_args()
    username = os.environ.get('PROFILE_USERNAME', 'kamilaisn23')
    data = json.loads(args.calendar.read_text(encoding='utf-8-sig')) if args.calendar else fetch_calendar(username, args.year)
    if args.calendar or args.year is not None:
        build(data, args.year)
    else:
        state = json.loads(STATE_PATH.read_text(encoding='utf-8')) if STATE_PATH.exists() else {}
        previous_state = json.dumps(state, sort_keys=True)
        versions = {'latest': refresh_calendar(data, None, state)}
        first_year = int(data['accountCreatedAt'][:4])
        current_year = datetime.now(PROFILE_TIMEZONE).year
        years = list(range(current_year, first_year - 1, -1))
        for year in years:
            versions[str(year)] = refresh_calendar(fetch_calendar(username, year), year, state)
        update_year_choices(years, versions)
        if json.dumps(state, sort_keys=True) != previous_state:
            STATE_PATH.parent.mkdir(exist_ok=True)
            STATE_PATH.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
