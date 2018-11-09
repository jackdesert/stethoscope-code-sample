import ipdb
from datetime import datetime

class ReplicationHelper:
    def __init__(self, klass):
        self.klass = klass
        self.table_name = klass.__table__.name

    def insert_bulk(self, objects):
        sql = ''
        for obj in objects:
            sql += self.insert_single(obj)

        return sql

    def insert_single(self, obj):
        csv_column_names = ', '.join(self._columns())
        sql = f'INSERT INTO {self.table_name} ({csv_column_names}) VALUES ('
        values = []

        for attribute in self._columns():
            value = getattr(obj, attribute)
            values.append(self._format_value(value))

        sql += ', '.join(values)
        sql += ');\n\n'
        return sql

    def _columns(self):
        return (str(col).split('.')[1] for col in self.klass.__table__.columns)

    def _format_value(self, value):
        if isinstance(value, int):
            # Plain string
            return str(value)
        elif isinstance(value, str) or isinstance(value, datetime):
            # Quoted string (Use single quotes inside string for postgres)
            return f"'{value}'"
        elif value == None:
            return 'NULL'
        else:
            raise TypeError
