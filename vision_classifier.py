from functools import lru_cache

import torch
from PIL import Image, ImageOps
from transformers import AutoImageProcessor, SiglipForImageClassification

MODEL_NAME = "prithivMLmods/Trash-Net"
CATEGORY_MAP = {
    "cardboard": "Бумага", "paper": "Бумага",
    "plastic": "Пластик", "metal": "Металл",
    "glass": "Стекло", "organic": "Органика", "biological": "Органика",
    "trash": "Другое", "garbage": "Другое",
}

@lru_cache(maxsize=1)
def _load_model():
    processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
    model = SiglipForImageClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return processor, model

def classify_image(uploaded_file):
    image = ImageOps.exif_transpose(Image.open(uploaded_file)).convert("RGB")
    processor, model = _load_model()
    inputs = processor(images=image, return_tensors="pt")
    with torch.inference_mode():
        probabilities = torch.softmax(model(**inputs).logits, dim=1)[0]
    index = int(torch.argmax(probabilities).item())
    confidence = float(probabilities[index].item())
    predicted_class = str(model.config.id2label[index]).lower().strip()
    category = CATEGORY_MAP.get(predicted_class, "Другое")
    return category, confidence, predicted_class
