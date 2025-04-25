from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

class EmotionClass:
    def __init__(self,model="gpt-4o-mini"):
        self.chat = None
        self.Emotion = None
        self.chatmodel = ChatOpenAI(model=model, api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))

    def Emotion_Sensing(self, input):

        original_input = input
        if len(input) > 100:
            input = input[:100]
            print(f"Input is too long, only the first 100 characters will be used. Original length: {len(original_input)}")
        
        print(f"Processing input: {input}")
        
        json_schema = {
            "title": "emotions",
            "description": "feedback emotions",
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "the user input",
                    "minLength": 1,
                    "maxLength": 100
                },
                "output": {
                    "type": "string",
                    "description": "the emotion of the user input",
                    "enum": ["depressed", "friendly", "default", "angry", "cheerful"]
                }
            },
            "required": ["input", "output"],
        }
        llm = self.chatmodel.with_structured_output(json_schema)
        
        prompt_emotion = """
Judge the user's emotions based on the user's input, and the response rules are as follows:
1. If the content is negative, only "depressed" is returned, and no other content, such as depressive and depressed sentences.
2. If the content is positive, only "friendly" is returned, and no other content, such as friendly and polite sentences.
3. If the content is neutral, only "default" is returned, and no other content.
4. If the content is angry, only "angry" is returned, and no other content, such as angry, insulting, stupid, and hateful sentences.
5. If the content contains very happy emotions, only "cheerful" is returned, and no other content, such as happy, ecstatic, excited, and praise sentences.
User input content: {input}
        """

        EmotionChain = ChatPromptTemplate.from_messages([("system", prompt_emotion), ("user", input)]) | llm
        
        try:
            if not input.strip():
                print("Empty input received")
                return None
            
            if EmotionChain is not None:
                result = EmotionChain.invoke({"input": input})
                print(f"API response: {result}")
            else:
                raise ValueError("EmotionChain is not properly instantiated.")
            
            self.Emotion = result["output"]
            return result["output"]
        except Exception as e:
            print(f"Error in Emotion_Sensing: {str(e)}")
            return None
