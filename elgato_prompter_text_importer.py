import os
import json
import uuid

def get_appdata_path():
    return os.environ.get('APPDATA', '')

def convert_text_file(file_path):
    # Read the text file and split it into nonempty, stripped lines (chapters)
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def generate_json_data(chapters, guid_str, friendly_name, index):
    # Build the JSON structure
    data = {
        "GUID": guid_str,
        "chapters": chapters,
        "friendlyName": friendly_name,
        "index": index
    }
    return data

def save_json_to_texts(data, guid_str):
    # Build the destination directory path: %APPDATA%\Elgato\CameraHub\Texts
    appdata = get_appdata_path()
    dest_dir = os.path.join(appdata, "Elgato", "CameraHub", "Texts")
    os.makedirs(dest_dir, exist_ok=True)
    # Save file as GUID.json
    file_path = os.path.join(dest_dir, f"{guid_str}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return file_path

def update_appsettings(guid_str):
    # Path to AppSettings.json: %APPDATA%\Elgato\CameraHub\AppSettings.json
    appdata = get_appdata_path()
    settings_path = os.path.join(appdata, "Elgato", "CameraHub", "AppSettings.json")
    
    # Load existing settings, or create a new dict if the file doesn't exist or is empty.
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = {}
    else:
        settings = {}
    
    # Ensure the key exists as a list
    key = "applogic.prompter.libraryList"
    if key not in settings or not isinstance(settings[key], list):
        settings[key] = []
    
    # Append the new GUID (without extension) if it's not already present.
    if guid_str not in settings[key]:
        settings[key].append(guid_str)
    
    # Write back the settings
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
    
    return settings_path

def main():
    # Step 0: Ask for the text file
    text_file = input("Enter the path to the text file: ").strip()
    if not os.path.isfile(text_file):
        print("The provided file does not exist.")
        return
    
    # Step 1: Convert TYPE1 text to chapters (TYPE2 conversion)
    chapters = convert_text_file(text_file)
    
    # Ask for additional information
    friendly_name = input("Enter the friendly name: ").strip()
    
    while True:
        try:
            index = int(input("Enter the index (as an integer): ").strip())
            break
        except ValueError:
            print("Please enter a valid integer for the index.")
    
    # Step 2: Generate a GUID (uppercase) to use as filename (without extension)
    guid_str = str(uuid.uuid4()).upper()
    
    # Build the JSON data structure
    json_data = generate_json_data(chapters, guid_str, friendly_name, index)
    
    # Save the JSON file into %APPDATA%\Elgato\CameraHub\Texts
    saved_path = save_json_to_texts(json_data, guid_str)
    print(f"Saved TYPE2 JSON to: {saved_path}")
    
    # Step 3: Update AppSettings.json to include the new file (GUID without extension)
    settings_path = update_appsettings(guid_str)
    print(f"Updated AppSettings.json at: {settings_path}")

if __name__ == "__main__":
    main()
