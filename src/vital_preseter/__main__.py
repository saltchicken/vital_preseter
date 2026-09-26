import json
import argparse
import sys
import importlib.resources as pkg_resources
from pathlib import Path
from typing import Any, Dict, List

# ==========================================
# 1. I/O AND ASSET MANAGEMENT
# ==========================================

def load_json_file(path: Path) -> Any:
    """Loads and parses a JSON file from the filesystem."""
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find file at '{path}'.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: '{path}' is not a valid JSON file. {e}")
        sys.exit(1)

def save_json_file(path: Path, data: Dict[str, Any]) -> None:
    """Saves a dictionary to a JSON file on the filesystem."""
    # Ensure the parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Success! Saved preset to {path}")
    except Exception as e:
        print(f"Error writing file to {path}: {e}")
        sys.exit(1)

def load_bundled_asset(filename: str) -> Any:
    """Loads a JSON asset bundled within the installed Python package."""
    try:
        # read_text is compatible with Python >=3.8
        content = pkg_resources.read_text('vital_preseter.assets', filename)
        return json.loads(content)
    except FileNotFoundError:
        print(f"Error: Bundled asset '{filename}' not found. Is the package installed correctly?")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Bundled asset '{filename}' is corrupted.")
        sys.exit(1)

# ==========================================
# 2. CORE ENGINE LOGIC
# ==========================================

def mutate_preset(template_data: Dict[str, Any], patch_data: Dict[str, Any], wt_lib: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Injects patch data into the vital template and returns the modified dictionary."""
    data = template_data.copy()

    if "preset_name" in patch_data:
        data["preset_name"] = patch_data["preset_name"]

    settings = data.get('settings', {})

    # Apply top-level settings
    for key, value in patch_data.get("settings", {}).items():
        settings[key] = value

    # Process modulations
    if 'modulations' not in settings:
        settings['modulations'] = []
        
    next_idx = 0
    for mod in patch_data.get("modulations", []):
        # Auto-assign index if omitted, preventing KeyErrors and accidental overwrites
        idx = mod.get("index", next_idx)
        if idx >= next_idx:
            next_idx = idx + 1
            
        mod_num = idx + 1 
        
        while len(settings['modulations']) <= idx:
            settings['modulations'].append({"source": "", "destination": ""})
            
        settings['modulations'][idx] = {
            "source": mod.get("source", ""),
            "destination": mod.get("destination", "")
        }
        
        # Apply all Vital modulation attributes
        settings[f'modulation_{mod_num}_amount'] = mod.get("amount", 0.0)
        settings[f'modulation_{mod_num}_bipolar'] = mod.get("bipolar", 0.0)
        settings[f'modulation_{mod_num}_power'] = mod.get("power", 0.0)
        settings[f'modulation_{mod_num}_stereo'] = mod.get("stereo", 0.0)
        settings[f'modulation_{mod_num}_bypass'] = mod.get("bypass", 0.0)

    # Process wavetables
    if "wavetables" not in settings:
        settings["wavetables"] = [{}, {}, {}]

    if "use_wavetables" in patch_data:
        wt_dict = {wt.get("name", ""): wt for wt in wt_lib}
        
        for i, wt_name in enumerate(patch_data["use_wavetables"]):
            if wt_name in wt_dict:
                if i < len(settings["wavetables"]):
                    settings["wavetables"][i] = wt_dict[wt_name]
            else:
                print(f"Warning: Wavetable '{wt_name}' not found in library.")

    elif "wavetables" in patch_data:
        if len(patch_data["wavetables"]) == 3:
            settings["wavetables"] = patch_data["wavetables"]
        else:
            print("Warning: Direct 'wavetables' array must have exactly 3 elements. Skipping injection.")

    data['settings'] = settings
    return data


# ==========================================
# 3. CLI INTERFACE
# ==========================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Vital Preset Generator: Build presets programmatically.")
    parser.add_argument("-p", "--patch", required=True, type=Path, help="Path to the JSON patch definition file")
    parser.add_argument("-i", "--input", type=Path, help="Path to a custom source .vital Init template (optional)")
    parser.add_argument("-o", "--output", type=Path, help="Path for the generated output preset")
    parser.add_argument("-w", "--wavetables", type=Path, help="Path to a custom wavetable JSON library (optional)")
    
    args = parser.parse_args()
    
    # 1. Load the patch file
    patch_data = load_json_file(args.patch)
    
    # 2. Load Template (use explicitly provided path, or fall back to package asset)
    if args.input:
        template_data = load_json_file(args.input)
    else:
        template_data = load_bundled_asset("vital-init.vital")
        
    # 3. Load Wavetables (use explicitly provided path, or fall back to package asset)
    if args.wavetables:
        wt_lib = load_json_file(args.wavetables)
    else:
        wt_lib = load_bundled_asset("wavetables.json")
        
    # 4. Build the preset dictionary
    new_preset_data = mutate_preset(template_data, patch_data, wt_lib)
    
    # 5. Determine exact output path
    output_path = args.output
    if not output_path:
        # Fallback to local ./presets/ folder if no specific path is given
        preset_name = patch_data.get("preset_name", "Generated_Preset")
        output_filename = f"{preset_name.replace(' ', '_')}.vital"
        output_path = Path("presets") / output_filename
        
    # 6. Save the final file
    save_json_file(output_path, new_preset_data)

if __name__ == "__main__":
    main()
