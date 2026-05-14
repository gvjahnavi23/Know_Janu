from pipeline import HybridRAGPipeline

pipeline = HybridRAGPipeline()

while True:

    query = input("Ask Know Janu: ").strip()
    if query == "":
        print("You didn't ask anything :( I am going to exit..")
        break
    if query.lower() == "exit":
        break

    response = pipeline.ask(query)

    print("Know Janu's response:")
    for r in response:
        print(r, end="", flush=True)
    print("\n")