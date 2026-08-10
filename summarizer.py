import os
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

class NewsBriefSchema(BaseModel):
    title: str = Field(description="Concise, impactful news headline")
    category: str = Field(description="Category name (e.g. National, Business, Technology, Law & Policy)")
    summary: str = Field(description="Objective factual brief between 100 to 180 words")
    keypoints: list[str] = Field(description="3 distinct bullet points highlighting core facts")

def summarize_article(raw_title: str, raw_text: str) -> NewsBriefSchema:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    system_instruction = (
        "You are an editor for DailyBrief, a short-form news portal. "
        "Summarize news objectively. Never hallucinate or add facts not present in the input text. "
        "Select the single best category from: [National, International, Current Affairs, Business, Stock Market, Technology, Law & Policy, Sports]."
    )

    prompt = f"Source Title: {raw_title}\nSource Content: {raw_text}"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=NewsBriefSchema,
            temperature=0.2,
        ),
    )

    return NewsBriefSchema.model_validate_json(response.text)