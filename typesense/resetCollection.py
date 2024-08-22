 # Function to delete existing collections and recreate them
def reset_collections():
    collections = ['plays', 'characters', 'acts', 'scenes', 'speeches']
    for collection in collections:
        try:
            client.collections[collection].delete()
        except:
            pass  # Collection doesn't exist, so we don't need to delete it
