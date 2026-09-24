"""Compare the relocated story with the preserved v3 and test Pages-style URLs.

Run: python tests/adventure_hub_test.py --output ../hub-review
Requires Playwright and its Chromium browser (see tests/README.md).
"""

import argparse
import base64
import hashlib
import json
import re
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = '50841bd009b1a14e00f673b23fa5e5b7828dfb66'
BASELINE_BLOB = '2071c1f9b662637e7db6708217d8d3c20c8cec5d'
BASELINE = subprocess.check_output(['git', 'show', f'{BASELINE_COMMIT}:index.html'], cwd=REPO)
RESULTS = []


def record(name, detail):
    RESULTS.append({'check': name, 'result': 'PASS', 'detail': detail})
    print(f'PASS {name}', flush=True)


def preserved_story():
    original = BASELINE.decode().replace('\r\n', '\n')
    moved = (REPO / 'stories/moon-cave/index.html').read_text(encoding='utf-8')
    stripped = re.sub(r'<!-- Adventure hub navigation:.*?</style>\n', '', moved, flags=re.S)
    stripped = re.sub(r'<nav class="adventure-home".*?</nav>\n', '', stripped)
    assert stripped == original, 'Story changed beyond the separate return navigation'
    git_blob = hashlib.sha1(f'blob {len(BASELINE)}\0'.encode() + BASELINE).hexdigest()
    assert git_blob == BASELINE_BLOB
    images = json.loads(re.search(r'const IMAGES=(.*);', original)[1])
    cover = base64.b64decode(images['cover'].split(',')[1])
    assert cover == (REPO / 'assets/moon-cave-cover.webp').read_bytes()
    assert not re.search(r'(?:fetch\(|new Worker\(|url\(|<base\b|<script[^>]+src=)', original)
    record('preservation', 'Original story code, styles, text and embedded images are unchanged; cover bytes match v3.')


class Handler(BaseHTTPRequestHandler):
    legacy_root = False

    def log_message(self, *_):
        pass

    def do_GET(self):
        route = unquote(urlsplit(self.path).path)
        if route in ('/baseline/', '/baseline/index.html') or (self.legacy_root and route == '/Moon-cave/'):
            data, mime = BASELINE, 'text/html; charset=utf-8'
        elif route.startswith('/Moon-cave/'):
            target = (REPO / route[len('/Moon-cave/'):]).resolve()
            if not target.is_relative_to(REPO):
                self.send_error(403)
                return
            if target.is_dir():
                if not route.endswith('/'):
                    self.send_response(301)
                    self.send_header('Location', route + '/')
                    self.end_headers()
                    return
                target = target / 'index.html'
            if not target.is_file():
                self.send_error(404)
                return
            data = target.read_bytes()
            mime = {'.webp': 'image/webp', '.png': 'image/png'}.get(target.suffix, 'text/html; charset=utf-8')
        elif route == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        try:
            self.wfile.write(data)
        except ConnectionError:
            pass  # A navigation can cancel an in-flight page response.


def scene(page, expected):
    page.wait_for_function('(name) => state.scene === name', arg=expected)
    page.wait_for_function('Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)')


def action(page, handler):
    # Let the v3 fade and native touch/scroll settling finish between scenes.
    page.wait_for_timeout(400)
    page.locator(f'button[onclick="{handler}"]').tap()


def stored(page):
    return page.evaluate('Object.fromEntries(Object.entries(localStorage))')


def reward(page, item):
    page.wait_for_selector('.reward-card')
    assert page.evaluate(f'state.{item}') is True
    page.clock.run_for(5000)
    assert page.locator('.reward-card').is_visible(), 'Reward disappeared without Continue'
    page.locator('.reward-continue').tap()


def key_challenge(page):
    action(page, 'readDiary()')
    action(page, 'keyChallenge()')
    assert page.locator('.timer').inner_text() == '15'
    page.clock.run_for(2000)
    assert page.locator('.timer').inner_text() == '15'
    page.locator('.startTimer').tap()
    page.clock.run_for(14000)
    assert page.evaluate('state.key') is False
    page.clock.run_for(1100)
    reward(page, 'key')
    scene(page, 'mapPrompt')


def finish_after_touch_reload(page):
    # In baseline Chromium emulation, the first tap after raw CDP dragging +
    # reload can produce touch events without a click. Record it, do not hide
    # it with a blanket retry, and require the relocated version to match.
    action(page, "go('final')")
    page.wait_for_timeout(250)
    taps = 1
    if page.evaluate('state.scene') != 'final':
        action(page, "go('final')")
        taps = 2
    scene(page, 'final')
    return taps


def touch_drag(page, cdp, item, destination):
    source = page.locator(f'.dragitem[data-type="{item}"]')
    source.scroll_into_view_if_needed()
    start = source.bounding_box()
    target = page.locator(f'.dropzone[data-type="{destination}"]').bounding_box()
    sx, sy = start['x'] + start['width'] / 2, start['y'] + start['height'] / 2
    tx, ty = target['x'] + target['width'] / 2, target['y'] + target['height'] / 2
    assert min(sy, ty) >= 0 and max(sy, ty) < page.viewport_size['height']
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': sx, 'y': sy, 'id': 1}]})
    for step in range(1, 9):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': sx + (tx-sx)*step/8, 'y': sy + (ty-sy)*step/8, 'id': 1}]})
    assert page.locator(f'.dropzone[data-type="{destination}"]').evaluate('e => e.classList.contains("active")')
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})


def to_door(page, treasure=False):
    action(page, "go('witch')")
    if treasure:
        action(page, "go('fakegold')")
        scene(page, 'fakegold')
        action(page, "go('clue')")
    else:
        action(page, "go('clue')")
    action(page, "go('door')")
    scene(page, 'door')


def story_regression(browser, base, route, label, out):
    context = browser.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True)
    page = context.new_page()
    errors, bad_responses = [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('response', lambda r: bad_responses.append(r.url) if r.status >= 400 else None)
    page.clock.install()
    page.goto(base + route)
    scene(page, 'cover')
    assert 'maximum-scale=5' in page.locator('meta[name=viewport]').get_attribute('content')
    action(page, "resetState('intro')")
    action(page, "go('entrance')")
    page.get_by_role('button', name='放大文字').tap()
    assert abs(page.evaluate('scale') - 1.1) < .001
    page.reload()
    scene(page, 'entrance')
    assert abs(page.evaluate('scale') - 1.1) < .001
    page.get_by_role('button', name='縮小文字').tap()
    assert abs(page.evaluate('scale') - 1) < .001
    action(page, 'chooseStone()')
    action(page, 'shieldChallenge()')
    page.clock.run_for(5500)
    assert page.locator('.shield-clock').inner_text() == '5.0 秒'
    page.locator('.num[data-n="3"]').tap()
    assert page.locator('.num[data-n="3"]').evaluate('e => e.classList.contains("wrong")')
    assert not page.locator('.challenge-fail').is_visible()
    page.clock.run_for(5100)
    assert page.get_by_role('button', name='重新挑戰').is_visible()
    page.get_by_role('button', name='重新挑戰').tap()
    assert page.locator('.shield-clock').inner_text() == '5.0 秒'
    for n in range(1, 6):
        page.locator(f'.num[data-n="{n}"]').tap()
    page.clock.run_for(400)
    reward(page, 'shield')
    scene(page, 'skeleton')
    key_challenge(page)
    hidden = page.locator('.hidden-link')
    assert hidden.evaluate('e => getComputedStyle(e).animationName') == 'none'
    assert hidden.evaluate('e => getComputedStyle(e).boxShadow') == 'none'
    hidden.tap()
    scene(page, 'vine')
    action(page, 'revealSpider()')
    action(page, 'jumpChallenge()')
    for i in range(9):
        page.locator('.overlay .challenge-btn').tap()
        assert page.locator('.stars .on').count() == i + 1
        assert not page.evaluate('state.moon')
    page.locator('.overlay .challenge-btn').tap()
    page.clock.run_for(400)
    reward(page, 'moon')
    scene(page, 'witch')
    action(page, "go('clue')")
    action(page, "go('door')")
    scene(page, 'door')
    cdp = context.new_cdp_session(page)
    touch_drag(page, cdp, 'moon', 'shield')
    assert page.locator('.dropzone.filled').count() == 0
    assert page.locator('.dragitem.placed').count() == 0
    touch_drag(page, cdp, 'moon', 'moon')
    assert page.locator('.dropzone[data-type="moon"] .slot-icon').inner_text() == '🌙'
    assert page.locator('.dropzone.filled').evaluate('e => getComputedStyle(e).boxShadow') != 'none'
    page.reload()
    scene(page, 'door')
    assert page.locator('.dragitem').count() == 3
    assert page.locator('.dropzone.filled').count() == 0, 'v3 does not persist partially placed slots'
    for item in ['moon', 'shield', 'key']:
        touch_drag(page, cdp, item, item)
    assert page.locator('.slot-icon').count() == 3
    page.screenshot(path=str(out / f'{label}-slots.png'))
    page.clock.run_for(1000)
    scene(page, 'secret')
    assert page.evaluate('state.ending') == 'secret'
    page.reload()
    scene(page, 'secret')
    secret_finish_taps = finish_after_touch_reload(page)
    action(page, "resetState('entrance')")
    assert not page.evaluate('state.shield || state.moon || state.key')
    action(page, 'chooseVine()')
    action(page, 'leaveBranch()')
    key_challenge(page)
    to_door(page, treasure=True)
    assert page.locator('.dragitem').count() == 1
    touch_drag(page, cdp, 'key', 'key')
    page.clock.run_for(1000)
    scene(page, 'ordinary')
    assert page.evaluate('state.ending') == 'ordinary'
    page.reload()
    scene(page, 'ordinary')
    ordinary_finish_taps = finish_after_touch_reload(page)
    action(page, "resetState('cover')")
    scene(page, 'cover')
    assert not page.evaluate('state.shield || state.moon || state.key')
    final_state = stored(page)
    assert set(final_state) == {'moonCaveState', 'moonCaveTextScale'}
    assert not errors, errors
    assert not bad_responses, bad_responses
    record(label, {'journeys': '3 challenges, retry, manual rewards, branches/endings, A−/A+, reload, touch dragging, slot retention and restart passed.', 'finish_taps_after_drag_and_reload': {'secret': secret_finish_taps, 'ordinary': ordinary_finish_taps}})
    context.close()
    return {'storage': final_state, 'finish_taps': [secret_finish_taps, ordinary_finish_taps]}


def hub_and_legacy_storage(browser, base, out):
    for width, height in [(820, 1180), (768, 1024), (1024, 1366), (1180, 820), (390, 844)]:
        context = browser.new_context(viewport={'width': width, 'height': height}, has_touch=True)
        page = context.new_page()
        font_requests = []
        page.on('request', lambda r: font_requests.append(r.url) if re.search(r'\.(ttf|otf|woff2?)(?:\?|$)', r.url) else None)
        page.goto(base + '/Moon-cave/')
        page.wait_for_function('Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)')
        assert page.title() == '阿通的冒險世界'
        assert page.locator('.text-image').count() == 9
        assert page.get_by_role('heading', name='阿通的冒險世界').is_visible()
        assert page.get_by_role('link', name='開始冒險', exact=False).is_visible()
        assert page.locator('article').count() == 1
        assert page.locator('.cover-link img').evaluate('i => i.complete && i.naturalWidth === 1055')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.locator('.start').bounding_box()['height'] >= 56
        assert stored(page) == {}, 'Hub must not write localStorage'
        page.screenshot(path=str(out / f'hub-{width}x{height}.png'), full_page=True)
        page.locator('.start').tap()
        page.wait_for_url(base + '/Moon-cave/stories/moon-cave/')
        assert page.url == base + '/Moon-cave/stories/moon-cave/'
        scene(page, 'cover')
        page.get_by_role('link', name='返回冒險首頁').tap()
        page.wait_for_url(base + '/Moon-cave/')
        assert page.url == base + '/Moon-cave/'
        page.locator('.cover-link').tap()
        page.wait_for_url(base + '/Moon-cave/stories/moon-cave/')
        scene(page, 'cover')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(out / f'story-{width}x{height}.png'), full_page=True)
        assert not font_requests, 'No raw font should be served to the browser'
        context.close()
    record('responsive-navigation', 'Portrait/landscape tablet and phone layouts; cover and CTA entry; explicit return link; no horizontal overflow.')

    context = browser.new_context(viewport={'width': 820, 'height': 1180}, has_touch=True)
    page = context.new_page()
    Handler.legacy_root = True
    try:
        page.goto(base + '/Moon-cave/')
        action(page, "resetState('intro')")
        action(page, "go('entrance')")
        action(page, 'chooseStone()')
        page.get_by_role('button', name='放大文字').tap()
        previous = stored(page)
    finally:
        Handler.legacy_root = False
    page.reload()
    assert page.title() == '阿通的冒險世界'
    assert stored(page) == previous
    page.locator('.start').tap()
    page.wait_for_url(base + '/Moon-cave/stories/moon-cave/')
    scene(page, 'stone')
    assert stored(page) == previous
    assert abs(page.evaluate('scale') - 1.1) < .001
    page.get_by_role('link', name='返回冒險首頁').tap()
    page.wait_for_url(base + '/Moon-cave/')
    assert stored(page) == previous
    page.reload()
    page.locator('.cover-link').tap()
    page.wait_for_url(base + '/Moon-cave/stories/moon-cave/')
    scene(page, 'stone')
    assert stored(page) == previous
    record('legacy-storage', 'A v3 save created at the former root resumes at the nested path without key migration or changed values.')
    context.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('../hub-review'))
    parser.add_argument('--browser-executable')
    parser.add_argument('--only', choices=['all', 'baseline', 'relocated', 'hub'], default='all')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    preserved_story()
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path=args.browser_executable)
            try:
                if args.only in ['all', 'hub']:
                    hub_and_legacy_storage(browser, base, out)
                if args.only in ['all', 'baseline']:
                    before = story_regression(browser, base, '/baseline/', 'v3-baseline', out)
                if args.only in ['all', 'relocated']:
                    after = story_regression(browser, base, '/Moon-cave/stories/moon-cave/', 'relocated-v3', out)
                if args.only == 'all':
                    assert before == after
                    record('baseline-parity', 'The same complete UI journeys produce identical persisted state before and after relocation.')
            except Exception:
                failed_page = browser.contexts[-1].pages[-1]
                failed_page.screenshot(path=str(out / 'failure.png'), full_page=True)
                print('Failure state:', failed_page.evaluate('JSON.stringify(state)'), flush=True)
                raise
            browser.close()
    finally:
        server.shutdown()
        (out / 'test-results.json').write_text(json.dumps(RESULTS, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
