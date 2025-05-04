import sqlite3
from core.utils.logger import logger


def get_user_profile_from_db(user_id: int):
    try:
        conn = sqlite3.connect("my_bd")
        cursor = conn.cursor()
        cursor.execute("SELECT share, price, count FROM profile WHERE id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        logger.exception("Ошибка при получении данных из БД")
        return []


def save_share_to_db(user_id: int, share: str, price: float, count: int):
    try:
        conn = sqlite3.connect("my_bd")
        cursor = conn.cursor()

        normalized_share = share.upper()

        cursor.execute(
            "SELECT 1 FROM profile WHERE id = ? AND share = ?",
            (user_id, normalized_share)
        )

        if cursor.fetchone():
            cursor.execute(
                """UPDATE profile 
                SET count = count + ?, 
                    price = ((price * count) + (? * ?)) / (count + ?)
                WHERE id = ? AND share = ?""",
                (count, price, count, count, user_id, normalized_share)
            )
        else:
            cursor.execute(
                "INSERT INTO profile (id, share, price, count) VALUES (?, ?, ?, ?)",
                (user_id, normalized_share, price, count)
            )

        conn.commit()
    except Exception as e:
        logger.exception(f"Ошибка при сохранении акции в БД: {str(e)}")
    finally:
        conn.close()
