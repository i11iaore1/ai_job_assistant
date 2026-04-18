from fastapi import APIRouter

# from llm_service import llm_client
# from serializers.reviews import ReviewVacancyResponseSerializer, ReviewVacancySerializer

router = APIRouter()


# @router.post("/review")
# def review_vacancy(payload: ReviewVacancySerializer) -> ReviewVacancyResponseSerializer:
#     resume_text = "Skills: Python, Django, JavaScript"
#     context = "Looking for a first remote fulltime job. I have no experience yet"

#     result = llm_client.evaluate_vacancy(
#         resume_text=resume_text,
#         context=context,
#         vacancy_description=payload.vacancy_description,
#     )

#     return result
