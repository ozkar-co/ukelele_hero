# Instalación

## Requisitos

- Python 3.10 o superior.
- `make`.
- PortAudio en Linux: `sudo apt install portaudio19-dev`.
- Conexión a red solo la primera vez, o un `wheelhouse/` ya poblado.

## Entorno

```bash
make config
```

`make config` crea `.venv/` e instala desde `wheelhouse/` sin red.
`make fetch` descarga los wheels necesarios usando la red.

## Ejecutar

```bash
.venv/bin/python main.py
```

## Tests

```bash
make test
```

## Limpiar

```bash
make clean
```

Elimina `.venv/`, `build/` y `dist/`, pero conserva `wheelhouse/`.

## Distribución

Ver [distribución](distribution.md).
