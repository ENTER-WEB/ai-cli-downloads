"""Build the public page and stable download routes from reviewed release metadata."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'

def read_manifest():
    data = json.loads((ROOT / 'releases.json').read_text(encoding='utf-8'))
    assert data['repository'] == 'ENTER-WEB/ai-cli-downloads'
    assert {p['id'] for p in data['products']} == {'codex', 'claude'}
    for p in data['products']:
        assert re.fullmatch(r'[a-z0-9.-]+', p['tag'])
        assert re.fullmatch(r'[A-Za-z0-9.-]+\.exe', p['file'])
        assert re.fullmatch(r'[a-f0-9]{64}', p['sha256'])
        assert p['sourceDirectory'] in ('windows-codex-setup', 'windows-claude-setup')
    return data

def download_url(data, p):
    return f"https://github.com/{data['repository']}/releases/download/{p['tag']}/{p['file']}"

def frame(title, body):
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} | VAIZO</title><meta name="description" content="Windows向けCodex CLI・Claude Code CLIの環境セットアップ。必要なツールを選んでダウンロードできます。">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"><script src="/share.js" defer></script></head>
<body><a href="#main" class="skip">本文へ移動</a><header><a class="brand" href="/" aria-label="VAIZO セットアップ ホーム">VAIZO</a><nav aria-label="ページ案内"><a href="/#steps">使い方</a><a href="/changes.html">更新情報</a></nav></header>
<main id="main">{body}</main><footer><p>提供：株式会社VAIZO<br>本セットアップはVAIZOが作成した導入支援ツールです。OpenAI・Anthropicによる公式配布物ではありません。各CLI本体は公式配布元から取得します。</p><a href="https://github.com/ENTER-WEB/ai-cli-downloads/releases">配布ファイル一覧</a></footer></body></html>'''

def build():
    data = read_manifest()
    rows = []
    changes = []
    redirects = []
    checksums = []
    for p in data['products']:
        e = {k: html.escape(str(v)) for k,v in p.items() if not isinstance(v, list)}
        rows.append(f'''<article class="product" aria-labelledby="{e['id']}-name"><div><h2 id="{e['id']}-name">{e['name']}</h2><p>{e['description']}</p><div class="version">v{e['version']} · Windows 11 / x64 · 先行版</div><a class="details-link" href="/changes.html#{e['id']}">この版の更新内容</a></div><div class="actions"><a class="download" href="/download/{e['id']}" aria-label="{e['name']} Windows用セットアップをダウンロード"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/></svg>Windows版をダウンロード</a><span class="file-meta">EXE · 約 {round(p['bytes']/1024)} KB · 導入時にネット接続が必要</span></div></article>''')
        changes.append(f'''<article id="{e['id']}"><h2>{e['name']} v{e['version']}</h2><ul>{''.join('<li>'+html.escape(c)+'</li>' for c in p['changes'])}</ul><p>セットアップEXEの電子署名：{'署名あり' if p['signed'] else '未署名'}</p><p><a href="{download_url(data,p)}">{e['file']}</a></p><p class="hash">SHA-256: {e['sha256']}</p></article>''')
        redirects.append(f"/download/{p['id']} {download_url(data,p)} 302")
        checksums.append(f"{p['sha256']}  {p['file']}")
    body = '''<section class="intro"><h1>CodexとClaude Codeを、<br>Windowsへ。</h1><p>使いたいツールを選んで、セットアップを開始してください。<br>必要な実行環境と作業用ツールをまとめて準備します。</p><div class="requirements"><span>Windows 11</span><span>Intel / AMD 64bit</span><span>配布ページへのログイン不要</span></div></section>
<section aria-label="セットアップのダウンロード">''' + ''.join(rows) + '''</section>
<p class="notice">現在のセットアップEXEは未署名の先行版です。Windowsの設定によって警告や実行制限が表示される場合があります。詳細は下の「起動が制限されたとき」をご確認ください。</p>
<section class="steps" id="steps"><h2>ダウンロードしたら、3ステップ。</h2><ol><li><h3>EXEを開く</h3><p>ダウンロードしたファイルを開き、作業フォルダと必要な追加アプリを選んでセットアップを開始します。</p></li><li><h3>自分のアカウントでログイン</h3><p>画面の案内に沿って、選んだAIサービスへログインします。利用に必要なアカウント・契約はご自身のものを使います。</p></li><li><h3>ターミナルから起動</h3><p>ターミナルの全ウィンドウを閉じて開き直し、<code>codex</code> または <code>claude</code> と入力します。</p></li></ol></section>
<section class="help" aria-labelledby="help-title"><h2 id="help-title">導入前に確認すること</h2><details><summary>対応するPCと、必要なもの</summary><p>Windows 11のIntel / AMD x64版、インターネット接続、10GB以上を目安とした空き容量が必要です。追加アプリにより必要容量は増えます。Mac、Windows ARM、Sモードは今回の配布対象に含みません。管理されているPCでは、組織の導入ルールに従ってください。</p></details><details><summary>何がセットアップされますか？</summary><p>選んだCLI、専用のPython・Node.js、Git関連ツール、文書・表・PDF・画像処理用ライブラリ、ブラウザ操作用ツールなどを準備します。Chrome・VS Code・Obsidianなどの追加アプリは、セットアップ画面で選択できます。各AIサービスの利用料金は別途、契約内容に従います。</p></details><details><summary>起動が制限されたとき</summary><p>このセットアップEXEには、発行元を検証する電子署名がまだ付いていません。Windowsの保護機能で拒否された場合は、その機能を無効にせず、表示された内容を配布元または組織の管理者へお知らせください。ファイルの照合用ハッシュは更新情報に掲載しています。</p></details><details><summary>セットアップ後にコマンドが見つからないとき</summary><p>ターミナルの新しいタブを開くだけでは、設定が反映されない場合があります。すべてのターミナルウィンドウを閉じて開き直してください。VS Code内で使う場合は、VS Codeも開き直します。解消しない場合はセットアップの確認画面で状態を確認してください。</p></details></section>
<section class="share"><div><h2>ほかのPCにも、このページから。</h2><p>同じリンクから、公開中の最新版をダウンロードできます。</p></div><div class="share-control"><button type="button" id="copy-link">配布リンクをコピー</button><span id="copy-status" role="status" aria-live="polite"></span></div></section>'''
    (SITE/'index.html').write_text(frame('AI環境セットアップ',body),encoding='utf-8')
    (SITE/'changes.html').write_text(frame('更新情報','<section class="changes"><a class="back" href="/">セットアップ一覧へ戻る</a><h1>更新情報</h1><p>現在配布している版と、ファイルを照合するための情報です。</p>'+''.join(changes)+'<p><a href="/SHA256SUMS.txt">チェックサム一覧を開く</a></p></section>'),encoding='utf-8')
    (SITE/'_redirects').write_text('\n'.join(redirects)+'\n',encoding='utf-8')
    (SITE/'SHA256SUMS.txt').write_text('\n'.join(checksums)+'\n',encoding='utf-8')
    public = {k:v for k,v in data.items() if k != 'pagesProject'}
    public['products'] = [{k:v for k,v in p.items() if k != 'sourceDirectory'} for p in data['products']]
    (SITE/'versions.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (SITE/'404.html').write_text(frame('ページが見つかりません','<section class="intro"><h1>ページが見つかりません。</h1><p><a href="/">セットアップのダウンロード一覧へ戻る</a></p></section>'),encoding='utf-8')
    print(json.dumps({'products':len(rows),'siteFiles':sorted(p.name for p in SITE.iterdir())}))
    return data

if __name__ == '__main__':
    build()
