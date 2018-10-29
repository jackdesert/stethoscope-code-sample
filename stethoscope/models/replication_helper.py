import pdb

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
            value_formatted = f'"{value}"'
            values.append(value_formatted)

        sql += ', '.join(values)
        sql += ');\n\n'
        return sql

    def _columns(self):
        return (str(col).split('.')[1] for col in self.klass.__table__.columns)
