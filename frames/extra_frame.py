import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

from math import isnan

import modules.db_classes as db_get
from modules.database import execute, fetch_one
from frames.exception_frame import exception


class HeadFrame(ctk.CTkToplevel):
	def __init__(self, master, data, **kwargs):
		super().__init__(master, **kwargs)
		self.master = master
		self.data = data

		self.title(f'Изменение ответственного за проект')
		self.geometry('600x450')
		self.resizable(False, False)
		self.grid_columnconfigure(0, weight=1)

		workers = db_get.get_workers()
		project = db_get.get_projects().get(self.data, db_get.zero_project)
		
		self.head_of_project = workers.get(db_get.get_head_projects().get(self.data, db_get.zero_head).worker_id, db_get.zero_worker)
		
		label_project = ctk.CTkLabel(self, text=f'Ответственный за проект : {project.name}')
		label_project.grid(row=0, column=0, pady=(15, 5), columnspan=2)

		label_head = ctk.CTkLabel(self, text=f'(ID : {self.head_of_project._id}) : {self.head_of_project.full_name}')
		label_head.grid(row=1, column=0, pady=(15, 5), columnspan=2)

		self.columns = ('ID', 'Full Name')

		self.treescroll = ttk.Scrollbar(self)
		self.treescroll.grid(row=2, column=1, sticky='ns')

		self.treeview = ttk.Treeview(
			self, 
			yscrollcommand=self.treescroll.set, 
			show='headings', 
			columns=self.columns, 
			height=13,
			selectmode='browse'
		)

		self.treeview.grid(row=2, column=0, sticky='nsew', padx=(15, 0))

		self.treescroll.config(command=self.treeview.yview)

		for index, col_name in enumerate(self.columns):
			self.treeview.heading(col_name, text=col_name, anchor='center')
			self.treeview.column(col_name, width=100, anchor='center')

		self.treeview.column(0, width=10)
		self.treeview.column(1, width=200)

		for worker in dict(filter(lambda item: item[1].project_id == self.data, workers.items())).values():
			self.treeview.insert('', tk.END, 
				values=(worker._id, worker.full_name)
			)

		button = ctk.CTkButton(self, text='Назначить ответственного', command=self.action)
		button.grid(row=3, column=0, pady=(25, 5), columnspan=2)

	def action(self):
		selection = self.treeview.selection()
		if not selection:
			exception('Ничего не выбрано')
			return

		item = self.treeview.item(selection)['values'][0]
		if self.head_of_project._id == 0:
			sql = '''
				INSERT INTO Project_Worker
				(worker_id, project_id)
				VALUES
				(%s, %s)
			'''
		else:
			sql = '''
				UPDATE Project_Worker
				SET worker_id = %s
				WHERE project_id = %s
			'''

		execute(sql, (item, self.data))

		self.master.update_tables()
		self.destroy()


class ChangeFrame(ctk.CTkToplevel):
	def __init__(self, master, datatype, data, **kwargs):
		super().__init__(master, **kwargs)
		self.master = master
		self.datatype = datatype
		self.data = data

		self.title(f'Изменение элемента в таблице : {self.datatype}')
		self.resizable(False, False)

		match self.datatype:
			case 'Список персонала':
				self.geometry('600x500')
				self.grid_columnconfigure((0, 1), weight=1)
				keys = {
					'full_name' : 'Full Name',
					'job_title' : 'Job Title',
					'age' : 'Age (int)',
					'work_exp' : 'Work Experience (int)',
				}
				worker = db_get.get_workers().get(self.data, db_get.zero_worker)
				#salary = db_get.get_salaries().get(worker._id)
				values = {
					'full_name' : worker.full_name,
					'job_title' : worker.job_title,
					'age' : worker.age,
					'work_exp' : worker.work_exp,
				}

				self.entries = {}
				for index, (key, value) in enumerate(keys.items()):
					label = ctk.CTkLabel(self, text=value)
					label.grid(row=index, column=0, pady=(15, 5))
					entry = ctk.CTkEntry(self, textvariable=ctk.StringVar(value=values.get(key)), width=300)
					entry.grid(row=index, column=1, pady=(15, 5))
					self.entries[key] = entry

				sex = ['М', 'Ж']
				self.sex = ctk.CTkOptionMenu(self, values=sex, anchor='center', variable=ctk.StringVar(value=worker.sex))
				self.sex.grid(row=len(keys), column=0, pady=(15, 5), columnspan=2)
				
				departments = db_get.get_departments()
				self.departments = {'(ID : 0) : Без отдела' : None} \
				| {f'(ID : {departments._id}) : {departments.name}' : key for key, departments in departments.items()}
				department = f'(ID : {worker.department_id}) : {departments.get(worker.department_id, db_get.zero_department).name}' if worker.department_id else '(ID : 0) : Без отдела'
				
				self.choose_department = ctk.CTkOptionMenu(self, values=list(self.departments.keys()), anchor='center', variable=ctk.StringVar(value=department))
				self.choose_department.grid(row=len(keys)+1, column=0, pady=(15, 5), columnspan=2)

				projects = db_get.get_projects()
				self.projects = {'(ID : 0) : Без проекта' : None} \
				| {f'(ID : {project._id}) : {project.name}' : key for key, project in projects.items()}
				project = f'(ID : {worker.project_id}) : {projects.get(worker.project_id, db_get.zero_project).name}' if worker.project_id else '(ID : 0) : Без проекта'

				self.choose_project = ctk.CTkOptionMenu(self, values=list(self.projects.keys()), anchor='center', variable=ctk.StringVar(value=project))
				self.choose_project.grid(row=len(keys)+2, column=0, pady=(15, 5), columnspan=2)

				self.accept_button = ctk.CTkButton(self, text='Подтвердить запись изменений сотрудника', anchor='center', command=self.personal_action)
				self.accept_button.grid(row=len(keys)+3, column=0, pady=(15, 5), columnspan=2)

			case 'Отделы':
				self.geometry('1300x450')
				self.grid_columnconfigure((0, 2), weight=1)

				workers = db_get.get_workers()
				self.workers = dict(sorted(dict(filter(lambda item: item[1].department_id is None, workers.items())).items(), key=lambda item: item[0]))
				self.new_workers = dict(sorted(dict(filter(lambda item: item[1].department_id == self.data, workers.items())).items(), key=lambda item: item[0]))
				
				self.label = ctk.CTkLabel(self, text='Название департамента')
				self.label.grid(row=0, column=0, pady=(15, 5))
				self.name = ctk.CTkEntry(self, textvariable=ctk.StringVar(value=db_get.get_departments().get(self.data, db_get.zero_department).name), width=300)
				self.name.grid(row=0, column=2, columnspan=2, pady=(15, 5))

				self.create_tables()
				self.update_tables()

				self.accept_button = ctk.CTkButton(self, text='Подтвердить запись нового отдела', anchor='center', command=self.departmnet_action)
				self.accept_button.grid(row=3, column=0, pady=(15, 5), columnspan=4)


			case 'Проекты':
				self.geometry('1300x450')
				self.grid_columnconfigure((0, 2), weight=1)

				self.workers = dict(sorted(dict(filter(lambda item: item[1].project_id is None, db_get.get_workers().items())).items(), key=lambda item: item[0]))
				self.new_workers = dict(sorted(dict(filter(lambda item: item[1].project_id == self.data, db_get.get_workers().items())).items(), key=lambda item: item[0]))

				self.label = ctk.CTkLabel(self, text='Название проекта')
				self.label.grid(row=0, column=0, pady=(15, 5))
				self.name = ctk.CTkEntry(self, textvariable=ctk.StringVar(value=db_get.get_projects().get(self.data, db_get.zero_project).name), width=300)
				self.name.grid(row=0, column=2, columnspan=2, pady=(15, 5))

				self.create_tables()
				self.update_tables()

				self.accept_button = ctk.CTkButton(self, text='Подтвердить запись нового проекта', anchor='center', command=self.project_action)
				self.accept_button.grid(row=3, column=0, pady=(15, 5), columnspan=5)
	
	def create_tables(self):
		self.columns = ('ID', 'Full Name', 'Job Title', 'Age', 'Work Experience')

		self.label = ctk.CTkLabel(self, text='Свободные сотрудники')
		self.label.grid(row=1, column=0, columnspan=2)

		self.treescroll = ttk.Scrollbar(self)
		self.treescroll.grid(row=2, column=1, sticky='ns')

		self.treeview = ttk.Treeview(
			self, 
			yscrollcommand=self.treescroll.set, 
			show='headings', 
			columns=self.columns, 
			height=13,
			selectmode='browse'
		)
		self.treeview.grid(row=2, column=0, sticky='nsew', padx=(15, 0))

		self.treescroll.config(command=self.treeview.yview)

		for index, col_name in enumerate(self.columns):
			self.treeview.heading(col_name, text=col_name, anchor='center')
			self.treeview.column(col_name, width=100, anchor='center')

		self.treeview.column(0, width=10)
		self.treeview.column(1, width=200)

		#--------------------

		self.label_add = ctk.CTkLabel(self, text='Выбранные сотрудники')
		self.label_add.grid(row=1, column=2, columnspan=2)

		self.treescroll_add = ttk.Scrollbar(self)
		self.treescroll_add.grid(row=2, column=3, sticky='ns', padx=(0, 15))

		self.treeview_add = ttk.Treeview(
			self, 
			yscrollcommand=self.treescroll_add.set, 
			show='headings', 
			columns=self.columns, 
			height=13,
			selectmode='browse'
		)
		self.treeview_add.grid(row=2, column=2, sticky='nsew', padx=(15, 0))

		self.treescroll_add.config(command=self.treeview_add.yview)

		for index, col_name in enumerate(self.columns):
			self.treeview_add.heading(col_name, text=col_name, anchor='center')
			self.treeview_add.column(col_name, width=100, anchor='center')

		self.treeview_add.column(0, width=10)
		self.treeview_add.column(1, width=200)

		self.treeview.bind('<Double-Button-1>', self.add_into)
		self.treeview_add.bind('<Double-Button-1>', self.out_from)

	def update_tables(self):
		self.treeview.delete(*self.treeview.get_children())
		for worker in self.workers.values():
			self.treeview.insert('', tk.END, 
				values=(worker._id, worker.full_name, worker.job_title, worker.age, worker.work_exp)
			)

		self.treeview_add.delete(*self.treeview_add.get_children())
		for worker in self.new_workers.values():
			self.treeview_add.insert('', tk.END, 
				values=(worker._id, worker.full_name, worker.job_title, worker.age, worker.work_exp)
			)

	def add_into(self, event):
		selection = self.treeview.selection()
		if not selection:
			return 

		_id = self.treeview.item(selection)['values'][0]
		self.new_workers = dict(sorted((self.new_workers | {_id : self.workers.get(_id)}).items(), key=lambda item: item[0]))
		del self.workers[_id]

		self.update_tables()

	def out_from(self, event):
		selection = self.treeview_add.selection()
		if not selection:
			return 

		_id = self.treeview_add.item(selection)['values'][0]
		self.workers = dict(sorted((self.workers | {_id : self.new_workers.get(_id)}).items(), key=lambda item: item[0]))
		del self.new_workers[_id]

		self.update_tables()

	def personal_action(self):
		sex = self.sex.get()
		department_id = self.departments.get(self.choose_department.get())
		projects_id = self.projects.get(self.choose_project.get())

		#salary = self.entries['salary'].get()
		entry_values = {key: value.get() for key, value in self.entries.items()}
		if not all(list(entry_values.values())):
			exception('Не все поля заполнены')
			return
	
		try:
			age = int(entry_values.get('age'))
		except ValueError:
			exception('Недопустимое значение в поле возраста')
			return

		if abs(age) == float('inf') or isnan(age):
			exception('Возраст не может являтся INF/NaN')
			return

		if age < 0:
			exception('Возраст не может быть отрицательным')
			return

		try:
			work_exp = int(entry_values.get('work_exp'))
		except ValueError:
			exception('Недопустимое значение в поле стажа')
			return

		if abs(work_exp) == float('inf') or isnan(work_exp):
			exception('Стаж не может являтся INF/NaN')
			return

		if work_exp < 0:
			exception('Стаж не может быть отрицательным')
			return

		sql = '''
			UPDATE Worker 
			SET full_name = %s,
			job_title = %s,
			age = %s,
			work_experience = %s,
			sex = %s,
			department_id = %s,
			project_id = %s
			WHERE id = %s
		'''

		execute(sql, tuple(entry_values+[sex, department_id, projects_id, self.data]))

		self.master.update_tables()
		self.destroy()

	def departmnet_action(self):
		name = self.name.get()
		if not name:
			exception('Не введено имя')
			return

		sql = '''
			SELECT id
			FROM Department
			WHERE name = %s
		'''
		check_name = fetch_one(sql, (name,))
		if check_name and check_name.get('id') != self.data:
			exception('Такое название уже существует')
			return

		sql = '''
			UPDATE Department
			SET name = %s
			WHERE id = %s
		'''
		execute(sql, (name, self.data))

		sql = '''
			UPDATE Worker
			SET department_id = %s
			WHERE id = %s
		'''

		for worker in self.new_workers.values():
			execute(sql, (self.data, worker._id))

		sql = '''
			UPDATE Worker
			SET department_id = %s
			WHERE id = %s
		'''

		for worker in self.workers.values():
			execute(sql, (None, worker._id))

		self.master.update_tables()
		self.destroy()

	def project_action(self):
		name = self.name.get()
		if not name:
			exception('Не введено имя')
			return

		sql = '''
			SELECT id
			FROM Project
			WHERE name = %s
		'''
		check_name = fetch_one(sql, (name,))
		if check_name and check_name.get('id') != self.data:
			exception('Такое название уже существует')
			return

		sql = '''
			UPDATE Project
			SET name = %s
			WHERE id = %s
		'''
		execute(sql, (name, self.data))

		sql = '''
			UPDATE Worker
			SET project_id = %s
			WHERE id = %s
		'''

		for worker in self.new_workers.values():
			execute(sql, (self.data, worker._id))

		sql = '''
			UPDATE Worker
			SET project_id = %s
			WHERE id = %s
		'''

		for worker in self.workers.values():
			execute(sql, (None, worker._id))

		self.master.update_tables()
		self.destroy()
			


class AddFrame(ctk.CTkToplevel):
	def __init__(self, master, datatype, **kwargs):
		super().__init__(master, **kwargs)
		self.master = master
		self.datatype = datatype

		self.title(f'Добавление нового элемента в таблицу : {self.datatype}')
		self.resizable(False, False)

		# self.grid_rowconfigure(0, weight=1)
		

		match self.datatype:
			case 'Список персонала':
				self.geometry('600x500')
				self.grid_columnconfigure(0, weight=1)
				keys = {
					'full_name' : 'Full Name',
					'job_title' : 'Job Title',
					'age' : 'Age (int)',
					'work_exp' : 'Work Experience (int)',
					'salary' : 'Salary amount (float)'
				}

				self.entries = {}
				for index, (key, value) in enumerate(keys.items()):
					entry = ctk.CTkEntry(self, placeholder_text=value, width=200)
					entry.grid(row=index, column=0, pady=(15, 5))
					self.entries[key] = entry

				sex = ['М', 'Ж']
				self.sex = ctk.CTkOptionMenu(self, values=sex, anchor='center', variable=ctk.StringVar(value='М'))
				self.sex.grid(row=len(keys), column=0, pady=(15, 5))
				
				self.departments = {'(ID : 0) : Без отдела' : None} \
				| {f'(ID : {departments._id}) : {departments.name}' : key for key, departments in db_get.get_departments().items()}

				self.choose_department = ctk.CTkOptionMenu(self, values=list(self.departments.keys()), anchor='center', variable=ctk.StringVar(value='(ID : 0) : Без отдела'))
				self.choose_department.grid(row=len(keys)+1, column=0, pady=(15, 5))

				self.projects = {'(ID : 0) : Без проекта' : None} \
				| {f'(ID : {project._id}) : {project.name}' : key for key, project in db_get.get_projects().items()}

				self.choose_project = ctk.CTkOptionMenu(self, values=list(self.projects.keys()), anchor='center', variable=ctk.StringVar(value='(ID : 0) : Без проекта'))
				self.choose_project.grid(row=len(keys)+2, column=0, pady=(15, 5))

				self.accept_button = ctk.CTkButton(self, text='Подтвердить запись нового сотрудника', anchor='center', command=self.personal_action)
				self.accept_button.grid(row=len(keys)+3, column=0, pady=(15, 5))

			case 'Отделы':
				self.geometry('1300x450')
				self.grid_columnconfigure((0, 2), weight=1)

				self.workers = dict(sorted(dict(filter(lambda item: item[1].department_id is None, db_get.get_workers().items())).items(), key=lambda item: item[0]))
				self.new_workers = {}
				
				self.name = ctk.CTkEntry(self, placeholder_text='Название департамента', width=300)
				self.name.grid(row=0, column=0, columnspan=4, pady=(15, 5))

				self.create_tables()
				self.update_tables()

				self.accept_button = ctk.CTkButton(self, text='Подтвердить запись нового отдела', anchor='center', command=self.departmnet_action)
				self.accept_button.grid(row=3, column=0, pady=(15, 5), columnspan=4)


			case 'Проекты':
				self.geometry('1300x450')
				self.grid_columnconfigure((0, 2), weight=1)

				self.workers = dict(sorted(dict(filter(lambda item: item[1].project_id is None, db_get.get_workers().items())).items(), key=lambda item: item[0]))
				self.new_workers = {}

				self.name = ctk.CTkEntry(self, placeholder_text='Название проекта', width=300)
				self.name.grid(row=0, column=0, columnspan=4, pady=(15, 5))

				self.create_tables()
				self.update_tables()

				self.accept_button = ctk.CTkButton(self, text='Подтвердить запись нового проекта', anchor='center', command=self.project_action)
				self.accept_button.grid(row=3, column=0, pady=(15, 5), columnspan=5)
				

	def create_tables(self):
		self.columns = ('ID', 'Full Name', 'Job Title', 'Age', 'Work Experience')

		self.label = ctk.CTkLabel(self, text='Свободные сотрудники')
		self.label.grid(row=1, column=0, columnspan=2)

		self.treescroll = ttk.Scrollbar(self)
		self.treescroll.grid(row=2, column=1, sticky='ns')

		self.treeview = ttk.Treeview(
			self, 
			yscrollcommand=self.treescroll.set, 
			show='headings', 
			columns=self.columns, 
			height=13,
			selectmode='browse'
		)
		self.treeview.grid(row=2, column=0, sticky='nsew', padx=(15, 0))

		self.treescroll.config(command=self.treeview.yview)

		for index, col_name in enumerate(self.columns):
			self.treeview.heading(col_name, text=col_name, anchor='center')
			self.treeview.column(col_name, width=100, anchor='center')

		self.treeview.column(0, width=10)
		self.treeview.column(1, width=200)

		#--------------------

		self.label_add = ctk.CTkLabel(self, text='Выбранные сотрудники')
		self.label_add.grid(row=1, column=2, columnspan=2)

		self.treescroll_add = ttk.Scrollbar(self)
		self.treescroll_add.grid(row=2, column=3, sticky='ns', padx=(0, 15))

		self.treeview_add = ttk.Treeview(
			self, 
			yscrollcommand=self.treescroll_add.set, 
			show='headings', 
			columns=self.columns, 
			height=13,
			selectmode='browse'
		)
		self.treeview_add.grid(row=2, column=2, sticky='nsew', padx=(15, 0))

		self.treescroll_add.config(command=self.treeview_add.yview)

		for index, col_name in enumerate(self.columns):
			self.treeview_add.heading(col_name, text=col_name, anchor='center')
			self.treeview_add.column(col_name, width=100, anchor='center')

		self.treeview_add.column(0, width=10)
		self.treeview_add.column(1, width=200)

		self.treeview.bind('<Double-Button-1>', self.add_into)
		self.treeview_add.bind('<Double-Button-1>', self.out_from)

	def update_tables(self):
		self.treeview.delete(*self.treeview.get_children())
		for worker in self.workers.values():
			self.treeview.insert('', tk.END, 
				values=(worker._id, worker.full_name, worker.job_title, worker.age, worker.work_exp)
			)

		self.treeview_add.delete(*self.treeview_add.get_children())
		for worker in self.new_workers.values():
			self.treeview_add.insert('', tk.END, 
				values=(worker._id, worker.full_name, worker.job_title, worker.age, worker.work_exp)
			)

	def add_into(self, event):
		selection = self.treeview.selection()
		if not selection:
			return 

		_id = self.treeview.item(selection)['values'][0]
		self.new_workers = dict(sorted((self.new_workers | {_id : self.workers.get(_id)}).items(), key=lambda item: item[0]))
		del self.workers[_id]

		self.update_tables()

	def out_from(self, event):
		selection = self.treeview_add.selection()
		if not selection:
			return 

		_id = self.treeview_add.item(selection)['values'][0]
		self.workers = dict(sorted((self.workers | {_id : self.new_workers.get(_id)}).items(), key=lambda item: item[0]))
		del self.new_workers[_id]

		self.update_tables()

	def personal_action(self):
		sex = self.sex.get()
		department_id = self.departments.get(self.choose_department.get())
		projects_id = self.projects.get(self.choose_project.get())

		salary = self.entries['salary'].get()
		entry_values = {key: value.get() for key, value in self.entries.items() if key != 'salary'}
		if not all(list(entry_values.values())) or not salary:
			exception('Не все поля заполнены')
			return
	
		try:
			salary = float(salary)
		except ValueError:
			exception('Недопустимое значение в поле зарплаты')
			return

		if abs(salary) == float('inf') or isnan(salary):
			exception('Зарплаты не может являтся INF/NaN')
			return

		if salary < 0:
			exception('Зарплата не может быть отрицательной')
			return

		try:
			age = int(entry_values.get('age'))
		except ValueError:
			exception('Недопустимое значение в поле возраста')
			return

		if abs(age) == float('inf') or isnan(age):
			exception('Возраст не может являтся INF/NaN')
			return

		if age < 0:
			exception('Возраст не может быть отрицательным')
			return

		try:
			work_exp = int(entry_values.get('work_exp'))
		except ValueError:
			exception('Недопустимое значение в поле стажа')
			return

		if abs(work_exp) == float('inf') or isnan(work_exp):
			exception('Стаж не может являтся INF/NaN')
			return

		if work_exp < 0:
			exception('Стаж не может быть отрицательным')
			return


		sql = '''
			INSERT INTO Worker 
			(full_name, job_title, age, work_experience, sex, department_id, project_id)
			VALUES
			(%s, %s, %s, %s, %s, %s, %s)
		'''
		execute(sql, tuple(list(entry_values.values())+[sex, department_id, projects_id]))

		sql = '''
			SELECT max(id) as id
			FROM Worker 
		'''
		_id = fetch_one(sql).get('id')

		sql = '''
			INSERT INTO Salary
			(worker_id, total_amount, business_trip_part, work_experience_part) 
			VALUES 
			(%s, %s, 0, 0);
		'''
		execute(sql, (_id, salary))

		self.master.update_tables()
		self.destroy()

	def departmnet_action(self):
		name = self.name.get()
		if not name:
			exception('Не введено имя')
			return

		sql = '''
			SELECT id
			FROM Department
			WHERE name = %s
		'''
		check_name = fetch_one(sql, (name,))
		if check_name:
			exception('Такое название уже существует')
			return

		sql = '''
			INSERT INTO Department
			(name)
			VALUES
			(%s)
		'''
		execute(sql, (name,))

		sql = '''
			SELECT id
			FROM Department
			WHERE name = %s
		'''

		_id = fetch_one(sql, (name,))['id']
		sql = '''
			UPDATE Worker
			SET department_id = %s
			WHERE id = %s
		'''

		for worker in self.new_workers.values():
			execute(sql, (_id, worker._id))

		self.master.update_tables()
		self.destroy()

	def project_action(self):
		name = self.name.get()
		if not name:
			exception('Не введено имя')
			return

		sql = '''
			SELECT id
			FROM Project
			WHERE name = %s
		'''
		check_name = fetch_one(sql, (name,))
		if check_name:
			exception('Такое название уже существует')
			return

		sql = '''
			INSERT INTO Project
			(name)
			VALUES
			(%s)
		'''
		execute(sql, (name,))

		sql = '''
			SELECT id
			FROM Project
			WHERE name = %s
		'''

		_id = fetch_one(sql, (name,))['id']
		sql = '''
			UPDATE Worker
			SET project_id = %s
			WHERE id = %s
		'''

		for worker in self.new_workers.values():
			execute(sql, (_id, worker._id))

		self.master.update_tables()
		self.destroy()
