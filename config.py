import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DB_USER = os.environ['db_user']
DB_PASS = os.environ['db_pass']

TITLE = 'Databse Manager (Beta v0.1)'

WINDOW_SIZE = 1200, 600
MINSIZE_MODE = True # if true -> Frame will be resizable, else not
