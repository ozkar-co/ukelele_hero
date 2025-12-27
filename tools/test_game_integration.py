"""
Ejemplo de integración de tablaturas en la UI del juego
"""

import sys
from pathlib import Path
import json

# Agregar src al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from music.tablature_manager import TablatureManager


class GameTablatureLoader:
    """Cargador de tablaturas para la UI del juego"""
    
    def __init__(self):
        self.manager = TablatureManager()
        self.current_tablature = None
    
    def list_available_tablatures(self):
        """Lista todas las tablaturas guardadas"""
        tablatures = self.manager.get_saved_tablatures()
        return tablatures
    
    def load_tablature_for_game(self, tablature_name):
        """
        Carga una tablatura para usar en el juego
        
        Args:
            tablature_name (str): Nombre de la tablatura guardada
            
        Returns:
            Dict: Datos formateados para la UI o None
        """
        # Cargar datos JSON
        tab_data = self.manager.load_tablature(tablature_name)
        
        if not tab_data:
            return None
        
        # Convertir a formato UI
        ui_data = self.manager.export_to_ui_format(tab_data)
        self.current_tablature = ui_data
        
        return ui_data
    
    def get_notes_for_string(self, string_name):
        """
        Obtiene las notas de una cuerda específica
        
        Args:
            string_name (str): Nombre de la cuerda (G, C, E, A)
            
        Returns:
            List: Notas de esa cuerda
        """
        if not self.current_tablature:
            return []
        
        return self.current_tablature['strings'].get(string_name, [])
    
    def get_all_notes_sorted_by_time(self):
        """
        Obtiene todas las notas ordenadas por tiempo
        
        Returns:
            List: Todas las notas ordenadas
        """
        if not self.current_tablature:
            return []
        
        all_notes = []
        for string_name, notes in self.current_tablature['strings'].items():
            all_notes.extend(notes)
        
        # Ordenar por tiempo de inicio
        all_notes.sort(key=lambda n: n['start_time'])
        
        return all_notes
    
    def get_tablature_info(self):
        """Obtiene información general de la tablatura actual"""
        if not self.current_tablature:
            return None
        
        return {
            'source': self.current_tablature['source'],
            'track': self.current_tablature['track'],
            'tempo': self.current_tablature['tempo'],
            'total_notes': self.current_tablature['total_notes'],
            'duration': self.current_tablature['statistics']['duration'],
            'octaves_transposed': self.current_tablature['octaves_transposed']
        }


# Ejemplo de uso
def main():
    print("\n" + "="*60)
    print("🎮 EJEMPLO - Integración en UI del Juego")
    print("="*60 + "\n")
    
    loader = GameTablatureLoader()
    
    # Listar tablaturas disponibles
    tablatures = loader.list_available_tablatures()
    
    print("📊 Tablaturas disponibles:")
    for idx, tab_name in enumerate(tablatures, 1):
        print(f"   {idx}. {tab_name}")
    
    if not tablatures:
        print("   (Ninguna)")
        return
    
    # Cargar la primera tablatura
    print(f"\n⏳ Cargando: {tablatures[0]}...")
    data = loader.load_tablature_for_game(tablatures[0])
    
    if not data:
        return
    
    # Mostrar información
    info = loader.get_tablature_info()
    print(f"\n✅ Información de la Tablatura:")
    print(f"   Fuente: {info['source']}")
    print(f"   Pista: {info['track']}")
    print(f"   Tempo: {info['tempo']} BPM")
    print(f"   Notas totales: {info['total_notes']}")
    print(f"   Duración: {info['duration']:.2f}s")
    print(f"   Transposición: {info['octaves_transposed']:+d} octava(s)")
    
    # Ejemplo: Acceder a notas de una cuerda específica
    print(f"\n🎸 Notas de la cuerda A:")
    notes_a = loader.get_notes_for_string('A')
    for note in notes_a:
        print(f"   Traste {note['fret']} ({note['note']}) | "
              f"Tiempo: {note['start_time']:.2f}s - {note['end_time']:.2f}s | "
              f"Duración: {note['duration']:.2f}s")
    
    # Ejemplo: Obtener todas las notas en orden temporal
    print(f"\n⏱️ Todas las notas en orden temporal:")
    all_notes = loader.get_all_notes_sorted_by_time()
    for idx, note in enumerate(all_notes[:10], 1):  # Mostrar solo las primeras 10
        string_map = {'G': '4ª', 'C': '3ª', 'E': '2ª', 'A': '1ª'}
        string_num = string_map.get(note.get('string'), '?')
        print(f"   {idx}. Cuerda {string_num} | Traste {note['fret']} ({note['note']}) | "
              f"Tiempo: {note['start_time']:.2f}s")
    
    if len(all_notes) > 10:
        print(f"   ... y {len(all_notes) - 10} más")
    
    # Mostrar estructura JSON para debugging
    print(f"\n💾 Estructura JSON completa (para debugging):")
    print("─" * 60)
    print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")


if __name__ == "__main__":
    main()
