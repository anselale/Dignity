from agentforge.tools.semantic_chunk import semantic_chunk
from agentforge.tools.get_text import GetText
from pathlib import Path


class LoadKB:

    def __init__(self, memory_instance):
        self.gettext_instance = GetText()
        self.folder = Path('./Utilities/KB/In').resolve()
        self.storage = memory_instance  # ChromaStorage instance
        self.current_files = set()
        self.all_sources = set()
        print("checking KB")
        self.get_entries()
        print("deleting entries")
        self.delete_not_found()
        print("processing KB")
        self.process_files()
        print("kb processed")

    @staticmethod
    def list_files(directory: Path, exts=None):
        print("Building file pile")
        directory = Path(directory)
        exts = {e.lower() for e in (exts or ['.txt', '.md', '.rst', '.json', '.yaml', '.yml'])}
        out = []
        for p in directory.rglob('*'):
            if p.is_file():
                if not exts or p.suffix.lower() in exts:
                    out.append(p.resolve())
        print("files built")
        return out

    def refresh_current_files(self):
        self.current_files = set(self.list_files(self.folder))
        print(f"Discovered {len(self.current_files)} files under {self.folder}")

    # NEW: Only index files not already present in the DB
    def compute_files_to_process(self):
        return sorted(p for p in self.current_files if p not in self.all_sources)

    def get_entries(self):
        # Always refresh snapshot first
        self.refresh_current_files()
        try:
            data = self.storage.load_collection(collection_name='docs', include=["metadatas"]) or {}
            metadatas = data.get('metadatas', []) or []
            self.all_sources = set(Path(m['Source']).resolve() for m in metadatas if m and 'Source' in m)
        except Exception as e:
            print(f"Error querying the database: {e}")
            self.all_sources = set()

        print(f"Current files in 'In' directory: {[str(p) for p in sorted(self.current_files)]}")
        print(f"Sources found in the database: {[str(p) for p in sorted(self.all_sources)]}")

    def delete_not_found(self):
        missing = self.all_sources - self.current_files
        for source in sorted(missing):
            print(f"File {source} no longer exists. Removing its entries from the database.")
            try:
                # CHANGED: use get-style load with metadata filter; no vector query
                result = self.storage.load_collection(
                    collection_name='docs',
                    include=[],  # valid: return ids only
                    where={'Source': str(source)}
                ) or {}
                ids = result.get('ids') or []
                if ids:
                    self.storage.delete_from_storage('docs', ids)
                self.all_sources.discard(Path(str(source)).resolve())  # keep snapshot tidy
            except Exception as e:
                print(f"Error removing entries for {source}: {e}")

    def process_files(self):
        # Ensure current snapshot
        self.refresh_current_files()

        # CHANGED: skip files that already exist in the DB
        to_process = self.compute_files_to_process()
        print(
            f"Skipping {len(self.current_files) - len(to_process)} existing files; processing {len(to_process)} new files.")

        for file_path in to_process:
            file_str = str(file_path)
            print(f"Processing file: {file_str}")

            try:
                text = self.gettext_instance.read_file(file_str)
            except Exception as e:
                print(f"Error reading {file_str}: {e}")
                continue

            try:
                chunks = semantic_chunk(text) or []
            except Exception as e:
                print(f"Error chunking {file_str}: {e}")
                continue

            # REMOVED: existing = self.storage.query_storage(...); delete_from_storage(...)
            # Reason: no re-indexing of existing files; only new files are added. [Chroma upsert is unchanged]

            documents = []
            metadatas = []
            for position, chunk in enumerate(chunks):
                content = getattr(chunk, 'content', chunk)
                if not content:
                    continue
                documents.append(content)
                metadatas.append({'Source': file_str, 'Position': position})

            if not documents:
                continue

            try:
                self.storage.save_to_storage(collection_name='docs', data=documents, metadata=metadatas)
                for m in metadatas:
                    print(f"Added: ID: {m.get('id')}, Position: {m.get('Position')}")
                self.all_sources.add(file_path.resolve())  # keep in-memory snapshot current
            except Exception as e:
                print(f"Error saving chunks for {file_str}: {e}")

        print("Database update complete.")


def ensure_input_dir(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    return base


def write_sample_files(in_dir_test: Path):
    samples = {
        'example1.txt': 'This is a small example document. It has a few sentences for chunking.',
        'example2.md': '# Title\n\nSecond file with some markdown content. Another sentence.'
    }
    for name, content in samples.items():
        (in_dir_test / name).write_text(content, encoding='utf-8')


if __name__ == '__main__':
    from agentforge.storage.chroma_storage import ChromaStorage
    import os

    # 1) Prepare input folder with a couple of sample files
    project_root = Path.cwd()
    in_dir = ensure_input_dir(project_root / 'In')

    # If directory is empty, write sample files for a smoke test
    if not any(in_dir.iterdir()):
        write_sample_files(in_dir)
        print(f"Wrote sample files to {in_dir}")

    # 2) Create or get a ChromaStorage instance for an isolated test namespace
    storage_id = 'loadkb_smoke_test'
    memory = ChromaStorage.get_or_create(storage_id)

    # Optional: fresh start per run (if your Config allows it already, skip)
    # memory.reset_storage()

    # 3) Run the loader (constructor triggers get_entries -> delete_not_found -> process_files)
    loader = LoadKB(memory)

    # 4) Inspect collection contents
    print("\n--- Collection peek (docs) ---")
    peek = memory.peek('docs')
    print(peek)

    # 5) Verify entries for each file
    print("\n--- Entries per source ---")
    for p in sorted(loader.current_files):
        src = str(p)
        res = memory.load_collection(
            collection_name='docs',
            include=[],  # ids are always returned
            where={'Source': src}
        ) or {}
        count = len(res.get('ids', []))
        print(f"Source: {src}\nCount: {count}")

    # 6) Simulate deletion: remove one file and re-run loader
    removed = None
    for p in sorted(loader.current_files):
        removed = p
        break
    if removed and removed.exists():
        os.remove(removed)
        print(f"\nRemoved file: {removed}")
        # Re-run phases to test delete_not_found
        loader.get_entries()
        loader.delete_not_found()
        print("Re-processed deletions.")

    # 7) Final peek
    print("\n--- Final peek (docs) ---")
    final_peek = memory.peek('docs')
    print(final_peek)
