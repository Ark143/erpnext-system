import sys
try:
    import pypika
    from pypika import Table, Field, functions as fn
    from pypika.terms import Function, CustomFunction

    t = Table('tabSales Invoice')
    f1 = Function('sum', t.base_grand_total)
    print('Function with Field:', f1.get_sql(quote_char='"'))

    f2 = Function('sum', 'base_grand_total')
    print('Function with str:', f2.get_sql(quote_char='"'))

    # Notice: what if Table['base_grand_total'] is a Table object or Term?
    # In PyPika, Table['field'] returns Field('field', table=Table)
    # But in Function('sum', arg):
    # If arg is passed to Function:
    # Function.__init__ takes *args.
    # In pypika.terms.Function:
    # def __init__(self, name, *args, **kwargs):
    #     self.args = [arg if isinstance(arg, Term) else ValueWrapper(arg) for arg in args]
    # If arg is a string, it wraps it as ValueWrapper('base_grand_total') which outputs 'base_grand_total' (string literal)!
    # If arg is Field('base_grand_total', table=t), it outputs "tabSales Invoice"."base_grand_total".
    
    # What if aggregation is 'sum' and Table is DocType('Sales Invoice')?
    # In goal.py:
    # Table = DocType(goal_doctype)
    # Function(aggregation, Table[goal_field])
except Exception as e:
    print('Error:', e)
