import json

def build_blade_runner_preset(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # 1. Update Metadata
    data['preset_name'] = "Blade Runner CS-80 V2"
    settings = data.get('settings', {})

    # 2. Oscillators (Lush 5-voice unison)
    settings['osc_1_unison_voices'] = 5.0
    settings['osc_1_unison_detune'] = 3.0 # Slightly lower than default for tighter brass
    
    settings['osc_2_on'] = 1.0
    settings['osc_2_unison_voices'] = 5.0
    settings['osc_2_unison_detune'] = 4.0 
    settings['osc_2_pitch_transpose'] = -12.0 # Drop Osc 2 an octave for thick low-end

    # 3. Envelopes (Classic CS-80 Brass Shape)
    # Env 1 (Amp - Fast swell, decays to 60% sustain, long cinematic release)
    settings['env_1_attack'] = 0.15  
    settings['env_1_decay'] = 1.5    
    settings['env_1_sustain'] = 0.6  
    settings['env_1_release'] = 2.0  
    
    # Env 2 (Filter - Plucks faster than the amp, drops to low sustain)
    settings['env_2_attack'] = 0.08  
    settings['env_2_decay'] = 1.0    
    settings['env_2_sustain'] = 0.2  
    settings['env_2_release'] = 2.0  

    # 4. Filter (Analog 24dB, starting very dark)
    settings['filter_1_on'] = 1.0
    settings['filter_1_cutoff'] = 35.0  # MIDI Note value (Low, around B1)
    settings['filter_1_resonance'] = 0.35 # Just enough to "quack" on the attack
    settings['filter_1_drive'] = 1.5 # Warm analog saturation

    # 5. LFO (Very slow, free-running for tape drift)
    settings['lfo_1_sync'] = 0.0 # Free running mode
    settings['lfo_1_frequency'] = 0.15 # Very slow Hz

    # 6. Effects
    settings['chorus_on'] = 1.0
    settings['chorus_dry_wet'] = 0.35
    
    settings['reverb_on'] = 1.0
    settings['reverb_size'] = 0.75
    settings['reverb_decay_time'] = 0.6
    settings['reverb_dry_wet'] = 0.35 # Cinematic tail

    # 7. Modulation Routing (Strictly Normalized 0.0 - 1.0)
    
    # Mod 1: Env 2 opening the Filter
    data['settings']['modulations'][0] = {"destination": "filter_1_cutoff", "source": "env_2"}
    # 0.35 = 35% of the total filter frequency range
    data['settings']['modulation_1_amount'] = 0.35 
    data['settings']['modulation_1_bipolar'] = 0.0
    
    # Mod 2: LFO 1 modulating Osc 1 Pitch (Vintage Drift)
    data['settings']['modulations'][1] = {"destination": "osc_1_tune", "source": "lfo_1"}
    # 0.008 = A fraction of a semitone. Perfect analog wobble.
    data['settings']['modulation_2_amount'] = 0.008 
    data['settings']['modulation_2_bipolar'] = 1.0 # Swing pitch up AND down
    
    # Mod 3: LFO 1 modulating Osc 2 Pitch (Inverted for wide stereo feel)
    data['settings']['modulations'][2] = {"destination": "osc_2_tune", "source": "lfo_1"}
    data['settings']['modulation_3_amount'] = -0.008 
    data['settings']['modulation_3_bipolar'] = 1.0

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2) 
        print(f"Success! Saved fixed preset to {output_file}")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    build_blade_runner_preset("vital-init.vital", "BladeRunnerCS80_Fixed.vital")
