from langchain_community.tools.tavily_search import TavilySearchResults

# Web Search Tool wrapper
web_search_tool = TavilySearchResults(max_results=3)