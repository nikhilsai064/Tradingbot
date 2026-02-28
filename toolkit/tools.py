from langchain.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from lancedb.rerankers import LinearCombinationReranker
from langchain_community.vectorstores import LanceDB
from langchain_community.tools import TavilySearchResults
from langchain_community.tools.polygon.financials import PolygonFinancials
from langchain_community.utilities.polygon import PolygonAPIWrapper
from langchain_community.tools.bing_search import BingSearchResults
import os
import sys

# Ensure project root (parent of `toolkit`) is on sys.path so imports like
# `data_models` work when this module is run directly.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import data_models.models

@tool(args_schema=data_models.models.RagToolSchema)
def retriever_tool(question):
    """A tool that retrieves relevant documents from a vector store based on a query."""
    pass
@tool
def tavily_tool(question:str):
    """A tool that retrieves search results from Tavily based on a query."""
    # instantiate the Tavily search tool and run the query
    tool = TavilySearchResults()
    return tool.run(question)
@tool
def create_polygon_tool(question:str):
    """A tool that retrieves financial data from Polygon based on a query."""
    # instantiate the Polygon financials tool and run the query
    tool = PolygonFinancials()
    return tool.run(question)

def create_bing_tool(question:str):
    """A tool that retrieves search results from Bing based on a query."""
    # instantiate the Bing search tool and run the query
    tool = BingSearchResults()
    return tool.run(question)

def get_all_tools():
    return [retriever_tool, tavily_tool, create_polygon_tool, create_bing_tool]

if __name__ == "__main__":
    print(get_all_tools())
