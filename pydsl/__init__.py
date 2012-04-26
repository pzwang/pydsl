
import byteplay as bp
import lang
import sys

interpreters = {
    "sql": lang.sql.Interpreter,
    "cpp": lang.cpp.Interpreter,
    "forth": lang.forth.Interpreter,
    "data": lang.data.Interpreter,
    }

def register(debug=False):
    from dslimporter import DSLImporter
    DSLImporter.debug = debug
    import sys
    sys.meta_path.append(DSLImporter)

def updatelocals(newvars):
    """ Pushes key,values from newvars into our parent caller's namespace.
    """
    import pdb; pdb.set_trace()
    if newvars:
        callerframe = sys._getframe(1)
        callerframe.f_locals.update(newvars)

    # It is not enough to merely update the local vars, you also have to
    # change the bytecode of the caller so that LOAD_GLOBALS become
    # LOAD_FAST.
    #newvarnames = set(newvars.keys())
    #code = bp.Code.from_code(callerframe.f_code)
    #for i, instr in enumerate(code.code):
    #    if instr[1] in newvarnames:
    #        code.code[i] = (bp.LOAD_FAST, instr[1])

    #dummy.func_code = code.to_code()
    #callerframe.f_code.co_code = code.to_code()

