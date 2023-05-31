import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

import modules.db_classes as db_get
from modules.database import execute, fetch_one
from frames.exception_frame import exception

from math import isnan


class ChangeSalary(ctk.CTkToplevel):
	def __init__(self, master, salarytype, data, **kwargs):
		super().__init__(master, **kwargs)
		self.master = master
		self.salarytype = salarytype
		self.data = data

		self.title(f'Изменение зарплаты : {self.salarytype}')
		self.resizable(False, False)

		self.geometry('600x500')
		self.grid_columnconfigure(0, weight=1)

		match self.salarytype:
			case 'Сотруднику':
				self.geometry('600x250')
				self.salary = db_get.get_salaries().get(self.data)
				self.worker = db_get.get_workers().get(self.data, db_get.zero_worker)
				
				name = ctk.CTkLabel(self, text=f'(ID : {self.worker._id}) : {self.worker.full_name}')
				name.grid(row=0, column=0, pady=(15, 5))

				add_label = ctk.CTkLabel(self, text='Заработная плата (Добавление/Отбавление)')
				add_label.grid(row=1, column=0, pady=(15, 5))

				self.add_entry = ctk.CTkEntry(self, placeholder_text=f'{(self.salary.total_amount):.1f}')
				self.add_entry.grid(row=2, column=0, pady=(15, 5))

				add_button = ctk.CTkButton(self, text='Добавить/Отнять значение', command=self.add_amount)
				add_button.grid(row=3, column=0, pady=(15, 5))
			case 'Отделу/Проекту':
				self.geometry('800x450')
				self.grid_columnconfigure((0,2), weight=1)

				department_label = ctk.CTkLabel(self, text='Отделы')
				department_label.grid(row=0, column=0, pady=(15, 5), columnspan=2)

				project_label = ctk.CTkLabel(self, text='Проекты')
				project_label.grid(row=0, column=2, pady=(15, 5), columnspan=2)

				self.columns_department = ('ID', 'Department Name')
				self.treescroll_department = ttk.Scrollbar(self)
				self.treescroll_department.grid(row=1, column=1, sticky='ns')

				self.treeview_department = ttk.Treeview(
					self, 
					yscrollcommand=self.treescroll_department.set, 
					show='headings', 
					columns=self.columns_department, 
					height=13,
					selectmode='browse'
				)
				self.treeview_department.grid(row=1, column=0, sticky='nsew', padx=(15, 0))

				self.treescroll_department.config(command=self.treeview_department.yview)

				for index, col_name in enumerate(self.columns_department):
					self.treeview_department.heading(col_name, text=col_name, anchor='center')
					self.treeview_department.column(col_name, width=100, anchor='center')

				self.treeview_department.column(0, width=10)
				self.treeview_department.column(1, width=200)

				#--------------------------------------

				self.columns_project = ('ID', 'Project Name')
				self.treescroll_project = ttk.Scrollbar(self)
				self.treescroll_project.grid(row=1, column=3, sticky='ns')

				self.treeview_project = ttk.Treeview(
					self, 
					yscrollcommand=self.treescroll_project.set, 
					show='headings', 
					columns=self.columns_project, 
					height=13,
					selectmode='browse'
				)
				self.treeview_project.grid(row=1, column=2, sticky='nsew', padx=(15, 0))

				self.treescroll_project.config(command=self.treeview_project.yview)

				for index, col_name in enumerate(self.columns_project):
					self.treeview_project.heading(col_name, text=col_name, anchor='center')
					self.treeview_project.column(col_name, width=100, anchor='center')

				self.treeview_project.column(0, width=10)
				self.treeview_project.column(1, width=200)

				#self.treeview.delete(*self.treeview.get_children())
				for department in dict(sorted(db_get.get_departments().items(), key=lambda item: item[0])).values():
					self.treeview_department.insert('', tk.END, 
						values=(department._id, department.name)
					)

				#self.treeview_add.delete(*self.treeview_add.get_children())
				for project in dict(sorted(db_get.get_projects().items(), key=lambda item: item[0])).values():
					self.treeview_project.insert('', tk.END, 
						values=(project._id, project.name)
					)

				self.department_entry = ctk.CTkEntry(self, placeholder_text='+1000')
				self.department_entry.grid(row=2, column=0, pady=(15, 5))

				department_button = ctk.CTkButton(self, text='Добавить/Отнять значение', command=lambda:self.add_amount('Отделы'))
				department_button.grid(row=3, column=0, pady=(15, 5))

				self.project_entry = ctk.CTkEntry(self, placeholder_text='+1000')
				self.project_entry.grid(row=2, column=2, pady=(15, 5))

				project_button = ctk.CTkButton(self, text='Добавить/Отнять значение', command=lambda:self.add_amount('Проекты'))
				project_button.grid(row=3, column=2, pady=(15, 5))

			case 'С условием':
				self.geometry('600x250')
				
				self.condition_entry = ctk.CTkEntry(self, placeholder_text=f'Условие : (более кол-ва лет стажа)', width=300)
				self.condition_entry.grid(row=0, column=0, pady=(15, 5))

				add_label = ctk.CTkLabel(self, text='Заработная плата (Добавление)')
				add_label.grid(row=1, column=0, pady=(15, 5))

				self.add_entry = ctk.CTkEntry(self, placeholder_text=f'1000')
				self.add_entry.grid(row=2, column=0, pady=(15, 5))

				add_button = ctk.CTkButton(self, text='Добавить значение', command=self.add_amount)
				add_button.grid(row=3, column=0, pady=(15, 5))


	def add_amount(self, table_type=None):
		match table_type:
			case 'Отделы':
				salary = self.department_entry.get()
				data = self.treeview_department.selection()
				if not data:
					exception('Ничего не выбрано')
					return

				item = self.treeview_department.item(data)['values'][0]
			case 'Проекты':
				salary = self.project_entry.get()
				data = self.treeview_project.selection()
				if not data:
					exception('Ничего не выбрано')
					return

				item = self.treeview_project.item(data)['values'][0]
			case _:
				salary = self.add_entry.get()
		
		if not salary:
			exception('Недопустимое значение')
			return

		try:
			salary = float(salary)
		except ValueError:
			exception('Недопустимое значение в поле зарплаты')
			return

		if abs(salary) == float('inf') or isnan(salary):
			exception('Зарплата не может являтся INF/NaN')
			return


		match self.salarytype:
			case 'Сотруднику':
				if (self.salary.total_amount + salary) < 0:
					salary = -self.salary.total_amount

				sql = '''
					UPDATE Salary
					SET total_amount = total_amount + %s
					WHERE worker_id = %s
				'''
				execute(sql, (salary, self.data))
			case 'Отделу/Проекту':
				match table_type:
					case 'Отделы':
						sql = '''
							WITH department_salary_temp AS (
							    SELECT s.worker_id, w.department_id
							    FROM Salary s join Worker w on w.id = s.worker_id
							)
							UPDATE Salary
							SET total_amount = (case when (total_amount + %s) > 0 then (total_amount + %s) else 0 end)
							FROM department_salary_temp dst
							WHERE dst.department_id = %s
							AND dst.worker_id = Salary.worker_id; 
						'''
					case 'Проекты':
						sql = '''
							WITH project_salary_temp AS (
							    SELECT s.worker_id, w.project_id
							    FROM Salary s join Worker w on w.id = s.worker_id
							)
							UPDATE Salary
							SET total_amount = (case when (total_amount + %s) > 0 then (total_amount + %s) else 0 end)
							FROM project_salary_temp pst
							WHERE pst.project_id = %s
							AND pst.worker_id = Salary.worker_id; 
						'''

				execute(sql, (salary, salary, item))
			case 'С условием':
				if salary < 0:
					exception('Нельзя понизить зарплату')
					return 

				work_exp = self.condition_entry.get()
				if not work_exp:
					exception('Нельзя оставлять поле пустым')
					return

				try:
					work_exp = int(work_exp)
				except ValueError:
					exception('Недопустимое значние в поле условия')
					return

				sql = '''
					WITH worker_salary_temp AS (
					    SELECT w.id as worker_id, w.work_experience, s.id
					    FROM Salary s join Worker W on W.id = s.worker_id
					)
					UPDATE Salary
					SET work_experience_part = %s,
					    total_amount = s.total_amount + %s
					FROM worker_salary_temp wst
					     join Salary s on wst.worker_id = s.worker_id
					WHERE wst.work_experience > %s and s.id = salary.id;
				'''
				execute(sql, (salary, salary, work_exp))
		
		self.destroy()
		self.master.update_tables()


class BusinessTripFrame(ctk.CTkToplevel):
	def __init__(self, master, data, **kwargs):
		super().__init__(master, **kwargs)
		self.master = master
		self.data = data

		self.title(f'Манипулирование командировками')
		self.resizable(False, False)

		self.grid_columnconfigure(0, weight=1)

		workers = db_get.get_workers()
		business_trips = db_get.get_business_trips()
		self.worker = workers.get(self.data, db_get.zero_worker)
		if self.worker.business_trip_id:
			self.geometry('600x250')
			self.business_trip = business_trips.get(self.worker.business_trip_id, db_get.zero_trip)
			
			self.label = ctk.CTkLabel(self, text=f'(ID : {self.worker._id}) : {self.worker.full_name}, в данный момент в командировке')
			self.label.grid(row=0, column=0, pady=(15, 5))
			self.city_label = ctk.CTkLabel(self, text=f'Город командировки : {self.business_trip.city}')
			self.city_label.grid(row=1, column=0, pady=(15, 5))
			self.payment_label = ctk.CTkLabel(self, text=f'За это он(она) получит : {(self.business_trip.payment):.1f} руб.')
			self.payment_label.grid(row=2, column=0, pady=(15, 5))

			self.button_eject = ctk.CTkButton(self, text='Вернуть сотрудника из командировки', command=self.return_from)
			self.button_eject.grid(row=3, column=0, pady=(25, 5))
		else:
			self.geometry('600x250')
			self.business_trip = business_trips.get(self.worker.business_trip_id, db_get.zero_trip)
			
			self.label = ctk.CTkLabel(self, text=f'(ID : {self.worker._id}) : {self.worker.full_name}, в данный момент не в командировке')
			self.label.grid(row=0, column=0, pady=(15, 5))

			self.city_entry = ctk.CTkEntry(self, placeholder_text='Выберите город, в который отправится сотрудник', width=350)
			self.city_entry.grid(row=1, column=0, pady=(15, 5))

			self.payment_entry = ctk.CTkEntry(self, placeholder_text='Напишите сумму, которую получит сотрудник', width=350)
			self.payment_entry.grid(row=2, column=0, pady=(15, 5))

			self.button_eject = ctk.CTkButton(self, text='Отправить сотрудника в командировку', command=self.insert_to)
			self.button_eject.grid(row=3, column=0, pady=(25, 5))

	def return_from(self):
		business_trip = self.business_trip
		worker = self.worker

		sql = '''
			UPDATE Salary
			SET business_trip_part = %s,
			    total_amount = total_amount + %s
			WHERE worker_id = %s;
			DELETE FROM Business_Trip
			WHERE id = %s;
		'''
		execute(sql, (business_trip.payment, business_trip.payment, worker._id, business_trip._id))
		
		self.destroy()
		self.master.update_tables()

	def insert_to(self):
		city = self.city_entry.get()
		payment = self.payment_entry.get()

		if not city:
			exception('Не выбран город')
			return

		if city.isnumeric():
			exception('Город не может называться цифрами')
			return


		if not payment:
			payment = 0

		try:
			payment = float(payment)
		except ValueError:
			exception('Недопустимое значение в поле надбавки')
			return

		if abs(payment) == float('inf') or isnan(payment):
			exception('Надбавка не может являтся INF/NaN')
			return

		sql = '''
			INSERT INTO Business_Trip
			(city, payment)
			VALUES
			(%s, %s);
		'''
		execute(sql, (city, payment))

		sql = '''
			SELECT max(id) as id
			FROM Business_Trip 
		'''
		_id = fetch_one(sql).get('id')

		sql = '''
			UPDATE Worker
			SET business_trip_id = %s
			WHERE id = %s
		'''
		execute(sql, (_id, self.worker._id))

		self.destroy()
		self.master.update_tables()
