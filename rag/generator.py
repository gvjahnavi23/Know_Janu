import ollama

from rag.prompt_builder import prompt_builder


def generator(query):
    prompt = prompt_builder(query)
    response = ollama.generate(
        model="phi3:mini",
        prompt=prompt
    )

    return response["response"]