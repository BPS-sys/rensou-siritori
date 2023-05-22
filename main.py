import rensou
import tkinter as tk


ROOT = tk.Tk()
rensou.App(ROOT, model_name='wiki_model_sg_20.model')
ROOT.mainloop()