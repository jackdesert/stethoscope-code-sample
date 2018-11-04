import ipdb
from datetime import datetime

class ReplicationHelper:
    def __init__(self, klass):
        self.klass = klass
        self.table_name = klass.__table__.name

    def insert_bulk(self, objects):
        # Run single inserts inside a transaction to boost performance
        sql = '\n\nBEGIN TRANSACTION;\n'
        for obj in objects:
            sql += self.insert_single(obj)

        sql += 'COMMIT;\n'

        return sql

    def insert_single(self, obj):
        sql = f'INSERT INTO {self.table_name} VALUES ('
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
            # Quoted string
            return f'"{value}"'
        elif value == None:
            return 'NULL'
        else:
            raise TypeError
