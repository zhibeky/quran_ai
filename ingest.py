from minsearch import AppendableIndex
import json

with open("quran_with_tafsir.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

index = AppendableIndex(
    text_fields=["text", "tafsir_text"],
    keyword_fields=["surah_number", "surah_name", "ayah_number", "reference", "text", "tafsir_text"]
)

index.fit(documents)
print("Ingestion done ✅")