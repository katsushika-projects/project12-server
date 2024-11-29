"""Utility functions for tasks app."""

import json

from django.conf import settings
from openai import OpenAI

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
)

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
- If the person is using a PC, consider them to be studying.
- If the image is taken from a PC camera, consider the person to be studying.
- Ensure the results are accurate and concise.
- Write the comment in natural, human-readable language.
- Write the comment in Japanese.
- Always return the results in valid JSON format.
- Confirm that data = json.loads(your response) does not produce an error.
- Do not format the response as a code block, such as in markdown.
"""


def get_ai_response(base64_image: str) -> dict:
    """Get AI response from OpenAI API."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "low"},
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    data = response.choices[0].message.content
    if data is not None:
        return json.loads(data)
    return {"is_studying": True, "comment": "AI から適切なレスポンスが得られませんでした。"}
