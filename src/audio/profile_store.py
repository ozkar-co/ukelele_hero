"""
Almacenamiento de perfiles de calibración del micrófono.

Cada calibración se guarda como un JSON independiente con fecha en el
nombre. Nunca se sobrescribe un perfil anterior, de modo que sirven como
histórico para análisis de micrófono, ruido de sala y detección.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


PROFILE_PREFIX = "profile_"


def _default_profile_folder():
    if getattr(sys, "frozen", False):
        project_root = Path(sys.executable).resolve().parent
    else:
        project_root = Path(__file__).parent.parent.parent
    return project_root / "assets" / "calibration"


class CalibrationProfileStore:
    """Guarda y recupera perfiles de calibración en assets/calibration/."""

    def __init__(self, folder=None):
        self.folder = Path(folder) if folder is not None else _default_profile_folder()

    def save(self, profile):
        """Guarda un perfil nuevo y devuelve la ruta del archivo."""
        self.folder.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        data = dict(profile)
        data.setdefault("created_at", now.isoformat(timespec="seconds"))

        filename = f"{PROFILE_PREFIX}{now.strftime('%Y%m%d_%H%M%S_%f')}.json"
        path = self.folder / filename
        while path.exists():
            path = self.folder / f"{path.stem}_1.json"

        temp_path = path.with_suffix(".tmp")
        temp_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        temp_path.replace(path)
        return path

    def list_profiles(self):
        """Devuelve las rutas de perfiles ordenadas de más antiguo a más reciente."""
        if not self.folder.exists():
            return []
        return sorted(self.folder.glob(f"{PROFILE_PREFIX}*.json"))

    def load_latest(self):
        """Carga el perfil más reciente; devuelve None si no hay o está corrupto."""
        for path in reversed(self.list_profiles()):
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
        return None
