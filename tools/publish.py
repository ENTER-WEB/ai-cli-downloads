"""Prepare, publish and read back selected binaries. No paid CI or saved credentials."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import urllib.request
from build_site import ROOT, build, download_url

def run(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True, encoding='utf-8').strip()

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent':'VAIZO-setup-download-verification'})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()

def prepare(data):
    assets = {}
    for p in data['products']:
        source = ROOT.parent / p['sourceDirectory'] / 'dist' / p['file']
        raw = source.read_bytes()
        if digest(raw) != p['sha256'] or len(raw) != p['bytes']:
            raise RuntimeError(f"Selected EXE does not match reviewed metadata: {p['id']}")
        target = ROOT/'output'/'release-assets'/p['id']
        target.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target/p['file'])
        checksum=target/'SHA256SUMS.txt'
        checksum.write_text(f"{p['sha256']}  {p['file']}\n",encoding='utf-8')
        instructions=target/'START-HERE.txt'
        instructions.write_text(f"""{p['name']} 環境セットアップ {p['version']}
提供：株式会社VAIZO

Windows 11 / Intel・AMD x64向け。ネット接続と十分な空き容量が必要です。

1. {p['file']} を開く。
2. 作業フォルダと必要な追加アプリを選び、セットアップを開始する。
3. 画面の案内に沿って本人のAIサービスのアカウントでログインする。
4. ターミナルの全ウィンドウを閉じ、開き直す。
5. {p['id']} と入力して起動する。

現在のセットアップEXEは未署名の先行版です。Windowsの保護機能に拒否された場合は、
機能を無効にせず、配布元または組織管理者へ表示内容を伝えてください。
Mac、Windows ARM、Sモードは対象外です。各AIサービスの利用条件・契約は別途必要です。

本セットアップはOpenAI・Anthropicの公式配布物ではありません。
各CLI本体は公式の配布元から取得します。
""",encoding='utf-8-sig')
        notes=target/'RELEASE-NOTES.md'
        notes.write_text(f"# {p['name']} 環境セットアップ {p['version']}\n\nWindows 11 / Intel・AMD x64向けの先行版です。\n\n"+'\n'.join('- '+c for c in p['changes'])+f"\n\nセットアップEXE：未署名。認証情報・アカウント設定は含みません。各CLI本体は公式配布元から取得します。\n\n使い方は添付の START-HERE.txt を参照してください。\n\nSHA-256（{p['file']}）\n\n`{p['sha256']}`\n",encoding='utf-8')
        assets[p['id']]=[target/p['file'],checksum,instructions,notes]
    return assets

def publish(data, assets):
    repo=data['repository']
    metadata=json.loads(run('gh','api',f'repos/{repo}'))
    if metadata['private'] or metadata['full_name'] != repo:
        raise RuntimeError('Public distribution repository identity mismatch')
    existing=json.loads(run('gh','release','list','--repo',repo,'--limit','100','--json','tagName,isDraft,isPrerelease'))
    receipt=[]
    for p in data['products']:
        known=next((r for r in existing if r['tagName']==p['tag']),None)
        if known is not None:
            if known['isDraft']:
                raise RuntimeError(f"A draft already exists; inspect before resuming: {p['tag']}")
        else:
            run('gh','release','create',p['tag'],*[str(a) for a in assets[p['id']]],'--repo',repo,'--title',f"{p['name']} setup {p['version']}",'--notes-file',str(assets[p['id']][-1]),'--prerelease','--latest=false','--target','main')
        release=json.loads(run('gh','release','view',p['tag'],'--repo',repo,'--json','tagName,isDraft,isPrerelease,url,assets'))
        assert release['tagName']==p['tag'] and not release['isDraft'] and release['isPrerelease']
        verified=[]
        for asset in assets[p['id']]:
            url=f"https://github.com/{repo}/releases/download/{p['tag']}/{asset.name}"
            raw=fetch(url)
            if digest(raw) != digest(asset.read_bytes()):
                raise RuntimeError(f'Anonymous download mismatch: {asset.name}')
            verified.append({'file':asset.name,'bytes':len(raw),'sha256':digest(raw)})
        receipt.append({'id':p['id'],'releaseUrl':release['url'],'downloadUrl':download_url(data,p),'anonymousVerified':verified})
    (ROOT/'output'/'release-readback.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--publish',action='store_true',help='Publish reviewed assets; otherwise only prepare locally')
    parser.add_argument('--deploy',action='store_true',help='After release readback, deploy the static site to Cloudflare')
    args=parser.parse_args()
    if args.deploy and not args.publish:
        parser.error('--deploy requires --publish and successful anonymous release readback')
    data=build()
    assets=prepare(data)
    if args.publish:
        publish(data,assets)
    if args.deploy:
        sha=run('git','rev-parse','HEAD')
        if run('git','status','--porcelain','--untracked-files=all'):
            raise RuntimeError('Commit the selected manifest and generated site before deployment')
        executable=shutil.which('wrangler.cmd') or shutil.which('wrangler')
        if not executable:
            raise RuntimeError('Wrangler CLI is not installed')
        subprocess.run([executable,'pages','deploy','site','--project-name',data['pagesProject'],'--branch','main','--commit-hash',sha],cwd=ROOT,check=True)
    if not args.publish:
        print('Prepared assets locally; nothing published.')
