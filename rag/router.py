from rag.embedder import embedder
from utils.helper import category_map


def detect_categories(query):
    CATEGORY_MAP = category_map()
    query = query.lower()

    scores = {}

    for category, keywords in CATEGORY_MAP.items():

        score = 0

        for keyword in keywords:

            if keyword in query:
                score += 1

        scores[category] = score

    sorted_categories = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    selected_categories = [
        category
        for category, score in sorted_categories
        if score > 0
    ]

    return selected_categories


def category_filter(query):
    categories = detect_categories(query)
    query_embedding = embedder.encode(
        query
    ).tolist()

    where_filter = {"category": "profile"}

    if categories:

        if len(categories) == 1:

            where_filter = {
                "category": categories[0]
            }

        else:

            where_filter = {
                "$or": [
                    {"category": category}
                    for category in categories
                ]
            }

    return [where_filter, query_embedding]