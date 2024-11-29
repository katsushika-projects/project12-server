"""yamlファイルのサンプルに環境変数を代入し、新しいyamlファイルを作成するスクリプト."""

import os
from pathlib import Path

import yaml

# YAMLファイルのパスを指定
INPUT_FILE = Path("dev_db_data_sample.yaml")
OUTPUT_FILE = Path("dev_db_data.yaml")

# 環境変数から新しいパスワードを取得
DJANGO_CLIENT_ID_OF_GOOGLE = os.getenv("DJANGO_CLIENT_ID_OF_GOOGLE")
DJANGO_CLIENT_SECRET_OF_GOOGLE = os.getenv("DJANGO_CLIENT_SECRET_OF_GOOGLE")

if not DJANGO_CLIENT_ID_OF_GOOGLE:
    message = "環境変数 'DJANGO_CLIENT_ID_OF_GOOGLE' が設定されていません。"
    raise ValueError(message)

if not DJANGO_CLIENT_SECRET_OF_GOOGLE:
    message = "環境変数 'DJANGO_CLIENT_SECRET_OF_GOOGLE' が設定されていません。"
    raise ValueError(message)


def create_new_yaml(input_file: Path, output_file: Path, client_id: str, client_secret: str) -> None:
    """yamlファイルのサンプルに、環境変数を代入し新しいyamlファイルを作成する関数."""
    # YAMLファイルを読み込む
    with Path.open(input_file) as f:
        data = yaml.safe_load(f)

    # データを更新する
    for entry in data:
        if entry.get("model") == "oauth2_provider.application":  # oauth2_provider.applicationモデルを探す
            entry["fields"]["client_id"] = client_id
            entry["fields"]["client_secret"] = client_secret

    # 更新後のデータを新しいファイルに保存
    with Path.open(output_file, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


# スクリプトの実行
create_new_yaml(INPUT_FILE, OUTPUT_FILE, DJANGO_CLIENT_ID_OF_GOOGLE, DJANGO_CLIENT_SECRET_OF_GOOGLE)
