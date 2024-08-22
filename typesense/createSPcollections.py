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
    'connection_timeout_seconds': 5
}

# Initialize Typesense client
client = Client(client_config)

# Function to create a collection
def create_collection(name, fields):
    schema = {
        'name': name,
        'fields': fields
    }
    try:
        client.collections.create(schema)
        print(f"Collection '{name}' created successfully.")
    except Exception as e:
        if 'already exists' in str(e):
            print(f"Collection '{name}' already exists. Skipping creation.")
        else:
            print(f"Error creating collection '{name}': {str(e)}")

# Define collection schemas
collections = [
    {
        'name': 'plays',
        'fields': [
            {'name': 'id', 'type': 'string'},
            {'name': 'title', 'type': 'string'},
            {'name': 'fm', 'type': 'string'},
            {'name': 'scndescr', 'type': 'string'},
            {'name': 'playsubt', 'type': 'string'}
        ]
    },
    {
        'name': 'characters',
        'fields': [
            {'name': 'id', 'type': 'string'},
            {'name': 'play_id', 'type': 'string'},
            {'name': 'name', 'type': 'string'},
            {'name': 'group_description', 'type': 'string', 'optional': True}
        ]
    },
    {
        'name': 'acts',
        'fields': [
            {'name': 'id', 'type': 'string'},
            {'name': 'play_id', 'type': 'string'},
            {'name': 'title', 'type': 'string'},
            {'name': 'subtitle', 'type': 'string', 'optional': True},
            {'name': 'act_number', 'type': 'int32'}
        ]
    },
    {
        'name': 'scenes',
        'fields': [
            {'name': 'id', 'type': 'string'},
            {'name': 'act_id', 'type': 'string'},
            {'name': 'title', 'type': 'string'},
            {'name': 'subtitle', 'type': 'string', 'optional': True},
            {'name': 'scene_number', 'type': 'int32'}
        ]
    },
    {
        'name': 'speeches',
        'fields': [
            {'name': 'id', 'type': 'string'},
            {'name': 'scene_id', 'type': 'string'},
            {'name': 'speaker', 'type': 'string'},
            {'name': 'content', 'type': 'string'}
        ]
    },
    {
        'name': 'prologues',
        'fields': [
            {'name': 'id', 'type': 'string'},
            {'name': 'play_id', 'type': 'string'},
            {'name': 'act_id', 'type': 'string', 'optional': True},
            {'name': 'title', 'type': 'string'},
            {'name': 'subtitle', 'type': 'string', 'optional': True},
            {'name': 'content', 'type': 'string'}
        ]
    },
    {
        'name': 'epilogues',
        'fields': [
            {'name': 'id', 'type': 'string'},
            {'name': 'play_id', 'type': 'string'},
            {'name': 'act_id', 'type': 'string', 'optional': True},
            {'name': 'title', 'type': 'string'},
            {'name': 'subtitle', 'type': 'string', 'optional': True},
            {'name': 'content', 'type': 'string'}
        ]
    },
    {
        'name': 'inductions',
        'fields': [
            {'name': 'id', 'type': 'string'},
            {'name': 'play_id', 'type': 'string'},
            {'name': 'title', 'type': 'string'},
            {'name': 'subtitle', 'type': 'string', 'optional': True},
            {'name': 'content', 'type': 'string'}
        ]
    }
]

if __name__ == "__main__":
    # Create all collections
    for collection in collections:
        create_collection(collection['name'], collection['fields'])

    print("Collection creation process completed.")
