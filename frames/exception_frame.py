import customtkinter as ctk

class ExceptionFrame(ctk.CTkToplevel):
	def __init__(self, text, **kwargs):
		super().__init__(**kwargs)
		self.text = text

		self.title('Ошибка!')
		self.geometry('400x200')
		self.resizable(False, False)
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)
		
		self.label = ctk.CTkLabel(self, text=self.text)
		self.label.grid(row=0, column=0, padx=(15, 15), pady=(15, 15))


def exception(text):
	exception_frame = ExceptionFrame(text=text)
	exception_frame.after(100, exception_frame.lift)