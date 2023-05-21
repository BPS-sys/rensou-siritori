
import music2ps


mp = music2ps.music()
# パスの設定
mp.set_path(NEUTRINO='NEUTRINO', music='さくら.musicxml', lyrics='さくら.txt')
# モデル読み込み
model = mp.load_model('wiki_model_sg_20.model', max_word=200, similar_percent=0.6)
# 歌詞ファイル読み込み、加工
texts = mp.load_lyrics_file()
# 歌詞改変
converted_text = mp.convert(model=model, texts=texts)
# NEUTRINO実行
mp.run(converted_text)
# 再生
mp.play(converted_text)
