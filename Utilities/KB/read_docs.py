from agentforge.tools.SemanticChunk import semantic_chunk
from agentforge.tools.GetText import GetText
from agentforge.utils.chroma_utils import ChromaUtils
import os

gettext_instance = GetText()
folder = './In'
storage = ChromaUtils()


def list_files(directory):
    files = []
    for entry in os.scandir(directory):
        if entry.is_file():
            files.append(entry.path)
        elif entry.is_dir():
            files.extend(list_files(entry.path))  # Recurse into subdirectory
    return files


files = list_files(folder)
for file in files:
    text = gettext_instance.read_file(file)
    chunks = semantic_chunk(text)
    for chunk in chunks:
        source_id = storage.count_collection('docs')
        source_id_string = [str(source_id + 1)]
        position = chunks.index(chunk)
        content = chunk.content
        metadata = {
            "Source": file,
            "Position": position
        }
        storage.save_memory(collection_name='docs', data=content, ids=source_id_string, metadata=[metadata])
        print(f"Data: {content}\nID: {source_id_string}\nPosition: {position}")
