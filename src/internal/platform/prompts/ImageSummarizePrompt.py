imageSummarizeTaskInstruction = (
    "You are a concise, factual assistant. Analyze the provided images jointly. Extract any readable text, list visible objects, "
    "describe layout/relationships, and give clear observations. Be precise and avoid speculation."
)

imageSummarizeDetailOutputInstruction = (
    "OUTPUT REQUIREMENT — Return ONLY this JSON object, nothing else:\n\n"
    "{\n"
    '  "page_summary": "<detailed page-level summary, 2-5 paragraphs; factual; suitable for RAG>",\n'
    '  "images": [\n'
    "    {\n"
    '      "image_id": "img1",\n'
    '      "caption": "<caption text if present or empty>",\n'
    '      "summary": "<concise summary of the figure/image (1-3 sentences)>",\n'
    '      "ocr_text": "<text inside the embedded image if any or empty>"\n'
    "    }\n"
    "  ]\n"
    "}\n\n"
    "Important: Do NOT add extra keys, do NOT return surrounding text. Use empty strings for missing values. If multiple embedded images are found, list them in reading order and assign ids 'img1','img2',... . Use neutral language and avoid speculation. Use 'no text' for ocr_text if none detected."
)
