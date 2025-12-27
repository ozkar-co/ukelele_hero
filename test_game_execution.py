"""
Test script to verify game execution and functionality
"""

import sys
from pathlib import Path

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from music.tablature_manager import TablatureManager

# Test TablatureManager
print("=" * 60)
print("Testing TablatureManager")
print("=" * 60)

manager = TablatureManager()
tablatures = manager.get_saved_tablatures()

print(f"✓ Found {len(tablatures)} tablatures:")
for tab in tablatures:
    print(f"  - {tab}")

if tablatures:
    first_tab = tablatures[0]
    print(f"\n✓ Loading tablature: {first_tab}")
    
    try:
        notes = manager.load_tablature(first_tab)
        print(f"✓ Loaded {len(notes['notes'])} notes")
        print(f"  - Tempo: {notes['configuration']['tempo']} BPM")
        print(f"  - Octave adjustment: {notes['configuration']['octaves_transposed']}")
        print(f"  - Source: {notes['source']['midi_file']}")
        
        # Show first few notes
        print(f"\n  First 3 notes:")
        for i, note in enumerate(notes['notes'][:3]):
            print(f"    [{i+1}] Pitch: {note['pitch']}, Time: {note['start_time']:.2f}s, Duration: {note['end_time']-note['start_time']:.2f}s")
            
    except Exception as e:
        print(f"✗ Error loading tablature: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("Game Ready! Use game_main.py to launch the UI")
print("=" * 60)
