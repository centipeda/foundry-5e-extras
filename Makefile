
FOUNDRY = dnd5e-extras
EXPORTDIR = ${FOUNDRY}/packs/src
BIN = bin/
DATA = data/

all: build extract transform

download: ${BIN}/download.py
	./${BIN}/download.py

extract: ${BIN}/extract.py ${DATA}/index.json
	./${BIN}/extract.py

export: ${DATA}/db.json ${BIN}/export.py
	./${BIN}/export.py ${EXPORTDIR}

build: export
	cd ${FOUNDRY}; npm run build:db
