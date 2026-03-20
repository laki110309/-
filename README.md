# Discord Reminder Bot for Railway

24時間稼働し、スラッシュコマンドでリマインド設定ができるDiscordボットです。

## 🚀 セットアップ手順

### 1. Discord Botの作成
1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセスし、`New Application`をクリックします。
2. `Bot`タブに移動し、`Reset Token`をクリックしてボットの**トークン**をコピーしておきます。
3. 同じ`Bot`タブで、`Message Content Intent`を**ON**にします。
4. `OAuth2` -> `URL Generator`で、`bot`と`applications.commands`を選択し、ボットの権限（`Send Messages`など）にチェックを入れて生成されたURLでサーバーに招待します。

### 2. GitHubリポジトリの作成
1. GitHubで新しいリポジトリを作成します。
2. このフォルダの内容をGitHubにアップロードします。

### 3. Railwayへのデプロイ
1. [Railway](https://railway.app/)にログインし、`New Project` -> `Deploy from GitHub repo`を選択します。
2. 作成したリポジトリを選択します。
3. `Variables`タブで、以下の環境変数を設定します。
   - `DISCORD_TOKEN`: ステップ1でコピーしたボットのトークン

### 4. 使い方
Discord上で `/remind` と入力すると、リマインド設定ができます。
- `time`: リマインドする時間（例: 08:30）
- `message`: 送りたい一言
- `user`: メンションしたい相手（未指定なら自分）

---
このボットはRailway上で24時間稼働し続け、指定した時間になると自動的にメッセージを送信します。
