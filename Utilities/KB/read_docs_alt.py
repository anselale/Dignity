from agentforge.tools.SemanticChunk import semantic_chunk
from agentforge.tools.GetText import GetText
from agentforge.utils.chroma_utils import ChromaUtils
import os

gettext_instance = GetText()
folder = './In'
storage = ChromaUtils()


def list_files(directory):
    with os.scandir(directory) as entries:
        return [entry.path for entry in entries if entry.is_file()]


# Get current files in the "In" directory
current_files = set(list_files(folder))

# Safely get all unique sources from the database
try:
    all_entries = storage.load_collection(collection_name='docs')
    if all_entries is None:
        print(
            "Warning: query_memory returned None. The database might be empty or there might be an issue with the Chroma backend.")
        all_sources = set()
    else:
        all_sources = set(
            metadata['Source'] for metadata in all_entries.get('metadatas', []) if metadata and 'Source' in metadata)
except Exception as e:
    print(f"Error querying the database: {str(e)}")
    print("Proceeding with an empty set of existing sources.")
    all_sources = set()

print(f"Current files in 'In' directory: {current_files}")
print(f"Sources found in the database: {all_sources}")

# Remove entries for files that no longer exist
for source in all_sources:
    if source not in current_files:
        print(f"File {source} no longer exists. Removing its entries from the database.")
        try:
            entries_to_remove = storage.query_memory(collection_name='docs', query={"metadata.Source": source})
            if entries_to_remove and 'ids' in entries_to_remove and entries_to_remove['ids']:
                for entry_id in entries_to_remove['ids']:
                    storage.delete_memory('docs', entry_id)
        except Exception as e:
            print(f"Error removing entries for {source}: {str(e)}")

# Process current files
for file in current_files:
    print(f"Processing file: {file}")
    text = gettext_instance.read_file(file)
    chunks = semantic_chunk(text)

    # Check if the file already exists in the database
    try:
        existing_entries = storage.query_memory(collection_name='docs', query={"metadata.Source": file})
        print(f"Existing entries for {file}: {existing_entries}")

        if existing_entries and 'ids' in existing_entries and existing_entries['ids']:
            # Remove existing entries
            for existing_id in existing_entries['ids']:
                storage.delete_memory('docs', existing_id)
    except Exception as e:
        print(f"Error querying or deleting existing entries for {file}: {str(e)}")

    for chunk in chunks:
        try:
            source_id = storage.count_collection('docs')
            source_id_string = str(source_id + 1)
            position = chunks.index(chunk)
            content = chunk.content
            metadata = {
                "Source": file,
                "Position": position
            }
            storage.save_memory(collection_name='docs', data=content, ids=[source_id_string], metadata=[metadata])
            print(f"Added: ID: {source_id_string}, Position: {position}")
        except Exception as e:
            print(f"Error saving chunk for {file}: {str(e)}")

print("Database update complete.")