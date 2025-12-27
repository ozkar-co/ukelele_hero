"""
Cargador de archivos MIDI para extraer información de pistas
"""

import os
from pathlib import Path
import pretty_midi
from typing import Optional, List, Tuple, Dict


class MIDILoader:
    """Carga y parsea archivos MIDI"""
    
    # Rango de notas MIDI para ukulele (típicamente C3 a E6)
    UKULELE_MIN_NOTE = 36  # C2
    UKULELE_MAX_NOTE = 88  # E6
    
    def __init__(self, midi_folder: str = None):
        """
        Inicializa el cargador MIDI
        
        Args:
            midi_folder (str): Ruta a la carpeta con archivos MIDI
                              Por defecto, usa assets/midi
        """
        if midi_folder is None:
            # Usar carpeta assets/midi por defecto
            project_root = Path(__file__).parent.parent.parent
            midi_folder = project_root / "assets" / "midi"
        
        self.midi_folder = Path(midi_folder)
        self.midi_files = []
        self._scan_midi_files()
    
    def _scan_midi_files(self):
        """Escanea la carpeta y lista todos los archivos .mid"""
        if not self.midi_folder.exists():
            print(f"⚠️ Carpeta MIDI no encontrada: {self.midi_folder}")
            return
        
        self.midi_files = list(self.midi_folder.glob("*.mid")) + \
                         list(self.midi_folder.glob("*.midi"))
        self.midi_files.sort()
        
        if self.midi_files:
            print(f"✅ {len(self.midi_files)} archivos MIDI encontrados")
    
    def get_midi_files(self) -> List[str]:
        """
        Retorna lista de nombres de archivos MIDI disponibles
        
        Returns:
            List[str]: Nombres de los archivos MIDI
        """
        return [f.stem for f in self.midi_files]
    
    def load_midi(self, filename: str) -> Optional[pretty_midi.PrettyMIDI]:
        """
        Carga un archivo MIDI
        
        Args:
            filename (str): Nombre del archivo (sin extensión)
            
        Returns:
            pretty_midi.PrettyMIDI: Objeto MIDI o None si no existe
        """
        # Buscar archivo con extensión .mid o .midi
        midi_file = self.midi_folder / f"{filename}.mid"
        if not midi_file.exists():
            midi_file = self.midi_folder / f"{filename}.midi"
        
        if not midi_file.exists():
            print(f"❌ Archivo MIDI no encontrado: {filename}")
            return None
        
        try:
            midi = pretty_midi.PrettyMIDI(str(midi_file))
            print(f"✅ MIDI cargado: {filename}")
            return midi
        except Exception as e:
            print(f"❌ Error al cargar MIDI: {e}")
            return None
    
    def get_track_info(self, midi: pretty_midi.PrettyMIDI) -> List[Dict]:
        """
        Obtiene información de todas las pistas
        
        Args:
            midi (pretty_midi.PrettyMIDI): Objeto MIDI cargado
            
        Returns:
            List[Dict]: Lista con info de cada pista
        """
        tracks_info = []
        
        for idx, instrument in enumerate(midi.instruments):
            info = {
                'index': idx,
                'name': instrument.name or f"Pista {idx}",
                'program': instrument.program,
                'is_drum': instrument.is_drum,
                'note_count': len(instrument.notes),
                'start_time': instrument.notes[0].start if instrument.notes else 0,
                'end_time': instrument.notes[-1].end if instrument.notes else 0,
            }
            tracks_info.append(info)
        
        return tracks_info
    
    def get_track_notes(self, midi: pretty_midi.PrettyMIDI, 
                       track_index: int = 0) -> List[Tuple[int, float, float]]:
        """
        Extrae las notas de una pista específica
        
        Args:
            midi (pretty_midi.PrettyMIDI): Objeto MIDI
            track_index (int): Índice de la pista (por defecto 0)
            
        Returns:
            List[Tuple[int, float, float]]: Lista de (pitch, start_time, end_time)
        """
        if track_index >= len(midi.instruments):
            print(f"❌ Pista {track_index} no existe")
            return []
        
        instrument = midi.instruments[track_index]
        notes = []
        
        for note in instrument.notes:
            # Filtrar notas dentro del rango del ukulele
            if self.UKULELE_MIN_NOTE <= note.pitch <= self.UKULELE_MAX_NOTE:
                notes.append((note.pitch, note.start, note.end))
        
        # Ordenar por tiempo de inicio
        notes.sort(key=lambda x: x[1])
        return notes
    
    @staticmethod
    def midi_note_to_name(pitch: int) -> str:
        """
        Convierte número MIDI a nombre de nota
        
        Args:
            pitch (int): Número MIDI (0-127)
            
        Returns:
            str: Nombre de la nota (ej: "C4", "D#5")
        """
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (pitch // 12) - 1
        note_index = pitch % 12
        return f"{note_names[note_index]}{octave}"
    
    @staticmethod
    def midi_note_to_frequency(pitch: int) -> float:
        """
        Convierte número MIDI a frecuencia en Hz
        
        Args:
            pitch (int): Número MIDI
            
        Returns:
            float: Frecuencia en Hz
        """
        # A4 (pitch 69) = 440 Hz
        return 440 * (2 ** ((pitch - 69) / 12))
    
    def transpose_notes(self, notes: List[Tuple[int, float, float]], 
                       octaves: int = 0) -> List[Tuple[int, float, float]]:
        """
        Transpone notas por octavas completas
        
        Args:
            notes (List[Tuple[int, float, float]]): Lista de (pitch, start_time, end_time)
            octaves (int): Número de octavas a transponer (+/- 12 semitones por octava)
            
        Returns:
            List[Tuple[int, float, float]]: Notas transponidas
        """
        semitones = octaves * 12
        transposed = []
        
        for pitch, start, end in notes:
            new_pitch = pitch + semitones
            # Asegurar que esté dentro del rango MIDI válido (0-127)
            new_pitch = max(0, min(127, new_pitch))
            transposed.append((new_pitch, start, end))
        
        return transposed
    
    def get_notes_range(self, notes: List[Tuple[int, float, float]]) -> Tuple[int, int]:
        """
        Obtiene el rango (min, max) de notas
        
        Args:
            notes (List[Tuple[int, float, float]]): Lista de (pitch, start_time, end_time)
            
        Returns:
            Tuple[int, int]: (nota_mínima, nota_máxima) en MIDI
        """
        if not notes:
            return (0, 0)
        
        pitches = [pitch for pitch, _, _ in notes]
        return (min(pitches), max(pitches))
    
    def adjust_to_ukulele_range(self, notes: List[Tuple[int, float, float]]) -> Tuple[List[Tuple[int, float, float]], int]:
        """
        Ajusta automáticamente notas al rango del ukulele
        
        Args:
            notes (List[Tuple[int, float, float]]): Lista de (pitch, start_time, end_time)
            
        Returns:
            Tuple: (notas_ajustadas, octavas_transponidas)
        """
        min_note, max_note = self.get_notes_range(notes)
        
        # Rango típico del ukulele soprano: C4 (60) a E6 (88)
        uke_min = 60  # C4
        uke_max = 88  # E6
        
        octaves_needed = 0
        adjusted_notes = notes
        
        # Si las notas están todas demasiado bajas
        if max_note < uke_min:
            while max(pitch for pitch, _, _ in adjusted_notes) < uke_min:
                octaves_needed += 1
                adjusted_notes = self.transpose_notes(adjusted_notes, 1)
        
        # Si las notas están todas demasiado altas
        elif min_note > uke_max:
            while min(pitch for pitch, _, _ in adjusted_notes) > uke_max:
                octaves_needed -= 1
                adjusted_notes = self.transpose_notes(adjusted_notes, -1)
        
        return adjusted_notes, octaves_needed
