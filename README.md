# Vital Preset Builder: Blade Runner CS-80 Pad

This script provides a safe, programmatic way to generate custom presets for the [Vital Synthesizer](https://vital.audio/) using Python. 

By default, this script transforms a blank Init patch into a lush, vintage CS-80 style brass pad inspired by the *Blade Runner* soundtrack—complete with analog filter drive, cinematic reverb, and slow pitch drift to simulate vintage hardware.

## Why use Python instead of writing the JSON directly?
Although `.vital` presets are technically plain text JSON files, they contain massive Base64-encoded audio blobs for their wavetables and noises. Attempting to write a `.vital` file from a blank page (or generating one from scratch using an LLM) almost always truncates the audio data or misses mandatory C++ schema keys, resulting in a corrupted file that crashes the synth.

This script uses a **template injection method**. It parses a valid, pre-existing Init patch, safely injects the new modulation routing and parameter math into the JSON dictionary, and saves a new file. The critical audio blobs remain untouched.

## Prerequisites
* Python 3.x
* [Vital Synthesizer](https://vital.audio/) (Standalone or Plugin)

## Usage Instructions

### 1. Export an Init Template
First, you need to provide the script with a clean slate that contains your system's default wavetable data.
1. Open Vital.
2. Click the **hamburger menu** (three horizontal lines) at the top center.
3. Click **Init Preset**.
4. Click the menu again and select **Save External Preset**.
5. Save the file in the same directory as this script and name it exactly `vital-init.vital`.

### 2. Run the Script
Open your terminal in the directory containing the script and your template, then run:

```bash
python make_synth.py
```

If successful, the script will output:
`Success! Saved fixed preset to BladeRunnerCS80_Fixed.vital`

### 3. Load the New Sound
1. Go back to Vital.
2. Click the **hamburger menu** and select **Open External Preset**.
3. Select the newly generated `BladeRunnerCS80_Fixed.vital`.
4. Play a chord! (If you want to keep it in your permanent library, click the Save icon at the top).

## Customizing the Script
You can use `make_synth.py` as a master template to programmatically build any patch you want. 

**A warning on Vital's internal math:**
If you start changing the parameter values in the Python script, be aware that Vital normalizes almost all of its modulation amounts to a `0.0` to `1.0` float scale. 
* Do not pass human-readable values (like `35.0`) to a modulation amount. It will blow past the 1.0 limit and max out the synth engine, creating audio glitches. 
* For example, to modulate the filter by 35%, set `"modulation_1_amount": 0.35`. 
* To create a slight pitch wobble, set the modulation amount to something tiny like `0.008`.
