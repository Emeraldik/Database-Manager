import customtkinter as ctk

from modules.database import execute
from frames.extra_frame import AddFrame, ChangeFrame, HeadFrame
from frames.salary_frame import ChangeSalary, BusinessTripFrame
from frames.exception_frame import exception


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
				self.button4 = DataButton(self, text='Манпулировать командировкой', command=self.trip_action)
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
				self.button4 = DataButton(self, text='Установить ответственного', command=self.set_head)
				self.button4.grid(row=0, column=3, sticky='nsew', padx=(5, 5), pady=(5, 5))
			case 'Распределение зарплаты сотрудников':
				self.grid_columnconfigure((0, 1, 2), weight=1)
				self.button1 = DataButton(self, text='Изменить зарплату сотруднику', command=lambda: self.change_salary_action('Сотруднику'))
				self.button1.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=(5, 5))
				self.button2 = DataButton(self, text='Изменить зарплату отделу/проекту', command=lambda: self.change_salary_action('Отделу/Проекту'))
				self.button2.grid(row=0, column=1, sticky='nsew', padx=(5, 5), pady=(5, 5))
				self.button3 = DataButton(self, text='Изменить зарплату с условием', command=lambda: self.change_salary_action('С условием'))
				self.button3.grid(row=0, column=2, sticky='nsew', padx=(5, 5), pady=(5, 5))

		self.add_frame = None
		self.change_frame = None
		self.salary_frame = None
		self.trip_frame = None
		self.set_head_frame = None

	def set_head(self):
		if self.set_head_frame is None or not self.set_head_frame.winfo_exists():
			selection = self.master.treeview.selection()
			if not selection:
				exception('Вы не выбрали ничего')
				return

			data = self.master.treeview.item(selection)['values'][0]

			self.set_head_frame = HeadFrame(self.master, data)
			self.set_head_frame.after(100, self.set_head_frame.lift)
		else:
			self.set_head_frame.focus()


	def trip_action(self):
		if self.trip_frame is None or not self.trip_frame.winfo_exists():
			selection = self.master.treeview.selection()
			if not selection:
				exception('Вы не выбрали ничего')
				return

			data = self.master.treeview.item(selection)['values'][0]

			self.trip_frame = BusinessTripFrame(self.master, data)
			self.trip_frame.after(100, self.trip_frame.lift)
		else:
			self.trip_frame.focus()

	def change_salary_action(self, salarytype):
		if self.salary_frame is None or not self.salary_frame.winfo_exists():
			data = None
			if salarytype == 'Сотруднику':
				selection = self.master.treeview.selection()
				if not selection:
					exception('Вы не выбрали ничего')
					return

				data = self.master.treeview.item(selection)['values'][0]

			self.salary_frame = ChangeSalary(self.master, salarytype, data)
			self.salary_frame.after(100, self.salary_frame.lift)
		else:
			self.salary_frame.focus()

	def add_action(self):
		if self.add_frame is None or not self.add_frame.winfo_exists():
			self.add_frame = AddFrame(self.master, self.datatype)
			self.add_frame.after(100, self.add_frame.lift)
		else:
			self.add_frame.focus()

	def change_action(self):	
		if self.change_frame is None or not self.change_frame.winfo_exists():
			selection = self.master.treeview.selection()
			if not selection:
				exception('Вы не выбрали ничего')
				return

			data = self.master.treeview.item(selection)['values'][0]

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