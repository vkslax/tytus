from parse.ast_node import ASTNode
from util import *
from jsonMode import *
from parse.errors import Error, ErrorType


class Update(ASTNode):
    def __init__(self, table_name, update_list, where, line, column, graph_ref):
        ASTNode.__init__(self, line, column)
        self.table_name = table_name
        self.update_list = update_list
        self.where = where
        self.graph_ref = graph_ref

    def execute(self, table, tree):
        super().execute(table, tree)

        header = []
        # get all columns and add into header array
        columns = table.get_fields_from_table(self.table_name)
        columns.sort(key=lambda x: x.field_index)
        primary_key = 0
        for c in columns:
            header.append(str(c.field_name))
            if c.is_pk:
                primary_key = c.field_index

        data = extractTable(table.get_current_db().name, self.table_name)
        # Apply filter for each row by call the execute function if execute return true we kept the row else remove that
        if self.where:
            data = self.where.execute(data, header)
        to_update = list(map(lambda x: f'{x[primary_key]}|', data))
        # Mapping values to set into a dictionary
        reg = {}
        all_fields_symbol = table.get_fields_from_table(self.table_name)
        for item in self.update_list:
            # reg[item.column_name] = item.exp.val
            column_symbol = next((sym for sym in all_fields_symbol if sym.field_name == item.column_name), None)
            reg[column_symbol.field_index] = item.exp.execute(table, tree)
        for index in to_update:
            result = update(table.get_current_db().name, self.table_name, reg, [index])
            if result == 1:
                raise Error(0, 0, ErrorType.RUNTIME, '5800: system_error')
            elif result == 2:
                raise Error(0, 0, ErrorType.RUNTIME, '42P04: database_does_not_exists')
            elif result == 3:
                raise Error(0, 0, ErrorType.RUNTIME, '42P07: table_does_not_exists')
            elif result == 4:
                raise Error(0, 0, ErrorType.RUNTIME, '42P10: PK_does_not_exists')
        return f'Update in {self.table_name}'


class UpdateItem(ASTNode):
    def __init__(self, column_name, exp, line, column, graph_ref):
        ASTNode.__init__(self, line, column)
        self.column_name = column_name
        self.exp = exp
        self.graph_ref = graph_ref

    def execute(self, table, tree):
        super().execute(table, tree)
        return True
