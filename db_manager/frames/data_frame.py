import customtkinter as ctk

import tkinter as tk
from tkinter import ttk

from dataclasses import asdict

from db_manager.frames.button_frame import DataButtonFrames
import db_manager.modules.db_classes as db_get
from db_manager.modules.database import fetch_one, fetch_all


class MoreInfoFrame(ctk.CTkToplevel):
	def __init__(self, datatype, data, **kwargs):
		super().__init__(**kwargs)
		self.datatype = datatype
		self.data = data
		
		self.geometry('600x400')
		self.grid_columnconfigure(0, weight=1)
		
		#print(self.datatype, self.data)
		match self.datatype:
			case 'Список персонала' | 'Распределение зарплаты сотрудников':
				self.title(f'Подробная информация : {self.datatype} ({self.data.get("full_name")})')
				departments = db_get.get_departments()
				projects = db_get.get_projects()
				business_trips = db_get.get_business_trips()

				keys = {
					'_id': f'ID : {self.data.get("id")}',
					'full_name': f'Полное имя : {self.data.get("full_name")}',
					'job_title': f'Должность : {self.data.get("job_title")}',
					'sex': f'Пол : {self.data.get("sex")}',
					'age': f'Возраст (в годах) : {self.data.get("age")}',
					'work_experience': f'Стаж работы (в годах) : {self.data.get("work_experience")}',
					'department_id': f'Название отдела : {departments.get(self.data.get("department_id"), db_get.zero_department).name}',
					'project_id': f'Название проекта : {projects.get(self.data.get("project_id"), db_get.zero_project).name}',
					'business_trip_id': f'Город командировки : {business_trips.get(self.data.get("business_trip_id"), db_get.zero_trip).city}'
				}

				if self.datatype == 'Распределение зарплаты сотрудников':
					keys = keys | {'total_amount': f'Заработная плата : {(self.data.get("total_amount")):.1f} руб.'}

				for index, value in enumerate(keys.values()):
					info = ctk.CTkLabel(self, text=value)
					info.grid(row=index, column=0, pady=(5, 5), sticky='ew')

			case 'Отделы':
				self.title(f'Подробная информация : {self.datatype} ({self.data.get("name")})')

				self.grid_rowconfigure(0, weight=1)
				self.tabview = ctk.CTkTabview(self)
				self.workers_tab = self.tabview.add('Сотрудники')
				self.projects_tab = self.tabview.add('Проекты')
				self.tabview.grid(row=0, column=0, sticky='nsew')

				self.workers_tab.grid_columnconfigure(0, weight=1)
				self.workers_tab.grid_rowconfigure(0, weight=1)
				self.projects_tab.grid_columnconfigure(0, weight=1)
				self.projects_tab.grid_rowconfigure(0, weight=1)

				for i, tab in enumerate((self.workers_tab, self.projects_tab)):
					if i == 0:
						columns = ('ID', 'Full Name', 'Project Name')
					elif i == 1:
						columns = ('ID', 'Project Name', 'Count of workers')

					treescroll = ttk.Scrollbar(tab)
					treescroll.grid(row=0, column=1, sticky='ns')

					treeview = ttk.Treeview(
						tab, 
						yscrollcommand=treescroll.set, 
						show='headings', 
						columns=columns, 
						height=13,
						selectmode='none'
					)
					treeview.grid(row=0, column=0, sticky='nsew')

					treescroll.config(command=treeview.yview)

					for index, col_name in enumerate(columns):
						treeview.heading(col_name, text=col_name, anchor='center')
						treeview.column(col_name, width=150, anchor='center')

					treeview.column(0, width=10)

					workers_raw = db_get.get_workers()
					workers = list(filter(lambda item: item.department_id == self.data.get('id'), workers_raw.values()))
					projects_raw = db_get.get_projects()
					if i == 0:
						for worker in workers:
							treeview.insert('', tk.END, 
								values=(worker._id, worker.full_name, projects_raw.get(worker.project_id, db_get.zero_project).name)
							)
					elif i == 1:
						projects_id = sorted(set([worker.project_id for worker in workers if worker.project_id]))
						for project_id in projects_id:
							project = projects_raw.get(project_id, db_get.zero_project)
							workers_in_project = len(list(filter(lambda item: item.project_id == project._id, workers_raw.values())))
							treeview.insert('', tk.END, 
								values=(project._id, project.name, workers_in_project)
							)

			case 'Проекты':
				self.title(f'Подробная информация : {self.datatype} ({self.data.get("name")})')

				self.grid_rowconfigure(2, weight=1)
				workers_raw = db_get.get_workers()
				head_worker_in_project = workers_raw.get(db_get.get_head_projects().get(self.data.get('id'), db_get.zero_head).worker_id, db_get.zero_worker)

				label_project = ctk.CTkLabel(self, text=f'Ответственный за проект : {self.data.get("name")}')
				label_project.grid(row=0, column=0, pady=(15, 5), columnspan=2)

				label_head = ctk.CTkLabel(self, text=f'(ID : {head_worker_in_project._id}) : {head_worker_in_project.full_name}')
				label_head.grid(row=1, column=0, pady=(15, 5), columnspan=2)


				self.tabview = ctk.CTkTabview(self)
				self.workers_tab = self.tabview.add('Сотрудники')
				self.departments_tab = self.tabview.add('Отделы')
				self.tabview.grid(row=2, column=0, sticky='nsew', pady=(15, 5))

				self.workers_tab.grid_columnconfigure(0, weight=1)
				self.workers_tab.grid_rowconfigure(0, weight=1)
				self.departments_tab.grid_columnconfigure(0, weight=1)
				self.departments_tab.grid_rowconfigure(0, weight=1)
				

				for i, tab in enumerate((self.workers_tab, self.departments_tab)):
					if i == 0:
						columns = ('ID', 'Full Name', 'Department Name')
					elif i == 1:
						columns = ('ID', 'Department Name', 'Count of workers')

					treescroll = ttk.Scrollbar(tab)
					treescroll.grid(row=0, column=1, sticky='ns')

					treeview = ttk.Treeview(
						tab, 
						yscrollcommand=treescroll.set, 
						show='headings', 
						columns=columns, 
						height=13,
						selectmode='none'
					)
					treeview.grid(row=0, column=0, sticky='nsew')

					treescroll.config(command=treeview.yview)

					for index, col_name in enumerate(columns):
						treeview.heading(col_name, text=col_name, anchor='center')
						treeview.column(col_name, width=150, anchor='center')

					treeview.column(0, width=10)

					workers = list(filter(lambda item: item.project_id == self.data.get('id'), workers_raw.values()))
					departments_raw = db_get.get_departments()
					if i == 0:
						for worker in workers:
							treeview.insert('', tk.END, 
								values=(worker._id, worker.full_name, departments_raw.get(worker.department_id, db_get.zero_department).name)
							)
					elif i == 1:
						departments_id = sorted(set([worker.department_id for worker in workers if worker.department_id]))
						for department_id in departments_id:
							department = departments_raw.get(department_id, db_get.zero_department)
							workers_in_department = len(list(filter(lambda item: item.department_id == department._id, workers_raw.values())))
							treeview.insert('', tk.END, 
								values=(department._id, department.name, workers_in_department)
							)



class MainDataFrame(ctk.CTkFrame):
	def __init__(self, master, datatype, **kwargs):
		super().__init__(master, **kwargs)
		self.datatype = datatype

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)
		
		match self.datatype:
			case 'Список персонала':
				self.columns = ('ID', 'Full Name', 'Department', 'Project', 'Business Trip City')
			case 'Отделы':
				self.columns = ('ID', 'Department Name', 'Count workers')
			case 'Проекты':
				self.columns = ('ID', 'Project Name', 'Count workers')
			case 'Распределение зарплаты сотрудников':
				self.columns = ('ID', 'Full Name', 'Total Amount')

		self.treescroll = ttk.Scrollbar(self)
		self.treescroll.grid(row=0, column=1, sticky='ns')

		self.treeview = ttk.Treeview(
			self, 
			yscrollcommand=self.treescroll.set, 
			show='headings', 
			columns=self.columns, 
			height=13,
			selectmode='browse'
		)
		self.treeview.grid(row=0, column=0, sticky='nsew')

		self.treescroll.config(command=self.treeview.yview)
		self.treeview.bind('<Double-Button-1>', self.get_full_info)

		self.opened_frames = {}

		self.button_frame = DataButtonFrames(self, self.datatype)
		self.button_frame.grid(row=1, column=0, pady=(5, 5), sticky='ew')

	def get_full_info(self, event):
		selection = self.treeview.selection()
		if not selection:
			return

		opened_frame = self.opened_frames.get(selection) 
		if not(opened_frame is None or not opened_frame.winfo_exists()):
			opened_frame.focus()
			return

		item = self.treeview.item(selection)

		match self.datatype:
			case 'Список персонала':
				sql = '''
					SELECT * 
					FROM Worker 
					WHERE id = %s
				'''
				result = fetch_one(sql, (item['values'][0],))
			case 'Отделы':
				sql = '''
					SELECT * 
					FROM Department 
					WHERE id = %s
				'''
				result = fetch_one(sql, (item['values'][0],))
			case 'Проекты':
				sql = '''
					SELECT * 
					FROM Project 
					WHERE id = %s
				'''
				result = fetch_one(sql, (item['values'][0],))
			case 'Распределение зарплаты сотрудников':
				sql = '''
					SELECT w.*, s.total_amount
					FROM Salary as s
						join Worker w on s.worker_id = w.id
					WHERE s.worker_id = %s
				'''
				result = fetch_one(sql, (item['values'][0],))

		if not result: 
			self.update_tables()
			return

		new_frame = MoreInfoFrame(self, self.datatype, result)
		self.opened_frames[selection] = new_frame

	def update_tables(self):
		self.treeview.delete(*self.treeview.get_children())

		for index, col_name in enumerate(self.columns):
			self.treeview.heading(col_name, text=col_name, anchor='center')
			self.treeview.column(col_name, width=150, anchor='center')

		self.treeview.column(0, width=10)

		match self.datatype:
			case 'Список персонала':
				workers = db_get.get_workers()
				departments = db_get.get_departments()
				projects = db_get.get_projects()
				business_trips = db_get.get_business_trips()
				
				for worker in sorted(workers.values(), key=lambda item: item._id):
					department = departments.get(worker.department_id, db_get.zero_department)
					project = projects.get(worker.project_id, db_get.zero_project)
					business_trip = business_trips.get(worker.business_trip_id, db_get.zero_trip)
					self.treeview.insert('', tk.END, 
						values=(worker._id, worker.full_name, department.name, project.name, business_trip.city)
					)
			case 'Отделы':
				workers = db_get.get_workers()
				departments = db_get.get_departments()

				for department in sorted(departments.values(), key=lambda item: item._id):
					count_worker = len(list(filter(lambda item: item.department_id == department._id, workers.values())))
					self.treeview.insert('', tk.END, 
						values=(department._id, department.name, count_worker)
					)
			case 'Проекты':
				workers = db_get.get_workers()
				projects = db_get.get_projects()

				for project in sorted(projects.values(), key=lambda item: item._id):
					count_worker = len(list(filter(lambda item: item.project_id == project._id, workers.values())))
					self.treeview.insert('', tk.END, 
						values=(project._id, project.name, count_worker)
					)
			case 'Распределение зарплаты сотрудников':
				workers = db_get.get_workers()
				salaries = db_get.get_salaries()

				for salary in salaries.values():
					worker = workers.get(salary.worker_id, db_get.zero_worker)
					self.treeview.insert('', tk.END, 
						values=(worker._id, worker.full_name, f'{(salary.total_amount):.1f}')
					)