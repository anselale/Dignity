from agentforge.utils.chroma_utils import ChromaUtils

def query_and_rerank(query_results, rerank_query, num_results=5):
    chroma_utils = ChromaUtils()

    # Combine all query results
    combined_query_results = chroma_utils.combine_query_results(*query_results)

    reranked_results = chroma_utils.rerank_results(
        query_results=combined_query_results,
        query=rerank_query,
        temp_collection_name="temp_reranking_collection",
        num_results=num_results
    )

    return reranked_results

def main():
    chroma_utils = ChromaUtils()

    # Get the number of queries from the user
    num_queries = int(input("Enter the number of queries: "))
    
    # Collect queries and their results
    query_results = []
    for i in range(num_queries):
        query = input(f"Enter query {i+1}: ")
        collection_name = input(f"Enter collection name for query {i+1}: ")
        
        results = chroma_utils.query_memory(
            collection_name=collection_name,
            query=query,
            num_results=10
        )
        query_results.append(results)

    rerank_query = input("Enter your reranking query: ")
    
    results = query_and_rerank(query_results, rerank_query)

    if results:
        print("Reranked Documents:")
        for result in results["documents"]:
            print(result)
    else:
        print("Reranking failed. Please check the query results and try again.")

if __name__ == "__main__":
    main()

