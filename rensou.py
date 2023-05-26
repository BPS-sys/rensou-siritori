
import tkinter as tk
import gensim
from pykakasi import kakasi
import string
import threading
import webbrowser
import sys
import os


class App(tk.Frame):

    def __init__(self, root, model_name=None):
        super().__init__(root)
        self.model_name = model_name
        self.record = []
        self.max_word = 500
        self.judge_max_word = 50000
        self.first = True
        self.rensou_mode = False
        self.ai_word_hira = ''
        self.ai_words = ''
        self.root = root
        read_thread = threading.Thread(target=self.read_model)
        self.setting_gui()
        read_thread.start()
    
    # GUI設定
    def setting_gui(self):
        self.root.title('連想・連想しりとりゲーム')
        self.root.geometry('640x480')
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(width=640, height=480,
                                bg='black', highlightthickness=0)
        self.canvas.place(x=0, y=0)
        self.entry_box = tk.Entry(self.canvas)
        self.entry_box.place(x=60, y=420, width=480, height=40)
        self.send_button = tk.Button(self.canvas, text='送信',
                                     width=3, height=2,
                                     command=self.send_click, anchor=tk.CENTER)
        self.send_button['state'] = 'disabled'
        self.send_button.place(x=550, y=420)
        self.change_button = tk.Button(self.canvas, text='変更',
                                     width=3, height=2,
                                     command=self.change_click, anchor=tk.CENTER)
        self.change_button['state'] = 'disabled'
        self.change_button.place(x=20, y=420)
        self.search_button = tk.Button(self.canvas, text='検索',
                                     width=3, height=2,
                                     command=self.search_click, anchor=tk.CENTER)
        self.search_button['state'] = 'disabled'
        self.search_button.place(x=590, y=420)
        icon_img = tk.PhotoImage(file=self.resource_path('icon.png'))
        self.root.iconphoto(False, icon_img)

    # モデル読み込み
    def read_model(self):
        self.canvas.create_text(320, 50, text='モデルロード中...', 
                                    fill='white', tag='sys_message', anchor=tk.CENTER,
                                    font=('', 30))
        self.model = gensim.models.Word2Vec.load(self.model_name)
        self.send_button['state'] = 'normal'
        self.change_button['state'] = 'normal'
        self.search_button['state'] = 'normal'
        self.canvas.delete('sys_message')
        self.canvas.create_text(320, 50, text='ロード完了', 
                                    fill='white', tag='sys_message', anchor=tk.CENTER,
                                    font=('', 30))
    
    #展開されたファイルの読み込み
    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    # ボタンクリック処理
    def send_click(self):
        # ユーザー入力
        user_word = self.entry_box.get()
        self.entry_box.delete(0, tk.END)
        if not self.rensou_mode:
            self.rensou_siritori(user_word)
        else:
            self.rensou(user_word)

    # ゲームモード変更
    def change_click(self):
        if self.rensou_mode:
            self.rensou_mode = False
            self.first = True
            self.record = []
            self.canvas.delete('sys_message')
            self.canvas.create_text(320, 50, text='連想しりとりモードに変更されました', 
                                fill='white', tag='sys_message', anchor=tk.CENTER,
                                font=('', 30))
        else:
            self.rensou_mode = True
            self.first = True
            self.record = []
            self.canvas.delete('sys_message')
            self.canvas.create_text(320, 50, text='連想モードに変更されました', 
                                fill='white', tag='sys_message', anchor=tk.CENTER,
                                font=('', 30))

    # 連想しりとり
    def rensou_siritori(self, user_word):
        if user_word == '' or '　'in user_word or ' 'in user_word:
            return
        # 英数字を弾く
        for word in user_word:
            if word in string.printable:
                self.canvas.delete('sys_message')
                self.canvas.create_text(320, 50, text='英数字は使えません。', 
                                    fill='white', tag='sys_message', anchor=tk.CENTER,
                                    font=('', 30))
                return        
        # 既出のものは弾く
        if user_word in self.record:
            self.canvas.delete('sys_message')
            self.canvas.create_text(320, 50, text='既出のものは使えません。', 
                                    fill='white', tag='sys_message', anchor=tk.CENTER,
                                    font=('', 30))
            return
        # ひらがな、カタカナ変換
        kks = kakasi()
        user_kakasi = kks.convert(user_word)
        user_word_hira = ''
        for j in range(len(user_kakasi)):
            user_word_hira += user_kakasi[j]['hira']
        while user_word[-1] == 'ー':
            user_word = user_word[:-1]
        if not user_word:
            return
        user_word_hira = self.replace_tail(user_word_hira)
        # ユーザーの入力の語尾が「ん」
        if user_word_hira[-1] == 'ん':
            self.canvas.delete('ai_word')
            self.canvas.delete('sys_message')
            self.canvas.create_text(320, 50, text='USERの負け。', 
                                    fill='white', tag='sys_message', anchor=tk.CENTER,
                                    font=('', 30))
            self.first = True
            self.record = []
            return
        # 初ターンは無視
        if not self.first:
            # ユーザーの入力がしりとりになっているか
            if user_word_hira[0] != self.ai_word_hira[-1]:
                self.canvas.delete('sys_message')
                self.canvas.create_text(320, 50, text='しりとりで答えてくださ' \
                                        'い。', fill='white', tag='sys_message',
                                        anchor=tk.CENTER, font=('', 30))
                return
        # aiの知らない言葉は弾く
        try:
            self.model.wv.most_similar(user_word, topn=self.judge_max_word)
        except KeyError:
            self.canvas.delete('sys_message')
            self.canvas.create_text(320, 50, text='aiの知らない言葉です。', 
                                    fill='white', tag='sys_message', anchor=tk.CENTER,
                                    font=('', 30))
            return
        # 初ターンは無視
        if not self.first:
            # ユーザーの入力が連想になっているか
            judge_words = self.model.wv.most_similar(self.ai_word, topn=self.judge_max_word)
            for i in range(self.max_word):
                if judge_words[i][0] == user_word:
                    break
            else:
                self.canvas.delete('sys_message')
                self.canvas.create_text(320, 50, text='連想できません。',
                                        fill='white', tag='sys_message',
                                        anchor=tk.CENTER, font=('', 30))
                return
        self.record.append(user_word_hira)
        self.ai_words = self.model.wv.most_similar(user_word, topn=self.judge_max_word)
        # 二回目以降はFalse
        self.first = False
        # 同じ言葉はなし！のルール
        for i in range(self.max_word):
            self.ai_word = self.ai_words[i][0]
            # 英数字を弾く
            if self.ai_word in string.printable:
                continue
            # ひらがな変換
            ai_kakasi = kks.convert(self.ai_word)
            self.ai_word_hira = ''
            for j in range(len(ai_kakasi)):
                self.ai_word_hira += ai_kakasi[j]['hira']
            # 既出のものは弾く
            if self.ai_word in self.record:
                continue
            if not self.ai_word_hira:
                continue
            # しりとりルール!
            if self.ai_word_hira[0] == user_word_hira[-1] and self.ai_word_hira[-1] != 'ん' and self.ai_word_hira[-1] != 'ー':
                self.ai_word_hira = self.replace_tail(self.ai_word_hira)
                self.record.append(self.ai_word_hira)
                self.canvas.delete('ai_word')
                self.canvas.delete('sys_message')
                self.canvas.create_text(320, 190, text=self.ai_word_hira, 
                                        fill='white', tag='ai_word',
                                        anchor=tk.CENTER, font=('', 10))
                self.canvas.create_text(320, 220, text=self.ai_word, 
                                        fill='white', tag='ai_word', 
                                        anchor=tk.CENTER, font=('', 25))
                break
        # max_word内で見つからなかった場合の判定
        else:
            self.canvas.delete('ai_word')
            self.canvas.delete('sys_message')
            self.canvas.create_text(320, 50, text='AIの負け！', fill='white', 
                                    tag='sys_message', anchor=tk.CENTER, font=('', 30))
            self.first = True
            self.record = []
            return
    
    def rensou(self, user_word):
        # 空白を弾く
        if user_word == '' or '　'in user_word or ' 'in user_word:
            return
        # 既出を弾く
        if user_word in self.record:
            self.canvas.delete('sys_message')
            self.canvas.create_text(320, 50, text='既出のものは使えません。', 
                                    fill='white', tag='sys_message', anchor=tk.CENTER,
                                    font=('', 30))
            return
        for word in user_word:
            if word in string.printable[62:-6]:
                self.canvas.delete('sys_message')
                self.canvas.create_text(320, 50, text='記号は使えません。', 
                                    fill='white', tag='sys_message', anchor=tk.CENTER,
                                    font=('', 30))
                return        
        # ai認知テスト
        try:
            self.model.wv.most_similar(user_word, topn=self.judge_max_word)
        except KeyError:
            self.canvas.delete('sys_message')
            self.canvas.create_text(320, 50, text='aiの知らない言葉です。', 
                                    fill='white', tag='sys_message', anchor=tk.CENTER,
                                    font=('', 30))
            return
        # 初回は弾く
        if not self.first:
            # ユーザーの入力が連想になっているか
            judge_words = self.model.wv.most_similar(self.ai_word,
                                                     topn=self.judge_max_word)
            for i in range(self.max_word):
                if judge_words[i][0] == user_word:
                    break
            else:
                self.canvas.delete('sys_message')
                self.canvas.create_text(320, 50, text='連想できません。',
                                        fill='white', tag='sys_message',
                                        anchor=tk.CENTER, font=('', 30))
                return
        self.ai_words = self.model.wv.most_similar(user_word, topn=self.judge_max_word)
        self.record.append(user_word)
        # 二回目以降はFalse
        self.first = False
        # 同じ言葉はなし！のルール
        for i in range(self.max_word):
            self.ai_word = self.ai_words[i][0]
            if self.ai_word in string.ascii_letters:
                continue
            if not self.ai_word:
                continue
            kks = kakasi()
            ai_kakasi = kks.convert(self.ai_word)
            self.ai_word_hira = ''
            for j in range(len(ai_kakasi)):
                self.ai_word_hira += ai_kakasi[j]['hira']
            if self.ai_word in self.record or self.ai_word_hira in self.record:
                continue
            self.record.append(self.ai_word)
            self.canvas.delete('ai_word')
            self.canvas.delete('sys_message')
            self.canvas.create_text(320, 190, text=self.ai_word_hira, 
                                        fill='white', tag='ai_word', 
                                        anchor=tk.CENTER, font=('', 10))
            self.canvas.create_text(320, 220, text=self.ai_word, 
                                    fill='white', tag='ai_word', 
                                    anchor=tk.CENTER, font=('', 25))
            break
        # max_word内で見つからなかった場合の判定
        else:
            self.canvas.delete('ai_word')
            self.canvas.delete('sys_message')
            self.canvas.create_text(320, 50, text='AIの負け！', fill='white', 
                                    tag='sys_message', anchor=tk.CENTER, font=('', 30))
            self.first = True
            self.record = []
            return
    
    def search_click(self):
        if not self.first:
            webbrowser.open(f'https://www.google.com/search?q={self.ai_word}')

    # 小文字の置き換え
    def replace_tail(self, word):
        original_word = ['ゃ', 'ゅ', 'ょ', 'ぁ', 'ぃ', 'ぅ', 'ぇ', 'ぉ', 'っ']
        change_word = ['や', 'ゆ', 'よ', 'あ', 'い', 'う', 'え', 'お', 'つ']
        for i, original in enumerate(original_word):
            if word[-1] == original:
                word = word[:-1] + change_word[i]
        return word
