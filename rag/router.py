def category_filter(query):

    query = query.lower()

    if any(word in query for word in [

        "used",
        "implemented",
        "where was",
        "technology",
        "technologies",
        "framework",
        "frameworks",
        "built with",
        "worked with",
        "which project used",
        "which one used"

    ]):

        return {
            "category": "skill_usage"
        }

    if any(word in query for word in [

        "project",
        "projects",
        "built",
        "developed",
        "created"

    ]):
        return {
            "$and": [
                {"category": "projects"},
                {"type": "overview"}
            ]
        }

    # broad skills query

    if any(word in query for word in [

        "skills",
        "skill set",
        "expertise",
        "technologies known",
        "technical skills",
        "what does jahnavi know",
        "what are jahnavi skills"

    ]):

        return {
            "category": "skills"
        }



    if any(word in query for word in [

        "experience",
        "worked",
        "company",
        "companies",
        "job",
        "role",
        "accenture",
        "internship"

    ]):

        return {
            "$and": [
                {"category": "experience"},
                {"type": "role"}
            ]
        }



    if any(word in query for word in [

        "education",
        "study",
        "studied",
        "college",
        "btech",
        "degree",
        "school",
        "university",
        "graduation",
        "qualification"

    ]):
        return {"category": "education"}


    if any(word in query for word in [

        "achievement",
        "achievements",
        "award",
        "awards",
        "certification",
        "certifications",
        "organizer",
        "leadership"

    ]):

        return {
                "$and":[ {"category":"achievements"},

                    {"$or":[
                            {"type":"award"},
                            {"type":"leadership"}
                        ]
                    }
                ]
            }



    if any(phrase in query for phrase in [

        "who is jahnavi",
        "summary about jahnavi",
        "about jahnavi",
        "jahnavi profile",
        "profile summary",
        "introduce jahnavi",
        "who is she"

    ]):
        return {
            "$and":[
                {"category": "profile"},
                {"type": "summary"}
            ]
        }

    if any(phrase in query for phrase in [
        "education",
        "qualification",
    ]):
        return {"category": "education"},

    return None