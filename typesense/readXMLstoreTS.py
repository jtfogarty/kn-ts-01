import os
import xml.etree.ElementTree as ET
from typesense import Client

# Typesense client configuration
client_config = {
    'nodes': [{
        'host': 'typesense.documentresearch.dev',
        'port': '8080',
        'protocol': 'http'
    }],
    'api_key': os.getenv('TYPESENSE_API_KEY'),
    'connection_timeout_seconds': 5
}

# Initialize Typesense client
client = Client(client_config)

# Function to delete a collection if it exists
def delete_collection(collection_name):
    try:
        if collection_name in client.collections:
            print(f"Deleting Collection {collection_name}")
            client.collections[collection_name].delete()
            print(f"Collection {collection_name} deleted")
        else:
            print(f"Collection {collection_name} does not exist")
    except Exception as e:
        print(f"Error deleting collection {collection_name}: {str(e)}")

# Function to reset all collections
def reset_collections():
    print("resetting collections")
    collections = ['speeches', 'scenes', 'acts', 'characters', 'plays']
    for collection in collections:
        print(f"calling delete collection {collection}")
        delete_collection(collection)

    # Recreate collections
    from createSPcollections import create_collection
    for collection in reversed(collections):
        create_collection(collection)

# Function to process XML and store in Typesense
def process_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract play information
    play_title = root.find('TITLE').text
    play_id = os.path.splitext(os.path.basename(file_path))[0]

    # Store play information
    client.collections['plays'].documents.create({
        'id': play_id,
        'title': play_title,
        'fm': ' '.join([p.text for p in root.find('FM').findall('P')]),
        'scndescr': root.find('SCNDESCR').text,
        'playsubt': root.find('PLAYSUBT').text
    })

    # Process characters
    for persona in root.find('PERSONAE').findall('.//PERSONA'):
        client.collections['characters'].documents.create({
            'id': f"{play_id}_{persona.text.strip()}",
            'play_id': play_id,
            'name': persona.text.strip()
        })

    # Process acts, scenes, speeches
    for act_num, act in enumerate(root.findall('ACT'), 1):
        act_id = f"{play_id}_act_{act_num}"
        client.collections['acts'].documents.create({
            'id': act_id,
            'play_id': play_id,
            'title': act.find('TITLE').text,
            'act_number': act_num
        })

        for scene_num, scene in enumerate(act.findall('SCENE'), 1):
            scene_id = f"{act_id}_scene_{scene_num}"
            client.collections['scenes'].documents.create({
                'id': scene_id,
                'act_id': act_id,
                'title': scene.find('TITLE').text,
                'scene_number': scene_num
            })

            for speech_num, speech in enumerate(scene.findall('SPEECH'), 1):
                speaker = speech.find('SPEAKER').text
                content = ' '.join([line.text for line in speech.findall('LINE') if line.text])
                speech_id = f"{scene_id}_{speaker}_{speech_num}_{hash(content) % 1000000}"  # Truncate hash to 6 digits
                client.collections['speeches'].documents.create({
                    'id': speech_id,
                    'scene_id': scene_id,
                    'speaker': speaker,
                    'content': content
                })

# Reset collections before processing
reset_collections()

# Find and process all XML files in the 'data' subdirectory
data_dir = 'data'
for filename in os.listdir(data_dir):
    if filename.endswith('.xml'):
        file_path = os.path.join(data_dir, filename)
        print(f"Processing {file_path}")
        process_xml_file(file_path)

print("All XML files processed and stored in Typesense.")
