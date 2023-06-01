import customtkinter as ctk
from db_manager.frames.data_frame import MainDataFrame
from db_manager.frames.button_frame import NavigationButton

class NavigationBar(ctk.CTkFrame):
	def __init__(self, master, **kwargs):
		super().__init__(master, **kwargs)

		self.grid_rowconfigure(5, weight=1)
		self.rowconfigure((6,7), weight=0)

		self.set_appearance = ctk.CTkOptionMenu(self, values=['Dark', 'Light', 'System'], command=lambda choice: ctk.set_appearance_mode(choice))
		self.set_appearance.grid(row=6, column=0, padx=(15, 15), pady=(20, 10), sticky="ew")
		
		values = [f'{k}%' for k in range(70, 181, 10)]
		self.set_scale = ctk.CTkOptionMenu(self, values=values, variable=ctk.StringVar(value='100%'), command=lambda choice: ctk.set_widget_scaling(int(choice.replace('%', '')) / 100))
		self.set_scale.grid(row=7, column=0, padx=(15, 15), pady=(20, 20), sticky="ew")

		self.navigation_frame_label = ctk.CTkLabel(
			self, 
			text="Навигация",
			compound="center", 
			font=ctk.CTkFont(size=30, weight="bold")
		)
		self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=(10, 0))

		self.personal = NavigationButton(
			self, 
			text="Список персонала",
			command=lambda: self.select_frame_by_name('Список персонала')
		)
		self.personal.grid(row=1, column=0, pady=(10, 10), sticky="ew")

		self.department = NavigationButton(
			self, 
			text="Отделы",
			command=lambda: self.select_frame_by_name('Отделы')
		)
		self.department.grid(row=2, column=0, pady=(10, 10), sticky="ew")

		self.projects = NavigationButton(
			self, 
			text="Проекты",
			command=lambda: self.select_frame_by_name('Проекты')
		)
		self.projects.grid(row=3, column=0, pady=(10, 10), sticky="ew")

		self.salary = NavigationButton(
			self, 
			text="Распределение зарплаты сотрудников",
			command=lambda: self.select_frame_by_name('Распределение зарплаты сотрудников')
		)
		self.salary.grid(row=4, column=0, pady=(10, 10), sticky="ew")

		self.buttons = {
			'Список персонала':self.personal, 
			'Отделы':self.department, 
			'Проекты':self.projects, 
			'Распределение зарплаты сотрудников':self.salary
		}

		self.frames = {}
		for frame_name in ('Список персонала', 'Отделы', 'Проекты', 'Распределение зарплаты сотрудников'):
			frame = MainDataFrame(self.master, self, datatype=frame_name)
			frame.grid(row=0, column=1, padx=(5, 5), sticky="nsew")
			self.frames[frame_name] = frame

		self.selected_frame = ''
		self.select_frame_by_name('Список персонала')

	def select_frame_by_name(self, name, button=None):
		if self.selected_frame == name:
			return

		self.selected_frame = name

		for but in self.buttons.values():
			but.configure(fg_color='transparent')

		self.buttons[name].configure(fg_color=("gray75", "gray25"))
		self.frames[name].update_tables()
		self.frames[name].tkraise()
