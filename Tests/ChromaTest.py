from agentforge.utils.chroma_utils import ChromaUtils


class ChromaTest:

    def __init__(self):
        self.chroma = ChromaUtils()

    def test_minmax(self, collection, metadata):
        var = self.chroma.search_metadata_min_max(collection, metadata, 'max')
        print(var["target"])

    def list_collections(self, filter_string=None):
        var = self.chroma.collection_list()

        if filter_string:
            var = [collection.name for collection in var if filter_string in collection.name]
        else:
            var = [collection.name for collection in var]

        return var

    def delete_record(self, collection, id):
        self.chroma.delete_memory(collection, id)

    def check_records(self):
        all_collections = self.list_collections()
        for collection in all_collections:
            print(collection)

    def record_lengths(self, collection):
        content = self.chroma.load_collection(collection)
        # Initialize the 'len' key as an empty dictionary
        index = {}
        index['len_doc'] = []
        index['doc_content'] = []
        index['id'] = []
        index['len_response'] = []
        index['response_content'] = []

        for key, (record, doc) in zip(content.keys(), zip(content['ids'], content['documents'])):
            length = len(doc)
            id = record
            index['len_doc'].append(length)
            index['doc_content'].append(doc)
            index['id'].append(id)


        for key, (record, doc) in zip(content.keys(), zip(content['ids'], content['metadatas'])):
            try:
                if doc['Response']:
                    length = len(doc['Response'])
                    index['len_response'].append(length)
                    index['response_content'].append(doc['Response'])

            except:
                index['len_response'].append('')
                index['response_content'].append('')

        return index

    def get_records(self, collection):
        results = self.chroma.load_collection(collection)
        return results

    @staticmethod
    def write_to_file(content):
        with open("output.txt", "w", encoding="utf-8") as file:
            file.write(content)

    def dump_responses(self, collection_list):
        results = ''
        for collection in collection_list:
            print(collection)
            result = self.record_lengths(collection)
            print(result)

            formatted_string = ""
            for i in range(len(result['id'])):
                formatted_string += f"Collection Name: {collection}\n"
                formatted_string += f"Document ID: {result['id'][i]}\n"
                formatted_string += f"Document Length: {result['len_doc'][i]}\n"
                formatted_string += f"Response Length: {result['len_response'][i]}\n"
                formatted_string += f"Response Content:\n{result['response_content'][i]}\n\n"

            results += f'{formatted_string}'

        self.write_to_file(str(results))

    def dump_docs(self, collection_list):
        results = ''
        for collection in collection_list:
            print(collection)
            result = self.record_lengths(collection)
            print(result)

            formatted_string = ""
            for i in range(len(result['id'])):
                formatted_string += f"Collection Name: {collection}\n"
                formatted_string += f"Document ID: {result['id'][i]}\n"
                formatted_string += f"Document Length: {result['len_doc'][i]}\n"
                formatted_string += f"Response Length: {result['len_response'][i]}\n"
                formatted_string += f"Document Content:\n{result['doc_content'][i]}\n\n"

            results += f'{formatted_string}'

        self.write_to_file(str(results))


if __name__ == '__main__':
    test = ChromaTest()
    collection_list = test.list_collections('journal')

    print(collection_list)


