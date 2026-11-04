"""Build the profile's animated SVGs (light + dark) with fonts and drawings embedded.

GitHub serves README images through a proxy as <img>, so every SVG must be
self-contained: no external fonts, images or scripts. SMIL animation survives.
"""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT.parent
FONTS = ROOT / 'fonts'
OUT = ROOT / 'assets'

THEMES = {
    'light': dict(paper='#eeeeec', paper2='#e3e4e1', ink='#151515', soft='#3b3c3a', wash='#8a8b88', red='#c23a2b', blend='multiply'),
    'dark': dict(paper='#161615', paper2='#1f1f1e', ink='#e9e8e3', soft='#c4c3bd', wash='#7a7b77', red='#e0533f', blend='normal'),
}


def data_uri(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode()


FONT_FACES = '\n'.join(
    f"@font-face{{font-family:'{name}';src:url({data_uri(FONTS / file, 'font/woff2')}) format('woff2');font-weight:{weight}}}"
    for name, file, weight in [
        ('Mincho', 'shippori-mincho-b1-latin-700-normal.woff2', 700),
        ('Pen', 'nanum-pen-script-latin-400-normal.woff2', 400),
        ('Grotesk', 'hanken-grotesk-latin-wght-normal.woff2', '100 900'),
    ]
)



def style(t, fonts=True):
    return f"""<style>{FONT_FACES if fonts else ''}
.m{{font-family:Mincho,'Shippori Mincho',serif;font-weight:700;fill:{t['ink']}}}
.p{{font-family:Pen,'Nanum Pen Script',cursive;fill:{t['soft']}}}
.g{{font-family:Grotesk,'Hanken Grotesk',sans-serif;fill:{t['soft']}}}
.ink{{fill:{t['ink']}}} .wash{{fill:{t['wash']}}} .paper{{fill:{t['paper']}}} .red{{fill:{t['red']}}}
.st{{stroke:{t['ink']};fill:none;stroke-linecap:round;stroke-linejoin:round}}
.char{{mix-blend-mode:{t['blend']}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""


FILTERS = """<filter id="dry" filterUnits="userSpaceOnUse" x="0" y="0" width="900" height="900">
<feTurbulence type="fractalNoise" baseFrequency="0.55" numOctaves="2" seed="4" result="n"/>
<feColorMatrix in="n" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.3 1.2" result="m"/>
<feComposite in="SourceGraphic" in2="m" operator="in"/></filter>
<filter id="boil"><feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" seed="3">
<animate attributeName="seed" values="3;7;11;3" dur="0.5s" calcMode="discrete" repeatCount="indefinite"/></feTurbulence>
<feDisplacementMap in="SourceGraphic" scale="3"/></filter>"""


BORRAO = json.loads((ROOT / 'tools/borrao-paths.json').read_text())


def borrao(t, mood='smile'):
    """Borrão with the portfolio's own brush paths (tools/borrao-paths.json, made from src/lib/brush.ts)."""
    mouth = {'smile': 'M26 36 Q30 39.5 34 36', 'open': 'M28 36 Q30 41 32 36 Q30 34.5 28 36'}[mood]
    return f"""<g>
<ellipse cx="30" cy="60" rx="14" ry="3" class="wash" opacity=".3"/>
<g class="st" stroke-width="3"><path d="M24 40 L22 58"><animateTransform attributeName="transform" type="rotate" values="0 24 40;6 24 40;0 24 40" dur="1.6s" repeatCount="indefinite"/></path>
<path d="M36 40 L38 58"><animateTransform attributeName="transform" type="rotate" values="0 36 40;-6 36 40;0 36 40" dur="1.6s" repeatCount="indefinite"/></path></g>
<g>
<path d="{BORRAO['body']}" class="ink" filter="url(#boil)"/>
<path d="{BORRAO['tuft']}" class="ink"/><path d="{BORRAO['tuftSmall']}" class="ink"/>
<circle cx="25" cy="27" r="4.2" class="paper"/><circle cx="35" cy="27" r="4.2" class="paper"/>
<circle cx="25" cy="27" r="1.9" class="ink"><animate attributeName="cx" values="25;26.6;26.6;23.6;25" dur="6s" repeatCount="indefinite"/></circle>
<circle cx="35" cy="27" r="1.9" class="ink"><animate attributeName="cx" values="35;36.6;36.6;33.6;35" dur="6s" repeatCount="indefinite"/></circle>
<rect x="19" y="21" width="22" height="0" class="ink"><animate attributeName="height" values="0;0;12;0" keyTimes="0;.93;.965;1" dur="4.2s" repeatCount="indefinite"/></rect>
<path d="{mouth}" stroke="{t['paper']}" stroke-width="1.8" fill="none" stroke-linecap="round"/></g>
</g>"""


def hanko(x, y, size=34):
    return f"""<g transform="translate({x} {y})"><rect width="{size}" height="{size}" rx="4" class="red" filter="url(#dry)"/>
<text x="{size/2}" y="{size*0.68}" text-anchor="middle" font-family="Mincho,serif" font-weight="700" font-size="{size*0.42}" fill="{THEME_PAPER}">AL</text></g>"""


def svg(w, h, t, body, label):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">
<title>{label}</title>{style(t)}<defs>{FILTERS}</defs>
<rect width="{w}" height="{h}" rx="6" class="paper"/>{body}</svg>"""


def bubble(x, y, lines, period=3.2):
    """Speech bubble that cycles through Borrão's lines from the portfolio, one at a time."""
    n = len(lines); total = n * period
    out = [f'<g transform="translate({x} {y})"><path d="M0 0 Q2 -30 70 -32 Q140 -30 142 -4 Q140 22 72 22 Q40 22 22 18 L6 30 L12 14 Q0 10 0 0Z" class="paper" stroke="{THEME_INK}" stroke-width="2" filter="url(#dry)"/>']
    for i, line in enumerate(lines):
        start, end = i / n, (i + 1) / n
        out.append(f'<text x="71" y="-1" text-anchor="middle" class="p" font-size="21" opacity="0">{line}'
                   f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;{start+.01:.3f};{end-.02:.3f};{end:.3f};1" dur="{total}s" repeatCount="indefinite" calcMode="discrete"/></text>')
    out.append('</g>')
    return ''.join(out)


def header(t):
    # The ensō is one stroke; pathLength=1 lets the dash animation run 0→1 regardless of geometry
    enso = """<path d="M232 76 A100 100 0 1 1 172 88" class="st" stroke-width="24" filter="url(#dry)" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">
<animate attributeName="stroke-dashoffset" to="0" dur="2s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".6 0 .2 1"/></path>"""
    mascot = f"""<g opacity="0"><animate attributeName="opacity" to="1" begin="1.7s" dur=".4s" fill="freeze"/>
<g transform="translate(140 104) scale(1.75)">{borrao(t)}</g>
{bubble(250, 70, ['oi!', 'sou feito de tinta', 'cuidado, eu mancho', 'fica à vontade'])}</g>"""
    words = """<g opacity="0"><animate attributeName="opacity" to="1" begin=".8s" dur="1s" fill="freeze"/>
<text x="430" y="150" class="m" font-size="56">André Luan</text></g>
<path d="M432 168 Q570 160 760 170" class="st" stroke-width="4" filter="url(#dry)" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">
<animate attributeName="stroke-dashoffset" to="0" begin="1.5s" dur=".6s" fill="freeze"/></path>
<g opacity="0"><animate attributeName="opacity" to="1" begin="1.9s" dur="1s" fill="freeze"/>
<text x="432" y="200" class="g" font-size="15" letter-spacing="3">DESENVOLVEDOR FULLSTACK</text></g>"""
    return svg(860, 300, t, enso + words + hanko(800, 252), 'André Luan, desenvolvedor fullstack, ao lado de um ensō')


def sheet(t):
    """Character sheet adapted from the portfolio's 'Jogador 1' card and the old profile bio."""
    bio = ['Me chamo André Luan Bernardo, tenho 22 anos e sou da Paraíba.',
           'Curso Ciência da Computação na UEPB e uno a base teórica',
           '(algoritmos e estruturas de dados) à prática de design,',
           'front-end e back-end.']
    attrs = [('algoritmos', .75), ('front-end', .85), ('back-end', .65), ('design', .75), ('café', 1)]
    out = [f'<text x="40" y="58" class="p" font-size="24">Jogador 1</text>',
           f'<text x="40" y="100" class="m" font-size="34">André Luan Bernardo</text>',
           f'<text x="40" y="130" class="g" font-size="14" letter-spacing="1">CLASSE: FRONT-END  ·  NÍVEL: EM EVOLUÇÃO</text>',
           '<path d="M40 148 L500 146" class="st" stroke-width="1.5" opacity=".5"/>']
    for i, line in enumerate(bio):
        out.append(f'<text x="40" y="{180 + i*26}" class="g" font-size="15">{line}</text>')
    out.append('<path d="M540 40 L541 380" class="st" stroke-width="1.5" opacity=".4" stroke-dasharray="4 6"/>')
    out.append('<text x="580" y="70" class="m" font-size="22">Atributos</text>')
    for i, (label, value) in enumerate(attrs):
        y = 112 + i * 44; w = 220 * value
        out.append(f'<text x="580" y="{y}" class="p" font-size="22">{label}</text>')
        out.append(f'<path d="M580 {y+12} L800 {y+12}" class="st" stroke-width="10" opacity=".12"/>')
        out.append(f'<path d="M580 {y+12} L{580+w:.0f} {y+11}" class="st" stroke-width="10" filter="url(#dry)" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
                   f'<animate attributeName="stroke-dashoffset" to="0" begin="{.3 + i*.18:.2f}s" dur=".9s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".5 0 .2 1"/></path>')
    return svg(860, 330, t, ''.join(out), 'Ficha de personagem: André Luan Bernardo')


def inventory(t):
    """The old devicon row, redrawn as ink tags so it stays in the neutral palette."""
    groups = [('front-end', ['HTML', 'CSS', 'JavaScript', 'TypeScript', 'React', 'Next.js', 'Astro + GSAP']),
              ('estilo', ['Tailwind', 'Bootstrap', 'Figma', 'design systems']),
              ('back-end', ['PHP', 'Laravel', 'Python', 'NestJS', 'Postgres']),
              ('ferramentas', ['Git', 'GitHub Actions', 'Claude Code'])]
    out = ['<text x="40" y="56" class="m" font-size="22">Inventário</text>',
           '<text x="170" y="56" class="p" font-size="22">o que levo na mochila</text>']
    y = 92; delay = 0
    for title, items in groups:
        out.append(f'<text x="40" y="{y+22}" class="p" font-size="22">{title}</text>')
        x = 170
        for item in items:
            w = 22 + len(item) * 8.6
            if x + w > 830:
                x = 170; y += 44
            r = (len(item) * 7) % 5 - 2
            out.append(f'<g opacity="0" transform="rotate({r*.4:.1f} {x+w/2:.0f} {y+14})"><animate attributeName="opacity" to="1" begin="{delay:.2f}s" dur=".35s" fill="freeze"/>'
                       f'<path d="M{x} {y+1} L{x+w:.0f} {y-1} L{x+w+1:.0f} {y+30} L{x-1} {y+29} Z" class="st" stroke-width="1.8" filter="url(#dry)"/>'
                       f'<text x="{x+w/2:.0f}" y="{y+21}" text-anchor="middle" class="g" font-size="14">{item}</text></g>')
            x += w + 12; delay += .07
        y += 52
    return svg(860, y + 20, t, ''.join(out), 'Inventário de tecnologias')


def stats(t):
    """Own stats card from data/stats.json (tools/stats.py), so no third-party stats service is needed."""
    d = json.loads((ROOT / 'data/stats.json').read_text(encoding='utf8'))
    numbers = [(d['total'], 'contribuições no ano'), (d['longest'], 'maior sequência (dias)'),
               (d['current'], 'sequência atual (dias)'), (d['repos'], 'repositórios')]
    out = ['<text x="40" y="56" class="m" font-size="22">Registro de tinta</text>',
           f'<text x="250" y="56" class="p" font-size="22">o ano em pinceladas · atualizado em {d["updated"][8:]}/{d["updated"][5:7]}</text>']
    for i, (value, label) in enumerate(numbers):
        x, y = 40 + (i % 2) * 200, 120 + (i // 2) * 84
        out.append(f'<g opacity="0"><animate attributeName="opacity" to="1" begin="{.2 + i*.15:.2f}s" dur=".5s" fill="freeze"/>'
                   f'<text x="{x}" y="{y}" class="m" font-size="40">{value}</text>'
                   f'<text x="{x}" y="{y+24}" class="p" font-size="19">{label}</text></g>')
    # Weekly totals become one brush stroke: the year's rhythm, not a grid
    weeks = d['weeks']; peak = max(weeks) or 1
    points = ' '.join(f'{40 + i * 360 / (len(weeks) - 1):.1f} {330 - 50 * w / peak:.1f}' for i, w in enumerate(weeks))
    out.append(f'<path d="M{points}" class="st" stroke-width="3" filter="url(#dry)" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
               '<animate attributeName="stroke-dashoffset" to="0" begin=".6s" dur="2.4s" fill="freeze"/></path>')
    out.append('<text x="40" y="358" class="p" font-size="18">ritmo semanal do ano</text>')
    out.append('<path d="M450 80 L451 350" class="st" stroke-width="1.5" opacity=".4" stroke-dasharray="4 6"/>')
    out.append('<text x="490" y="100" class="m" font-size="20">Línguas mais usadas</text>')
    for i, (name, share) in enumerate(d['languages']):
        y = 140 + i * 36; w = 300 * share / d['languages'][0][1]
        out.append(f'<text x="490" y="{y}" class="g" font-size="14">{name}</text><text x="820" y="{y}" text-anchor="end" class="p" font-size="18">{share*100:.0f}%</text>')
        out.append(f'<path d="M490 {y+11} L{490+w:.0f} {y+10}" class="st" stroke-width="8" filter="url(#dry)" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
                   f'<animate attributeName="stroke-dashoffset" to="0" begin="{.4 + i*.15:.2f}s" dur=".9s" fill="freeze"/></path>')
    return svg(860, 380, t, ''.join(out), f"Estatísticas: {d['total']} contribuições no último ano")


def footer(t):
    body = f"""<path d="M40 50 Q430 38 820 52" class="st" stroke-width="2" opacity=".4" filter="url(#dry)"/>
<g transform="translate(60 4) scale(.75)"><g>{borrao(t)}<animateMotion path="M0 0 L960 0" dur="16s" repeatCount="indefinite"/></g></g>
<text x="430" y="88" text-anchor="middle" class="p" font-size="22">obrigado pela visita — volte quando a tinta secar</text>{hanko(800, 64, 26)}"""
    return svg(860, 104, t, body, 'Rodapé com o Borrão passeando')


for name, t in THEMES.items():
    THEME_PAPER, THEME_INK = t['paper'], t['ink']
    (OUT / f'ficha-{name}.svg').write_text(sheet(t), encoding='utf8')
    (OUT / f'inventario-{name}.svg').write_text(inventory(t), encoding='utf8')
    (OUT / f'enso-{name}.svg').write_text(header(t), encoding='utf8')
    (OUT / f'stats-{name}.svg').write_text(stats(t), encoding='utf8')
print('ok')
