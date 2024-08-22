import os
import json
import typesense

# Initialize Typesense client
client = typesense.Client({
  'nodes': [{
    'host': 'typesense.documentresearch.dev',  # Replace with your Typesense host
    'port': '8080',       # Replace with your Typesense port
    'protocol': 'http'    # Use 'https' if your Typesense server uses SSL
  }],
  'api_key': os.getenv('TYPESENSE_API_KEY'),
  'connection_timeout_seconds': 5
})

# Define the schema for the collection
schema = {
  'name': 'shakespeare_works',
  'fields': [
    {'name': 'id', 'type': 'string'},
    {'name': 'title', 'type': 'string'}
  ]
}

# Create the collection
try:
    client.collections.create(schema)
    print("Collection created successfully")
except typesense.exceptions.ObjectAlreadyExists:
    print("Collection already exists")

# Load the JSON data
with open('sp-works.json', 'r') as file:
    works = json.load(file)

# Import the data into Typesense
try:
    import_results = client.collections['shakespeare_works'].documents.import_(works)
    print(f"Successfully imported {len(works)} documents")
    print(f"Import results: {import_results}")
except typesense.exceptions.TypesenseClientError as e:
    print(f"Error importing documents: {e}")
