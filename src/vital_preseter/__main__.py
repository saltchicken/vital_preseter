import json
import argparse
import sys

# ==========================================
# 1. ENGINE LOGIC
# ==========================================

def apply_patch(input_file, output_file, patch_data):
    """Loads a template, injects patch data, and saves the new preset."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find the template file at '{input_file}'. Did you export it from Vital?")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{input_file}' is not a valid JSON file. It may be corrupted.")
        sys.exit(1)

    if "preset_name" in patch_data:
        data["preset_name"] = patch_data["preset_name"]

    settings = data.get('settings', {})

    for key, value in patch_data.get("settings", {}).items():
        settings[key] = value

    if 'modulations' not in settings:
        settings['modulations'] = []
        
    for mod in patch_data.get("modulations", []):
        idx = mod["index"]
        mod_num = idx + 1 
        
        while len(settings['modulations']) <= idx:
            settings['modulations'].append({})
            
        settings['modulations'][idx] = {
            "source": mod["source"],
            "destination": mod["destination"]
        }
        
        settings[f'modulation_{mod_num}_amount'] = mod["amount"]
        settings[f'modulation_{mod_num}_bipolar'] = mod["bipolar"]

    data['settings'] = settings

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2) 
        print(f"Success! Saved preset to {output_file}")
    except Exception as e:
        print(f"Error writing file: {e}")
        sys.exit(1)


# ==========================================
# 2. CLI INTERFACE
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="Vital Preset Generator: Build presets programmatically.")
    parser.add_argument("-p", "--patch", required=True, help="Path to the JSON patch definition file")
    parser.add_argument("-i", "--input", default="vital-init.vital", help="Path to the source .vital Init template")
    parser.add_argument("-o", "--output", help="Path for the generated output preset (defaults to preset_name)")
    
    args = parser.parse_args()
    
    # 1. Load the external patch file
    try:
        with open(args.patch, 'r', encoding='utf-8') as f:
            patch_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find patch file '{args.patch}'.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: '{args.patch}' is not valid JSON. {e}")
        sys.exit(1)
    
    # 2. Dynamically determine the output filename
    output_filename = args.output
    if not output_filename:
        preset_name = patch_data.get("preset_name", "Generated_Preset")
        output_filename = f"{preset_name.replace(' ', '_')}.vital"
    
    # 3. Build the preset
    apply_patch(args.input, output_filename, patch_data)

if __name__ == "__main__":
    main()
