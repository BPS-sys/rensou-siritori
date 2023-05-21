# 連想しりとり
## 使い方
### 1. gensimのword2vecを同一ディレクトリ内に設置する
### 2. 必要なライブラリをインストール
```
pip install pykakasi
pip install gensim
```
### 3. main.py（main.ipynb）を編集する
```
class App(tk.Frame):

    def __init__(self, root):
        super().__init__(root)
        self.model_name = 'wiki_model_sg_20.model'
        self.record = []
```
**self.model_nameにgensimのword2vecのモデル名をいれる**
### 4.実行
