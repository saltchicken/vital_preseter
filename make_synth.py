import json
import argparse
import sys

# ==========================================
# 1. PATCH DATA REPOSITORY
# ==========================================

PATCH = {
    "preset_name": "Escape From NY Pluck",
    "settings": {
        # Oscillators (Prophet-5 style dual setup)
        "osc_1_on": 1.0,
        "osc_1_unison_voices": 1.0, # Classic mono analog feel
        "osc_2_on": 1.0,
        "osc_2_unison_voices": 1.0,
        "osc_2_pitch_transpose": -12.0, # Sub octave for weight

        # Envelopes (Plucky sequences)
        # Amp Env (Env 1)
        "env_1_attack": 0.005,
        "env_1_decay": 0.45,
        "env_1_sustain": 0.0,
        "env_1_release": 0.2,
        
        # Filter Env (Env 2)
        "env_2_attack": 0.001,
        "env_2_decay": 0.35,
        "env_2_sustain": 0.0,
        "env_2_release": 0.15,

        # Filter (Dark Analog Lowpass)
        "filter_1_on": 1.0,
        "filter_1_cutoff": 28.0, # Low baseline, opened by envelope
        "filter_1_resonance": 0.45, # Squelchy analog bite
        "filter_1_drive": 0.8,

        # LFO (Analog component drift)
        "lfo_1_sync": 0.0,
        "lfo_1_frequency": 0.2,

        # Effects (Classic delay for the sequencer feel)
        "delay_on": 1.0,
        "delay_feedback": 0.4,
        "delay_dry_wet": 0.35,
        "reverb_on": 1.0,
        "reverb_size": 0.3,
        "reverb_decay_time": 0.4,
        "reverb_dry_wet": 0.15,
    },
    "modulations": [
        # Filter Envelope plucking the cutoff (Mod 1 -> Index 0)
        {"index": 0, "source": "env_2", "destination": "filter_1_cutoff", "amount": 0.55, "bipolar": 0.0},
        # Vintage Pitch Drift on Osc 1 (Mod 2 -> Index 1)
        {"index": 1, "source": "lfo_1", "destination": "osc_1_tune", "amount": 0.008, "bipolar": 1.0},
        # Vintage Pitch Drift on Osc 2 (Mod 3 -> Index 2)
        {"index": 2, "source": "lfo_1", "destination": "osc_2_tune", "amount": -0.011, "bipolar": 1.0},
    ]
}


# ==========================================
# 2. ENGINE LOGIC
# ==========================================

def apply_patch(input_file, output_file, patch_data):
    """Loads a template, injects patch data, and saves the new preset."""
    # 1. Safely load the template
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find the template file at '{input_file}'. Did you export it from Vital?")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{input_file}' is not a valid JSON file. It may be corrupted.")
        sys.exit(1)

    # 2. Update Root Metadata
    if "preset_name" in patch_data:
        data["preset_name"] = patch_data["preset_name"]

    # Ensure settings dictionary exists
    settings = data.get('settings', {})

    # 3. Apply standard settings
    for key, value in patch_data.get("settings", {}).items():
        settings[key] = value

    # 4. Apply Modulations (Original Override Method)
    # We pad the list just in case it's shorter than expected to avoid IndexError
    if 'modulations' not in settings:
        settings['modulations'] = []
        
    for mod in patch_data.get("modulations", []):
        idx = mod["index"]
        mod_num = idx + 1 # 1-based for the amount/bipolar keys
        
        while len(settings['modulations']) <= idx:
            settings['modulations'].append({})
            
        settings['modulations'][idx] = {
            "source": mod["source"],
            "destination": mod["destination"]
        }
        
        settings[f'modulation_{mod_num}_amount'] = mod["amount"]
        settings[f'modulation_{mod_num}_bipolar'] = mod["bipolar"]

    data['settings'] = settings

    # 5. Save the modified JSON
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2) 
        print(f"Success! Saved preset to {output_file}")
    except Exception as e:
        print(f"Error writing file: {e}")
        sys.exit(1)


# ==========================================
# 3. CLI INTERFACE
# ==========================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vital Preset Generator: Build presets programmatically.")
    parser.add_argument("-i", "--input", default="vital-init.vital", help="Path to the source .vital Init template")
    parser.add_argument("-o", "--output", help="Path for the generated output preset (defaults to preset_name)")
    
    args = parser.parse_args()
    
    # Dynamically determine the output filename
    output_filename = args.output
    if not output_filename:
        preset_name = PATCH.get("preset_name", "Generated_Preset")
        # Replace spaces with underscores for safe cross-platform file names
        output_filename = f"{preset_name.replace(' ', '_')}.vital"
    
    apply_patch(args.input, output_filename, PATCH)
