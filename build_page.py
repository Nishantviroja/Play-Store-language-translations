"""Builds ~/Documents/arrow-puzzle-store-listing/index.html from the NN-*.txt listing files."""
import glob, json, os, sys

folder = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else '~/Documents/arrow-puzzle-store-listing')

def section(text, head, nxt):
    a = text.index(head) + len(head)
    b = text.index(nxt) if nxt else len(text)
    return text[a:b].strip()

langs = []
for path in sorted(glob.glob(os.path.join(folder, '[0-9][0-9]-*.txt'))):
    t = open(path, encoding='utf-8').read()
    lang = section(t, 'LANGUAGE:', 'APP NAME').splitlines()[0].strip()
    label, _, code = lang.partition(' – ')
    langs.append({
        'language': lang,
        'label': label.strip(),
        'code': code.strip(),
        'name': section(t, 'APP NAME (max 30):', 'SHORT DESCRIPTION'),
        'short': section(t, 'SHORT DESCRIPTION (max 80):', 'FULL DESCRIPTION'),
        'full': section(t, 'FULL DESCRIPTION (max 4000):', None),
    })

data = json.dumps(langs, ensure_ascii=False).replace('</', '<\\/')

html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Arrow Puzzle Listings</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #070E22;
    --face: #0A1330;
    --raised: #13204A;
    --stroke: #22305A;
    --edge: #040817;
    --text: #F1F5F9;
    --muted: #94A3B8;
    --accent: #38BDF8;
    --accent-2: #2D68F0;
    --ok: #34D399;
    --warn: #F87171;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Rubik', system-ui, -apple-system, 'Segoe UI', 'Noto Sans', sans-serif;
    font-size: 15px;
  }
  .app { display: flex; height: 100vh; }

  /* ---------- Sidebar ---------- */
  aside {
    width: 270px;
    flex-shrink: 0;
    background: var(--face);
    border-right: 1px solid var(--stroke);
    display: flex; flex-direction: column;
  }
  .brand { padding: 20px 18px 12px; }
  .brand h1 { margin: 0; font-size: 18px; font-weight: 700; }
  .brand p { margin: 4px 0 0; color: var(--muted); font-size: 13px; }
  .search {
    margin: 4px 14px 10px;
    padding: 10px 12px;
    border-radius: 10px;
    border: 1px solid var(--stroke);
    background: var(--bg);
    color: var(--text);
    font: inherit; font-size: 14px;
  }
  .search:focus { outline: 2px solid var(--accent); outline-offset: 0; }
  nav { overflow-y: auto; padding: 0 10px 16px; flex: 1; }
  nav button {
    width: 100%;
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
    padding: 10px 12px;
    margin-bottom: 4px;
    border: 0; border-radius: 10px;
    background: transparent;
    color: var(--text);
    font: inherit; font-size: 14px; font-weight: 500;
    text-align: left; cursor: pointer;
  }
  nav button:hover { background: var(--raised); }
  nav button.active { background: var(--accent-2); box-shadow: 0 3px 0 #1E3F9E; }
  nav button .num { color: var(--muted); font-size: 12px; width: 22px; flex-shrink: 0; }
  nav button.active .num, nav button.active .code { color: #DCE7FF; }
  nav button .lbl { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  nav button .code { color: var(--muted); font-size: 12px; font-weight: 400; }

  /* ---------- Main ---------- */
  main { flex: 1; overflow-y: auto; padding: 28px 32px 48px; }
  .inner { max-width: 860px; margin: 0 auto; }
  .field {
    background: var(--face);
    border: 1px solid var(--stroke);
    border-radius: 16px;
    margin-bottom: 18px;
    box-shadow: 0 4px 0 var(--edge);
  }
  .field-head {
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    padding: 14px 16px 0;
  }
  .field-title { font-size: 12px; font-weight: 700; letter-spacing: .08em; color: var(--muted); }
  .count { font-size: 12px; font-weight: 600; color: var(--ok); margin-left: 8px; letter-spacing: 0; }
  .count.over { color: var(--warn); }
  .value {
    margin: 0;
    padding: 12px 16px 16px;
    white-space: pre-wrap;
    word-wrap: break-word;
    line-height: 1.55;
    font-size: 15px;
  }
  .value.big { font-size: 20px; font-weight: 600; }
  .copy {
    flex-shrink: 0;
    display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 14px 9px;
    border: 0; border-radius: 10px;
    background: var(--accent-2);
    color: #fff;
    font: inherit; font-size: 13px; font-weight: 600;
    cursor: pointer;
    box-shadow: 0 3px 0 #1E3F9E;
  }
  .copy:hover { filter: brightness(1.1); }
  .copy:active { transform: translateY(2px); box-shadow: 0 1px 0 #1E3F9E; }
  .copy:focus-visible, nav button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .copy.done { background: #10B981; box-shadow: 0 3px 0 #047857; }
  .copy svg { width: 14px; height: 14px; }

  /* ---------- Phone ---------- */
  @media (max-width: 760px) {
    .app { flex-direction: column; height: auto; min-height: 100vh; }
    aside, main, nav { min-width: 0; max-width: 100%; }
    .value { overflow-wrap: anywhere; }
    aside { width: 100%; border-right: 0; border-bottom: 1px solid var(--stroke); }
    nav { display: flex; overflow-x: auto; overflow-y: hidden; gap: 6px; padding: 0 14px 12px; }
    nav button { width: auto; flex-shrink: 0; margin: 0; }
    nav button .num { display: none; }
    main { padding: 18px 16px 40px; overflow: visible; }
    .value.big { font-size: 18px; }
  }
</style>
</head>
<body>
<div class="app">
  <aside>
    <div class="brand">
      <h1>Arrow Puzzle</h1>
      <p>Play Store listing · <span id="langCount"></span> languages</p>
    </div>
    <input class="search" id="search" type="search" placeholder="Search language or code" aria-label="Search languages">
    <nav id="nav" aria-label="Languages"></nav>
  </aside>
  <main><div class="inner" id="content"></div></main>
</div>

<script>
const LANGS = __DATA__;

const FIELDS = [
  { key: 'language', title: 'LANGUAGE', max: null, big: true },
  { key: 'name', title: 'APP NAME', max: 30, big: true },
  { key: 'short', title: 'SHORT DESCRIPTION', max: 80 },
  { key: 'full', title: 'FULL DESCRIPTION', max: 4000 },
];

const COPY_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';

// Play counts characters (code points), not bytes.
const charCount = s => Array.from(s.normalize('NFC')).length;

const nav = document.getElementById('nav');
const content = document.getElementById('content');
document.getElementById('langCount').textContent = LANGS.length;

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}

LANGS.forEach((l, i) => {
  const b = el('button');
  b.dataset.i = i;
  b.append(el('span', 'num', String(i + 1).padStart(2, '0')), el('span', 'lbl', l.label), el('span', 'code', l.code));
  b.addEventListener('click', () => select(i));
  nav.append(b);
});

function select(i) {
  const l = LANGS[i];
  nav.querySelectorAll('button').forEach(b => b.classList.toggle('active', +b.dataset.i === i));
  const activeBtn = nav.querySelector('button.active');
  if (activeBtn) activeBtn.scrollIntoView({ block: 'nearest', inline: 'center' });
  content.replaceChildren();
  FIELDS.forEach(f => {
    const text = l[f.key];
    const card = el('section', 'field');
    const head = el('div', 'field-head');
    const title = el('div', 'field-title', f.title + (f.max ? ' (max ' + f.max + ')' : ''));
    if (f.max) {
      const n = charCount(text);
      title.append(el('span', 'count' + (n > f.max ? ' over' : ''), n + ' / ' + f.max));
    }
    const btn = el('button', 'copy');
    btn.type = 'button';
    btn.innerHTML = COPY_ICON + '<span>Copy</span>';
    btn.setAttribute('aria-label', 'Copy ' + f.title.toLowerCase());
    btn.addEventListener('click', () => copy(text, btn));
    head.append(title, btn);
    const val = el('p', 'value' + (f.big ? ' big' : ''), text);
    val.dir = 'auto';
    card.append(head, val);
    content.append(card);
  });
  try { localStorage.setItem('apl-lang', l.code); } catch (e) {}
  if (history.replaceState) history.replaceState(null, '', '#' + l.code);
  document.querySelector('main').scrollTop = 0;
}

async function copy(text, btn) {
  let ok = false;
  try { await navigator.clipboard.writeText(text); ok = true; } catch (e) {
    const ta = el('textarea');
    ta.value = text;
    ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.append(ta); ta.select();
    try { ok = document.execCommand('copy'); } catch (e2) {}
    ta.remove();
  }
  const label = btn.querySelector('span');
  label.textContent = ok ? 'Copied!' : 'Copy failed';
  btn.classList.toggle('done', ok);
  clearTimeout(btn._t);
  btn._t = setTimeout(() => { label.textContent = 'Copy'; btn.classList.remove('done'); }, 1500);
}

document.getElementById('search').addEventListener('input', e => {
  const q = e.target.value.trim().toLowerCase();
  nav.querySelectorAll('button').forEach(b => {
    const l = LANGS[+b.dataset.i];
    b.hidden = q && !(l.label + ' ' + l.code).toLowerCase().includes(q);
  });
});

let start = 0;
let wanted = decodeURIComponent(location.hash.slice(1));
if (!wanted) { try { wanted = localStorage.getItem('apl-lang') || ''; } catch (e) {} }
const found = LANGS.findIndex(l => l.code === wanted);
if (found >= 0) start = found;
select(start);
</script>
</body>
</html>
'''

out = os.path.join(folder, 'index.html')
open(out, 'w', encoding='utf-8').write(html.replace('__DATA__', data))
print(f'{len(langs)} languages -> {out}')
for l in langs:
    print(l['code'], l['label'])
