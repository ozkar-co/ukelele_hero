"""
Gestor de tablaturas - Serialización y almacenamiento
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class TablatureManager:
    """Gestiona el guardado y carga de tablaturas configuradas"""
    
    def __init__(self, tablature_folder: str = None):
        """
        Inicializa el gestor de tablaturas
        
        Args:
            tablature_folder (str): Ruta a carpeta para guardar tablaturas
                                   Por defecto, usa assets/tablatures
        """
        if tablature_folder is None:
            project_root = Path(__file__).parent.parent.parent
            tablature_folder = project_root / "assets" / "tablatures"
        
        self.tablature_folder = Path(tablature_folder)
        self.tablature_folder.mkdir(parents=True, exist_ok=True)
    
    def save_tablature(self, 
                      midi_filename: str,
                      track_index: int,
                      notes: List[Tuple[int, float, float]],
                      octaves_transposed: int = 0,
                      tempo: float = 120,
                      metadata: Dict = None) -> str:
        """
        Guarda una tablatura configurada
        
        Args:
            midi_filename (str): Nombre del archivo MIDI original
            track_index (int): Índice de la pista
            notes (List[Tuple]): Notas (pitch, start, end)
            octaves_transposed (int): Octavas transponidas
            tempo (float): Tempo en BPM
            metadata (Dict): Datos adicionales
            
        Returns:
            str: Nombre del archivo guardado
        """
        # Crear nombre de archivo
        tab_name = f"{midi_filename}_track{track_index}_oct{octaves_transposed:+d}"
        tab_filename = f"{tab_name}.json"
        tab_path = self.tablature_folder / tab_filename
        
        # Convertir notas a formato serializable
        notes_data = [
            {
                "pitch": pitch,
                "start_time": start,
                "end_time": end,
                "note_name": self._midi_to_name(pitch)
            }
            for pitch, start, end in notes
        ]
        
        # Crear estructura de datos
        tablature_data = {
            "version": "1.0",
            "source": {
                "midi_file": midi_filename,
                "track_index": track_index
            },
            "configuration": {
                "octaves_transposed": octaves_transposed,
                "tempo": tempo
            },
            "notes": notes_data,
            "statistics": {
                "total_notes": len(notes),
                "duration": notes[-1][2] if notes else 0,
                "min_pitch": min(pitch for pitch, _, _ in notes) if notes else 0,
                "max_pitch": max(pitch for pitch, _, _ in notes) if notes else 0
            },
            "metadata": metadata or {}
        }
        
        # Guardar JSON
        with open(tab_path, 'w', encoding='utf-8') as f:
            json.dump(tablature_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Tablatura guardada: {tab_filename}")
        return tab_filename
    
    def load_tablature(self, filename: str) -> Optional[Dict]:
        """
        Carga una tablatura guardada
        
        Args:
            filename (str): Nombre del archivo (con o sin .json)
            
        Returns:
            Dict: Datos de la tablatura o None
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        tab_path = self.tablature_folder / filename
        
        if not tab_path.exists():
            print(f"❌ Archivo no encontrado: {filename}")
            return None
        
        try:
            with open(tab_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Tablatura cargada: {filename}")
            return data
        except Exception as e:
            print(f"❌ Error al cargar tablatura: {e}")
            return None
    
    def get_saved_tablatures(self) -> List[str]:
        """
        Lista todas las tablaturas guardadas
        
        Returns:
            List[str]: Lista de nombres de tablatura
        """
        if not self.tablature_folder.exists():
            return []
        
        tablatures = [f.stem for f in self.tablature_folder.glob("*.json")]
        return sorted(tablatures)
    
    def delete_tablature(self, filename: str) -> bool:
        """
        Elimina una tablatura guardada
        
        Args:
            filename (str): Nombre del archivo
            
        Returns:
            bool: True si se eliminó, False si no existe
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        tab_path = self.tablature_folder / filename
        
        if tab_path.exists():
            tab_path.unlink()
            print(f"✅ Tablatura eliminada: {filename}")
            return True
        else:
            print(f"❌ Archivo no encontrado: {filename}")
            return False
    
    def export_to_ui_format(self, tablature_data: Dict) -> Dict:
        """
        Convierte datos de tablatura al formato para la UI del juego
        
        Args:
            tablature_data (Dict): Datos cargados con load_tablature
            
        Returns:
            Dict: Formato optimizado para UI
        """
        notes = tablature_data.get("notes", [])
        
        # Organizar notas por cuerda (string)
        strings = {
            'G': [],
            'C': [],
            'E': [],
            'A': []
        }
        
        for note in notes:
            pitch = note["pitch"]
            note_name = note["note_name"]
            fret = self._get_fret(pitch)
            string = self._get_string(pitch)
            
            # Add 1 second offset for initial silence before gameplay starts
            start_time = note["start_time"] + 1.0
            end_time = note["end_time"] + 1.0
            
            strings[string].append({
                "fret": fret,
                "pitch": pitch,
                "note": note_name,
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time
            })
        
        return {
            "source": tablature_data["source"]["midi_file"],
            "track": tablature_data["source"]["track_index"],
            "tempo": tablature_data["configuration"]["tempo"],
            "octaves_transposed": tablature_data["configuration"]["octaves_transposed"],
            "strings": strings,
            "statistics": tablature_data["statistics"],
            "total_notes": len(notes)
        }
    
    @staticmethod
    def _midi_to_name(pitch: int) -> str:
        """Convierte MIDI a nombre de nota"""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (pitch // 12) - 1
        note_index = pitch % 12
        return f"{note_names[note_index]}{octave}"
    
    @staticmethod
    def _get_string(pitch: int) -> str:
        """Determina la cuerda para un pitch"""
        # Afinación GCEA: G4=67, C4=60, E4=64, A4=69
        strings_tuning = {
            'G': 67,
            'C': 60,
            'E': 64,
            'A': 69
        }
        
        # Encontrar la cuerda más cercana
        min_diff = float('inf')
        closest_string = 'A'
        
        for string_name, base_pitch in strings_tuning.items():
            # Comparar dentro del mismo rango de octavas
            distance = abs(pitch - base_pitch)
            if distance < min_diff:
                min_diff = distance
                closest_string = string_name
        
        return closest_string
    
    @staticmethod
    def _get_fret(pitch: int) -> int:
        """Calcula el traste para un pitch"""
        # Usar C4 como referencia (cuerda C, traste 0)
        base_pitch = 60  # C4
        return pitch - base_pitch
