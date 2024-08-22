import os
import xml.etree.ElementTree as ET
from typesense import Client
import time

# Typesense client configuration
client_config = {
    'nodes': [{
        'host': 'typesense.documentresearch.dev',
        'port': '8080',
        'protocol': 'http'
    }],
    'api_key': os.getenv('TYPESENSE_API_KEY'),
    'connection_timeout_seconds': 10,
    'num_retries': 3,
    'retry_interval_seconds': 1
}

# Initialize Typesense client
client = Client(client_config)

# Path for the processed files list
PROCESSED_FILES_PATH = 'processed_files.txt'

def load_processed_files():
    if os.path.exists(PROCESSED_FILES_PATH):
        with open(PROCESSED_FILES_PATH, 'r') as f:
            return set(f.read().splitlines())
    return set()

def save_processed_file(filename):
    with open(PROCESSED_FILES_PATH, 'a') as f:
        f.write(f"{filename}\n")

# Function to process XML and store in Typesense
def process_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract play information
    play_title = root.find('TITLE').text
    play_id = os.path.splitext(os.path.basename(file_path))[0]

    stats = {
        'plays': {'added': 0, 'skipped': 0},
        'characters': {'added': 0, 'skipped': 0},
        'acts': {'added': 0, 'skipped': 0},
        'scenes': {'added': 0, 'skipped': 0},
        'speeches': {'added': 0, 'skipped': 0}
    }

    # Store play information
    try:
        client.collections['plays'].documents.create({
            'id': play_id,
            'title': play_title,
            'fm': ' '.join([p.text for p in root.find('FM').findall('P')]),
            'scndescr': root.find('SCNDESCR').text,
            'playsubt': root.find('PLAYSUBT').text
        })
        stats['plays']['added'] += 1
    except Exception as e:
        if 'already exists' in str(e):
            print(f"Play document for {play_id} already exists. Skipping play creation.")
            stats['plays']['skipped'] += 1
        else:
            print(f"Error creating play document: {str(e)}")
            return False, stats

    def get_character_context(persona):
        parent = persona.getparent()
        if parent.tag == 'PGROUP':
            grpdescr = parent.find('GRPDESCR')
            group_desc = grpdescr.text if grpdescr is not None else None
            return group_desc, None
        elif parent.tag == 'PERSONAE':
            # Check if the next element is the character's description
            next_elem = persona.getnext()
            if next_elem is not None and next_elem.tag == 'GRPDESCR':
                return None, next_elem.text
        return None, None

    # Process characters
    for persona in root.findall('.//PERSONA'):
        character_name = persona.text.strip()
        group_desc, individual_desc = get_character_context(persona)

        character_id = f"{play_id}_{character_name.replace(' ', '_').lower()}"

        try:
            character_data = {
                'id': character_id,
                'play_id': play_id,
                'name': character_name,
            }
            if group_desc:
                character_data['group_description'] = group_desc
            if individual_desc:
                character_data['individual_description'] = individual_desc

            client.collections['characters'].documents.create(character_data)
            stats['characters']['added'] += 1
            print(f"Added character: {character_name} in {play_id}")
            if group_desc:
                print(f"  Group description: {group_desc}")
            if individual_desc:
                print(f"  Individual description: {individual_desc}")
        except Exception as e:
            if 'already exists' in str(e):
                print(f"Character {character_name} already exists in Typesense. Updating...")
                client.collections['characters'].documents[character_id].update(character_data)
                stats['characters']['updated'] += 1
            else:
                print(f"Error creating/updating character document: {str(e)}")
                stats['characters']['skipped'] += 1

    # Process acts, scenes, speeches
    for act_num, act in enumerate(root.findall('ACT'), 1):
        act_id = f"{play_id}_act_{act_num}"
        try:
            client.collections['acts'].documents.create({
                'id': act_id,
                'play_id': play_id,
                'title': act.find('TITLE').text,
                'act_number': act_num
            })
            stats['acts']['added'] += 1
        except Exception as e:
            if 'already exists' in str(e):
                print(f"Act document for {act_id} already exists. Skipping.")
                stats['acts']['skipped'] += 1
            else:
                print(f"Error creating act document: {str(e)}")
                continue

        for scene_num, scene in enumerate(act.findall('SCENE'), 1):
            scene_id = f"{act_id}_scene_{scene_num}"
            try:
                client.collections['scenes'].documents.create({
                    'id': scene_id,
                    'act_id': act_id,
                    'title': scene.find('TITLE').text,
                    'scene_number': scene_num
                })
                stats['scenes']['added'] += 1
            except Exception as e:
                if 'already exists' in str(e):
                    print(f"Scene document for {scene_id} already exists. Skipping.")
                    stats['scenes']['skipped'] += 1
                else:
                    print(f"Error creating scene document: {str(e)}")
                    continue

            for speech_num, speech in enumerate(scene.findall('SPEECH'), 1):
                speaker = speech.find('SPEAKER').text
                content = ' '.join([line.text for line in speech.findall('LINE') if line.text])
                speech_id = f"{scene_id}_{speaker.replace(' ', '_').lower()}_{speech_num}"
                try:
                    client.collections['speeches'].documents.create({
                        'id': speech_id,
                        'scene_id': scene_id,
                        'speaker': speaker,
                        'content': content
                    })
                    stats['speeches']['added'] += 1
                except Exception as e:
                    if 'already exists' in str(e):
                        print(f"Speech document for {speech_id} already exists. Skipping.")
                        stats['speeches']['skipped'] += 1
                    else:
                        print(f"Error creating speech document: {str(e)}")

    return True, stats

# Load the list of processed files
processed_files = load_processed_files()

# Find and process all XML files in the 'data' subdirectory
data_dir = 'data'
for filename in os.listdir(data_dir):
    if filename.endswith('.xml') and filename not in processed_files:
        file_path = os.path.join(data_dir, filename)
        print(f"Processing {file_path}")
        try:
            success, stats = process_xml_file(file_path)
            if success:
                total_added = sum(stat['added'] for stat in stats.values())
                total_skipped = sum(stat['skipped'] for stat in stats.values())
                if total_added > 0:
                    save_processed_file(filename)
                    print(f"Successfully processed {filename}")
                    print(f"Added: {total_added} documents, Skipped: {total_skipped} documents")
                    for category, counts in stats.items():
                        print(f"  {category}: Added {counts['added']}, Skipped {counts['skipped']}")
                else:
                    print(f"No new documents added for {filename}. File not marked as processed.")
            else:
                print(f"Failed to process {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

print("All new XML files processed and stored in Typesense.")
