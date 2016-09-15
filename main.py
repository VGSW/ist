import csv

class Log (object):
    def __init__ (self, **kwa):
        filename = kwa.get ('filename')
        self.fh = open (filename, 'w')

    def log (self, msg, level = 'DEBUG'):
        self.fh.write ('[%(level)s] %(msg)s' % dict (level=level, msg=msg))

class Foo (object):

    def __init__ (self, **kwa):
        self.filename = kwa.get ('filename') or './data.csv'
        self.sort     = kwa.get ('sort')
        self.sort_col = kwa.get ('sort_col')

        if self.sort not in ('asc', 'desc'):
            raise UserWarning ("sort must be either 'asc' or 'desc'")

        self._logger = Log (filename = 'main.log')
        self.log = lambda msg: self._logger.log (msg)

        self._table = self.mk_table()
        self.table = lambda: self._table

    def mk_table (self):

        def sort_rows (rows):

            def sorter (row):
                # we'll assume columns named 'id' are ints
                if self.sort_col == 'id':
                    try:
                        return int (row.get (self.sort_col))
                    except ValueError:
                        raise UserWarning ("columns named 'id' may only hold ints")
                else:
                    return row.get (self.sort_col)

            sorted_rows = sorted (reader, key = sorter)

            if self.sort == 'desc':
                return reversed (sorted_rows)
            else:
                return sorted_rows

        html = '<html>'
        html = '<head>'
        html = '</head>'
        html += '<body>'

        html += '<table>'
        html += '<tr>'

        # will remember ordering of headers for later accessing keys of a DictReader-row
        headers = list()

        with open (self.filename, 'r') as f:
            headers = f.readline().strip().split(';')
            html += ''.join (['<th>%s</th>' % h for h in headers])

        if self.sort_col not in headers:
            raise UserWarning ("sort_col must be either one of given headers: %s" % headers)

        html += '</tr>'

        with open (self.filename, 'r') as csvfile:
            reader = csv.DictReader (csvfile, delimiter = ';')

            for row in sort_rows (reader):
                html += '<tr>' + ''.join (['<td>%s</td>' % row.get (col_name) for col_name in headers]) + '</tr>'

        html += '</table>'
        html += '</body>'
        html += '</html>'

        return html
