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

# Function to delete a collection if it exists
def delete_collection(collection_name):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Attempting to delete collection {collection_name} (Attempt {attempt + 1})")
            if collection_name in client.collections:
                print(f"Deleting Collection {collection_name}")
                client.collections[collection_name].delete()
                print(f"Collection {collection_name} deleted successfully")
                return
            else:
                print(f"Collection {collection_name} does not exist")
                return
        except Exception as e:
            print(f"Error deleting collection {collection_name} (Attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"Failed to delete collection {collection_name} after {max_retries} attempts")

# Function to reset all collections
def reset_collections():
    print("Resetting collections")
    collections = ['speeches', 'scenes', 'acts', 'characters', 'plays']
    for collection in collections:
        print(f"Attempting to delete collection {collection}")
        delete_collection(collection)
        print(f"Finished attempt to delete collection {collection}")

    print("All collections deletion attempts completed")

    # Recreate collections
    from createSPcollections import create_collection
    for collection in reversed(collections):
        print(f"Creating collection {collection}")
        create_collection(collection)
        print(f"Collection {collection} created")

    print("All collections reset completed")

# Function to process XML and store in Typesense
def process_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract play information
    play_title = root.find('TITLE').text
    play_id = os.path.splitext(os.path.basename(file_path))[0]

    # Store play information
    try:
        client.collections['plays'].documents.create({
            'id': play_id,
            'title': play_title,
            'fm': ' '.join([p.text for p in root.find('FM').findall('P')]),
            'scndescr': root.find('SCNDESCR').text,
            'playsubt': root.find('PLAYSUBT').text
        })
    except Exception as e:
        if 'already exists' in str(e):
            print(f"Play document for {play_id} already exists. Skipping play creation.")
        else:
            print(f"Error creating play document: {str(e)}")
            return False  # Indicate processing failure

    # Process characters
    for persona in root.find('PERSONAE').findall('.//PERSONA'):
        try:
            client.collections['characters'].documents.create({
                'id': f"{play_id}_{persona.text.strip()}",
                'play_id': play_id,
                'name': persona.text.strip()
            })
        except Exception as e:
            if 'already exists' in str(e):
                print(f"Character document for {play_id}_{persona.text.strip()} already exists. Skipping.")
            else:
                print(f"Error creating character document: {str(e)}")

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
        except Exception as e:
            if 'already exists' in str(e):
                print(f"Act document for {act_id} already exists. Skipping.")
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
            except Exception as e:
                if 'already exists' in str(e):
                    print(f"Scene document for {scene_id} already exists. Skipping.")
                else:
                    print(f"Error creating scene document: {str(e)}")
                    continue

            for speech_num, speech in enumerate(scene.findall('SPEECH'), 1):
                speaker = speech.find('SPEAKER').text
                content = ' '.join([line.text for line in speech.findall('LINE') if line.text])
                speech_id = f"{scene_id}_{speaker}_{speech_num}_{hash(content) % 1000000}"  # Truncate hash to 6 digits
                try:
                    client.collections['speeches'].documents.create({
                        'id': speech_id,
                        'scene_id': scene_id,
                        'speaker': speaker,
                        'content': content
                    })
                except Exception as e:
                    if 'already exists' in str(e):
                        print(f"Speech document for {speech_id} already exists. Skipping.")
                    else:
                        print(f"Error creating speech document: {str(e)}")

    return True  # Indicate successful processing

# Reset collections before processing
# reset_collections()

# Load the list of processed files
processed_files = load_processed_files()

# Find and process all XML files in the 'data' subdirectory
data_dir = 'data'
for filename in os.listdir(data_dir):
    if filename.endswith('.xml') and filename not in processed_files:
        file_path = os.path.join(data_dir, filename)
        print(f"Processing {file_path}")
        try:
            if process_xml_file(file_path):
                save_processed_file(filename)
                print(f"Successfully processed and saved {filename}")
            else:
                print(f"Failed to process {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

print("All new XML files processed and stored in Typesense.")
