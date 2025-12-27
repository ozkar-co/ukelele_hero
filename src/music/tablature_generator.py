"""
Generador de tablaturas para ukulele a partir de notas MIDI
"""

from typing import List, Tuple, Optional


class UkuleleTableGenerator:
    """Genera tablaturas de ukulele a partir de notas MIDI"""
    
    # Afinación estándar GCEA del ukulele
    # NOTA: En MIDI, C4 = 60
    UKULELE_TUNING = {
        'G4': 67,  # Sol
        'C4': 60,  # Do
        'E4': 64,  # Mi
        'A4': 69,  # La
    }
    
    # Mapa inverso: MIDI pitch -> (cuerda, traste)
    STRING_FRETS = {}
    
    def __init__(self):
        """Inicializa el generador de tablaturas"""
        self._build_fret_map()
    
    def _build_fret_map(self):
        """Construye un mapa de pitches MIDI a trastes del ukulele"""
        # Para cada cuerda, mapear todos los trastes disponibles
        # Tipicamente 12-20 trastes en un ukulele
        
        string_names = ['G', 'C', 'E', 'A']
        string_pitches = [
            self.UKULELE_TUNING['G4'],  # G (cuerda 1)
            self.UKULELE_TUNING['C4'],  # C (cuerda 2)
            self.UKULELE_TUNING['E4'],  # E (cuerda 3)
            self.UKULELE_TUNING['A4'],  # A (cuerda 4)
        ]
        
        # Crear mapa: pitch MIDI -> (nombre_cuerda, traste)
        for string_idx, base_pitch in enumerate(string_pitches):
            for fret in range(20):  # Hasta traste 20
                pitch = base_pitch + fret
                string_name = string_names[string_idx]
                self.STRING_FRETS[pitch] = (string_name, fret)
    
    def generate_tab_from_notes(self, notes: List[Tuple[int, float, float]], 
                                tempo: float = 120,
                                beats_per_measure: int = 4,
                                page_width: int = 80) -> str:
        """
        Genera tablatura paginada a partir de notas MIDI
        
        Args:
            notes (List[Tuple[int, float, float]]): Lista de (pitch, start_time, end_time)
            tempo (float): Tempo en BPM (por defecto 120)
            beats_per_measure (int): Beats por compás (por defecto 4)
            page_width (int): Ancho de página en caracteres (por defecto 80)
            
        Returns:
            str: Tablatura paginada en formato ASCII
        """
        if not notes:
            return "❌ No hay notas para generar tablatura"
        
        # Calcular duración de la canción
        song_duration = notes[-1][2]
        
        # Crear lista de eventos (solo note_on)
        events = []
        for pitch, start, end in notes:
            events.append((start, pitch, 'note_on'))
        
        # Agrupar eventos por tiempo (con pequeña tolerancia)
        time_groups = {}
        for time, pitch, event_type in events:
            time_key = round(time * 100) / 100  # Redondear a 2 decimales
            if time_key not in time_groups:
                time_groups[time_key] = []
            time_groups[time_key].append((pitch, event_type))
        
        sorted_times = sorted(time_groups.keys())
        
        # Ancho disponible para tablatura (menos el nombre de la cuerda)
        tab_width = page_width - 7  # "G----|" = 6 caracteres + 1 espacio
        
        # Dividir tablatura en páginas
        pages = []
        current_page_notes = []
        current_width = 0
        
        for time in sorted_times:
            for pitch, event_type in time_groups[time]:
                if pitch in self.STRING_FRETS:
                    # Cada nota ocupa aproximadamente 2-3 caracteres (traste + separador)
                    note_width = 3
                    
                    if current_width + note_width > tab_width and current_page_notes:
                        # Comenzar nueva página
                        pages.append(current_page_notes)
                        current_page_notes = []
                        current_width = 0
                    
                    current_page_notes.append((time, pitch, event_type))
                    current_width += note_width
        
        if current_page_notes:
            pages.append(current_page_notes)
        
        # Generar output de todas las páginas
        tab_output = []
        
        # Header general
        tab_output.append("═" * page_width)
        tab_output.append("TABLATURA UKULELE - TRACK 1".center(page_width))
        tab_output.append("═" * page_width)
        tab_output.append("")
        tab_output.append(f"Tempo: {tempo} BPM | Duración: {song_duration:.2f}s | Notas: {len(notes)}")
        tab_output.append("")
        tab_output.append("Afinación (GCEA):")
        tab_output.append("G (4ª cuerda) | C (3ª cuerda) | E (2ª cuerda) | A (1ª cuerda)")
        tab_output.append("─" * page_width)
        
        # Generar cada página
        for page_num, page_notes in enumerate(pages, 1):
            tab_output.append(f"\n[Página {page_num}/{len(pages)}]")
            
            # Inicializar líneas de tablatura
            tab_lines_list = ["G----", "C----", "E----", "A----"]
            
            for time, pitch, event_type in page_notes:
                if pitch in self.STRING_FRETS:
                    string, fret = self.STRING_FRETS[pitch]
                    
                    # Mapear strings a líneas
                    string_to_line = {'G': 0, 'C': 1, 'E': 2, 'A': 3}
                    line_idx = string_to_line.get(string, 0)
                    
                    # Agregar el traste
                    fret_str = str(fret)
                    for i in range(len(tab_lines_list)):
                        if i == line_idx:
                            tab_lines_list[i] += fret_str + "-"
                        else:
                            tab_lines_list[i] += "--"
            
            # Agregar líneas al output
            for line in tab_lines_list:
                tab_output.append(line)
            
            if page_num < len(pages):
                tab_output.append("")
                tab_output.append("─" * page_width)
        
        tab_output.append("")
        tab_output.append("═" * page_width)
        
        return "\n".join(tab_output)
    
    def generate_simple_tab(self, notes: List[Tuple[int, float, float]]) -> str:
        """
        Genera una tablatura simple (solo trastes)
        
        Args:
            notes (List[Tuple[int, float, float]]): Lista de (pitch, start_time, end_time)
            
        Returns:
            str: Tablatura simplificada
        """
        if not notes:
            return "❌ No hay notas"
        
        tab = ["═" * 50]
        tab.append("TABLATURA UKULELE (Vista Simple)")
        tab.append("═" * 50)
        tab.append("")
        
        # Información de cada nota
        for idx, (pitch, start, end) in enumerate(notes, 1):
            if pitch in self.STRING_FRETS:
                string, fret = self.STRING_FRETS[pitch]
                duration = end - start
                
                from .midi_loader import MIDILoader
                note_name = MIDILoader.midi_note_to_name(pitch)
                
                tab.append(f"{idx:3d}. Cuerda {string} | Traste {fret:2d} | "
                          f"Nota: {note_name} | Duración: {duration:.2f}s")
        
        tab.append("")
        tab.append("═" * 50)
        
        return "\n".join(tab)
