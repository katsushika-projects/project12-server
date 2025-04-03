# project12-server

everstudyのバックエンド

## セットアップ

### 1. .envファイルの作成

```bash
pwd
# /path/to/project12-server
cp .env.dev .env
```

### 2. GoogleのClient IDとClient Secretを.envファイルに記述

Google Cloud Consoleでいろいろすると入手できます．

Client IDの値をSOCIAL_AUTH_GOOGLE_OAUTH2_KEYにセットし，
Client Secretの値をSOCIAL_AUTH_GOOGLE_OAUTH2_SECRETにセットしてください．


### 3. Dockerコンテナの起動

```bash
pwd
# /path/to/project12-server
make dev
```

で立ち上がります．

## コードのフォーマット等について

pushする前に，以下のコマンドでテストまで含めて問題がないことをチェックすると良い

```bash
make check
```

## Google認証の流れ．

### フロントエンド側で行うべき処理は以下

#### 1. ユーザーがGoogle認証ボタンを押す．

ボタンを押した際に，URLに情報を含めてGoogleのページに移動する．
JavaScriptのサンプルコードは以下

```js
const clientId = "< .envファイルののSOCIAL_AUTH_GOOGLE_OAUTH2_KEYと同じ値 >"; // Google Cloud Consoleで取得したクライアントID
        const redirectUri = "< 例: http://localhost:3000/callback >"; // 認証後のリダイレクト先 フロント側のURL
        const scope = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"; // 必要なスコープ

        // Google認証ページにリダイレクト
        document.getElementById("google-login").addEventListener("click", () => {
            const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?response_type=token&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${encodeURIComponent(scope)}`;
            window.location.href = authUrl;
        });
```

#### 2. リダイレクトしてきたURLからトークン情報を抜き出す.

ユーザーがGoogleの画面でポチポチすると，「1.ユーザーがGoogle認証ボタンを押す.」で指定したリダイレクト先にリダイレクトされる．
リダイレクト先のURLには，Googleのアクセストークン(Googleトークンと呼ぶことにする)が含まれるため，それを取り出す.

JavaScriptのサンプルコードは以下

```js
// URLからGoogleトークンを取得
function getGoogleAccessTokenFromUrl() {
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    return params.get("access_token");
}
```

#### 3. Googleトークンをバックエンドに送り，バックエンドとの通信用のアクセストークンを取得する．

流れは

1. Googleから受け取ったGoogleトークンをバックエンドに送信する．
2. そのGoogleトークンの有効性をバックエンド側で検証する．
3. OKだった場合バックエンドはフロントエンドにアクセストークン（を含むjson）を返す（このアクセストークンはGoogleトークンとは関係ない．）
4. 以後，このアクセストークンでバックエンドと通信する．

となる．

サンプルコードとしては以下

```js
// Django API endpoint
const backendUrl = "http://localhost:8000/auth/convert-token"; // Djangoのトークン変換エンドポイント
const djangoClientId = "< .envファイルのDJANGO_CLIENT_ID_OF_GOOGLEと同じ値 >"; // Django OAuth ToolkitのクライアントID

// GoogleアクセストークンをDjangoバックエンドに送信
async function sendTokenToDjango(googleToken) {
    const responseOutput = document.getElementById("response-output");
    const data = new URLSearchParams({
        grant_type: "convert_token",
        client_id: djangoClientId,
        backend: "google-oauth2",
        token: googleToken
    });

    try {
        const response = await fetch(backendUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: data
        });

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const jsonResponse = await response.json();
        responseOutput.textContent = JSON.stringify(jsonResponse, null, 2);
    } catch (error) {
        responseOutput.textContent = `Error: ${error.message}`;
    }
}
```