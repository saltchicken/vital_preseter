import json
import argparse
import sys
import os

# ==========================================
# 1. ENGINE LOGIC
# ==========================================

def apply_patch(input_file, output_file, patch_data, wt_lib_path="wavetables.json"):
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

    # --- WAVETABLE INJECTION LOGIC ---
    # Vital strictly requires exactly 3 wavetables INSIDE the 'settings' block.
    if "wavetables" not in settings:
        settings["wavetables"] = [{}, {}, {}] # Failsafe fallback

    if "use_wavetables" in patch_data:
        try:
            with open(wt_lib_path, 'r', encoding='utf-8') as f:
                wt_lib = json.load(f)
            
            # Map wavetable names to their data blocks
            wt_dict = {wt.get("name", ""): wt for wt in wt_lib}
            
            for i, wt_name in enumerate(patch_data["use_wavetables"]):
                if wt_name in wt_dict:
                    if i < len(settings["wavetables"]):
                        settings["wavetables"][i] = wt_dict[wt_name]
                else:
                    print(f"Warning: Wavetable '{wt_name}' not found in {wt_lib_path}.")

        except FileNotFoundError:
            print(f"Warning: Wavetable library '{wt_lib_path}' not found. Cannot inject named wavetables.")
    
    # Fallback: Direct injection if full array is provided in patch file
    elif "wavetables" in patch_data:
        if len(patch_data["wavetables"]) == 3:
            settings["wavetables"] = patch_data["wavetables"]
        else:
            print("Warning: Direct 'wavetables' array must have exactly 3 elements. Skipping injection.")

    # ---------------------------------

    # Reattach the updated settings block back to the main data
    data['settings'] = settings

    output_file = f"presets/{output_file}"

    # Ensure presets directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

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
    parser.add_argument("-o", "--output", help="Path for the generated output preset")
    parser.add_argument("-w", "--wavetables", default="wavetables.json", help="Path to the wavetable JSON library")
    
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
    apply_patch(args.input, output_filename, patch_data, args.wavetables)

if __name__ == "__main__":
    main()
