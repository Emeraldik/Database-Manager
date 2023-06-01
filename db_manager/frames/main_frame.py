import customtkinter as ctk

import db_manager.config as cfg
from db_manager.frames.navigation_frame import NavigationBar

class App(ctk.CTk):
	def __init__(self):
		super().__init__()
		self.title(cfg.TITLE)
		
		if cfg.MINSIZE_MODE:
			self.resizable(True, True)
			self.minsize(*(cfg.WINDOW_SIZE))
		else:
			width, height = cfg.WINDOW_SIZE
			self.resizable(False, False)
			self.geometry(f'{width}x{height}')


		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)

		self.navigation_frame = NavigationBar(self)
		self.navigation_frame.grid(row=0, column=0, sticky='nsew')