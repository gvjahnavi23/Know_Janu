import ollama


def generator(prompt):
    response = ollama.generate(
        model="phi3:mini",
        prompt=prompt,
        stream=True
    )

    for chunk in response:
        yield chunk["response"]