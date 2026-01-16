#!/usr/bin/env python3
import psycopg
from dotenv import load_dotenv
import os

load_dotenv()

db_user = os.getenv('DB_USER', 'postgres')
db_pass = os.getenv('DB_PASS', 'finance_dev_pass_2024')
db_name = os.getenv('DB_NAME', 'finance_db')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5433')  # ← Тепер читає з .env!

conn_string = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

print("=" * 60)
print("   PostgreSQL Connection Test")
print("=" * 60)
print()
print(f"🔍 Підключення до: {db_name}@{db_host}:{db_port}")
print()

try:
    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT version();')
            version = cur.fetchone()[0]
            print(f"✅ Підключення успішне!")
            print(f"📊 {version[:70]}...")
            print()

            cur.execute("""
                SELECT tablename
                FROM pg_catalog.pg_tables
                WHERE schemaname = 'public';
            """)
            tables = cur.fetchall()

            if tables:
                print("📋 Таблиці:")
                for t in tables:
                    print(f"   - {t[0]}")
            else:
                print("ℹ️  Таблиці ще не створені (нормально для нової БД)")

            print()
            print("✨ Завдання #3 виконано успішно! ✅")
except Exception as e:
    print(f"❌ Помилка: {e}")