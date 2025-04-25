from langchain.memory import ConversationTokenBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_openai import ChatOpenAI
from src.Prompt import PromptClass
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

class MemoryClass:
    def __init__(self,memorykey="chat_history",model="gpt-4o-mini"):
        self.memorykey = memorykey
        self.memory = []
        self.chatmodel = ChatOpenAI(model=model, api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))

    def summary_chain(self,store_message):
        SystemPrompt = PromptClass().SystemPrompt
        Moods = PromptClass().MOODS
        prompt = ChatPromptTemplate.from_messages([
            ("system", SystemPrompt+"\n\n\nYou are Master Chen, a mystical fortune-teller. The following is a sequence of past conversations between you and a seeker of fate.\n"
 "Please summarize the interaction from **your perspective** using first person narration (e.g., 'I replied', 'I noticed'). Only highlight key turning points in the dialogue.\n"
 "At the end, extract any **key user details** that may help future readings — such as their name, birthday, or personal interests.\n"
 "\n Output format must be:\n"
 "Summary text | key info\n"
 "\nFor example:\n"
 "The seeker greeted me warmly. I returned the kindness. They asked about their fate for this year, and I unveiled what the stars revealed. Then they took their leave. | John Smith, born March 5, 1993\n"),
            ("user", "{input}")
        ])
        chain = prompt | self.chatmodel
        summary = chain.invoke({"input": store_message,"who_you_are":Moods["default"]["roloSet"]})
        return summary
    
    def get_memory(self):
        try:
            chat_message_history =RedisChatMessageHistory(
                url="redis://localhost:6379/0", session_id="session1"
            )
            store_message = chat_message_history.messages
            if len(store_message) > 10:
                str_message = ""
                for message in store_message:
                    str_message+=f"{type(message).__name__}: {message.content}"
                summary = self.summary_chain(str_message)
                chat_message_history.clear()
                chat_message_history.add_message(summary)
                print("After adding summarization:",chat_message_history.messages)
                return chat_message_history
            else:
                print("go to next step")
                return chat_message_history
        except Exception as e:
            print(e)
            return None

    def set_memory(self):
        self.memory = ConversationTokenBufferMemory(
            llm=self.chatmodel,
            human_prefix="user",
            ai_prefix="Master Chen",
            memory_key=self.memorykey,
            output_key="output",
            return_messages=True,
            max_token_limit=1000,
            chat_memory=self.get_memory(),
        )
        return self.memory

    