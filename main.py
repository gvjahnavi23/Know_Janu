from pipeline import HybridRAGPipeline

pipeline = HybridRAGPipeline()

while True:

    query = input("Ask Janu: ")

    if query.lower() == "exit":
        break

    response = pipeline.ask(query)

    print("Know Janu's response:\n")
    for r in response:
        print(r, end="", flush=True)