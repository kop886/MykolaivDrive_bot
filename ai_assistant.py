from google import genai

# Твій ключ
API_KEY = "AIzaSyDPVGEo-PQ3gm81o3L_oUF5X8nNbfnhtzE"

# Ініціалізація клієнта
client = genai.Client(api_key=API_KEY)

async def get_ai_answer(user_question):
    try:
        # 1. Отримуємо список моделей
        # В новій бібліотеці це ітератор, тому перетворюємо на список
        available_models = [
            m.name for m in client.models.list() 
            if 'generateContent' in m.supported_actions
        ]

        if not available_models:
            return "На жаль, доступних моделей не знайдено."

        # 2. Шукаємо 1.5-flash (зазвичай це 'models/gemini-1.5-flash')
        model_name = next((m for m in available_models if "1.5-flash" in m), available_models[0])

        # 3. Твій оригінальний промпт
        prompt = (
            f"Ти — професійний автомеханік СТО 'MykolaivDrive'. "
            f"Твоє завдання: відповідати ВИКЛЮЧНО на питання, пов'язані з автомобілями, їх ремонтом та обслуговуванням. "
            f"Якщо питання не стосується авто (наприклад, математика, історія, кулінарія чи теорема Піфагора), "
            f"ввічливо відмов і скажи, що ти консультуєш лише щодо автомобілів. "
            f"Відповідай простою мовою БЕЗ використання символів форматування тексту, таких як зірочки чи решітки. "
            f"Запит клієнта: {user_question}. "
            f"В кінці додай фразу: 'Це лише порада. Запишіться до нас у меню!'"
        )

        # 4. ГЕНЕРАЦІЯ (правильний метод — generate_content)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        # Перевіряємо наявність тексту у відповіді
        if response.text:
            clean_text = response.text.replace("*", "").replace("#", "")
            return clean_text
        else:
            return "ШІ не зміг сформувати текстову відповідь."

    except Exception as e:
        # Якщо знову вискочить 429 — це вже точно ліміт Google Free Tier
        if "429" in str(e):
            return "На сьогодні ліміт запитів до ШІ вичерпано. Спробуйте завтра!"
        return f"Вибачте, сталася технічна помилка з ШІ: {e}"