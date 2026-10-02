"""Verify shipped Story 05 assets, originals and runtime text/audio references."""
import hashlib, json, wave
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
STORY=ROOT/'stories/story-05'

def main():
    config=json.loads((STORY/'story.json').read_text(encoding='utf-8'))
    images=json.loads((STORY/'assets/ASSET_MANIFEST.json').read_text(encoding='utf-8'))
    text=json.loads((STORY/'assets/text/text.json').read_text(encoding='utf-8'))
    audio=json.loads((STORY/'assets/audio/manifest.json').read_text(encoding='utf-8'))
    assert set(config['labels'])==set(text['labels'])
    assert len(config['scenes'])==16
    assert ''.join(''.join(s['letters']) for s in config['stages'])=='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for item in images['assets']:
        path=STORY/'assets/images'/item['file'];assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'],item['file']
    referenced=set()
    for label,entry in text['labels'].items():
        assert entry['text']==config['labels'][label]
        for part in entry['parts']:
            path=STORY/'assets/text'/part['src'];referenced.add(path.name)
            with Image.open(path) as image:
                assert image.size==(part['width'],part['height']) and image.mode=='RGBA'
                box=image.getbbox();assert box and box[0]>0 and box[1]>0 and box[2]<image.width and box[3]<image.height
    assert referenced=={p.name for p in (STORY/'assets/text').glob('*.png')}
    for key,entry in audio['entries'].items():
        path=STORY/'assets/audio'/entry['src'];assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'],key
        if path.suffix=='.wav':
            with wave.open(str(path),'rb') as wav:assert wav.getnframes()>1000 and wav.getsampwidth()==2
        else:assert path.suffix=='.mp3' and entry['license']=='CC BY 4.0'
    sources=json.loads((STORY/'assets/audio/letters/sources.json').read_text(encoding='utf-8'))
    records=json.loads((STORY/'assets/audio/letters/manifest.json').read_text(encoding='utf-8'))
    assert [s['letter'] for s in sources]==list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    assert [s['letter'] for s in records]==list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    pcm_hashes=set()
    for source,record in zip(sources,records):
        letter=source['letter'];entry=audio['entries']['letter-'+letter]
        assert record=={k:entry[k] for k in record},letter
        assert entry['src']=='letters/'+letter.lower()+'.wav',letter
        assert source['sourceFile'][6].upper()==letter,letter
        original=STORY/'assets/audio/letters'/source['original']
        assert hashlib.sha1(original.read_bytes()).hexdigest()==source['sourceSha1'],letter
        assert source['license'] in ('Public domain','CC BY-SA 3.0','CC BY-SA 4.0')
        with wave.open(str(STORY/'assets/audio'/entry['src']),'rb') as wav:
            pcm=wav.readframes(wav.getnframes());digest=hashlib.sha256(pcm).hexdigest()
            assert any(pcm) and digest not in pcm_hashes,('duplicate letter audio',letter)
            pcm_hashes.add(digest)
    assert len(pcm_hashes)==26
    assert not list(STORY.rglob('*.ttf')) and not list(STORY.rglob('*.woff*')) and not list(STORY.rglob('*.otf'))
    print(f'PASS {len(images["assets"])} unchanged original PNGs, {len(text["labels"])} labels / {len(referenced)} text PNGs, {len(audio["entries"])} audio files, no fonts')

if __name__=='__main__':main()
