import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from huggingface_hub import InferenceClient
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Ключи из Secrets
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# Инициализация клиента Hugging Face (вместо OpenRouter)
# Вы можете выбрать любую модель, например: "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
client = InferenceClient(token=HF_TOKEN)

# 1. Загрузка стиля из JSON (RAG)
print("📂 Загрузка базы знаний...")
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Универсальный обработчик структуры JSON
texts = []
# Если это экспорт из Telegram Desktop (словарь с ключом 'messages')
if isinstance(data, dict) and 'messages' in data:
    raw_messages = data['messages']
# Если это просто список сообщений
elif isinstance(data, list):
    raw_messages = data
else:
    raw_messages = [data]

for msg in raw_messages:
    if isinstance(msg, dict):
        # В Telegram текст может быть строкой или списком (если есть ссылки/эмодзи)
        t = msg.get('text', '')
        if isinstance(t, list):
            # Собираем текст из кусочков
            t = "".join([part if isinstance(part, str) else part.get('text', '') for part in t])
        if t:
            texts.append(str(t))
    elif isinstance(msg, str):
        texts.append(msg)

# Если тексты не найдены, создаем минимальную заглушку
if not texts:
    texts = ["Привет", "Как дела?"]
    print("⚠️ Тексты не найдены в JSON!")
else:
    print(f"✅ Успешно извлечено {len(texts)} сообщений.")

# Далее идет создание базы знаний (оставляйте как было)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = FAISS.from_texts(texts, embeddings)

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

@dp.message()
async def chat(message: types.Message):
    # Поиск примеров стиля
    docs = vector_db.similarity_search(message.text, k=3)
    style_context = "\n---\n".join([d.page_content for d in docs])

    prompt = f"Ты участник сообщества. Твои примеры стиля:\n{style_context}\n\nСообщение: {message.text}\nОтвет:"

    try:
        # Прямой вызов бесплатной модели через Hugging Face
        response = client.text_generation(
            prompt,
            model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", # Или "mistralai/Mistral-7B-Instruct-v0.3"
            max_new_tokens=200,
            temperature=0.7
        )
        await message.answer(response)
    except Exception as e:
        print(f"Ошибка: {e}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())