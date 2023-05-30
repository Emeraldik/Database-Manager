from dataclasses import dataclass

from modules.database import fetch_all

@dataclass()
class Department():
	_id: int
	name: str


@dataclass()
class Project():
	_id: int
	name: str


@dataclass()
class BusinessTrip():
	_id: int
	city: str
	payment: float


@dataclass()
class Worker():
	_id: int
	full_name: str
	job_title: str
	sex: str
	age: int
	work_exp: int
	department_id: Department
	project_id: Project
	business_trip_id: BusinessTrip


@dataclass()
class ProjectWorker():
	project_id: Project
	worker_id: Worker


@dataclass()
class Salary():
	_id: int
	worker_id: int
	total_amount: float
	business_trip_part: float
	work_exp_part: float


zero_worker = Worker(
	_id=0,
	full_name='-',
	job_title='-',
	sex='-',
	age=0,
	work_exp=0,
	department_id=0,
	project_id=0,
	business_trip_id=0
)

zero_trip = BusinessTrip(
	_id=0,
	city='-',
	payment=0
)

zero_project = Project(
	_id=0,
	name='-'
)

zero_department = Department(
	_id=0,
	name='-'
)

def get_workers():
	sql = 'SELECT * FROM Worker ORDER BY id'
	result = fetch_all(sql)
	return {
		worker['id']:
		Worker(
			_id = worker['id'],
			full_name = worker['full_name'],
			job_title = worker['job_title'],
			sex = worker['sex'],
			age = worker['age'],
			work_exp = worker['work_experience'],
			department_id = worker['department_id'],
			project_id = worker['project_id'],
			business_trip_id = worker['business_trip_id'],
		)
		for worker in result
	}


def get_departments():
	sql = '''
		SELECT id, name 
		FROM Department
	'''
	result = fetch_all(sql)
	return {
		department['id']:
		Department(
			_id = department['id'],
			name = department['name']
		)
		for department in result
	}


def get_projects():
	sql = '''
		SELECT id, name 
		FROM Project
	'''
	result = fetch_all(sql)
	return {
		project['id']:
		Project(
			_id = project['id'],
			name = project['name']
		)
		for project in result
	}

def get_head_projects():
	sql = '''
		SELECT project_id, worker_id
		FROM Project_Worker
	'''
	result = fetch_all(sql)
	return {
		project['project_id']:
		ProjectWorker(
			project_id = project['project_id'],
			worker_id = project['worker_id']
		)
		for project in result
	}

def get_business_trips():
	sql = '''
		SELECT id, city, payment
		FROM Business_Trip
	'''

	result = fetch_all(sql)
	
	return {
		trip['id']:
		BusinessTrip(
			_id=trip['id'],
			city=trip['city'],
			payment=trip['payment']
		)
		for trip in result
	}


def get_salaries():
	sql = '''
		SELECT id, worker_id, total_amount, business_trip_part, work_experience_part
		FROM Salary
		ORDER BY total_amount DESC
	'''

	result = fetch_all(sql)

	return {
		salary['worker_id']:
		Salary(
			_id = salary['id'],
			worker_id = salary['worker_id'],
			total_amount = salary['total_amount'],
			business_trip_part = salary['business_trip_part'],
			work_exp_part = salary['work_experience_part']
		)
		for salary in result
	}