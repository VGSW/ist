CURL_CMD=/usr/bin/curl --silent --location
PY_CMD=/usr/bin/python3
RM_CMD=/usr/bin/rm

BASE_URL=https://seafile.ist.ac.at/d/51139240e5/files/?p=
CSV_FILE=data.csv
DB_FILE=data.sqlite3

all: fetch run

clean:
	${RM_CMD} -f *.csv
	${RM_CMD} -f *.sqlite3

fetch:
	${CURL_CMD} --output data.csv "${BASE_URL}/${CSV_FILE}&dl=1"
	${CURL_CMD} --output data.sqlite3 "${BASE_URL}/${DB_FILE}&dl=1"

install:
	echo "arch linux only, make must run as root or via sudo"
	pacman -S python-bottle

test:
	${PY_CMD} -m unittest discover

run:
	${PY_CMD} index.py
