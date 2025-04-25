from langchain.agents import AgentExecutor,create_tool_calling_agent,tool
from langchain_community.utilities import SerpAPIWrapper
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate   
import os
import requests
from dotenv import load_dotenv
# os.environ["SERPAPI_API_KEY"] = os.getenv("SERPAPI_API_KEY")
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
@tool
def search(query: str) -> str:
    """This tool is only used when you need to know real-time information or something you don't know."""
    serp = SerpAPIWrapper()
    return serp.run(query)

@tool
def get_info_from_local(query: str) -> str:
    """This tool will only be used to answer questions related to 2024 fortune or the Year of the Dragon."""
    client = QdrantClient(path="/tmp/local_qdrant")
    retriever_qr = QdrantVectorStore(client, "local_documents_demo", OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE")))
    retriever = retriever_qr.as_retriever(search_type="mmr")
    result = retriever.get_relevant_documents(query)
    return result

@tool
def jiemeng(query: str):
    """This tool is only used to help users interpret dreams, and the dream content needs to be entered. ** if the input str is not Chinese, you should interpret it to Chinese before passing it to the prompt template"""
    url = f"https://api.yuanfenju.com/index.php/v1/Gongju/zhougong"
    LLM = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0, 
            streaming=True, api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE")
        )
    prompt = ChatPromptTemplate.from_template("Extract 1 keyword based on the input content, return only the keyword, input content:{topic}")
    prompt_value = prompt.invoke({"topic": query})
    print("==========Check point========")
    keyword = LLM.invoke(prompt_value)
    print("=======Submitting data=======")
    print(keyword.content)
    result = requests.post(url, data={"api_key": os.getenv("API_KEY"), "title_zhougong": keyword.content})
    if result.status_code == 200:
        print("=======Returning data=======")
        return result.text
    else:
        return "User input lacks details, please notify user to complete the information needed！"