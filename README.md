# VAIZO AI環境セットアップ

Windows向けのCodex CLI・Claude Code CLI環境セットアップの配布ページです。

配布ページ：https://vaizo-ai-setup.pages.dev/

利用者は配布ページでツールを選び、EXEを開いてセットアップします。GitHubアカウントは不要です。現在の版は先行版で、セットアップEXEは未署名です。

この公開リポジトリには配布ページ・公開用メタデータ・公開手順だけを置きます。セットアッパーの開発ソースは別の非公開リポジトリで管理します。

## 公開構成

- 静的ページ：Cloudflare Pages（`vaizo-ai-setup`）
- 配布ファイル：このリポジトリのGitHub Releases
- 固定ダウンロード経路：`/download/codex`、`/download/claude`
- 版情報：`releases.json`からページ、リダイレクト、ハッシュ一覧を同時生成
- rc版はGitHub上でもprereleaseとして保持。GitHubの`releases/latest`に依存しない

## 更新手順

1. 開発リポジトリでビルドと検証を完了し、新しいバージョン付きEXEを用意する。
2. `releases.json`の版・ファイル名・SHA-256・サイズ・更新内容を更新する。既存版のEXEを上書きしない。
3. `python tools/publish.py` でファイル照合、公開用手順書・チェックサム・ページ生成を実行する。
4. 生成物と差分を確認してコミットし、GitHubへpushする。
5. `python tools/publish.py --publish --deploy` でリリース公開、匿名ダウンロード照合、Pages反映を行う。
6. 固定URLから両EXEを再取得し、SHA-256、ブラウザのボタンとページ表示を確認する。

`publish.py`は既存リリースのファイルを置換しません。既存ファイルとローカル成果物が一致しない場合は停止します。作成途中のdraftを見つけた場合も、状態を確認してから再開します。

初回のみPagesプロジェクトの作成が必要です。通常更新は同じプロジェクト名・固定経路を使います。GitHub CLIとWranglerの既存ログインを使い、トークンをファイルへ保存しません。手元のWindows PCから実行するため、GitHub Actionsの課金は発生しません。

## 配布範囲

各リリースには、選択したEXE、`START-HERE.txt`、`RELEASE-NOTES.md`、`SHA256SUMS.txt`だけを添付します。内部レビューZIP・Git履歴bundle・業務資料・認証情報は公開しません。

本セットアップは株式会社VAIZOによる導入支援ツールです。OpenAI・Anthropicによる公式配布物ではありません。各CLI・追加ソフトの利用には、各提供元の利用条件が適用されます。
