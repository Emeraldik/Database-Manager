import customtkinter as ctk

from modules.database import execute
from frames.extra_frame import AddFrame, ChangeFrame

class NavigationButton(ctk.CTkButton):
	def __init__(self, master, **kwargs):
		super().__init__(
			master,
			corner_radius=0, 
			height=50, 
			border_spacing=10,
			fg_color="transparent", 
			text_color=("gray10", "gray90"), 
			hover_color=("gray70", "gray30"),
			anchor="center", 
			**kwargs
		)


class DataButton(ctk.CTkButton):
	def __init__(self, master, **kwargs):
		super().__init__(
			master,
			corner_radius=10, 
			height=60, 
			border_spacing=10,
			text_color=("gray10", "gray90"),
			anchor="center", 
			**kwargs
		)


class DataButtonFrames(ctk.CTkFrame):
	def __init__(self, master, datatype, **kwargs):
		super().__init__(master, **kwargs)
		self.master = master
		self.datatype = datatype
		self.grid_rowconfigure(0, weight=1)

		match self.datatype:
			case 'Список персонала':
				self.grid_columnconfigure((0, 1, 2, 3), weight=1)
				self.button1 = DataButton(self, text='Добавить сотрудника', command=self.add_action)
				self.button1.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=(5, 5))
				self.button2 = DataButton(self, text='Удалить сотрудника', command=self.delete_action)
				self.button2.grid(row=0, column=1, sticky='nsew', padx=(5, 5), pady=(5, 5))
				self.button3 = DataButton(self, text='Изменить сотрудника', command=self.change_action)
				self.button3.grid(row=0, column=2, sticky='nsew', padx=(5, 5), pady=(5, 5))
				self.button4 = DataButton(self, text='Манпулировать отпуском')
				self.button4.grid(row=0, column=3, sticky='nsew', padx=(5, 5), pady=(5, 5))
			case 'Отделы':
				self.grid_columnconfigure((0, 1, 2), weight=1)
				self.button1 = DataButton(self, text='Добавить отдел', command=self.add_action)
				self.button1.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=(5, 5))
				self.button2 = DataButton(self, text='Удалить отдел', command=self.delete_action)
				self.button2.grid(row=0, column=1, sticky='nsew', padx=(5, 5), pady=(5, 5))
				self.button3 = DataButton(self, text='Изменить отдел', command=self.change_action)
				self.button3.grid(row=0, column=2, sticky='nsew', padx=(5, 5), pady=(5, 5))
			case 'Проекты':
				self.grid_columnconfigure((0, 1, 2), weight=1)
				self.button1 = DataButton(self, text='Добавить проект', command=self.add_action)
				self.button1.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=(5, 5))
				self.button2 = DataButton(self, text='Удалить проект', command=self.delete_action)
				self.button2.grid(row=0, column=1, sticky='nsew', padx=(5, 5), pady=(5, 5))
				self.button3 = DataButton(self, text='Изменить проект', command=self.change_action)
				self.button3.grid(row=0, column=2, sticky='nsew', padx=(5, 5), pady=(5, 5))
			case 'Распределение зарплаты сотрудников':
				self.grid_columnconfigure((0, 1, 2), weight=1)
				self.button1 = DataButton(self, text='Изменить зарплату сотруднику')
				self.button1.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=(5, 5))
				self.button2 = DataButton(self, text='Изменить зарплату отделу/проекту')
				self.button2.grid(row=0, column=1, sticky='nsew', padx=(5, 5), pady=(5, 5))
				self.button3 = DataButton(self, text='Изменить зарплату с условием')
				self.button3.grid(row=0, column=2, sticky='nsew', padx=(5, 5), pady=(5, 5))

		self.add_frame = None
		self.change_frame = None

	def add_action(self):
		if self.add_frame is None or not self.add_frame.winfo_exists():
			self.add_frame = AddFrame(self.master, self.datatype)
			self.add_frame.after(100, self.add_frame.lift)
		else:
			self.add_frame.focus()

	def change_action(self):
		selection = self.master.treeview.selection()
		if not selection:
			print('Вы не выбрали ничего')
			return

		data = self.master.treeview.item(selection)['values'][0]

		if self.change_frame is None or not self.change_frame.winfo_exists():
			self.change_frame = ChangeFrame(self.master, self.datatype, data)
			self.change_frame.after(100, self.change_frame.lift)
		else:
			self.change_frame.focus()

	def delete_action(self):
		selection = self.master.treeview.selection()
		if not selection:
			return

		item = self.master.treeview.item(selection)
		match self.datatype:
			case 'Список персонала':
				sql = '''
					DELETE FROM Salary
					WHERE worker_id = %s;
					DELETE FROM Worker
					WHERE id = %s
				'''

				execute(sql, tuple(item['values'][0] for _ in range(2)))
			case 'Отделы':
				sql = '''
					DELETE FROM Department
					WHERE id = %s
				'''

				execute(sql, (item['values'][0],))
			case 'Проекты':
				sql = '''
					DELETE FROM Project
					WHERE id = %s
				'''

				execute(sql, (item['values'][0],))
		
		self.master.treeview.delete(selection)