import os
import json
import asyncio
import random
from aiogram import Bot, Dispatcher, types
from huggingface_hub import InferenceClient

# Ключи из Environment Variables
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(token=HF_TOKEN)

# 1. Загрузка стиля (упрощенная)
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    # Извлекаем только текст сообщений
    if isinstance(data, dict) and 'messages' in data:
        texts = if m.get('text')]
    else:
        texts = [str(t) for t in data if t]

def get_random_style(query, count=3):
    # Вместо тяжелого ИИ-поиска берем случайные примеры или ищем по словам
    # Для 2 МБ это работает мгновенно и экономит всю память
    relevant = [t for t in texts if any(word.lower() in t.lower() for word in query.split() if len(word) > 3)]
    if len(relevant) < count:
        return "\n---\n".join(random.sample(texts, min(len(texts), count)))
    return "\n---\n".join(random.sample(relevant, count))

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

@dp.message()
async def chat(message: types.Message):
    style_context = get_random_style(message.text)
    prompt = f"Ты участник сообщества. Твои примеры стиля:\n{style_context}\n\nСообщение: {message.text}\nОтвет:"
    
    try:
        # Используем легкую модель через API Hugging Face
        response = client.text_generation(
            prompt,
            model="mistralai/Mistral-7B-Instruct-v0.3",
            max_new_tokens=150,
            temperature=0.8
        )
        await message.answer(response)
    except Exception as e:
        print(f"Ошибка: {e}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
