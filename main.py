import os
import json
import asyncio
import random
from aiogram import Bot, Dispatcher, types
from huggingface_hub import InferenceClient

# Ключи из Environment Variables
TG_TOKEN = os.getenv("TG_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(token=HF_TOKEN)

# 1. Загрузка стиля (облегченная версия)
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    # Пытаемся достать сообщения из разных структур JSON
    if isinstance(data, dict) and 'messages' in data:
        raw_messages = data['messages']
    elif isinstance(data, list):
        raw_messages = data
    else:
        raw_messages = [data]

texts = []
for msg in raw_messages:
    if isinstance(msg, dict):
        t = msg.get('text', '')
        # Если текст пришел списком (бывает в некоторых API), склеиваем его
        if isinstance(t, list):
            t = "".join([str(part) for part in t])
        if t: 
            texts.append(str(t))
    elif isinstance(msg, str):
        texts.append(msg)

def get_style(query):
    # Берем 3 случайных примера из вашего JSON для имитации стиля
    if len(texts) > 3:
        samples = random.sample(texts, 3)
    else:
        samples = texts
    return "\n---\n".join(samples)

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

@dp.message()
async def chat(message: types.Message):
    style_context = get_style(message.text)
    # Формируем промпт для нейросети
    prompt = f"Ты участник сообщества. Твои примеры стиля:\n{style_context}\n\nПользователь пишет: {message.text}\nТвой ответ в этом стиле:"
    
    try:
        # Используем мощную, но доступную через API модель
        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="mistralai/Mistral-7B-Instruct-v0.3",
            max_tokens=200,
            temperature=0.8
        )
        await message.answer(response.choices[0].message.content)
    except Exception as e:
        print(f"Ошибка ИИ: {e}")

async def main():
    print("🚀 Бот запущен на Koyeb!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
