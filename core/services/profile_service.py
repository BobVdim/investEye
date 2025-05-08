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


def delete_share_from_db(user_id: int, share: str):
    try:
        conn = sqlite3.connect("my_bd")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM profile WHERE id = ? AND share = ?", (user_id, share.upper()))
        conn.commit()
    except Exception:
        logger.exception("Ошибка при удалении акции")
    finally:
        conn.close()


def delete_share_count_in_db(user_id: int, share: str, count_to_reduce: int):
    try:
        conn = sqlite3.connect("my_bd")
        cursor = conn.cursor()

        cursor.execute("SELECT count FROM profile WHERE id = ? AND share = ?", (user_id, share.upper()))
        result = cursor.fetchone()
        if not result:
            return False
        current_count = result[0]

        if current_count <= count_to_reduce:
            cursor.execute("DELETE FROM profile WHERE id = ? AND share = ?", (user_id, share.upper()))
        else:
            cursor.execute(
                "UPDATE profile SET count = count - ? WHERE id = ? AND share = ?",
                (count_to_reduce, user_id, share.upper())
            )

        conn.commit()
        return True
    except Exception:
        logger.exception("Ошибка при уменьшении количества акции")
        return False
    finally:
        conn.close()
