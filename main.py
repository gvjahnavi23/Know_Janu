from app import know_janu


def main():

    print("Know Janu Chatbot Started")
    print("Type 'exit' to stop\n")

    while True:

        query = input("You: ")

        if query.lower() == "exit":
            print("Goodbye!")
            break

        response = know_janu(query)

        print(f"\nBot: {response}\n")


if __name__ == "__main__":
    main()