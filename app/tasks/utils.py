"""Utility functions for tasks app."""

import base64
import json

import vertexai
from django.conf import settings
from vertexai.generative_models import GenerativeModel, Part

prompt = """
The following image captures a person's daily activities. Based on this image, please
determine whether the person is currently "studying" and describe their current state.

Tasks:
1. If the person in the image is studying, set is_studying to true. Otherwise, set it to false.
2. Based on the information obtained from the image,
describe the person's current action or state
(e.g., "looking at a smartphone," "writing in a notebook," "taking a break")
in the comment field with specific details.
3. Return the results in JSON format as follows:

{
    "is_studying": true,
    "comment": "Image uploaded successfully"
}

Examples:
- If the image shows a person writing in a notebook at a desk:
{
    "is_studying": true,
    "comment": "The person is writing notes and appears to be studying."
}

- If the image shows a person relaxing in a chair:
{
    "is_studying": false,
    "comment": "The person is relaxing and not engaged in studying activities."
}

Notes:
- Ensure the results are accurate and concise.
- Write the comment in natural, human-readable language.
- Write the comment in Japanese.
- Always return the results in valid JSON format.
- Confirm that data = json.loads(your response) does not produce an error.
- Do not format the response as a code block, such as in markdown.
"""


def get_ai_response(base64_image: str) -> dict:
    """Get AI response based on the provided base64 image."""
    try:
        project_id = settings.GOOGLE_CLOUD_PROJECT_ID
        vertexai.init(project=project_id)

        model = GenerativeModel("gemini-2.5-pro")

        response = model.generate_content(
            [Part.from_data(data=base64.b64decode(base64_image), mime_type="image/jpeg"), prompt]
        )
        response_text = response.text  # モデルからの生のレスポンス文字列
        cleaned_response_text = response_text.strip()
        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[len("```json") :].strip()
        if cleaned_response_text.endswith("```"):
            cleaned_response_text = cleaned_response_text[: -len("```")].strip()
            return json.loads(cleaned_response_text)
    except Exception:  # noqa: BLE001
        return {"is_studying": True, "comment": "AI から適切なレスポンスが得られませんでした。"}
