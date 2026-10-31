# Ukulele Hero — entorno offline y distribución portable.
#
# Runtime: pygame-ce, numpy, scipy, matplotlib y sounddevice son binarios
# grandes; `make dist` usa PyInstaller en modo onedir (no onefile), que
# empaqueta el intérprete sin compilar a C y arranca sin descomprimir.

.PHONY: config fetch test clean dist

PY := .venv/bin/python
APP := ukelele_hero

config: fetch
	python3 -m venv .venv
	$(PY) -m pip install -r requirements.txt --no-index --find-links wheelhouse/

# Usa el pip del venv; el Python del sistema puede no traer pip.
# pip download guarda wheels en wheelhouse/ para instalar sin red.
fetch:
	@test -x $(PY) || python3 -m venv .venv
	@if $(PY) -m pip download -r requirements.txt -d wheelhouse/ 2>/dev/null; then \
		echo "Wheelhouse actualizado."; \
	elif ls wheelhouse/*.whl >/dev/null 2>&1; then \
		echo "Sin red. Usando wheelhouse existente."; \
	else \
		echo "Error: sin red ni wheelhouse. Ejecutar con conexión primero." >&2; \
		exit 1; \
	fi

test:
	PYTHONPATH=src $(PY) -m unittest discover -s tests -v

clean:
	rm -rf .venv build dist
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +

# assets/ se copia junto al ejecutable, no dentro de _internal, para que
# las tablaturas guardadas queden en la misma carpeta portable.
dist:
	@test -x $(PY) || { echo "Error: ejecuta make config primero." >&2; exit 1; }
	rm -rf build dist
	$(PY) -m PyInstaller --noconfirm --clean --onedir \
		--name $(APP) \
		--paths src \
		--distpath dist \
		--workpath build/pyi-work \
		--specpath build/pyi \
		main.py
	cp -a assets dist/$(APP)/assets
	cp README.md dist/$(APP)/README.md
	@echo "Bundle: dist/$(APP)/  (ejecutar ./$(APP)/$(APP))"
