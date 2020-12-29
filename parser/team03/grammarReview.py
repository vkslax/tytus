import ply.lex as lex
import re
from parse.errors import Error as our_error
from parse.expressions.expressions_math import *
from parse.expressions.expressions_base import *
from parse.expressions.expressions_trig import *
from parse.sql_common.sql_general import *
from parse.sql_ddl.create import *
from parse.sql_ddl.alter import *
from parse.sql_dml.insert import *
from parse.sql_ddl.drop import *
from parse.sql_dml.select import *
from parse.sql_dml.update import *
from parse.sql_dml.delete import *
from treeGraph import *
from parse.symbol_table import *

#===========================================================================================
#==================================== LEXICAL ANALYSIS ==================================
#===========================================================================================
reserved = {
    'smallint' : 'SMALLINT',
    'integer' : 'INTEGER',
    'bigint' : 'BIGINT',
    'decimal' : 'DECIMAL',
    'numeric' : 'NUMERIC',
    'real' : 'REAL',
    'double' : 'DOUBLE',
    'precision' : 'PRECISION',
    'money' : 'MONEY',
    'caracter' : 'CARACTER',
    'varying' : 'VARYING',
    'varchar' : 'VARCHAR',
    'character' : 'CHARACTER',
    'char' : 'CHAR',
    'text' : 'TEXT',
    'timestamp' : 'TIMESTAMP',
    'date' : 'DATE',
    'time' : 'TIME',
    'interval' : 'INTERVAL',
    'year' : 'YEAR',
    'month' : 'MONTH',
    'day' : 'DAY',
    'hour' : 'HOUR',
    'minute' : 'MINUTE',
    'second' : 'SECOND',
    'extract' : 'EXTRACT',
    'date_part' : 'DATE_PART',
    'now' : 'NOW',
    'current_date' : 'CURRENT_DATE',
    'current_time' : 'CURRENT_TIME',
    'boolean' : 'BOOLEAN',
    'between' : 'BETWEEN',
    'symmetric' : 'SYMMETRIC',
    'in' : 'IN',
    'like' : 'LIKE',
    'ilike' : 'ILIKE',
    'similar' : 'SIMILAR',
    'is' : 'IS',
    'null' : 'NULL',
    'not' : 'NOT',
    'and' : 'AND',
    'or' : 'OR',
    'select' : 'SELECT',
    'from' : 'FROM',
    'where' : 'WHERE',
    'create' : 'CREATE',
    'type' : 'TYPE',
    'as' : 'AS',
    'enum' : 'ENUM',
    'replace' : 'REPLACE',
    'database' : 'DATABASE',
    'if' : 'IF',
    'exists' : 'EXISTS',
    'owner' : 'OWNER',
    'mode' : 'MODE',
    'show' : 'SHOW',
    'databases' : 'DATABASES',
    'alter' : 'ALTER',
    'rename' : 'RENAME',
    'to' : 'TO',
    'drop' : 'DROP',
    'current_user' : 'CURRENT_USER',
    'session_user' : 'SESSION_USER',
    'table' : 'TABLE',
    'default' : 'DEFAULT',
    'constraint' : 'CONSTRAINT',
    'unique' : 'UNIQUE',
    'check' : 'CHECK',
    'primary' : 'PRIMARY',
    'key' : 'KEY',
    'references' : 'REFERENCES',
    'foreign' : 'FOREIGN',
    'add' : 'ADD',
    'column' : 'COLUMN',
    'set' : 'SET',
    'inherits' : 'INHERITS',
    'insert' : 'INSERT',
    'into' : 'INTO',
    'values' : 'VALUES',
    'update' : 'UPDATE',
    'delete' : 'DELETE',
    'distinct' : 'DISTINCT',
    'group' : 'GROUP',
    'by' : 'BY',
    'having' : 'HAVING',
    'unknown' : 'UNKNOWN',
    'count' : 'COUNT',
    'min' : 'MIN',
    'max' : 'MAX',
    'sum' : 'SUM',
    'avg' : 'AVG',
    'abs' : 'ABS',
    'cbrt' : 'CBRT',
    'ceil' : 'CEIL',
    'ceiling' : 'CEILING',
    'degrees' : 'DEGREES',
    'div' : 'DIV',
    'exp' : 'EXP',
    'factorial' : 'FACTORIAL',
    'floor' : 'FLOOR',
    'gcd' : 'GCD',
    'lcm' : 'LCM',
    'ln' : 'LN',
    'log' : 'LOG',
    'log10' : 'LOG10',
    'min_scale' : 'MIN_SCALE',
    'mod' : 'MOD',
    'pi' : 'PI',
    'power' : 'POWER',
    'radians' : 'RADIANS',
    'round' : 'ROUND',
    'scale' : 'SCALE',
    'sign' : 'SIGN',
    'sqrt' : 'SQRT',
    'trim_scale' : 'TRIM_SCALE',
    'trunc' : 'TRUNC',
    'width_bucket' : 'WIDTH_BUCKET',
    'random' : 'RANDOM',
    'setseed' : 'SETSEED',
    'acos' : 'ACOS',
    'acosd' : 'ACOSD',
    'asin' : 'ASIN',
    'asind' : 'ASIND',
    'atan' : 'ATAN',
    'atand' : 'ATAND',
    'atan2' : 'ATAN2',
    'atan2d' : 'ATAN2D',
    'cos' : 'COS',
    'cosd' : 'COSD',
    'cot' : 'COT',
    'cotd' : 'COTD',
    'sin' : 'SIN',
    'sind' : 'SIND',
    'tan' : 'TAN',
    'tand' : 'TAND',
    'sinh' : 'SINH',
    'cosh' : 'COSH',
    'tanh' : 'TANH',
    'asinh' : 'ASINH',
    'acosh' : 'ACOSH',
    'atanh' : 'ATANH',
    'length' : 'LENGTH',
    'substring' : 'SUBSTRING',
    'trim' : 'TRIM',
    'get_byte' : 'GET_BYTE',
    'md5' : 'MD5',
    'set_byte' : 'SET_BYTE',
    'sha256' : 'SHA256',
    'substr' : 'SUBSTR',
    'convert' : 'CONVERT',
    'encode' : 'ENCODE',
    'decode' : 'DECODE',
    'substring' : 'SUBSTRING',
    'any' : 'ANY',
    'all' : 'ALL',
    'some' : 'SOME',
    'asc' : 'ASC',
    'desc' : 'DESC',
    'case' : 'CASE',
    'when' : 'WHEN',
    'then' : 'THEN',
    'else' : 'ELSE',
    'end' : 'END',
    'greatest' : 'GREATEST',
    'least' : 'LEAST',
    'order' : 'ORDER',
    'limit' : 'LIMIT',
    'offset' : 'OFFSET',
    'union' : 'UNION',
    'intersect' : 'INTERSECT',
    'except' : 'EXCEPT',
    'inner' : 'INNER',
    'left' : 'LEFT',
    'right' : 'RIGHT',
    'full' : 'FULL',
    'outer' : 'OUTER',
    'join' : 'JOIN',
    'on' : 'ON',
    'using' : 'USING',
    'natural' : 'NATURAL',
    'first' : 'FIRST',
    'last' : 'LAST',
    'nulls' : 'NULLS',
    'use' : 'USE',
}

tokens = [
    'PARA',
    'PARC',
    'CORCHA',
    'CORCHC',
    'PUNTO',
    'COMA',
    'PUNTOCOMA',
    'MAS',
    'MENOS',
    'POR',
    'DIAGONAL',
    'EXPONENCIANCION',
    'PORCENTAJE',
    'MAYOR',
    'MENOR',
    'IGUAL',
    'MAYORQ',
    'MENORQ',
    'DIFERENTE',
    'ENTERO',
    'FLOAT',
    'TEXTO',
    'FECHA_HORA',
    'PATTERN_LIKE',
    'BOOLEAN_VALUE',
    'ID',
    'SQUARE_ROOT',
    'CUBE_ROOT',
    'AMPERSON',
    'NUMERAL',
    'PRIME',
    'SHIFT_L',
    'SHIFT_R',
] +list(reserved.values()) 

t_PARA = r'\('
t_PARC = r'\)'
t_CORCHA = r'\['
t_CORCHC = r'\]'
t_PUNTO = r'\.'
t_COMA = r'\,'
t_PUNTOCOMA = r'\;'
t_MAS = r'\+'
t_MENOS = r'\-'
t_POR = r'\*'
t_DIAGONAL = r'\/'
t_EXPONENCIANCION = r'\^'
t_PORCENTAJE = r'%'
t_MAYOR = r'>'
t_MENOR = r'<'
t_IGUAL = r'='
t_MAYORQ = r'>='
t_MENORQ = r'<='
t_SQUARE_ROOT = r'\|'
t_CUBE_ROOT = r'\|\|'
t_AMPERSON = r'\&'
t_NUMERAL = r'\#'
t_PRIME = r'\~'
t_SHIFT_L = r'<<'
t_SHIFT_R = r'>>'



# ignored regular expressions
t_ignore = " \t"
t_ignore_COMMENT =r'\-\-.*'
t_ignore_COMMENTMULTI = r'(/\*(.|\n)*?\*/)|(//.*)'

def t_DIFERENTE(t):
    r'((<>)|(!=))'
    t.type = reserved.get(t.value,'DIFERENTE')    
    return t


def t_FLOAT(t):
    r'((\d+\.\d*)((e[\+-]?\d+)?)|(\d*e[\+-]?\d+))'
    t.value = float(t.value)    
    return t


def t_ENTERO(t):
    r'\d+'
    t.value = int(float(t.value))  
    return t

def t_FECHA_HORA(t):
    r'\'\d{4}-[0-1]?\d-[0-3]?\d [0-2]\d:[0-5]\d:[0-5]\d\''
    t.value = t.value[1:-1]
    t.type = reserved.get(t.value,'FECHA_HORA')
    return t

def t_PATTERN_LIKE(t):
    r'\'\%.*\%\''
    t.value = t.value[2:-2]
    t.type = reserved.get(t.value,'PATTERN_LIKE')
    return t

def t_TEXTO(t):
    r'\'([^\\\n]|(\\.))*?\''
    t.value = t.value[1:-1]
    t.type = reserved.get(t.value,'TEXTO')    
    return t
    
def t_BOOLEAN_VALUE(t):
    r'((false)|(true))'
    t.value = t.value.lower()
    t.type = reserved.get(t.value,'BOOLEAN_VALUE')    
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(),'ID')    
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
    
def t_error(t):
    err = Error(t.lineno, t.lexpos, ErrorType.LEXICAL, 'Ilegal character \''+ t.value[0] + '\'')
    errorsList.append(err)
    t.lexer.skip(1)


lexer = lex.lex(debug = False, reflags=re.IGNORECASE) 

#===========================================================================================
#==================================== SYNTACTIC ANALYSIS ==================================
#===========================================================================================

start = 'init'

precedence = (

    # Arthmetic
    ('left', 'MAS', 'MENOS'),
    ('left', 'POR', 'DIAGONAL'),
    ('left', 'EXPONENCIANCION'),
    ('right', 'UMENOS'),
    ('right', 'UMAS'),
    # Relational
    ('left', 'MENOR', 'MAYOR', 'IGUAL', 'MENORQ', 'MAYORQ'),
    # logic
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'AS')
)


def p_init(t):
    ''' init : statements'''
    t[0] = t[1]


def p_statements(t):
    ''' statements  :   statements statement    '''
    t[1].append(t[2])
    t[0] = t[1]


def p_statements2(t):
    ''' statements  :   statement '''
    t[0] = [t[1]]


def p_statement(t):
    '''statement    : stm_show   PUNTOCOMA
                    | stm_create PUNTOCOMA
                    | stm_alter  PUNTOCOMA
                    | stm_use_db PUNTOCOMA
                    | stm_select PUNTOCOMA
                    | stm_insert PUNTOCOMA
                    | stm_update PUNTOCOMA
                    | stm_delete PUNTOCOMA
                    | stm_drop   PUNTOCOMA
                    | stm_select UNION all_opt stm_select PUNTOCOMA
                    | stm_select INTERSECT all_opt stm_select PUNTOCOMA
                    | stm_select EXCEPT all_opt stm_select PUNTOCOMA
                    '''

#                    |    stm_select PUNTOCOMA
#                    |    stm_select UNION all_opt stm_select
#                    |    stm_select INTERSECT all_opt stm_select
#                    |    stm_select EXCEPT all_opt 
    try:
        if len(t) == 3:
            punteroinicio(t[1].graph_ref)
    except:
        print("falta parametro graph_ref")
    if len(t) == 3:
        t[0] = t[1]
    else:
        token_op = t.slice[2]
        graph_ref = None
        if token_op.type == 'UNION':
            childsProduction  = addNotNoneChild(t,[1,3,4])
            graph_ref = graph_node(str("stm_union"),    [t[1],t[2],t[3],t[4]]       ,childsProduction)
            punteroinicio(graph_ref)
            addCad("**\<STATEMENT>** ::= \<STM_SELECT> tUnion tAll \<STM_SELECT> ")
            t[0] = Union(t[1], t[4], True if t[3] is not None else False, token_op.lineno, token_op.lexpos, graph_ref)
        if token_op.type == 'INTERSECT':
            childsProduction  = addNotNoneChild(t,[1,3,4])
            graph_ref = graph_node(str("stm_intersect"),    [t[1],t[2],t[3],t[4]]       ,childsProduction)
            punteroinicio(graph_ref)
            addCad("**\<STATEMENT>** ::= \<STM_SELECT> tUnion tAll \<STM_SELECT> ")
            t[0] = Intersect(t[1], t[4], True if t[3] is not None else False, token_op.lineno, token_op.lexpos, graph_ref)
        if token_op.type == 'EXCEPT':
            childsProduction  = addNotNoneChild(t,[1,3,4])
            graph_ref = graph_node(str("stm_except"),    [t[1],t[2],t[3],t[4]]       ,childsProduction)
            punteroinicio(graph_ref)
            addCad("**\<STATEMENT>** ::= \<STM_SELECT> tUnion tAll \<STM_SELECT> ")
            t[0] = Except(t[1], t[4], True if t[3] is not None else False, token_op.lineno, token_op.lexpos, graph_ref)

def p_statement_error(t):
    '''statement    : error PUNTOCOMA
                    '''
    token = t.slice[1]
    t[0] = Error(token.lineno, token.lexpos, ErrorType.SYNTAX, 'Ilegal token '+str(token.lineno))


#################


def p_all_opt(t):
    '''all_opt  : ALL
                | empty'''
    token = t.slice[1]
    if token.type == "ALL":
        graph_ref = graph_node(str(t[1]) )
        addCad("**\<ALL_OPT>** ::= tAll ")
        t[0] = upNodo(True, 0, 0, graph_ref)
        #####        
    else: 
        t[0]=None 

def p_stm_select(t):
    '''stm_select : SELECT distinct_opt list_names FROM table_list where_clause_opt group_clause_opt having_clause_opt order_by_opt limit_opt offset_opt
                  | SELECT distinct_opt list_names  '''
    if len(t) == 4:
        lista=None
        childsProduction  = addNotNoneChild(t,[2])
        if t[3] != None:
            lista=t[3][0]
            childsProduction.append(lista.graph_ref)       
        graph_ref = graph_node(str("stm_select"),    [t[1], t[2],lista]       ,childsProduction)
        addCad("**\<STM_SELECT>** ::= tSelect \<LIST_NAMES> ")
        t[0] = Select(False, t[3], None, None, None, None, None, None, None, t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    else:    
        lista=None
        lista2=None        
        childsProduction  = addNotNoneChild(t,[2,6,7,8,9,10,11])
        if t[3] != None:
            lista=t[3][0]
            childsProduction.append(lista.graph_ref) 
        if t[5] != None:
            lista2=t[5][0]
            childsProduction.append(lista2.graph_ref)            
        graph_ref = graph_node(str("stm_select"),    [t[1], t[2], lista, t[4], lista2, t[6], t[7], t[8], t[9], t[10], t[11]]       ,childsProduction)
        addCad("**\<STM_SELECT>** ::= tSelect \<DISTINC_OPT> \<LIST_NAMES> tFrom \<TABLE_LIST>   \<WHERE_CLAUSE> \<GROUP_CLAUSE>\<HAVING_CLAUSE_OPT> \<ORDER_BY_OPT> <LIMIT_OPT>  ")
        t[0] = Select(True if t[2] else False, t[3], t[5], t[6], t[7], t[8], t[9], t[10], t[11], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)        


def p_distinct_opt(t):
    '''distinct_opt : not_opt DISTINCT
                    | empty'''

    if len(t) == 3:
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("distinct_opt"),    [t[1], t[2]]       ,childsProduction)
        addCad("**\<DISTINCT_OPT>** ::= \<NOT_OPT> tDistinct ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####        
    else: 
        t[0]=None 

def p_where_clause_opt(t):
    '''where_clause_opt : where_clause
                        | empty'''
    token = t.slice[1]
    if token.type == "where_clause":
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("where_clause_opt"),    [t[1]]       ,childsProduction)
        addCad("**\<WHERE_CLAUSE_OPT>** ::= \<WHERE_CLAUSE_OPT> ")
        t[1].graph_ref = graph_ref        
        t[0] = t[1]
        #TODO: Check the graph paint wuith empty       
    else: 
        t[0]=None 


def p_group_clause_opt(t):
    '''group_clause_opt : group_clause
                        | empty'''
    token = t.slice[1]
    if token.type == "group_clause":
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("group_clause_opt"),    [t[1]]       ,childsProduction)
        addCad("**\<GROUP_CLAUSE_OPT>** ::=  \<GROUP_CLAUSE>  ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####        
    else: 
        t[0]=None 

def p_having_clause_opt(t):
    '''having_clause_opt    : having_clause
                    | empty'''
    token = t.slice[1]
    if token.type == "having_clause":
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("having_clause_opt"),    [t[1]]       ,childsProduction)
        addCad("**\<HAVING_CLAUSE_OPT>** ::=  \<HAVING_CLAUSE>  ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####        
    else: 
        t[0]=None 


def p_order_by_opt(t):
    '''order_by_opt : ORDER BY col_name
                    | empty'''
    if len(t) == 4:
        childsProduction  = addNotNoneChild(t,[3])
        graph_ref = graph_node(str("order_by_opt"),    [t[1],t[2],t[3]]       ,childsProduction)
        addCad("**\<ORDER_BY_OPT>** ::= tOrder tBy \<COL_NAME>  ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####        
    else: 
        t[0]=None 

def p_limit_opt(t):
    '''limit_opt    : LIMIT ENTERO
                    | empty'''
    if len(t) == 3:
        graph_ref = graph_node(str(str(t[1]) +" "+str(t[2])  ))
        addCad("**\<LIMIT_OPT>** ::=  tLimit tEntero  ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####        
    else: 
        t[0]=None 

def p_offset_opt(t):
    '''offset_opt   : OFFSET ENTERO
                    | empty'''
    if len(t) == 3:
        graph_ref = graph_node(str(str(t[1]) +" "+str(t[2])  ))
        addCad("**\<OFFSET_OPT>** ::=  tOffset  tEntero  ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####        
    else: 
        t[0]=None 


def p_table(t):
    '''table    : ID 
                | ID AS TEXTO
                | ID AS ID
                '''

    if len(t) == 2:
        graph_ref = graph_node(str(str(t[1])))
        addCad("**\<TABLE>** ::=  tIdentificador  ")
        t[0] = Table(t[1], t[1], None, t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
        #####        
    else: 
        graph_ref = graph_node(str(str(t[1]) +" "+str(t[2])+" "+ str(t[3])  ))
        addCad("**\<TABLE>** ::=  tIdentificador tAs tTexto  ")
        t[0] = Table(t[1], t[3], None, t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
        ##### 


def p_table0(t):
    '''table    :  PARA stm_select PARC
                |  PARA stm_select PARC AS TEXTO
                |  PARA stm_select PARC AS ID
                '''
    if len(t) == 4:
        childsProduction  = addNotNoneChild(t,[2])
        graph_ref = graph_node(str("table"),    [t[1],t[2],t[3]]       ,childsProduction)
        addCad("**\<TABLE>*[* ::=  '(' \<STM_SELECT> ')' ")
        t[0] = Table(None, None, t[2], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
        
    else: 
        childsProduction  = addNotNoneChild(t,[2])
        graph_ref = graph_node(str("table"),    [t[1],t[2],t[3],t[4],t[5]]       ,childsProduction)
        addCad("**\<TABLE>** ::=  '(' \<STM_SELECT> ')' tAs  tTexto ")
        t[0] = Table(t[5], t[5], t[2], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    


def p_stm_insert(t):
    '''stm_insert   : INSERT INTO ID insert_ops'''
    childsProduction  = addNotNoneChild(t,[4])
    graph_ref = graph_node(str("stm_insert"), [t[1], t[2], t[3], t[4]], childsProduction)
    addCad("**\<STM_INSERT>** ::=  tInsert tInto tIdentifier \<INSERT_OPS>  ")
    token_insert = t.slice[1]
    t[0] = InsertInto(t[3], t[4].column_list, t[4].values_list, token_insert.lineno, token_insert.lexpos, graph_ref)
    #print(t)



def p_insert_ops(t):
    '''insert_ops   : column_list_param_opt VALUES PARA exp_list PARC
                    |   column_list_param_opt stm_select'''
    if len(t) == 6:
        lista=None
        childsProduction  = addNotNoneChild(t,[1])
        if t[4] != None:
            lista=t[4][0]
            childsProduction.append(lista.graph_ref)

        graph_ref = graph_node(str("insert_ops"),    [t[1], t[2], t[3], lista, t[5]], childsProduction)
        addCad("**\<INSERT_OPS>** ::=  \<COLUMN_LIST>  tValues  '(' \<EXP_LIST> ')' ")
        token_ops = t.slice[2]
        t[0] = InsertItem(t[1].val if t[1] is not None else None, t[4], token_ops.lineno, token_ops.lexpos, graph_ref)
    else:
        token_ops = t.slice[1]
        childsProduction = addNotNoneChild(t, [1, 2])
        graph_ref = graph_node(str("insert_ops"), [t[1], t[2]], childsProduction)
        addCad("**\<INSERT_OPS>** ::=  \<COLUMN_LIST>  \<STM_SELECT>  ")
        t[0] = InsertItem(t[1].val, t[2], 0, 0, graph_ref)


def p_table_list(t):
    '''table_list   : table_list COMA table_ref 
                    | table_ref'''
    if len(t) == 4:
        lista=None
        childsProduction  = addNotNoneChild(t,[3])
        if t[1] != None:
            lista=t[1][0]
            childsProduction.append(lista.graph_ref)
        graph_ref = graph_node(str("table_list"),    [lista,t[2],t[3]]       ,childsProduction)        
        addCad("**\<TABLE_LIST>** ::=  \<TABLE_LIST>  ',' \<TABLE_REF> ')' ")
        #TODO: Check graph of the list
        t[1][0].graph_ref = graph_ref
        t[1].append(t[3])
        t[0] = t[1]
                  
    else: 
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("table_list"),    [t[1]]       ,childsProduction)
        addCad("**\<TABLE_LIST>** ::=  \<TABLE_REF> ')' ")
        t[1].graph_ref = graph_ref
        t[0] = [t[1]]        


def p_table_ref(t):
    '''table_ref    : table NATURAL join_type JOIN table
                    | table join_type JOIN table
                    | table'''

    if len(t) == 6:
        childsProduction  = addNotNoneChild(t,[1,3,5])
        graph_ref = graph_node(str("table_ref"),    [t[1],t[2],t[3],t[4],t[5]]       ,childsProduction)
        addCad("**\<TABLE_REF>** ::=  \<TABLE> tNatural  \<JOIN_TYPE>  tJoin \<TABLE>   ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####                
    elif len(t) == 6:
        childsProduction  = addNotNoneChild(t,[1,2,4])
        graph_ref = graph_node(str("table_ref"),    [t[1],t[2],t[3],t[4]]       ,childsProduction)
        addCad("**\<TABLE_REF>** ::=  \<TABLE>  \<JOIN_TYPE>  tJoin \<TABLE>   ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####  
    elif len(t) == 2:
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("table_ref"),    [t[1]]       ,childsProduction)
        addCad("**\<TABLE_REF>** ::=  \<TABLE>    ")
        t[1].graph_ref=graph_ref
        t[0] = t[1]




def p_join_type(t):
    '''join_type    :  outer_join_type                 
                    |  outer_join_type OUTER
    '''

    if len(t) == 2:
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("join_type"),    [t[1]]       ,childsProduction)
        addCad("**\<JOIN_TYPE>** ::=  \<OUTER_JOIN_TYPE>   ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####                
    elif len(t) == 3:
        childsProduction  = addNotNoneChild(t,[1,2,4])
        graph_ref = graph_node(str("join_type"),    [t[1],t[2],t[3],t[4]]       ,childsProduction)
        addCad("**\<JOIN_TYPE>** ::=  \<OUTER_JOIN_TYPE>  tOuter ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        ####   
    
def p_join_type0(t):
    '''join_type    : INNER
                      '''
    graph_ref = graph_node(str(t[1]))
    addCad("**\<JOIN_TYPE>** ::=  tInner   ")
    t[0] = upNodo("token", 0, 0, graph_ref)


    
def p_outer_join_type(t):
    '''outer_join_type  : LEFT
                        | RIGHT
                        | FULL'''
    token = t.slice[1]
    graph_ref = graph_node(str(t[1]))
    addCad("**\<OUTER_JOIN_TYPE>** ::=   "+str(token.type))
    t[0] = upNodo("token", 0, 0, graph_ref)
    ##


def p_list_names(t):
    '''list_names   : list_names COMA names AS TEXTO
                    | list_names COMA names AS ID
                    | list_names COMA names
                    | POR
                    '''
    if len(t) == 6:
        lista=None
        childsProduction  = addNotNoneChild(t,[3])
        if t[1] != None:
            lista=t[1][0]
            childsProduction.append(lista.graph_ref)            
        graph_ref = graph_node(str("list_names"),    [lista,t[2],t[3],t[4],t[5]]       ,childsProduction)
        addCad("**\<LIST_NAMES>** ::=  \<LIST_NAMES>  ',' tNames tAs tTexto  ")
        t[3].alias = t[5]
        t[1][0].graph_ref=graph_ref
        t[1].append(t[3])
        t[0] = t[1]
                     
    elif len(t) == 4:
        lista=None
        childsProduction  = addNotNoneChild(t,[3])
        if t[1] != None:
            lista=t[1][0]
            childsProduction.append(lista.graph_ref)    
        graph_ref = graph_node(str("list_names"),    [lista,t[2],t[3]]       ,childsProduction)
        addCad("**\<LIST_NAMES>** ::=   \<LIST_NAMES>  ',' tNames ")
        t[1][0].graph_ref=graph_ref
        t[1].append(t[3])
        t[0] = t[1]
        
    elif len(t) == 2:
        
        graph_ref = graph_node(str("tPor"),    [t[1]], [])
        addCad("**\<LIST_NAMES>** ::=   tPor ")
        t[0] = [Names(True, None, None, t.slice[1].lineno, t.slice[1].lexpos, graph_ref)]



def p_list_names0(t):
    '''list_names   : names AS TEXTO
                    | names AS ID
                    | names'''

    if len(t) == 4:
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("list_names"),    [t[1],t[2],t[3]]       ,childsProduction)
        addCad("**\<LIST_NAMES>** ::=  \<NAMES> tAs tTexto  ")
        t[1].graph_ref=graph_ref
        t[1].alias = t[3]
        t[0] = [t[1]]
        
    elif len(t) == 2:
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("list_names"),    [t[1]]       ,childsProduction)
        addCad("**\<LIST_NAMES>** ::=  \<NAMES> ")
        t[1].graph_ref=graph_ref
        t[0] = [t[1]]
        


#def p_names(t):
#    '''names    : POR
#                       '''
#    graph_ref = graph_node(str(t[1]) )
#    addCad("**\<NAMES>** ::=  '*'  ")
#    t[0] = upNodo("token", 0, 0, graph_ref)
#    ##### 


def p_names(t):
    '''names    :  expression
                |  time_ops
                |  case_clause
                       '''
    token = t.slice[1]
    cadena = str(token.type)
    childsProduction  = addNotNoneChild(t,[1])
    graph_ref = graph_node(str("names"),    [t[1]]       ,childsProduction)
    addCad("**\<NAMES>** ::=  \<"+ cadena.upper() +" >"     )
    t[0] = Names(False,t[1], None, t[1].line, t[1].column, graph_ref)



def p_names1(t):
    '''names    :  GREATEST PARA exp_list PARC
                |  LEAST PARA exp_list PARC
                       '''
    token = t.slice[1]
    cadena = str(token.type)
    lista=None
    childsProduction  = []
    if t[3] != None:
        lista=t[3][0]
        childsProduction.append(lista.graph_ref)
    graph_ref = graph_node(str("names"),    [t[1],t[2],lista,t[4]]       ,childsProduction)
    addCad("**\<NAMES>** ::= "+ cadena +" '(' \<EXP_LIST> ')'  ")
    t[0] = upNodo("token", 0, 0, graph_ref)
    #####                



def p_group_clause(t):
    '''group_clause : GROUP BY PARA group_list PARC
    '''
    childsProduction  = addNotNoneChild(t,[4])
    graph_ref = graph_node(str("group_clause"),    [t[1],t[2],t[3],t[4],t[5]]       ,childsProduction)
    addCad("**\<GROUP_CLAUSE>** ::=  tGroup tBy '(' \<GROUP_LIST> ')'  ")
    t[0] = upNodo("token", 0, 0, graph_ref)
    #####

def p_group_list(t):
    '''group_list   : group_list COMA col_name
                    | col_name'''
    if len(t) == 4:
        childsProduction  = addNotNoneChild(t,[1,3])
        graph_ref = graph_node(str("group_list"),    [t[1],t[2],t[3]]       ,childsProduction)
        addCad("**\<GROUP_LIST>** ::=  \<GROUP_LIST> ','  \<COL_NAME>  ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####                
    elif len(t) == 2:
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("group_list"),    [t[1]]       ,childsProduction)
        addCad("**\<GROUP_LIST>** ::=  \<COL_NAME> ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #### 



def p_having_clause(t):
    '''having_clause    : HAVING logicExpression'''
    childsProduction  = addNotNoneChild(t,[2])
    graph_ref = graph_node(str("having_clause"),    [t[1],t[2]]       ,childsProduction)
    addCad("**\<HAVING_CLAUSE>** ::= tHaving  \<LOGICEXPRESSION> ")
    t[0] = upNodo("token", 0, 0, graph_ref)
    #### 

def p_case_clause(t):
    '''case_clause  : CASE case_inner ELSE expression
                    | CASE case_inner'''
    if len(t) == 5:
        childsProduction  = addNotNoneChild(t,[2,4])
        graph_ref = graph_node(str("case_clause"),    [t[1],t[2],t[3],t[4]]       ,childsProduction)
        addCad("**\<CASE_CLAUSE>** ::=  tCase \<CASE_INNER> tElse \<EXP>  ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####                
    elif len(t) == 3:
        childsProduction  = addNotNoneChild(t,[2])
        graph_ref = graph_node(str("case_clause"),    [t[1],t[2]]       ,childsProduction)
        addCad("**\<CASE_CLAUSE>** ::=  tCase \<CASE_INNER>  ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        ####

def p_case_inner(t):
    '''case_inner   : case_inner WHEN logicExpression THEN expression
                    | WHEN logicExpression THEN expression'''
    if len(t) == 6:
        childsProduction  = addNotNoneChild(t,[1,3,5])
        graph_ref = graph_node(str("case_inner"),    [t[1],t[2],t[3],t[4],t[5]]       ,childsProduction)
        addCad("**\<CASE_INNER>** ::=  \<CASE_INNER> tWhen \<LOGICEXPRESSION> tThen \<EXP>  ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####                
    elif len(t) == 5:
        childsProduction  = addNotNoneChild(t,[2,4])
        graph_ref = graph_node(str("case_inner"),    [t[1],t[2],t[3],t[4]]       ,childsProduction)
        addCad("**\<CASE_INNER>** ::=   tWhen \<LOGICEXPRESSION> tThen \<EXP>   ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        ####


def p_time_ops(t):
    '''time_ops :    EXTRACT PARA ops_from_ts  FECHA_HORA PARC
                |    DATE_PART PARA TEXTO COMA INTERVAL TEXTO PARC'''
    if len(t) == 6:
        childsProduction  = addNotNoneChild(t,[3])
        graph_ref = graph_node(str("time_ops"),    [t[1],t[2],t[3],t[4],t[5]]       ,childsProduction)
        addCad("**\<TIME_OPS>** ::=  tExtract '(' \<OPS_FROM_TS>  tFechaHora ')'  ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####                
    elif len(t) == 8:
        graph_ref = graph_node(str("time_ops"),    [t[1],t[2],t[3],t[4],t[5],t[6],t[7]]       ,[])
        addCad("**\<TIMES_OPS>** ::=   tDate_part '(' tText ',' tINTERVAL tText ')'   ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        ####


def p_ops_from_ts(t):
    '''ops_from_ts  : YEAR FROM TIMESTAMP
                |    HOUR FROM TIMESTAMP
                |    MINUTE FROM TIMESTAMP
                |    SECOND FROM TIMESTAMP
                |    MONTH FROM TIMESTAMP
                |    DAY FROM TIMESTAMP
    '''
    token = t.slice[1]
    cadena = str(token.type)
    graph_ref = graph_node(str("ops_from_ts"),    [t[1],t[2],t[3]]       ,[])
    addCad("**\<OPS_FROM_TS>** ::= "+ cadena +" tFrom tTimestamp  ")
    t[0] = upNodo("token", 0, 0, graph_ref)
    #####  

def p_column_list_param_opt(t):
    '''column_list_param_opt  : PARA column_list PARC
                                | empty'''    
    if len(t) == 4:
        lista=None
        childsProduction  = []
        if t[2] != None:
            lista=t[2][0]
            childsProduction.append(lista.graph_ref)
        graph_ref = graph_node(str("column_list_param_opt"), [t[1], lista, t[3]], childsProduction)
        addCad("**\<COLUMN_LIST_PARAM_OPT>** ::= '(' \<COLUMN_LIST>    ')' ")
        t[0] = upNodo(t[2], 0, 0, graph_ref)
    else: 
        t[0] = None


def p_column_list(t):
    '''column_list  : column_list COMA ID
                    | ID'''
    if len(t) == 4:
        lista=None
        childsProduction  = []
        if t[1] != None:
            lista=t[1][0]
            childsProduction.append(lista.graph_ref)
        graph_ref = graph_node(str("column_list"), [lista, t[2], t[3]], childsProduction)   
        addCad("**\<COLUMN_LIST>** ::= \<COLUMN_LIST> ',' tIdentifier ")
        token_id = t.slice[3]
        t[1][0].graph_ref=graph_ref
        t[1].append(Identifier(token_id.value, token_id.lineno, token_id.lexpos, graph_ref))
        t[0] = t[1]
    else: 
        graph_ref = graph_node(str(t[1]))
        addCad("**\<COLUMN_LIST>** ::=  tIdentifier ")
        token_id = t.slice[1]
        t[0] = [Identifier(token_id.value, token_id.lineno, token_id.lexpos, graph_ref)]


def p_stm_update(t):
    '''stm_update : UPDATE ID SET update_list where_clause
                    | UPDATE ID SET update_list'''
    token_up = t.slice[1]
    if len(t) == 6:
        lista = None
        childsProduction  = addNotNoneChild(t, [5])
        if t[4] != None:
            lista= t[4][0]
            childsProduction.append(lista.graph_ref)
        graph_ref = graph_node(str("stm_update"),    [t[1], t[2], t[3], lista, t[5]], childsProduction)
        addCad("**\<STM_UPDATE>** ::= tUpdate tIdentifier tSet \<UPDATE_LIST> \<WHERE_CLAUSE> ")
        t[0] = Update(t[2], t[4], t[5], token_up.lineno, token_up.lexpos, graph_ref)
    else: 
        lista = None
        childsProduction  = []
        if t[4] != None:
            lista= t[4][0]
            childsProduction.append(lista.graph_ref)
        graph_ref = graph_node(str("stm_update"),    [t[1], t[2], t[3], lista], childsProduction)
        addCad("**\<STM_UPDATE>** ::= tUpdate tIdentifier tSet \<UPDATE_LIST>  ")
        t[0] = Update(t[2], t[4], None, token_up.lineno, token_up.lexpos, graph_ref)

def p_update_list(t):
    '''update_list  : update_list COMA ID IGUAL logicExpression
                    | ID IGUAL logicExpression'''
    if len(t) == 6:
        token_up = t.slice[3]
        lista = None
        childsProduction  = addNotNoneChild(t,[5])
        if t[1] != None:
            lista= t[1][0]
            childsProduction.append(lista.graph_ref)
        graph_ref = graph_node(str("update_list"),    [lista, t[2], t[3], t[4], t[5]], childsProduction)
        addCad("**\<UPDATE_LIST>** ::= \<UPDATE_LIST> ',' tIdentifier '=' \<EXP_LOG> ")
        t[1][0].graph_ref=graph_ref
        t[1].append(UpdateItem(t[3], t[5], token_up.lineno, token_up.lexpos, graph_ref))
        t[0] = t[1]
    else: 
        token_up = t.slice[1]
        childsProduction  = addNotNoneChild(t,[3])
        graph_ref = graph_node(str("update_list"),    [t[1], t[2], t[3]], childsProduction)
        addCad("**\<UPDATE_LIST>** ::= tIdentifier '=' \<EXP_LOG> ")
        t[0] = [UpdateItem(t[1], t[3], token_up.lineno, token_up.lexpos, graph_ref)]


################################

def p_stm_use_db(t):
    '''stm_use_db   : USE DATABASE ID
                    | USE ID'''
    if len(t) == 4:
        tokenID = t.slice[3]
        graph_ref = graph_node(str("stm_use_db"),    [t[1],t[2],t[3]]       ,[])
        addCad("**\<STM_USE_DB>** ::= tUse tDatabase tIdentifier ")

        IDAST = Identifier(tokenID.value, tokenID.lineno, tokenID.lexpos,None)
        t[0] = UseDatabase(IDAST, t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    else:
        tokenID = t.slice[len(t)-1]
        graph_ref = graph_node(str("stm_use_db"),    [t[1],t[2]]       ,[])
        addCad("**\<STM_USE_DB>** ::= tUse tIdentifier  ")
        IDAST = Identifier(tokenID.value, tokenID.lineno, tokenID.lexpos,None)
        t[0] = UseDatabase(IDAST, t.slice[1].lineno, t.slice[1].lexpos, graph_ref)

##########   >>>>>>>>>>>>>>>>  STM_DELETE   AND  STM_ALTER  <<<<<<<<<<<<<<<<<<<<<<
def p_stm_delete(t):
    '''stm_delete   : DELETE FROM ID where_clause
                    | DELETE FROM ID'''
    token_del = t.slice[1]
    if len(t) == 5:
        childsProduction = addNotNoneChild(t, [4])
        graph_ref = graph_node(str("stm_delete"), [t[1], t[2], t[3], t[4]], childsProduction)
        addCad("**\<STM_DELETE>** ::= tDelete tFrom tIdentifier \<WHERE_CLAUSE>")
        t[0] = Delete(t[3], t[4], token_del.lineno, token_del.lexpos, graph_ref)
    else:
        childsProduction = addNotNoneChild(t, [2, 5, 6])
        graph_ref = graph_node(str("stm_delete"), [t[1], t[2], t[3]], childsProduction)
        addCad("**\<STM_DELETE>** ::= tDelete tFrom tIdentifier ")
        t[0] = Delete(t[3], None, token_del.lineno, token_del.lexpos, graph_ref)

        
def p_where_clause(t):
    '''where_clause : WHERE predicateExpression'''
    childsProduction = addNotNoneChild(t,[2])                
    graph_ref = graph_node(str("where_clause"), [t[1],t[2]]    ,childsProduction)
    addCad("**\<WHERE_CLAUSE>** ::= tWhere \<EXP_PREDICATE>")
    t[0] = Where(t[2], t.slice[1].lineno, t.slice[1].lexpos, graph_ref) 

def p_stm_create(t):
    '''stm_create   : CREATE or_replace_opt DATABASE if_not_exists_opt ID owner_opt mode_opt
                    | CREATE TABLE ID PARA tab_create_list PARC inherits_opt
                    | CREATE TYPE ID AS ENUM PARA exp_list PARC'''
    token = t.slice[1]
    tok = t.slice[3]
    if len(t) == 8 and tok.type == "DATABASE" :
        tokenID = t.slice[5]
        childsProduction = addNotNoneChild(t,[2,4,6,7])                
        graph_ref = graph_node(str("stm_create"), [t[1],t[2],t[3],t[4],t[5],t[6],t[7]]    ,childsProduction)
        addCad("**\<STM_CREATE>** ::=  tCreate \<OR_REPLACE_OPT> tDatabase tIdentifier  \<OWNER_OPT> \<MODE_OPT>")
        tvla = Identifier(tokenID.value, tokenID.lineno, tokenID.lexpos,None)         
        t[0] = CreateDatabase(tvla , None, t[7] if t[7] else 1, (True if t[2] else False) , (True if t[4] else False ), token.lineno, token.lexpos, graph_ref)       

    elif len(t) == 8:
        lista=None
        childsProduction = addNotNoneChild(t,[7])
        if t[5] != None:
            lista=t[5][0]
            childsProduction.append(lista.graph_ref)

        graph_ref = graph_node(str("stm_create"), [t[1],t[2],t[3],t[4],lista,t[6],t[7]]    ,childsProduction)
        addCad("<br><br>\n\n**\<STM_CREATE>** ::=  tCreate tTable tIdentifier '(' \<TAB_CREATE_LST> ')' \<INHERITS_OPT>")
        t[0] = CreateTable(t[3], t[7], t[5], None, token.lineno, token.lexpos, graph_ref) #TODO check if param check_exp is neceary and where we obtain that

    elif len(t) == 9:
        lista=None
        childsProduction=[]
        if t[7] != None:
            lista=t[7][0]
            childsProduction.append(lista.graph_ref)
        graph_ref = graph_node(str("stm_create"), [t[1],t[2],t[3],t[4],t[5],t[6],lista,t[8]]    ,childsProduction)
        addCad("**\<STM_CREATE>** ::=   tCreate tType tIdentifier tAs tEnum '(' \<EXP_LIST> ')' ")
        t[0] = CreateEnum(t[3], t[7], token.lineno, token.lexpos, graph_ref)
        


def p_if__not_exist_opt(t):
    '''if_not_exists_opt    : IF NOT EXISTS
                            | empty'''
    if len(t) == 4:
        graph_ref = graph_node(str(str(t[1])+" "+str(t[2])+" "+str(t[3])) ) 
        addCad("**\<IF_EXISTS_OPT>** ::= tIf tNot tExists ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####        
    else: 
        t[0]=None 


#for table columns and contrainst
def p_tab_create_list(t):
    '''tab_create_list  : tab_create_list COMA ID type nullable_opt primary_key_opt 
                        | ID type nullable_opt primary_key_opt'''
    if len(t) == 7:
        lista=None
        childsProduction = addNotNoneChild(t,[4,5,6])
        if t[1] != None:
            lista=t[1][0]
            childsProduction.append(lista.graph_ref)
        graph_ref = graph_node(str("tab_create_list"), [lista,t[2],t[3],t[4],t[5],t[6]]    ,childsProduction)
        addCad("**\<TAB_CREATE_LIST>** ::= \<TAB_CREATE_LST> ',' tIdentifier \<TYPE> \<NULLABLE_OPT> \<PRIMARY_KEY_OPT> ")
        TF = TableField(t.slice[3].value, t[4].val, t[4].max_size, t[5], (t[6] is not None) ,t.slice[3].lineno, t.slice[3].lexpos, graph_ref )
        t[1][0].graph_ref = graph_ref
        t[1].append(TF)
        t[0] = t[1]
    else:        
        childsProduction  = addNotNoneChild(t,[2,3,4])
        graph_ref = graph_node(str("tab_create__list"),    [t[1], t[2] ,t[3], t[4]]       ,childsProduction)
        addCad("**\<TAB_CREATE_LIST>** ::= tIdentifier \<TYPE> \<NULLABLE_OPT> \<PRIMARY_KEY_OPT> ")
        t[0] = [ TableField(t.slice[1].value, t[2].val, t[2].max_size, t[3], (t[4] is not None) ,t.slice[1].lineno, t.slice[1].lexpos, graph_ref )]
        
    

def p_primary_key_opt(t):
    '''primary_key_opt  : PRIMARY KEY
                        | empty'''
    if len(t) == 3:
        graph_ref = graph_node(str(t[1]+" "+t[2]))
        addCad("**\<PRIMARY_KEY_OPT>** ::= tPrimary tKey ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####       
    else:                      
        t[0] = None 



def p_nullable(t):
    '''nullable : NULL
                | NOT NULL'''    
    if len(t) == 2:
        graph_ref = graph_node(str(t[1]),[],[])
        addCad("**\<NULLABLE>** ::= tNull ")
        t[0] = Nullable(True, t.slice[1].lineno, t.slice[1].lexpos, graph_ref)        
    else:                 
        graph_ref = graph_node(str(t[1]+" "+t[2]))
        addCad("**\<NULLABLE>** ::= tNot tNull  ")        
        t[0] = Nullable(False, t.slice[1].lineno, t.slice[1].lexpos, graph_ref)

def p_nullable_opt(t):
    '''nullable_opt  : nullable
                    | empty'''
    token = t.slice[1]
    if token.type == "nullable":
        addCad("**\<NULLABLE_OPT>** ::= <NULLABLE> ")
        t[0] = t[1]
        #####        
    else:                 
        t[0] = None


def p_inherits_opt(t):
    '''inherits_opt : INHERITS PARA ID PARC
                    | empty'''
    if len(t) == 5:
        graph_ref = graph_node(str(t[1]+" "+str(t[2])+" "+str(t[3])+" "+str(t[4]) ))
        addCad("**\<INHERITS_OPT>** ::= tInherits '(' tIdentifier ')'  ")
        token = t.slice[3]
        t[0]= Identifier(token.value,token.lineno, token.lexpos,graph_ref)
    else:                 
        t[0] = None

#owner option
def p_owner_opt(t):
    '''owner_opt    : OWNER IGUAL ID
                    | OWNER IGUAL TEXTO'''
    graph_ref = graph_node(str(t[1]+" "+t[2]+" "+t[3]))
    addCad("**\<OWNER_OPT>** ::= tOwner '=' [tTexto | tIdentifier ]  ")
    tokenID = t.slice[3]
    t[0]= Identifier(tokenID.value, tokenID.lineno, tokenID.lexpos,graph_ref) 

def p_owner_opt0(t):
    '''owner_opt    : OWNER ID
                    | OWNER TEXTO'''
    tokenID = t.slice[2]
    graph_ref = graph_node(str(t[1]+" "+t[2]))
    addCad("**\<OWNER_OPT>** ::= tOwner [tTexto | tIdentifier ]  ")
    t[0]= Identifier(tokenID.value, tokenID.lineno, tokenID.lexpos,graph_ref)
    
    
def p_owner_opt1(t):
    '''owner_opt    : empty'''
    t[0]= None

#mode option
def p_mode_opt(t):
    '''mode_opt     : MODE IGUAL ENTERO'''
    tokenID = t.slice[3]
    graph_ref = graph_node(str(t[1]+" "+t[2]+" "+str(t[3])))
    addCad("**\<MODE_OPT>** ::= tMode '=' tEntero ")
    t[0]=Numeric(tokenID.value, tokenID.lineno, tokenID.lexpos, graph_ref)

def p_mode_opt1(t):
    '''mode_opt     : MODE ENTERO'''
    tokenID = t.slice[2]
    graph_ref = graph_node(str(t[1]+" "+str(t[2]) ) )
    addCad("**\<MODE_OPT>** ::= tMode  tEntero ")
    t[0]=Numeric(tokenID.value, tokenID.lineno, tokenID.lexpos, graph_ref)

def p_mode_opt2(t):
    '''mode_opt     : empty'''
    t[0] = None


#Replace OPTION
def p_or_replace_opt(t):
    '''or_replace_opt   : OR REPLACE
                        | empty'''
    if len(t) == 3:
        graph_ref = graph_node(str(t[1]+" "+t[2]))
        addCad("**\<OR_REPLACE_OPT>** ::= tOr tReplace ")        
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####        
    else:                 
        t[0] = None


def p_stm_alter(t):
    '''stm_alter    :    ALTER DATABASE ID RENAME TO ID    
                    |    ALTER DATABASE ID OWNER TO db_owner
'''
    token_alter = t.slice[4]
    if token_alter.type == "RENAME":
        graph_ref = graph_node(str("stm_alter"), [t[1], t[2], t[3], t[4], t[5], t[6]], [])
        addCad("**\<STM_ALTER>** ::=  tAlter tDatabase tIdentifier tRename tTo tIdentifier        ")
        t[0] = AlterDatabaseRename(t[3], t[6], token_alter.lineno, token_alter.lexpos, graph_ref)
    if token_alter.type == "OWNER":
        childsProduction = addNotNoneChild(t,[6])                
        graph_ref = graph_node(str("stm_alter"), [t[1], t[2], t[3], t[4], t[5], t[6]], childsProduction)
        addCad("**\<STM_ALTER>** ::=  tAlter tDatabase tIdentifier tOwner tTo \<DB_OWNER>        ")
        t[0] = AlterDatabaseOwner(t[3], t[6], token_alter.lineno, token_alter.lexpos, graph_ref)


def p_stm_alter0(t):
    '''stm_alter    :    ALTER TABLE ID DROP CONSTRAINT ID
                    |    ALTER TABLE ID DROP COLUMN ID
'''
    token_alter = t.slice[5]
    if token_alter.type == "CONSTRAINT":
        graph_ref = graph_node(str("stm_alter"), [t[1], t[2], t[3], t[4], t[5], t[6]], [])
        addCad("**\<STM_ALTER>** ::=  tAlter tTable tIdentifier tDrop tIdentifier        ")
        t[0] = upNodo("token", 0, 0, graph_ref)
    if token_alter.type == "COLUMN":
        graph_ref = graph_node(str("stm_alter"), [t[1], t[2], t[3], t[4], t[5], t[6]], [])
        addCad("**\<STM_ALTER>** ::=  tAlter tTable tIdentifier tDrop  tColumn tIdentifier   ")
        t[0] = AlterTableDropColumn(t[3], t[6], token_alter.lineno, token_alter.lexpos, graph_ref)


def p_stm_alter1(t):
    '''stm_alter    :    ALTER TABLE ID ADD COLUMN ID type nullable_opt
                    |    ALTER TABLE ID ADD CHECK PARA logicExpression PARC
                    |    ALTER TABLE ID ALTER COLUMN ID TYPE type param_int_opt
'''
    token_alter = t.slice[6]
    if token_alter.type == "ID" and t[7] != 'TYPE':
        childsProduction = addNotNoneChild(t, [7, 8])
        graph_ref = graph_node(str("stm_alter"), [t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8]], childsProduction)
        addCad("**\<STM_ALTER>** ::=  tAlter tTable tIdentifier tAdd tColumn  tIdentifier \<TYPE> \<PARAM_INT_OPT>   ")
        t[0] = AlterTableAddColumn(t[3], t[6], t[7], t[7].max_size, t[8], token_alter.lineno, token_alter.lexpos, graph_ref)
    if token_alter.type == "PARA":
        childsProduction = addNotNoneChild(t,[7])                
        graph_ref = graph_node(str("stm_alter"), [t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8]], childsProduction)
        addCad("**\<STM_ALTER>** ::=  tAlter tTable tIdentifier tAdd tCheck '('  \<EXP_LOG> ')'   ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####  
    if token_alter.type == "ID":
        childsProduction = addNotNoneChild(t, [8, 9])
        graph_ref = graph_node(str("stm_alter"), [t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8],t[9]], childsProduction)
        addCad("**\<STM_ALTER>** ::=  tAlter tTable tIdentifier tAlter tColumn tType \<TYPE> \<PARAM_INT_OPT>   ")
        t[0] = AlterTableChangeColumnType(t[3], t[6], t[8], t[8].max_size, token_alter.lineno, token_alter.lexpos, graph_ref)


def p_stm_alter2(t):
    '''stm_alter    :    ALTER TABLE ID RENAME COLUMN ID TO ID
                    |    ALTER TABLE ID ALTER COLUMN ID SET NULL
                    |    ALTER TABLE ID ALTER COLUMN ID SET NOT NULL 
                    |    ALTER TABLE ID ADD CONSTRAINT ID UNIQUE PARA ID PARC
                    |    ALTER TABLE ID ADD FOREIGN KEY PARA ID PARC REFERENCES ID 
'''
    token_alter = t.slice[1]
    if len(t) == 9 and t[4] == 'RENAME':
        graph_ref = graph_node(str("stm_alter"), [t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8]], [])
        addCad("**\<STM_ALTER>** ::=  tAlter tTable tIdentifier tRename tColumn tIdentifier tTo tIdentifier     ")
        t[0] = AlterTableRenameColumn(t[3], t[6], t[8], token_alter.lineno, token_alter.lexpos, graph_ref)
    elif len(t) == 9 and t[4] == 'ALTER':
        graph_ref = graph_node(str("stm_alter"), [t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8]], [])
        addCad("**\<STM_ALTER>** ::=  tAlter tTable tIdentifier tAlter tColumn tIdentifier tSet tNull     ")
        t[0] = AlterTableNotNull(t[3], t[6], True, token_alter.lineno, token_alter.lexpos, graph_ref)
    elif len(t) == 10:         
        graph_ref = graph_node(str("stm_alter"), [t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8], t[9]], [])
        addCad("**\<STM_ALTER>** ::=  tAlter tTable tIdentifier tAlter tColumn tIdentifier tSet tNot tNull     ")
        t[0] = AlterTableNotNull(t[3], t[6], False, token_alter.lineno, token_alter.lexpos, graph_ref)
    elif len(t) == 11:
        graph_ref = graph_node(str("stm_alter"), [t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8], t[9], t[10]], [])
        addCad("**\<STM_ALTER>** ::=  tAlter tTable tIdentifier tAdd tConstraint tIdentifier tUnique '(' tIdentifier ')'    ")
        t[0] = upNodo("token", 0, 0, graph_ref)
    elif len(t) == 12:
        graph_ref = graph_node(str("stm_alter"), [t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8], t[9], t[10], t[11]], [])
        addCad("**\<STM_ALTER>** ::=  tAlter tTable tIdentifier tAdd  tForeign  tKey '(' tIdentifier ')' tReference tIdentifier ")
        t[0] = upNodo("token", 0, 0, graph_ref)


def p_param_int_opt(t):
    '''param_int_opt  : PARA ENTERO PARC
                | empty''' 
    if len(t) == 4:
        graph_ref = graph_node(str(t[1]+" "+t[2]+" "+t[3] ))
        addCad("**\<PARAM_INT_OPT>** ::= '(' tEntero ')' ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####        
    else:                 
        t[0] = None


def p_db_owner(t):
    ''' db_owner    : ID
                    | CURRENT_USER
                    | SESSION_USER'''
    token_owner = t.slice[1]
    if token_owner.type == "ID":
        graph_ref = graph_node(str(t[1]))
        addCad("**\<DB_OWNER>** ::= tTexto ")
        t[0] = Identifier(t[1], token_owner.lineno, token_owner.lexpos, graph_ref)
    elif token_owner.type == "CURRENT_USER":
        graph_ref = graph_node(str(t[1]))
        addCad("**\<DB_OWNER>** ::= tCurrentUser ")
        t[0] = Identifier(token_owner.value, token_owner.lineno, token_owner.lexpos, graph_ref)
    elif token_owner.type == "SESSION_USER":
        graph_ref = graph_node(str(t[1]))
        addCad("**\<DB_OWNER>** ::= tSessionUser ")
        t[0] = Identifier(token_owner.value, token_owner.lineno, token_owner.lexpos, graph_ref)


def p_stm_drop(t):
    '''stm_drop : DROP DATABASE if_exists_opt ID
                | DROP TABLE ID'''
    token = t.slice[1]
    if len(t) == 5:
        tokenID = t.slice[4]
        childsProduction  = addNotNoneChild(t,[3])
        graph_ref = graph_node(str("stm_drop"),    [t[1], t[2] ,t[3], t[4]]       ,childsProduction)
        addCad("**\<STM_DROP>** ::=  tDrop tDatabase \<IF_EXISTS_OPT> tIdentifier")
        name_db = Identifier(tokenID.value, tokenID.lineno, tokenID.lexpos,None)
        t[0] = DropDatabase(name_db , (True if t[3] else False), token.lineno, token.lexpos, graph_ref)
        #####        
    else:
        tokenID = t.slice[3]
        graph_ref = graph_node(str("stm_drop"),    [t[1], t[2] ,t[3]]       ,[])
        addCad("**\<STM_DROP>** ::= tDrop tTable tIdentifier  ")
        name_db = Identifier(tokenID.value, tokenID.lineno, tokenID.lexpos,None)
        t[0] = DropTable(name_db, token.lineno, token.lexpos, graph_ref)
        #####  

def p_if_exist_opt(t):
    '''if_exists_opt    : IF EXISTS
                        | empty'''
    if len(t) == 3:
        graph_ref = graph_node(str(str(t[1])+" "+str(t[2])) )
        addCad("**\<IF_EXISTS_OPT>** ::= tIf tExists ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####        
    else: 
        t[0]=None 

#############################

def p_type(t):
    ''' type    : SMALLINT
                | INTEGER                
                | BIGINT
                | DECIMAL
                | NUMERIC
                | REAL
                | DOUBLE PRECISION
                | MONEY
                | CARACTER VARYING
                | VARCHAR PARA ENTERO PARC
                | CHARACTER
                | CHAR PARA ENTERO PARC
                | TEXT
                | TIMESTAMP
                | DATE
                | TIME
                | INTERVAL
                | BOOLEAN
                | ID'''
    token = t.slice[1]

    if token.type == "DOUBLE":
        graph_ref = graph_node(str(str(t[1])+" "+str(t[2])))
        addCad("**\<TYPE>** ::= DOUBLE PRECISION ")
        t[0] = TypeDef(token.type, None, None, token.lineno, token.lexpos)        

    elif (token.type == "CARACTER" or token.type == "CHAR")and  len(t) == 3:
        graph_ref = graph_node(str(str(t[1])+" "+str(t[2])))
        addCad("**\<TYPE>** ::= CARACTER VARYING")
        t[0] = TypeDef(token.type, 0, t[3], token.lineno, token.lexpos, graph_ref)

    elif token.type == "ID":
        graph_ref = graph_node(str(t[1]))
        addCad("**\<TYPE>** ::= " + str(token.value).upper())
        t[0] = TypeDef(str(token.value).upper(), None, None, token.lineno, token.lexpos, graph_ref)

    else:
        graph_ref = graph_node(str(t[1]))
        addCad("**\<TYPE>** ::= "+str(token.type))
        t[0] = TypeDef(token.type, None, None, token.lineno, token.lexpos, graph_ref)
    
######################

def p_time(t):
    ''' time    : YEAR
                | MONTH
                | DAY
                | HOUR
                | MINUTE
                | SECOND'''
    graph_ref = graph_node(str(t[1]))
    addCad("**\<TIME>** ::= "+str(token.type))
    t[0] = upNodo("token", 0, 0, graph_ref)
    ##

##############################
def p_not_opt(t):
    '''not_opt       : NOT
                    | empty'''
    token = t.slice[1]
    if token.type == "NOT":
        graph_ref = graph_node( str(t[1])  )
        addCad("**\<NOT_OPT>** ::= tNot ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####        
    else: 
        t[0]=None 


##################

def p_percentopt(t):
    '''percentopt   : PORCENTAJE
                    | empty'''

    token = t.slice[1]
    if token.type == "PORCENTAJE":
        graph_ref = graph_node( str(t[1])  )
        addCad("**\<PERCENTOPT>** ::=  '%' ")
        t[0] = upNodo("token", 0, 0, graph_ref)
        #####        
    else: 
        t[0]=None 




def p_stm_show0(t):
    '''stm_show     : SHOW DATABASES
                    | SHOW DATABASES LIKE TEXTO
                    | SHOW DATABASES LIKE PATTERN_LIKE'''
    token = t.slice[1]
    if len(t) == 3:
        graph_ref = graph_node(str("stm_show"), [t[1],t[2]]    ,[])
        addCad("**\<STM_SHOW>** ::= tShow tDatabases ")        
        t[0] = ShowDatabases(None, token.lineno, token.lexpos, graph_ref)
    else:
        graph_ref = graph_node(str("stm_show"), [t[1],t[2],t[3],t[4]]    ,[])
        addCad("**\<STM_SHOW>** ::= tShow tDatabases ")        
        t[0] = ShowDatabases(None, token.lineno, token.lexpos, graph_ref)

def p_exp_list(t):
    '''exp_list : exp_list COMA expression'''
    lista=None
    childsProduction = addNotNoneChild(t,[3])
    if t[1] != None:
        lista=t[1][0]
        childsProduction.append(lista.graph_ref)
    graph_ref = graph_node(str("exp_list"), [lista,t[2],t[3]]    ,childsProduction)
    addCad("**\<EXP_LIST>** ::= <EXP_LIST> ',' \<EXP_LIST>  ")
    t[1][0].graph_ref = graph_ref
    t[1].append(t[3])
    t[0] = t[1]


def p_exp_list0(t):    
    '''exp_list : expression'''    
    t[0] = [t[1]]

########## Definition of opttional productions, who could reduce to 'empty' (epsilon) ################
# def p_not_opt(t):
#    '''not_opt : NOT
#               | empty'''
########## Definition of Relational expressions ##############                        
def p_relExpression(t):
    '''relExpression    : expression MENOR expression 
                        | expression MAYOR  expression
                        | expression IGUAL  expression
                        | expression MENORQ expression
                        | expression MAYORQ expression
                        | expression DIFERENTE expression
                        | expression NOT LIKE TEXTO
                        | expression LIKE TEXTO
                        | expression NOT LIKE PATTERN_LIKE
                        | expression LIKE PATTERN_LIKE'''
    token = t.slice[2]
    if token.type == "MENOR":
        childsProduction  = addNotNoneChild(t,[1,3])
        graph_ref = graph_node(str("EXP_REL"),    [t[1], t[2] ,t[3]]       ,childsProduction)
        addCad("**\<EXP_REL>** ::=  \<EXP> '\<' \<EXP> ")
        t[0] = RelationalExpression(t[1], t[3], OpRelational.LESS, 0, 0, graph_ref)
    elif token.type == "MAYOR":
        childsProduction  = addNotNoneChild(t,[1,3])
        graph_ref = graph_node(str("EXP_REL"),    [t[1], t[2] ,t[3]]       ,childsProduction)
        addCad("**\<EXP_REL>** ::=  \<EXP> '>' \<EXP> ")
        t[0] = RelationalExpression(t[1], t[3], OpRelational.GREATER, 0, 0, graph_ref)
    elif token.type == "IGUAL":
        childsProduction  = addNotNoneChild(t,[1,3])
        graph_ref = graph_node(str("EXP_REL"),    [t[1], t[2] ,t[3]]       ,childsProduction)
        addCad("**\<EXP_REL>** ::=  \<EXP> '=' \<EXP> ")
        t[0] = RelationalExpression(t[1], t[3], OpRelational.EQUALS, 0, 0, graph_ref)
    elif token.type == "MENORQ":
        childsProduction  = addNotNoneChild(t,[1,3])
        graph_ref = graph_node(str("EXP_REL"),    [t[1], t[2] ,t[3]]       ,childsProduction)
        addCad("**\<EXP_REL>** ::=  \<EXP> '\<=' \<EXP> ")
        t[0] = RelationalExpression(t[1], t[3], OpRelational.LESS_EQUALS, 0, 0, graph_ref)
    elif token.type == "MAYORQ":
        childsProduction  = addNotNoneChild(t,[1,3])
        graph_ref = graph_node(str("EXP_REL"),    [t[1], t[2] ,t[3]]       ,childsProduction)
        addCad("**\<EXP_REL>** ::=  \<EXP> '>=' \<EXP> ")
        t[0] = RelationalExpression(t[1], t[3], OpRelational.GREATER_EQUALS, 0, 0, graph_ref)
    elif token.type == "DIFERENTE":
        childsProduction  = addNotNoneChild(t,[1,3])
        graph_ref = graph_node(str("EXP_REL"),    [t[1], t[2] ,t[3]]       ,childsProduction)
        addCad("**\<EXP_REL>** ::=  \<EXP> '!=' \<EXP> ")
        t[0] = RelationalExpression(t[1], t[3], OpRelational.NOT_EQUALS, 0, 0, graph_ref)
    elif token.type == "NOT":
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("EXP_REL"),    [t[1], t[2] ,t[3]]       ,childsProduction)
        addCad("**\<EXP_REL>** ::=  \<EXP> tNot tLike [tTexto|False|True] ")
        t[0] = RelationalExpression(t[1], t[4], OpRelational.NOT_LIKE, 0, 0, graph_ref)
    elif token.type == "LIKE":
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("EXP_REL"),    [t[1], t[2] ,t[3]]       ,childsProduction)
        addCad("**\<EXP_REL>** ::=  \<EXP> tLike [tTexto|False|True] ")
        t[0] = RelationalExpression(t[1], t[3], OpRelational.LIKE, 0, 0, graph_ref)
    else:
        print("Missing code from: ", t.slice)


def p_relExpReducExp(t):
    '''relExpression    : expression'''
    t[0] = t[1]
    addCad("**\<EXP_REL>** ::=  \<EXP>")


########## Definition of logical expressions ##############
def p_predicateExpression(t):
    '''predicateExpression  : BETWEEN expression AND expression'''
    token = t.slice[1]
    childsProduction  = addNotNoneChild(t,[2,4])
    graph_ref = graph_node(str("EXP_PREDICATE"),    [t[1], t[2] ,t[3], t[4]]       ,childsProduction)
    addCad("**\<EXP_PREDICATE>** ::= tBetween \<EXP>  tAnd \<EXP>   ")
    t[0] = PredicateExpression(t[2], t[4], OpPredicate.BETWEEN, token.lineno, token.lexpos,graph_ref)

def p_predicateExpression0(t):
    '''predicateExpression  : logicExpression'''
    t[0] = t[1]

def p_predicateExpression3(t):
    '''predicateExpression  : logicExpression BETWEEN expression AND expression'''
    token = t.slice[2]
    childsProduction  = addNotNoneChild(t,[1,3,5])
    graph_ref = graph_node(str("EXP_PREDICATE"),    [t[1], t[2] ,t[3], t[4],t[5]]       ,childsProduction)
    addCad("**\<EXP_PREDICATE>** ::=  \<EXP_LOG> tBetween \<EXP>  tAnd \<EXP>   ")
    t[0] = PredicateExpression(t[3], t[5], OpPredicate.BETWEEN, token.lineno, token.lexpos,graph_ref)



def p_predicateExpression1(t):
    '''predicateExpression  : expression IS NULL
                            | expression IS DISTINCT FROM expression
                            | expression IS BOOLEAN_VALUE 
                            | expression IS UNKNOWN   '''
    token = t.slice[3]
    if token.type == "NULL":
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("EXP_PREDICATE"),    [t[1], t[2] ,t[3]]       ,childsProduction)
        addCad("**\<EXP_PREDICATE>** ::= tIs tNull  ")
        t[0] = PredicateExpression(t[1], None, OpPredicate.NULL,  token.lineno, token.lexpos,graph_ref)
    elif token.type == "DISTINCT":
        childsProduction  = addNotNoneChild(t,[1,5])
        graph_ref = graph_node(str("EXP_PREDICATE"),    [t[1], t[2] ,t[3],t[4],t[5]]       ,childsProduction)
        addCad("**\<EXP_PREDICATE>** ::=   \<EXP> tIs tDisctint tFrom \<EXP>  ")
        t[0] = PredicateExpression(t[1], t[5], OpPredicate.DISTINCT,  token.lineno, token.lexpos,graph_ref)
    elif token.type == "BOOLEAN_VALUE":
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("EXP_PREDICATE"),    [t[1], t[2] ,t[3]]       ,childsProduction)
        addCad("**\<EXP_PREDICATE>** ::=   <EXP> tIs [tTrue|tFalse] \<EXP> ")      
        if bool(t[3]):
            t[0] = PredicateExpression(t[1], None, OpPredicate.TRUE, token.lineno, token.lexpos,graph_ref)
        else:
            t[0] = PredicateExpression(t[1], None, OpPredicate.FALSE, token.lineno, token.lexpos,graph_ref)
    elif token.type == "UNKNOWN":
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("EXP_PREDICATE"),    [t[1], t[2] ,t[3]]       ,childsProduction)
        addCad("**\<EXP_PREDICATE>** ::=   \<EXP> tIs  tUnknown  \<EXP>  ")  
        t[0] = PredicateExpression(t[1], None, OpPredicate.UNKNOWN, token.lineno, token.lexpos,graph_ref)

def p_predicateExpression2(t):
    '''predicateExpression  : expression IS NOT NULL
                            | expression IS NOT DISTINCT FROM expression
                            | expression IS NOT BOOLEAN_VALUE 
                            | expression IS NOT UNKNOWN   '''

    token = t.slice[4]
    if token.type == "NULL":
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("EXP_PREDICATE"),    [t[1], t[2] ,t[3],t[4]]       ,childsProduction)
        addCad("**\<EXP_PREDICATE>** ::= tIs tNull  ")
        t[0] = PredicateExpression(t[1], None, OpPredicate.NOT_NULL,  token.lineno, token.lexpos,graph_ref)

    elif token.type == "DISTINCT":
        childsProduction  = addNotNoneChild(t,[1,6])
        graph_ref = graph_node(str("EXP_PREDICATE"),    [t[1], t[2] ,t[3],t[4],t[5],t[6]]       ,childsProduction)
        addCad("**\<EXP_PREDICATE>** ::=   \<EXP> tIs tDisctint tFrom \<EXP>  ")
        t[0] = PredicateExpression(t[1], t[6], OpPredicate.NOT_DISTINCT,  token.lineno, token.lexpos,graph_ref)

    elif token.type == "BOOLEAN_VALUE":
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("EXP_PREDICATE"),    [t[1], t[2] ,t[3],t[4]]       ,childsProduction)
        addCad("**\<EXP_PREDICATE>** ::=   <EXP> tIs [tTrue|tFalse] \<EXP> ")      
        if bool(t[4]):
            pass
            t[0] = PredicateExpression(t[1], None, OpPredicate.NOT_TRUE, token.lineno, token.lexpos,graph_ref)
        else:
            pass
            t[0] = PredicateExpression(t[1], None, OpPredicate.NOT_FALSE, token.lineno, token.lexpos,graph_ref)
    elif token.type == "UNKNOWN":
        childsProduction  = addNotNoneChild(t,[1])
        graph_ref = graph_node(str("EXP_PREDICATE"),    [t[1], t[2] ,t[3],t[4]]       ,childsProduction)
        addCad("**\<EXP_PREDICATE>** ::=   \<EXP> tIs  tUnknown  \<EXP>  ")  
        t[0] = PredicateExpression(t[1], None, OpPredicate.NOT_UNKNOWN, token.lineno, token.lexpos,graph_ref)



def p_logicExpression(t):
    '''logicExpression  : relExpression'''
    t[0] = t[1]
    addCad("**\<EXP_LOG>** ::= \<EXP_REL> ")
    
def p_logicNotExpression(t):
    '''logicExpression  : NOT logicExpression'''
    token = t.slice[1]
    childsProduction = addNotNoneChild(t,[2])                
    graph_ref = graph_node(str(t[1]), [t[2]]    ,childsProduction)
    addCad("**\<EXP_LOG>** ::= \<EXP_LOG> tNot \<EXP_LOG> ")    
    t[0] = Negation(t[2],token.lineno,token.lexpos,graph_ref)

def p_binLogicExpression(t):     
    '''logicExpression  : logicExpression AND logicExpression
                        | logicExpression OR  logicExpression
                        '''    
    token = t.slice[2]
    if token.type == "AND":
        childsProduction = addNotNoneChild(t,[1,3])                
        graph_ref = graph_node(str(t[2]), [t[1],t[3]]    ,childsProduction)
        addCad("**\<EXP_LOG>** ::= \<EXP_LOG> tAnd \<EXP_LOG> ")
        t[0] = BoolExpression(t[1],t[3],OpLogic.AND,token.lineno,token.lexpos,graph_ref)
    elif token.type == "OR":
        childsProduction = addNotNoneChild(t,[1,3])                
        graph_ref = graph_node(str(t[2]), [t[1],t[3]]    ,childsProduction)
        addCad("**\<EXP_LOG>** ::= \<EXP_LOG> tOr \<EXP_LOG> ")
        t[0] = BoolExpression(t[1],t[3],OpLogic.OR,token.lineno,token.lexpos,graph_ref)
    else:
        print("Missing code for: ",token.type)

########## Defintions of produtions for expression :== ##############
def p_expression(t):
    ''' expression  : expression MAS expression
                    | expression MENOS expression
                    | expression POR expression
                    | expression DIAGONAL expression
                    | expression PORCENTAJE expression
                    | expression EXPONENCIANCION expression                    
                    '''
    if t[2] == '+':
        childsProduction = addNotNoneChild(t,[1,3])                
        graph_ref = graph_node(str(t[2]), [t[1],t[3]]    ,childsProduction)
        addCad("**\<EXP>** ::= \<EXP>  '+' \<EXP> ")
        t[0] = BinaryExpression(t[1], t[3], OpArithmetic.PLUS, 0, 0, graph_ref)
    elif t[2] == '-':
        childsProduction = addNotNoneChild(t,[1,3])                
        graph_ref = graph_node(str(t[2]), [t[1],t[3]]    ,childsProduction)
        addCad("**\<EXP>** ::= \<EXP>  '-' \<EXP> ")
        t[0] = BinaryExpression(t[1], t[3], OpArithmetic.MINUS, 0, 0, graph_ref)
    elif t[2] == '*':
        childsProduction = addNotNoneChild(t,[1,3])                
        graph_ref = graph_node(str(t[2]), [t[1],t[3]]    ,childsProduction)
        addCad("**\<EXP>** ::= \<EXP>  '*' \<EXP> ")
        t[0] = BinaryExpression(t[1], t[3], OpArithmetic.TIMES, 0, 0, graph_ref)
    elif t[2] == '/':
        childsProduction = addNotNoneChild(t,[1,3])                
        graph_ref = graph_node(str(t[2]), [t[1],t[3]]    ,childsProduction)
        addCad("**\<EXP>** ::= \<EXP>  '/' \<EXP> ")
        t[0] = BinaryExpression(t[1], t[3], OpArithmetic.DIVIDE, 0, 0, graph_ref)
    elif t[2] == '%':
        childsProduction = addNotNoneChild(t,[1,3])                
        graph_ref = graph_node(str(t[2]), [t[1],t[3]]    ,childsProduction)
        addCad("**\<EXP>** ::= \<EXP>  '%' \<EXP> ")
        t[0] = BinaryExpression(t[1], t[3], OpArithmetic.MODULE, 0, 0, graph_ref)
    elif t[2] == '^':
        childsProduction = addNotNoneChild(t,[1,3])                
        graph_ref = graph_node(str(t[2]), [t[1],t[3]]    ,childsProduction)
        addCad("**\<EXP>** ::= \<EXP>  '^' \<EXP> ")
        t[0] = BinaryExpression(t[1], t[3], OpArithmetic.POWER, 0, 0, graph_ref)
    else:
        print("You forgot wirte code for the operator: ", t[2])


def p_expNotExp(t):
    '''expression   : NOT expression'''
    token = t.slice[1]
    addCad("**\<EXP>** ::=  tNot \<EXP>  ")
    childsProduction = addNotNoneChild(t,[2])                
    graph_ref = graph_node(str(t[1]), [t[2]]    ,childsProduction)
    t[0] = Negation(t[1],token.lineno,token.lexpos, graph_ref)

def p_expPerenteLogic(t):
    '''expression   : PARA logicExpression PARC'''
    t[0] = t[2]
    addCad("**\<EXP>** ::=   '(' \<EXP_LOG> ')'            ")
    
def p_trigonometric(t):
    ''' expression  :   ACOS PARA expression PARC
                    |   ACOSD PARA expression PARC
                    |   ASIN PARA expression PARC
                    |   ASIND PARA expression PARC
                    |   ATAN PARA expression PARC
                    |   ATAND PARA expression PARC
                    |   ATAN2 PARA expression COMA expression PARC
                    |   ATAN2D PARA expression COMA expression PARC
                    |   COS PARA expression PARC
                    |   COSD PARA expression PARC
                    |   COT PARA expression PARC
                    |   COTD PARA expression PARC
                    |   SIN PARA expression PARC
                    |   SIND PARA expression PARC
                    |   TAN PARA expression PARC
                    |   TAND PARA expression PARC
                    |   SINH PARA expression PARC
                    |   COSH PARA expression PARC
                    |   TANH PARA expression PARC
                    |   ASINH PARA expression PARC
                    |   ACOSH PARA expression PARC
                    |   ATANH PARA expression PARC'''

    if t.slice[1].type == 'ACOS':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tAcos '(' \<EXP> ')' ")
        t[0] = Acos(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'ACOSD':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tAcosd '(' \<EXP> ')' ")
        t[0] = Acosd(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'ASIN':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tAsin '(' \<EXP> ')' ")
        t[0] = Asin(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'ASIND':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tAsind '(' \<EXP> ')' ")
        t[0] = Asind(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'ATAN':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tAtan '(' \<EXP> ')' ")                 
        t[0] = Atan(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'ATAND':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tAtand '(' \<EXP> ')' ")
        t[0] = Atand(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'ATAN2':
        childsProduction = addNotNoneChild(t,[3,5])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4],t[5],t[6]]    ,childsProduction)
        addCad("**\<EXP>** ::= tAtan2 '(' \<EXP> ',' \<EXP> ')' ")
        t[0] = Atan2(t[3], t[5], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'ATAN2D':
        childsProduction = addNotNoneChild(t,[3,5])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4],t[5],t[6]]    ,childsProduction)
        addCad("**\<EXP>** ::= tAtand2 '(' \<EXP> ',' \<EXP> ')' ")
        t[0] = Atan2d(t[3], t[5], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'COS':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tCos '(' \<EXP> ')' ")    
        t[0] = Cos(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'COSD':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tCosd '(' \<EXP> ')' ")
        t[0] = Cosd(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'COT':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tCot '(' \<EXP> ')' ")
        t[0] = Cot(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'COTD':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tCotd '(' \<EXP> ')' ")
        t[0] = Cotd(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'SIN':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tSin '(' \<EXP> ')' ")
        t[0] = Sin(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'SIND':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tSind '(' \<EXP> ')' ")
        t[0] = Sind(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'TAN':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tTan '(' \<EXP> ')' ")
        t[0] = Tan(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'TAND':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tTand '(' \<EXP> ')' ")
        t[0] = Tand(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'SINH':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tSinh '(' \<EXP> ')' ")
        t[0] = Sinh(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'COSH':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tCosh '(' \<EXP> ')' ")
        t[0] = Cosh(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'TANH':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tTanh '(' \<EXP> ')' ")
        t[0] = Tanh(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'ASINH':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tAsinh '(' \<EXP> ')' ")
        t[0] = Asinh(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'ACOSH':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tAcosh '(' \<EXP> ')' ")
        t[0] = Acosh(t[3], t.slice[1].lineno, t.slice[1].lexpos, graph_ref)
    elif t.slice[1].type == 'ATANH':
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::= tAtanh '(' \<EXP> ')' ")
        t[0] = Atanh(t[3], token.lineno, token.lexpos, graph_ref)


def p_aritmetic(t):
    '''expression   : ABS PARA expression PARC            
                    | CBRT PARA expression PARC
                    | CEIL PARA expression PARC
                    | CEILING PARA expression PARC
                    | DEGREES PARA expression PARC
                    | DIV PARA expression COMA expression PARC
                    | EXP PARA expression PARC
                    | FACTORIAL PARA expression  PARC 
                    | FLOOR PARA expression  PARC
                    | GCD PARA expression COMA expression PARC
                    | LCM PARA expression COMA expression PARC
                    | LN PARA expression PARC                    
                    | LOG PARA expression PARC
                    | LOG10 PARA expression PARC
                    | MIN_SCALE PARA expression PARC
                    | MOD PARA expression COMA expression PARC
                    | PI PARA PARC
                    | POWER PARA expression COMA expression PARC
                    | RADIANS PARA expression PARC                    
                    | ROUND PARA expression PARC
                    | ROUND PARA expression COMA expression PARC
                    | SCALE PARA expression PARC
                    | SIGN PARA expression PARC
                    | SQRT PARA expression PARC
                    | TRIM_SCALE PARA expression PARC
                    | WIDTH_BUCKET PARA expression COMA expression COMA expression COMA expression PARC
                    | RANDOM PARA PARC
                    | SETSEED PARA expression PARC
                    | TRUNC PARA expression PARC
                '''
    token = t.slice[1]
    if token.type == "ABS":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=  tAbs '(' \<EXP> ')' ")
        t[0] = Abs(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "CBRT":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=  tCbrt '(' \<EXP> ')'        ")
        t[0] = Cbrt(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "CEIL" or token.type == "CEILING":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=   [tCeil | tCeiling ] '(' \<EXP> ')'        ")
        t[0] = Ceil(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "DEGREES":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=    tDegrees '(' \<EXP> ')'        ")
        t[0] = Degrees(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "DIV":
        childsProduction = addNotNoneChild(t,[3,5])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4],t[5],t[6]]    ,childsProduction)
        addCad("**\<EXP>** ::=    tDiv '(' \<EXP> ','\<EXP> ')'     ")
        t[0] = Div(t[3], t[5], token.lineno, token.lexpos, graph_ref)
    elif token.type == "EXP":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=   tExp '(' \<EXP>  ')'      ")
        t[0] = Exp(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "FACTORIAL":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=  tFactorial '(' \<EXP>  ')'        ")
        t[0] = Factorial(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "FLOOR":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=   tFloor '(' \<EXP>  ')'      ")
        t[0] = Floor(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "GCD":
        childsProduction = addNotNoneChild(t,[3,5])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4],t[5],t[6]]    ,childsProduction)
        addCad("**\<EXP>** ::=   tGcd '(' \<EXP> ','\<EXP> ')'      ")
        t[0] = Gcd(t[3], t[5], token.lineno, token.lexpos, graph_ref)
        ###
    elif token.type == "LCM":
        childsProduction = addNotNoneChild(t,[3,5])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4],t[5],t[6]]    ,childsProduction)
        addCad("**\<EXP>** ::=  tLcm '(' \<EXP> ','\<EXP> ')'       ")
        t[0] = Lcm(t[3], t[5], token.lineno, token.lexpos, graph_ref)
    elif token.type == "LN":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=    tLn '(' \<EXP> ')'     ")
        t[0] = Ln(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "LOG":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=  tLog '(' \<EXP> ')'        ")
        t[0] = Log(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "LOG10":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=   tLog10 '(' \<EXP> ')'      ")
        t[0] = Log10(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "MIN_SCALE":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=  tMinscale '(' \<EXP> ')'       ")
        t[0] = MinScale(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "MOD":
        childsProduction = addNotNoneChild(t,[3,5])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4],t[5],t[6]]    ,childsProduction)
        addCad("**\<EXP>** ::=   tMod '(' \<EXP> ','\<EXP> ')'       ")
        t[0] = Mod(t[3], t[5], token.lineno, token.lexpos, graph_ref)
    elif token.type == "PI":
                     
        graph_ref = graph_node(str(str(t[1])+" "+str(t[2])+" "+str(t[3])) )
        addCad("**\<EXP>** ::=    tPi '()'     ")
        t[0] = PI(token.lineno, token.lexpos, graph_ref)
    elif token.type == "POWER":
        childsProduction = addNotNoneChild(t,[3,5])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4],t[5],t[6]]    ,childsProduction)
        addCad("**\<EXP>** ::=   tPower '(' \<EXP> ','\<EXP> ')'      ")
        t[0] = Power(t[3], t[5], token.lineno, token.lexpos, graph_ref)
    elif token.type == "RADIANS":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=   tRadians '(' \<EXP> ')'      ")
        t[0] = Radians(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "ROUND":
        if len(t) == 5:
            childsProduction = addNotNoneChild(t,[3])                
            graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
            addCad("**\<EXP>** ::=   tRound '(' \<EXP> ')'      ")
            t[0] = Round(t[3], 0, token.lineno, token.lexpos, graph_ref)
        else:
            childsProduction = addNotNoneChild(t,[3,5])                
            graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4],t[5],t[6]]    ,childsProduction)
            addCad("**\<EXP>** ::=   tRound '(' \<EXP> ','\<EXP> ')'      ")
            t[0] = Round(t[3], t[5], token.lineno, token.lexpos, graph_ref)
    elif token.type == "SCALE":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=   tScale '(' \<EXP> ')'      ")
        t[0] = Scale(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "SIGN":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=  tSign '(' \<EXP> ')'       ")
        t[0] = Sign(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "SQRT":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=  tSqrt '(' \<EXP> ')'       ")
        t[0] = Sqrt(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "TRIM_SCALE":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=  tTrimScale '(' \<EXP> ')'       ")
        t[0] = TrimScale(t[3], token.lineno, token.lexpos, graph_ref)
    elif token.type == "WIDTH_BUCKET":
        childsProduction = addNotNoneChild(t,[3,5,7,9])
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4],t[5],t[6],t[7],t[8],t[9],t[10]]    ,childsProduction)
        addCad("**\<EXP>** ::=  tWidthBucket '(' \<EXP> ',' \<EXP> ',' \<EXP> ',' \<EXP> ')' ") 
        t[0] = WidthBucket(t[3], t[5], t[7], t[9], token.lineno, token.lexpos, graph_ref)
    elif token.type == "RANDOM":
                       
        graph_ref = graph_node(str(str(t[1])+" "+str(t[2])+" "+str(t[3])))
        addCad("**\<EXP>** ::=  tRandom '()'       ")
        t[0] = Random(token.lineno, token.lexpos, graph_ref)
    elif token.type == "SETSEED":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=  tSetseed '(' \<EXP> ')'       ")
        t[0] = SetSeed(t[3], token.lineno, token.lexpos, graph_ref)        
    elif token.type == "TRUC":
        childsProduction = addNotNoneChild(t,[3])                
        graph_ref = graph_node(str("exp"), [t[1],t[2],t[3],t[4]]    ,childsProduction)
        addCad("**\<EXP>** ::=   tTruc '(' \<EXP> ')'      ")
        t[0] = Trunc(t[3], token.lineno, token.lexpos, graph_ref)


def p_exp_unary(t):
    '''expression : MENOS expression %prec UMENOS
                  | MAS expression %prec UMAS '''
    token = t.slice[2].value
    if t[1] == '+':
        childsProduction = addNotNoneChild(t,[2])                
        graph_ref = graph_node(str("exp"), [t[1],t[2]]    ,childsProduction)
        addCad("**\<EXP>** ::=  [+|-] \<EXP>")
        t[0] =  NumericPositive(t[2], token.line, token.column, graph_ref) 
    elif t[1] == '-':
        childsProduction = addNotNoneChild(t,[2])                
        graph_ref = graph_node(str("exp"), [t[1],t[2]]    ,childsProduction)
        addCad("**\<EXP>** ::=  [+|-] \<EXP>")
        t[0] = NumericNegative(t[2], token.line, token.column, graph_ref) 
    else:
        print("Missed code from unary expression")


def p_exp_num(t):
    '''expression : numero
                    | col_name'''
    t[0] = t[1]
    token = t.slice[1]   
    if token.type == "numero":
        addCad("**\<EXP>** ::= \<NUMERO>")
    elif token.type == "col_name":
        addCad("**\<EXP>** ::= \<COL_NAME>")


def p_exp_val(t):
    '''expression   : TEXTO
                    | BOOLEAN_VALUE                    
                    | NOW PARA PARC'''
    token = t.slice[1]    
    if token.type == "TEXTO":
        graph_ref = graph_node(str(t[1]))
        addCad("**\<EXP>** ::=  tTexto")
        t[0] = Text(token.value, token.lineno, token.lexpos, graph_ref)
    elif token.type == "BOOLEAN_VALUE":
        graph_ref = graph_node(str(t[1]))
        addCad("**\<EXP>** ::=  tTexto")
        t[0] = BoolAST(token.value, token.lineno, token.lexpos, graph_ref)
    elif token.type == "NOW":
        graph_ref = graph_node(str(str(t[1])+" "+str(t[2])+" "+str(t[3])))
        addCad("**\<EXP>** ::=  tNow '(' ')' ")
        t[0] = Now(token.lineno, token.lexpos, graph_ref)



# <NUMERO> ::=
def p_numero(t):
    ''' numero  : ENTERO
                | FLOAT'''
    token = t.slice[1]
    if token.type == "ENTERO":
        addCad("**\<NUMERO>** ::= tEntero")
    elif token.type == "FLOAT":
        addCad("**\<NUMERO>** ::= tFloat")
    graph_ref = graph_node(str(t[1]))
    t[0] = Numeric(token.value, token.lineno, token.lexpos, graph_ref)

# --- <COL_NAME> ::= tIdentificador [‘.’ tIdentificador]
def p_col_name(t):
    ''' col_name : ID PUNTO ID'''
    token = t.slice[1]
    graph_ref = graph_node(str(str(t[1])+" " + str(t[2])+ " " + str(t[3])))
    addCad("**\<COL_NAME>** ::= tIdentificador '.' tIdentificador")
    t[0] = ColumnName(t[1], t[3], token.lineno, token.lexpos, graph_ref)

def p_col_name1(t):
    ''' col_name : ID '''
    token = t.slice[1]
    graph_ref = graph_node(str(t[1]))
    addCad("**\<COL_NAME>** ::= tIdentificador")
    t[0] = ColumnName(None, t[1], token.lineno, token.lexpos, graph_ref)

# <EMPTY> ::=
def p_empty(t):
    '''empty :'''
    pass


import ply.yacc as yacc
from ply.yacc import token

parse = yacc.yacc()
errorsList = []
r = []

ST = SymbolTable([])##TODO Check is only one ST.


class grammarReview:
    def __init__(self, texto): 
        print("Executing AST root, please wait ...")
        global r
        r = []
        global errorsList
        errorsList = []
        global ST
        ST.LoadMETADATA()
        instrucciones = parse.parse(texto)
        generateReports()

        for instruccion in instrucciones:
            try:
                val = instruccion.execute(ST, None)
                print("AST excute result: ", val)
                if isinstance(instruccion, Select) or isinstance(instruccion, Union) \
                        or isinstance(instruccion, Intersect) or isinstance(instruccion, Except):
                    val = tabulate(val[1], val[0], tablefmt="psql")
                self.set_result(str(val) + '\n\n')
            except our_error as named_error:
                errorsList.append(named_error)

        for e in errorsList:
            print(e, "\n")
        
        
    def set_result(self, valor):
        global r
        r.append(valor)
        return r

    def get_result(self):
        global r
        return r

    def getTablaTabulada(self):
        global ST
        return ST.report_symbols()


    def report_errors(self):
        result2 = ["LINEA", "COLUMNA", "TIPO", "DESCRIPCION"]
        result = []
        global errorsList
        for our_error in errorsList:
            result.append([our_error.line, our_error.column, our_error.error_type, our_error.message])
        print(tabulate(result, result2, tablefmt="rst"))
        return tabulate(result, result2, tablefmt="rst")

'''if __name__ == "__main__":
    f = open("./entrada.txt", "r")
    input = f.read()
    print("Input: " + input +"\n")
    print("Executing AST root, please wait ...")
    ST = SymbolTable([])##TODO Check is only one ST.
    ST.LoadMETADATA()
    instrucciones = parse.parse(input)
    # createFile()
    # creategrafo()

    for instruccion in instrucciones:
        try:
            val = instruccion.execute(ST, None)
            if isinstance(instruccion, Select):
                print(tabulate(val[1], val[0], tablefmt="psql"))
            else:
                print("AST excute result: ", val)
        except our_error as named_error:
            errorsList.append(named_error)

    for e in errorsList:
        print(e,"\n")
    ST.report_symbols() '''
    