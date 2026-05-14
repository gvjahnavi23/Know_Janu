import json

def load_data():
    file_name = r'D:\learning\Know_Janu\data\Janu data.json'
    with open(file_name, "r") as f:
        data = json.load(f)

    documents = [
        item["document"]
        for item in data
    ]

    ids = [
        item["id"]
        for item in data
    ]

    metadata = [
        item["metadata"]
        for item in data
    ]

    return {'ids': ids,
            'documents' : documents,
            'metadata' : metadata
            }


def category_map():
    return {

        "skill_usage": [
            "used",
            "usage",
            "applied",
            "where",
            "implemented",
            "worked with",
            "technology used",
            "skills used",
            "framework used"
        ],

        "projects": [
            "project",
            "projects",
            "built",
            "developed",
            "created",
            "application",
            "platform",
            "chatbot",
            "system"
        ],

        "experience": [
            "experience",
            "worked",
            "job",
            "internship",
            "employment",
            "role",
            "company"
        ],

        "education": [
            "education",
            "qualification",
            "degree",
            "academic",
            "college",
            "university",
            "study"
        ],

        "skills": [
            "skills",
            "technologies",
            "frameworks",
            "languages",
            "tools",
            "expertise"
        ],

        "achievements": [
            "achievement",
            "award",
            "recognition",
            "organizer",
            "accomplishment"
        ],

        "profile": [
            "who is",
            "about",
            "profile",
            "summary",
            "introduction"
        ]
    }


def follow_up():
    return [
            "it",
            "they",
            "that",
            "those",
            "which one",
            "this",
            "these"
            ]

def query_type(query):
    broad = ["projects",
    "skills",
    "technologies",
    "tell me all",
    "experiences"]
    if any(
            phrase in query.lower()
            for phrase in broad
    ):
        return "broad"
    return "specific"