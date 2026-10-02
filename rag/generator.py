from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv


load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-3.5-turbo-0125",
    stream_usage=True,
    api_key=api_key
)


def generator(prompt):
    print(prompt)
    response = llm.invoke(prompt)

    for chunk in response:
        yield chunk["response"]