import os
from typesense import Client

# Typesense client configuration
client_config = {
    'nodes': [{
        'host': 'typesense.documentresearch.dev',
        'port': '8080',
        'protocol': 'http'
    }],
    'api_key': os.getenv('TYPESENSE_API_KEY'),
    'connection_timeout_seconds': 10
}

# Initialize Typesense client
client = Client(client_config)

def fetch_play_details(play_id):
    return client.collections['plays'].documents[play_id].retrieve()

def fetch_characters(play_id):
    return client.collections['characters'].documents.search({
        'q': '*',
        'filter_by': f'play_id:{play_id}',
        'per_page': 100
    })['hits']

def fetch_acts(play_id):
    return client.collections['acts'].documents.search({
        'q': '*',
        'filter_by': f'play_id:{play_id}',
        'sort_by': 'act_number:asc',
        'per_page': 100
    })['hits']

def fetch_scenes(act_id):
    return client.collections['scenes'].documents.search({
        'q': '*',
        'filter_by': f'act_id:{act_id}',
        'sort_by': 'scene_number:asc',
        'per_page': 100
    })['hits']

def reconstruct_play(play_id):
    play = fetch_play_details(play_id)
    characters = fetch_characters(play_id)
    acts = fetch_acts(play_id)

    print(f"Title: {play['title']}")
    print(f"Subtitle: {play['playsubt']}")
    print("\nCharacters:")
    for character in characters:
        print(f"- {character['document']['name']}")
        if 'group_description' in character['document']:
            print(f"  Group: {character['document']['group_description']}")
        if 'individual_description' in character['document']:
            print(f"  Description: {character['document']['individual_description']}")

    print("\nPlay:")
    print(play['fm'])
    print(f"\nScene: {play['scndescr']}\n")

    for act in acts:
        print(f"\n{act['document']['title']}")
        scenes = fetch_scenes(act['document']['id'])
        for scene in scenes:
            print(f"\n  {scene['document']['title']}")
            print(f"{scene['document']['full_text']}")

if __name__ == "__main__":
    reconstruct_play("merchant_of_venice_moby")
