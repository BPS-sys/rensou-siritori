# 連想しりとり
## 使い方
### 1. gensimのword2vecモデルを同一ディレクトリ内に設置する
### 2. 必要なライブラリをインストール
```
pip install pykakasi
pip install gensim
```
### 3. main.py（main.ipynb）を編集する
```
rensou.App(ROOT, model_name='wiki_model_sg_20.model')
```
**引数model_nameにgensimのword2vecのモデル名をいれる**
### 4.実行
