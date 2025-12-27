# 🎮 Ukulele Hero - Quick Start Guide

## Installation & Setup

### Prerequisites
- Python 3.14+
- Virtual environment (already created: `venv/`)

### Run the Game

```bash
# Navigate to project directory
cd c:\Users\oscar\Documents\Code\ukelele_hero

# Run the game
./venv/Scripts/python.exe game_main.py
```

**Expected Output:**
```
pygame-ce 2.5.6 (SDL 2.32.10, Python 3.14.2)
[pygame window opens with menu]
```

## Game Controls

### Main Menu
| Key | Action |
|-----|--------|
| ⬆️ Arrow Up | Select Previous |
| ⬇️ Arrow Down | Select Next |
| ENTER | Select Option |
| ESC | Quit |

### Tablature Game Mode
| Key | Action |
|-----|--------|
| G | Play G String (testing) |
| C | Play C String (testing) |
| E | Play E String (testing) |
| A | Play A String (testing) |
| SPACE | Pause Game |
| ESC | Return to Menu |

**Or use your microphone:**
- Play actual notes on your ukulele
- System detects pitch and validates hits

### Tuner Mode
| Key | Action |
|-----|--------|
| ESC | Return to Menu |

- Play any note on ukulele
- Visual feedback shows tuning accuracy

## Available Tablatures

Currently saved tablatures in `assets/tablatures/`:

1. **escala_ejemplo_track0_oct+0**
   - Scale exercise with 8 notes
   - Tempo: 120 BPM
   - Duration: 4 seconds
   - Perfect for testing note scrolling mechanics

2. **saria_song_track0_oct-1**
   - Saria's Song from Zelda
   - Custom octave transposition
   - Longer phrase to test endurance

## Game Mechanics

### Note Scrolling
```
RIGHT EDGE (spawn)  →  HIT ZONE (x=150)  →  LEFT EDGE
[time 0s]      [musical time]              [note age]
```

Notes travel horizontally from right to left. Hit them when they reach the gray hit zone on the left.

### Scoring System
| Timing Error | Points | Status |
|--------------|--------|--------|
| < 50ms | 1000 | PERFECT |
| < 100ms | 500 | GOOD |
| < 250ms | 100 | OK |
| > 250ms | 0 | MISS |

### String Lanes
```
G (Green)   ├─────────────────────────────────
C (Blue)    ├─────────────────────────────────
E (Red)     ├─────────────────────────────────
A (Yellow)  ├─────────────────────────────────
            0%    25%   50%   75%   100% (Time)
```

## Creating New Tablatures

### Method 1: Interactive Tool
```bash
./venv/Scripts/python.exe tools/create_tablature.py
```

Follow prompts to:
1. Select a MIDI file from `assets/midi/`
2. Choose which track to extract
3. Configure octave transposition (auto or manual ±2)
4. Add description
5. Save as JSON

### Method 2: Direct MIDI Processing
```bash
./venv/Scripts/python.exe tools/midi_tool.py path/to/midi.mid --track 0 --transpose auto
```

New tablatures save to `assets/tablatures/` automatically.

## Troubleshooting

### Game Won't Start
```bash
# Verify dependencies
./venv/Scripts/python.exe -m pip list

# Check python version
./venv/Scripts/python.exe --version

# Expected: Python 3.14.x
```

### No Audio Detection
- Ensure microphone is connected and enabled
- Check system audio input settings
- Test with speaker/recording to verify microphone works

### Tablatures Not Showing
```bash
# Check available tablatures
./venv/Scripts/python.exe test_game_execution.py

# Should list files in assets/tablatures/
```

### Notes Scrolling Too Fast/Slow
- Tempo is configured per tablature in JSON
- Edit `assets/tablatures/*.json` and change `"tempo"` value
- Higher BPM = faster scrolling
- Default: 120 BPM

## Performance Notes

- **FPS Target:** 60 FPS (adjustable in config.py)
- **Input Latency:** < 50ms for keyboard testing
- **Audio Latency:** ~100-200ms (depends on microphone/soundcard)
- **CPU Usage:** ~5-15% during gameplay

## Project Structure

```
ukelele_hero/
├── game_main.py              # Entry point
├── src/
│   ├── audio/               # Audio processing
│   ├── game/                # Game modes
│   ├── music/               # MIDI & tablatures
│   ├── utils/               # Configuration & helpers
│   └── config.py            # Game settings
├── assets/
│   ├── midi/                # MIDI files
│   └── tablatures/          # Saved tablatures (JSON)
├── tools/                   # Utility scripts
├── tests/                   # Test files
└── venv/                    # Python virtual environment
```

## Configuration

Edit `src/utils/config.py` to customize:

```python
# Window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Game speed
NOTE_SPEED_PIXELS_PER_SECOND = 400

# Hit zone position
HIT_ZONE_X = 150
HIT_ZONE_WIDTH = 40

# Audio parameters
SAMPLE_RATE = 44100
BUFFER_SIZE = 4096

# Colors (RGB tuples)
STRING_COLORS = {
    'G': GREEN,
    'C': BLUE,
    'E': RED,
    'A': YELLOW
}
```

## Help & Support

### Check Game Status
```bash
./venv/Scripts/python.exe test_game_execution.py
```

### View Game Documentation
See [GAME_STATUS.md](GAME_STATUS.md) for detailed system information

### Test Individual Components
```bash
# Test MIDI loading
./venv/Scripts/python.exe tools/test_tablature.py

# Test audio detection
python -c "from src.audio.note_detector import NoteDetector; print('Audio OK')"
```

## Tips for Better Gameplay

1. **Get the Feel** - Play first level slowly to understand note timing
2. **Listen to Tempo** - Pay attention to BPM for rhythm
3. **Warm Up** - Practice with scale exercises first
4. **Adjust Speed** - Slower custom tablatures available
5. **Use Microphone** - More accurate than keyboard simulation

---

**Ready to play? Run `game_main.py` and select "Modo Juego"!** 🎸🎵
