import psycopg2
from psycopg2.extras import RealDictCursor

from typing import Any
from collections.abc import Iterable
from typing_extensions import LiteralString

from db_manager.config import DB_USER, DB_PASS

def get_db():
	if not getattr(get_db, 'db', None):
		db = psycopg2.connect(
			database='production-db',
			host='localhost',
			user=DB_USER,
			password=DB_PASS,
			port=5432
		)
		get_db.db = db

	return get_db.db


def fetch_all(
	sql: LiteralString, params: Iterable[Any] | None = None
) -> dict | None:
	cursor = _get_cursor(sql, params)
	result = cursor.fetchall()
	cursor.close()
	return result


def fetch_one(
	sql: LiteralString, params: Iterable[Any] | None = None
) -> dict | None:
	cursor = _get_cursor(sql, params)
	row = cursor.fetchone()
	if not row:
		return None
	cursor.close()
	return row


def execute(
	sql: LiteralString, params: Iterable[Any] | None = None, *, autocommit: bool = True
) -> None:
	db = get_db()
	cursor = _get_cursor(sql, params)
	if autocommit:
		db.commit()

	cursor.close()


def close_db() -> None:
	get_db().close()


def _get_cursor(
	sql: LiteralString, params: Iterable[Any] | None = None
):
	db = get_db()
	args: tuple[LiteralString, Iterable[Any] | None] = (sql, params)
	cursor = db.cursor(cursor_factory = RealDictCursor)
	cursor.execute(*args)

	return cursor
