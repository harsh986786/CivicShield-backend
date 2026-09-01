import os
import json
import logging

logger = logging.getLogger(__name__)

def analyze_sarcasm(text: str) -> dict:
    result = analyze_sentiment_and_emotion(text)
    return {
        "is_sarcastic": result.get("is_sarcastic", False),
        "sarcasm_confidence": result.get("sarcasm_confidence", 0.0)
    }

def analyze_sentiment_and_emotion(text: str) -> dict:
    fallback_res = {
        "sentiment": "neutral",
        "emotion": "neutral",
        "confidence": 0.85,
        "model_version": "groq-llama-3.1-8b",
        "is_sarcastic": False,
        "sarcasm_confidence": 0.0
    }
    
    if not text or not str(text).strip():
        return fallback_res

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key.startswith("gsk_your"):
        return fallback_res

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        prompt = f"""Analyze this social post for civil tension/unrest. Return ONLY valid JSON:
{{"sentiment": "positive" | "negative" | "neutral", "emotion": "anger" | "fear" | "joy" | "sadness" | "neutral", "confidence": 0.88, "is_sarcastic": false, "sarcasm_confidence": 0.1}}

Text: "{str(text)[:300]}"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        data = json.loads(response.choices[0].message.content)
        return {
            "sentiment": str(data.get("sentiment", "neutral")).lower(),
            "emotion": str(data.get("emotion", "neutral")).lower(),
            "confidence": round(float(data.get("confidence", 0.85)), 2),
            "model_version": "groq-llama-3.1-8b",
            "is_sarcastic": bool(data.get("is_sarcastic", False)),
            "sarcasm_confidence": round(float(data.get("sarcasm_confidence", 0.0)), 2)
        }
    except Exception as e:
        logger.warning(f"Groq fallback engaged: {e}")
        return fallback_res