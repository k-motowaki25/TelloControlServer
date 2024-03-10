# TelloControlServer
## 概要
ドローンやカメラ等の接続端末を管理する為のサーバ。サーバに送信されたデータの管理、加工、送信等を行う。

## 環境
- python 3.11.4
- macOS 14 (Sonoma)

## 使用方法
### CUIベースでの使用
以下プロンプト実行によりサーバ起動。端末接続や送信処理が自動で行われる。
```
python3 server.py
```
### GUIベースでの使用
以下プロンプト実行によりサーバ起動。端末接続や送信処理が自動で行われる。
```
python3 monitor.py
```
### GUIベースでの使用(ドローン等の自動接続込み, mac限定)
1. run.appに実行権限を付与する
2. run.appをクリックして実行(起動中は操作をしない)

※ マイコンのssh認証が済んでいないとエラーを起こす