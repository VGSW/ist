import csv
import sqlite3
import json
from optparse import OptionParser

class Log (object):
    def __init__ (self, **kwa):
        filename = kwa.get ('filename')
        self.fh = open (filename, 'w')

    def log (self, msg, level = 'DEBUG'):
        self.fh.write ('[%(level)s] %(msg)s\n' % dict (level=level, msg=msg))
        self.fh.flush ()

class Lemmy (object):

    def __init__ (self, **kwa):
        self.csv_file = kwa.get ('csv_file') or './data.csv'
        self.db_file  = kwa.get ('db_file') or './data.sqlite3'
        self.sort     = kwa.get ('sort')
        self.sort_col = kwa.get ('sort_col')

        if self.sort not in ('asc', 'desc'):
            raise UserWarning ("sort must be either 'asc' or 'desc'")

        self._logger = Log (filename = './main.log')
        self.log = lambda msg: self._logger.log (msg)

        self._table = self.mk_table()
        self.table = lambda: self._table

    def mk_table (self):
        def sort_rows (reader):
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
        html += '<head>'
        html += '<title>IST Programming Exercise, Christian Veigl</title>'
        html += '</head>'
        html += '<body>'

        html += '<table>'
        html += '<tr><thead>'

        # will remember ordering of headers for later accessing keys of a DictReader-row
        headers = list()

        with open (self.csv_file, 'r') as f:
            headers = f.readline().strip().split(';')

            html += ''.join ([
                '<th>%(h)s<a href="/ist/%(h)s/asc">&darr;</a><a href="/ist/%(h)s/desc">&uarr;</a></th>' % dict (h=h)
                for h in headers
            ])

            html += '<th>geodata</th>'

        html += '</thead></tr>'

        if self.sort_col not in headers:
            raise UserWarning ("sort_col must be either one of given headers: %s" % headers)

        with open (self.csv_file, 'r') as csv_data:
            reader = csv.DictReader (csv_data, delimiter = ';')

            for row in sort_rows (reader):
                data    = ''.join (['<td>%s</td>' % row.get (col_name) for col_name in headers])
                geodata = self.load_geodata (pkey = row.get ('id'))

                if geodata:
                    data += '<td><a target="_blank" href="https://maps.google.com?q=%s,%s">&#8513;</a></td>' % (
                        geodata.get ('lat'),
                        geodata.get ('lng'),
                    )
                else:
                    data += '<td>N/A</td>'

                html += '<tr>%s</tr>' % data

        html += '</table>'
        html += '</body>'
        html += '</html>'

        return html

    def load_geodata (self, **kwa):
        # an exampe database entry looks like this:
        # we're using geometry.location.lat and .lng
        #
        #[{
        #    "address_components":[
        #        {"long_name":"Massachusetts Institute of Technology","short_name":"Massachusetts Institute of Technology","types":["establishment"]},
        #        {"long_name":"77","short_name":"77","types":["street_number"]},
        #        {"long_name":"Massachusetts Avenue","short_name":"Massachusetts Ave","types":["route"]},
        #        {"long_name":"MIT","short_name":"MIT","types":["neighborhood","political"]},
        #        {"long_name":"Cambridge","short_name":"Cambridge","types":["locality","political"]},
        #        {"long_name":"Middlesex County","short_name":"Middlesex County","types":["administrative_area_level_2","political"]},
        #        {"long_name":"Massachusetts","short_name":"MA","types":["administrative_area_level_1","political"]},
        #        {"long_name":"United States","short_name":"US","types":["country","political"]},
        #        {"long_name":"02139","short_name":"02139","types":["postal_code"]}
        #    ],
        #    "formatted_address":"Massachusetts Institute of Technology, 77 Massachusetts Avenue, Cambridge, MA 02139, USA",
        #    "geometry":{
        #        "bounds":{
        #            "northeast":{"lat":42.3659977,"lng":-71.0800246},
        #            "southwest":{"lat":42.3534404,"lng":-71.1089008}
        #        },
        #        "location":{"lat":42.360091,"lng":-71.09416},
        #        "location_type":"APPROXIMATE",
        #        "viewport":{
        #            "northeast":{"lat":42.3659977,"lng":-71.0800246},
        #            "southwest":{"lat":42.3534404,"lng":-71.1089008}
        #        }
        #    },
        #    "types":["university","establishment"]
        #}]

        pkey = kwa.get ('pkey')
        db   = sqlite3.connect (self.db_file)

        geodata = db.cursor().execute (
            'select geodata from institutions where id = ?',
            (pkey,)  # huch ? a tuple you want ?!
        ).fetchone()[0]

        geodata = json.loads (geodata)

        if geodata and len (geodata):
            return dict (
                lat = geodata[0].get ('geometry').get ('location').get ('lat'),
                lng = geodata[0].get ('geometry').get ('location').get ('lng'),
            )
        else:
            return None

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--sort", dest="sort", default="asc", help="sort asc or desc")
    parser.add_option("--sort_col", dest="sort_col", default="id", help="column to sort")
    (options, args) = parser.parse_args()

    print (Lemmy (
        sort_col = options.sort_col,
        sort     = options.sort,
    ).table())
