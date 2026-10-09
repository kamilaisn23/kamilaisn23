"""Code-drawn pink banner: web, mobile, learning, and little dreams."""
from pathlib import Path
from io import BytesIO
import argparse
import html
import math
import resvg_py
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
N = 120
INK = '#8c4368'

def heart(x, y, size=.5, opacity=1):
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({size})" opacity="{opacity:.2f}"><path d="M0 3C-10-8-20 4-12 12L0 23 12 12C20 4 10-8 0 3Z" fill="#e9a1be"/></g>'

def spark(x, y, size=8, opacity=.6):
    return f'<path d="M{x} {y-size}Q{x} {y} {x+size} {y}Q{x} {y} {x} {y+size}Q{x} {y} {x-size} {y}Q{x} {y} {x} {y-size}Z" fill="#d389ab" opacity="{opacity:.2f}"/>'

def flower(x, y, scale=.5):
    petals=''.join(f'<ellipse cy="-8" rx="6" ry="9" transform="rotate({a})" fill="#edb3ce"/>' for a in range(0,360,72))
    return f'<g transform="translate({x} {y}) scale({scale})">{petals}<circle r="4.5" fill="#fff2c9"/></g>'

def bunny(frame, mode='laptop'):
    phase=2*math.pi*frame/N
    bob=math.sin(phase*4)*2
    tilt=math.sin(phase*2)*2
    blink = frame % 60 in (42,43,44)
    happy = 70 <= frame <= 89
    eyes = '<path d="M-26-7q7-9 14 0m24 0q7-9 14 0" fill="none" stroke="#925473" stroke-width="3.5" stroke-linecap="round"/>' if happy else ('<path d="M-26-7q7 6 14 0m24 0q7 6 14 0" fill="none" stroke="#925473" stroke-width="3" stroke-linecap="round"/>' if blink else '<ellipse cx="-19" cy="-7" rx="4.5" ry="6" fill="#925473"/><ellipse cx="19" cy="-7" rx="4.5" ry="6" fill="#925473"/><circle cx="-20" cy="-9" r="1.5" fill="white"/><circle cx="18" cy="-9" r="1.5" fill="white"/>')
    head=f'''<g transform="translate(0 {bob:.2f}) rotate({tilt:.2f})">
    <g fill="#fffdfd" stroke="#c384a3" stroke-width="2.5"><ellipse cx="-26" cy="-60" rx="17" ry="43" transform="rotate({-12+tilt:.2f} -26 -60)"/><ellipse cx="26" cy="-60" rx="17" ry="43" transform="rotate({12+tilt:.2f} 26 -60)"/><ellipse cy="1" rx="62" ry="48"/></g>
    <ellipse cx="-26" cy="-62" rx="8" ry="30" transform="rotate({-12+tilt:.2f} -26 -62)" fill="#f7ccde"/><ellipse cx="26" cy="-62" rx="8" ry="30" transform="rotate({12+tilt:.2f} 26 -62)" fill="#f7ccde"/>
    <ellipse cx="-37" cy="11" rx="13" ry="8" fill="#f5bfd4"/><ellipse cx="37" cy="11" rx="13" ry="8" fill="#f5bfd4"/>{eyes}
    <path d="M-4 5q4-4 8 0L0 10Z" fill="#bd7396"/><path d="M0 10v4m0 0q-7 7-12 0m12 0q7 7 12 0" fill="none" stroke="#925473" stroke-width="2.5" stroke-linecap="round"/>
    <g transform="translate(45 -37) rotate(15)" fill="#e7a2c0" stroke="#bf779b" stroke-width="1.5"><path d="M0 0-18-10q-5 10 0 22ZM0 0 18-10q5 10 0 22Z"/><circle r="5" fill="#ffe2ed"/></g></g>'''
    body='<ellipse cy="48" rx="46" ry="45" fill="#fffdfd" stroke="#c384a3" stroke-width="2.5"/>'
    if mode=='laptop':
        wave = max(0, math.sin(phase))*28
        return f'''<ellipse cy="148" rx="117" ry="11" fill="#d9a0bb" opacity=".2"/>{body}{head}
        <g transform="rotate({-wave:.2f} -55 47)"><ellipse cx="-62" cy="35" rx="15" ry="22" fill="#fffdfd" stroke="#c384a3" stroke-width="2.5"/></g>
        <rect x="-98" y="48" width="196" height="101" rx="14" fill="#edbbd3" stroke="#bb7a9d" stroke-width="2.5"/><rect x="-87" y="59" width="174" height="77" rx="8" fill="#f7d6e6"/>
        <text x="0" y="110" text-anchor="middle" font-family="Consolas, monospace" font-size="33" font-weight="700" fill="#ba789b">&lt; / &gt;</text><path d="M-112 151h224l-11 10H-101Z" fill="#ffe7f0" stroke="#bb7a9d" stroke-width="2.5"/>
        <ellipse cx="61" cy="{49-bob:.2f}" rx="17" ry="11" fill="#fffdfd" stroke="#c384a3" stroke-width="2.2"/>'''
    if mode=='phone':
        return f'''<ellipse cy="100" rx="47" ry="9" fill="#d9a0bb" opacity=".2"/>{body}<ellipse cx="-23" cy="89" rx="20" ry="11" fill="#fffdfd" stroke="#c384a3" stroke-width="2.5"/><ellipse cx="23" cy="89" rx="20" ry="11" fill="#fffdfd" stroke="#c384a3" stroke-width="2.5"/>{head}
        <g transform="rotate({-8+tilt:.2f} 0 60)"><rect x="-24" y="26" width="48" height="69" rx="9" fill="#f1bfd6" stroke="#bc799c" stroke-width="2.5"/><rect x="-18" y="35" width="36" height="49" rx="5" fill="#fff7fb"/><rect x="-9" y="29" width="18" height="3" rx="1.5" fill="#bc799c"/>{heart(0,49,.65)}<circle cy="89" r="2" fill="#bc799c"/></g>
        <ellipse cx="-27" cy="56" rx="11" ry="9" fill="#fffdfd" stroke="#c384a3" stroke-width="2"/><ellipse cx="27" cy="56" rx="11" ry="9" fill="#fffdfd" stroke="#c384a3" stroke-width="2"/>'''
    step=math.sin(phase*15)*6
    return f'''{body}<ellipse cx="{-22+step:.2f}" cy="90" rx="20" ry="10" fill="#fffdfd" stroke="#c384a3" stroke-width="2.5"/><ellipse cx="{22-step:.2f}" cy="90" rx="20" ry="10" fill="#fffdfd" stroke="#c384a3" stroke-width="2.5"/>{head}<path d="M-30 39q30 17 60 0v15q-30 18-60 0Z" fill="#ecb1cd"/>{heart(0,49,.4)}'''

def banner(frame):
    phase=2*math.pi*frame/N
    phrase='Learning to code. Growing toward my dreams.'
    length=min(len(phrase), int(frame/55*len(phrase))) if frame<99 else max(0,int((119-frame)/20*len(phrase)))
    typed=html.escape(phrase[:length])
    caret=f'<rect x="{60+length*9.62:.2f}" y="232" width="2" height="19" rx="1" fill="#bc7699"/>' if frame%16<9 else ''
    runner=-60+frame/(N-1)*1320
    float_hearts=''.join(heart(x,y-10*math.sin(phase+shift),s,.7) for x,y,s,shift in [(773,104,.38,0),(1080,71,.45,1.4),(1145,170,.3,2.3),(740,290,.35,3.5)])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="400" viewBox="0 0 1200 400" role="img" aria-labelledby="title desc">
    <title id="title">Kamila Isnaini · web, mobile, and little dreams</title><desc id="desc">Two playful pink bunnies with a laptop and phone. Exploring web and mobile development, learning to code, and growing toward my dreams.</desc>
    <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff9fc"/><stop offset="1" stop-color="#f8dfed"/></linearGradient><radialGradient id="glow"><stop stop-color="#fffafd"/><stop offset="1" stop-color="#fff4fa" stop-opacity="0"/></radialGradient><pattern id="dot" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="1" fill="#d990b0" opacity=".16"/></pattern></defs>
    <rect x="1" y="1" width="1198" height="398" rx="30" fill="url(#bg)" stroke="#f1c6dd" stroke-width="2"/><rect x="2" y="2" width="1196" height="396" rx="29" fill="url(#dot)"/>
    <ellipse cx="923" cy="184" rx="252" ry="170" fill="url(#glow)"/>
    <path d="M728 332Q913 305 1170 340" fill="none" stroke="#e9bdd3" stroke-width="1.5"/><path d="M40 378H1160" fill="none" stroke="#e7b8cf" stroke-width="1.5" stroke-dasharray="2 10" stroke-linecap="round"/>
    <text x="60" y="68" font-family="Arial, sans-serif" font-size="15" font-weight="700" letter-spacing="3.3" fill="#b97298">WELCOME TO MY LITTLE CODING WORLD</text>
    <text x="56" y="146" font-family="Arial, sans-serif" font-size="66" font-weight="700" letter-spacing="-2.6" fill="{INK}">Kamila Isnaini</text>
    <text x="60" y="192" font-family="Arial, sans-serif" font-size="22" fill="#a66489">Exploring web &amp; mobile development</text>
    <text x="60" y="249" font-family="Consolas, monospace" font-size="17.5" fill="#b17294">{typed}</text>{caret}
    <g font-family="Arial, sans-serif" font-size="12" font-weight="700" letter-spacing="1.2" fill="#aa668b"><rect x="60" y="283" width="162" height="34" rx="17" fill="#fff9fc" stroke="#edbfd6"/><text x="80" y="305">ALWAYS CURIOUS</text><rect x="234" y="283" width="158" height="34" rx="17" fill="#fff9fc" stroke="#edbfd6"/><text x="256" y="305">SMALL STEPS</text><rect x="404" y="283" width="150" height="34" rx="17" fill="#fff9fc" stroke="#edbfd6"/><text x="432" y="305">BIG DREAMS</text></g>
    <g transform="translate(903 187) scale(.86)">{bunny(frame)}</g><g transform="translate(1100 260) rotate({math.sin(phase)*3:.2f}) scale(.5)">{bunny(frame+18,'phone')}</g>
    {float_hearts}{spark(763,178,9,.5+.3*math.sin(phase)**2)}{spark(1030,110,7,.5+.3*math.cos(phase)**2)}{spark(1160,287,7,.6)}{flower(791,330,.6)}{flower(1154,346,.45)}
    <g transform="translate({runner:.2f} {353-abs(math.sin(phase*15))*5:.2f}) scale(.21)">{bunny(frame,'walk')}</g>
    </svg>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'assets')
    parser.add_argument('--preview-dir', type=Path, help='Optional folder for six decoded GIF frames.')
    args = parser.parse_args()
    OUT = args.output_dir
    OUT.mkdir(parents=True, exist_ok=True)
    frames=[]
    reference=Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=banner(75)))).convert('RGB').quantize(colors=255)
    for index in range(N):
        source=Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=banner(index)))).convert('RGBA')
        quantized=source.convert('RGB').quantize(palette=reference,dither=Image.Dither.NONE)
        # Reserve palette index 255 for genuinely transparent pixels only.
        quantized.paste(255,mask=source.getchannel('A').point(lambda a:255 if a<128 else 0))
        palette=quantized.getpalette()
        palette += [0]*(768-len(palette))
        quantized.putpalette(palette)
        frames.append(quantized)
    frames[0].save(OUT/'pink-banner.gif',save_all=True,append_images=frames[1:],duration=80,loop=0,disposal=1,optimize=True,transparency=255)
    (OUT/'profile-banner.svg').write_text(banner(75),encoding='utf-8')
    with Image.open(OUT/'pink-banner.gif') as gif:
        assert gif.n_frames==N and gif.info['loop']==0
        assert gif.convert('RGBA').getpixel((0,0))[3]==0
        if args.preview_dir:
            preview = Path(args.preview_dir)
            preview.mkdir(parents=True, exist_ok=True)
            for index in (0,30,60,75,100,119):
                gif.seek(index)
                gif.convert('RGBA').save(preview/f'frame-{index:03d}.png')
    print(f'Created {N} frames; size: {(OUT/"pink-banner.gif").stat().st_size:,} bytes')

if __name__ == '__main__':
    main()
