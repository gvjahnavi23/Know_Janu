import json

def load_data():

    file_name = (
        r'D:\learning\Know_Janu'
        r'\data\Janu data.json'
    )

    with open(
        file_name,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data


def follow_up():

    return [

        "it",
        "they",
        "that",
        "those",
        "which one",
        "this",
        "these",
        "there"
    ]


def clean_text(text):

    return (
        text
        .replace("\n", " ")
        .strip()
    )