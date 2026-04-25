import sqlite3

class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.stvoriti_tablici()

    def stvoriti_tablici(self):
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                pib TEXT,
                phone TEXT,
                car_info TEXT,
                problem TEXT,
                status TEXT DEFAULT 'Новий запис'
            )
        """)
        self.connection.commit()

    def dodati_id(self, user_id):
        with self.connection:
            return self.cursor.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
                (user_id,)
            )

    def onoviti_zapis(self, user_id, pib, phone, car, problem):
        with self.connection:
            return self.cursor.execute("""
            UPDATE users 
            SET pib = ?, phone = ?, car_info = ?, problem = ?, status = 'Оновлено'
            WHERE user_id = ?
        """, (pib, phone, car, problem, user_id))

    def pereviriti_zapis(self, user_id):
        with self.connection:
            # Шукаємо тільки один  запис для конкретного юзера
            result = self.cursor.execute(
                "SELECT pib, car_info, problem FROM users WHERE user_id = ? AND car_info IS NOT NULL", 
                (user_id,)
            ).fetchone() 
            return result
        
    def vidaliti_zapis(self, user_id):
        with self.connection:
            # Ми не видаляємо юзера зовсім, а просто "обнуляємо" його запис
            return self.cursor.execute("""
                UPDATE users 
                SET pib = NULL, phone = NULL, car_info = NULL, problem = NULL 
                WHERE user_id = ?
            """, (user_id,))    
        
   