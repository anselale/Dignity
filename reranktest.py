from agentforge.utils.chroma_utils import ChromaUtils

# Create an instance of ChromaUtils
chroma_utils = ChromaUtils()

# Retrieve the query results from the "databass_chat_history" collection for the first query
query_results_1 = chroma_utils.query_memory(
    collection_name="adatabass_chat_history",
    query="your first query here",
    num_results=10  # Adjust the number of results as needed
)

print("Query Results 1:")
print(query_results_1)

# Retrieve the query results from the "databass_chat_history" collection for the second query
query_results_2 = chroma_utils.query_memory(
    collection_name="ageneral2_chat_history",
    query="your second query here",
    num_results=10  # Adjust the number of results as needed
)

print("Query Results 2:")
print(query_results_2)

# Combine the query results using the separate function
combined_query_results = chroma_utils.combine_query_results(query_results_1, query_results_2)

print("Combined Query Results:")
print(combined_query_results)

# Specify the temporary collection name for reranking
temp_collection_name = "temp_reranking_collection"

# Specify the reranking query
reranking_query = "your reranking query here"

# Call the rerank_results() method
reranked_results = chroma_utils.rerank_results(
    query_results=combined_query_results,
    query=reranking_query,
    temp_collection_name=temp_collection_name,
    num_results=5  # Adjust the number of reranked results as needed
)

print("Reranked Results:")
print(reranked_results)

if reranked_results is not None:
    print("Reranked Documents:")
    for result in reranked_results["documents"]:
        print(result)
else:
    print("Reranking failed. Please check the query results and try again.")

