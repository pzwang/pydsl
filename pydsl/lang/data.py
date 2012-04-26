
class Interpreter(object):

    def __init__(self, filename, format=None, output=None):
        """
        **format** is typically inferred from the extension of filename;
        however, it can be manually overriden here.

        **output** should be one of "numpy", "pandas", "list".  By default,
        if numpy is available, then an ndarray will be returned.
        """
        self.filename = filename

    def run(self, code):
        pass
        
    def read_array(filename, dtype, separator=','):
        """ Read a file with an arbitrary number of columns.
            The type of data in each column is arbitrary
            It will be cast to the given dtype at runtime

            from http://www.scipy.org/Cookbook/InputOutput
        """
        cast = N.cast
        data = [[] for dummy in xrange(len(dtype))]
        for line in open(filename, 'r'):
            fields = line.strip().split(separator)
            for i, number in enumerate(fields):
                data[i].append(number)
        for i in xrange(len(dtype)):
            data[i] = cast[dtype[i]](data[i])
        return N.rec.array(data, dtype=dtype)


