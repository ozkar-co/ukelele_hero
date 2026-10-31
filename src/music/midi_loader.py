"""
Cargador de archivos MIDI para extraer información de pistas
"""

import os
import sys
from pathlib import Path
import pretty_midi
from typing import Optional, List, Tuple, Dict

from .ukelele import pitch_to_string_fret


class MIDILoader:
    """Carga y parsea archivos MIDI"""

    # Rango para cargar notas y rango realmente tocable en GCEA.
    UKULELE_MIN_NOTE = 36  # C2
    UKULELE_MAX_NOTE = 88  # E6
    PLAYABLE_MIN_NOTE = 60  # C4, cuerda C al aire
    PLAYABLE_MAX_NOTE = 88  # E6
    MAX_FRET = 20
    HIGH_FRET = 8
    
    def __init__(self, midi_folder: str = None):
        """
        Inicializa el cargador MIDI
        
        Args:
            midi_folder (str): Ruta a la carpeta con archivos MIDI
                              Por defecto, usa assets/midi
        """
        if midi_folder is None:
            # Usar carpeta assets/midi por defecto
            if getattr(sys, "frozen", False):
                # En el bundle, assets/ vive junto al ejecutable.
                project_root = Path(sys.executable).resolve().parent
            else:
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
        Elige la octava que deja más notas y onsets tocables, con trastes cómodos.

        Prueba 0, -1, +1, -2 y +2 octavas. Devuelve solo las notas que caben
        en el ukulele (C4-E6 y trastes 0-20). En empate prefiere no transponer.
        """
        if not notes:
            return [], 0

        best_notes = []
        best_shift = 0
        best_score = float("-inf")

        for shift in (0, -1, 1, -2, 2):
            shifted = self.transpose_notes(notes, shift)
            playable, score = self._score_octave(notes, shifted)
            if score > best_score + 1e-9:
                best_score = score
                best_notes = playable
                best_shift = shift

        return best_notes, best_shift

    def _score_octave(self, original_notes, shifted_notes):
        """Puntúa una octava por cobertura, notas tocables y comodidad."""
        playable = []
        frets = []

        for note in shifted_notes:
            pitch, _start, _end = note
            if not (self.PLAYABLE_MIN_NOTE <= pitch <= self.PLAYABLE_MAX_NOTE):
                continue
            string_name, fret = pitch_to_string_fret(pitch, self.MAX_FRET)
            if string_name is None:
                continue
            playable.append(note)
            frets.append(fret)

        if not playable:
            return [], float("-inf")

        original_onsets = {round(start, 2) for _, start, _ in original_notes}
        playable_onsets = {round(start, 2) for _, start, _ in playable}
        onset_coverage = (
            len(original_onsets & playable_onsets) / len(original_onsets)
            if original_onsets else 0.0
        )
        note_ratio = len(playable) / len(original_notes)
        median_fret = sorted(frets)[len(frets) // 2]
        high_fret_ratio = sum(fret >= self.HIGH_FRET for fret in frets) / len(frets)

        score = (
            (0.45 * onset_coverage)
            + (0.35 * note_ratio)
            - (0.03 * median_fret)
            - (0.20 * high_fret_ratio)
        )
        return playable, score

    @staticmethod
    def trim_silence(notes: List[Tuple[int, float, float]], 
                     silence_threshold: float = 0.5) -> List[Tuple[int, float, float]]:
        """
        Elimina silencios al inicio y final de la secuencia de notas
        
        Args:
            notes (List[Tuple[int, float, float]]): Lista de (pitch, start_time, end_time)
            silence_threshold (float): Duración mínima considerada como silencio (segundos)
            
        Returns:
            List[Tuple[int, float, float]]: Notas sin silencios al inicio/final
        """
        if not notes:
            return notes
        
        # Obtener tiempo del primer evento de nota
        first_note_start = notes[0][1]
        last_note_end = notes[-1][2]
        
        # Recalcular tiempos relativos (eliminar silencio del inicio)
        adjusted_notes = []
        for pitch, start, end in notes:
            new_start = start - first_note_start
            new_end = end - first_note_start
            adjusted_notes.append((pitch, new_start, new_end))
        
        return adjusted_notes
