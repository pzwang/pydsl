
import imp
import os
import StringIO
import sys

# Template of python code that is emitted in the transformed output
DSL_CODE_TEMPLATE = """import pydsl
__DSL_INTERP = pydsl.interpreters["%(dsl_name)s"](%(dsl_args)s)
__DSL_OUT_DICT = __DSL_INTERP.run('''%(dsl_code)s''', ns=locals())
for kw, val in __DSL_OUT_DICT.items():
    exec kw + " = val"
"""

# This must include the "."
DSL_EXTENSION = ".pydsl"
DSL_KEYWORD = "extern"
DSL_TABSTOP = 4  # number of spaces

def transform(lines):
    import pydsl

    outlines = []
    dsl_lines = []
    dsl_name = None     # name of the DSL language to use
    dsl_args = ""       # a string that holds the initialization arguments 
                        # to the DSL invocation; this is passed verbatim
    dsl_indent = 0      # The indentation level of the original "using" 
                        # statement, in number of characters.
    mode = "python"     # either "python" or "dsl"
    
    trigger = DSL_KEYWORD + " "
    triggerlen = len(trigger)
    for line in lines:
        if mode == "python":
            # Check to see if we are starting a DSL block
            tmp = line.strip()
            if tmp.startswith(trigger) and tmp[-1] == ":":
                # If we are starting a DSL block, then extract the DSL configuration
                dsl_spec = tmp[triggerlen:-1]
                if "(" in dsl_spec:
                    start = dsl_spec.index("(")
                    stop = dsl_spec.index(")")
                    dsl_name = dsl_spec[:start]
                    dsl_args = dsl_spec[start+1:stop]
                else:
                    dsl_name = dsl_spec
                if dsl_name not in pydsl.interpreters:
                    raise ImportError("Unrecognized DSL language '%s'" % dsl_name)
                dsl_indent = line.index(trigger)
                mode = "dsl"
            else:
                # If we are not triggering a new DSL block, then just rstrip the code
                # and add it to the raw output
                outlines.append(line.rstrip())
        elif mode == "dsl":
            if len(line.strip()) == 0:
                # We escape this condition because we allow the DSL block to have
                # empty lines
                dsl_lines.append(line)
            elif len(line) - len(line.lstrip()) <= dsl_indent:
                # Add the wrapped/transformed DSL code into the output
                # line stream, then add the line of python that ended
                # the DSL block, and then switch the parsing mode back
                # to python mode from DSL mode.
                dsl_code = "\n".join(d[dsl_indent+DSL_TABSTOP:] for d in dsl_lines)
                transformed = (DSL_CODE_TEMPLATE % locals()).split("\n")
                outlines.extend(" "*dsl_indent + xl for xl in transformed)
                dsl_lines = []
                mode = "python"

                # The line which triggered the end of the DSL block needs to also
                # be appended, raw, to the output
                outlines.append(line.rstrip())
            else:
                dsl_lines.append(line)
    return outlines


class DSLImporter(object):
    """ The Importer object for sys.path_hooks.

    The classmethod dsl_importer() is registered in path_hooks, and returns
    an instance of DSLImporter.
    """

    # If this is true, then a file named {basename}.pydsl.out will be created
    debug = False

    def __init__(self, filename):
        self.filename = filename

    @classmethod
    def find_module(cls, fullname, path=None):
        modulename = fullname.split(".")[-1]
        if path is None:
            path = sys.path
        for p in path:
            filename = os.path.join(p,modulename+DSL_EXTENSION)
            if os.path.isfile(filename):
                return cls(filename)
        else:
            return None

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]

        with open(self.filename, "r") as f:
            rawlines = f.readlines()

        code = "\n".join(transform(rawlines))
        
        # The following code is from PEP 302's "minimal load_module()" example
        mod = imp.new_module(fullname)
        mod.__file__ = self.filename
        mod.__loader__ = self

        if self.debug:
            outname = os.path.splitext(self.filename)[0] + DSL_EXTENSION + ".out"
            try:
                with open(outname, "w") as f:
                    f.write(code)
            except IOError:
                sys.stderr.write("Warning: Unable to save debug output file '%s'\n" % outname)

        exec code in mod.__dict__
        return mod


def test_transform():
    testsrc = """
a = 3
b = 6
using sql:
    blah blah
    invalid syntax!@@
s = "back to python"
"""
    from pprint import pprint
    pprint(transform(testsrc.split("\n")))



