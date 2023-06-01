import customtkinter as ctk

import db_manager.frames.main_frame as mf


def main():
	ctk.set_appearance_mode('System') # Light, System, Dark
	ctk.set_default_color_theme('dark-blue') # blue, dark-blue, green

	app = mf.App()
	app.mainloop()


if __name__ == '__main__':
	main()