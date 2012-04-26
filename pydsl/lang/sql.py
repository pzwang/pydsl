
from numbers import Number
from sqlalchemy import create_engine



class Interpreter(object):

    def __init__(self, dburi, **connect_args):
        self.dburi = dburi
        self.connect_args = connect_args

    @staticmethod
    def _substitute_ns_vars(code, nsvars, identifier_map):
        """ Returns a code string with values of identifiers in
        identifier_map replaced by the values from nsvars dict.

        **nsvars** is a dict mapping identifier names to Python values.
        Any non-numeric values are interpolated as %s.

        **identifer_map** maps names to list of char locations in the
        source code string.
        """
        # First, we need to build a reverse dict of string positions to
        # identifier names.
        posmap = {}
        for name, positions in identifier_map.items():
            posmap.update((p,name) for p in positions)
        
        # Now go through the code string and substitute in nsvars values,
        # in reverse order based on posmap
        for pos in sorted(posmap.keys())[::-1]:
            identifier = posmap[pos]
            val = nsvars[identifier]
            if isinstance(val, Number):
                valstr = str(val)
            else:
                valstr = '"%s"' % val
            code = code[:pos] + valstr + code[pos+len(identifier):]
        return code


    def run(self, code, ns):

        # Not sure why we have to enablePackrat() but without this, some
        # predicates hang
        import pyparsing
        pyparsing.ParserElement.enablePackrat()

        import sql_select_parser
        from sql_select_parser import select_stmt
        # blow away the identifier map because it's a module-level global
        sql_select_parser.reset_id_map()
        res = select_stmt.parseString(code)

        # Fill in namespace variables from the ns dict, by looking at the
        # identifier map.
        idmap = sql_select_parser.identifier_map
        matched_vars = dict((k,v) for k,v in ns.items() if k in idmap)
        matched_pos = dict((k,v) for k,v in idmap.items() if k in matched_vars)
        new_code = Interpreter._substitute_ns_vars(code, matched_vars, matched_pos)

        # Run the query
        engine = create_engine(self.dburi, connect_args = self.connect_args)
        cursor = engine.execute(new_code)
        rows = cursor.fetchall()

        # Return a dict of new variable values. Automatically extract the
        # variable names from the sql statement
        column_names = list(res.columns)
        columns = zip(*rows)
        return dict(zip(column_names, columns))

