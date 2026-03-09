"""Reset the HouseBets database.

Usage:
  python reset_db.py           # wipe all data, keep schema
  python reset_db.py --hard    # delete the .db file entirely and recreate
"""

import sys
import os
import sqlite3
import config


def soft_reset(guild_id: str = None):
    """Delete all rows but keep tables intact. Optionally scope to a single guild."""
    if not os.path.exists(config.DATABASE_PATH):
        print("No database file found — nothing to reset.")
        return

    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()

    if guild_id:
        cursor.execute("DELETE FROM bets WHERE guild_id = ?", (guild_id,))
        cursor.execute("DELETE FROM markets WHERE guild_id = ?", (guild_id,))
        cursor.execute("DELETE FROM users WHERE guild_id = ?", (guild_id,))
        print(f"✅ Soft reset complete for guild {guild_id} — guild rows deleted, schema kept.")
    else:
        cursor.execute("DELETE FROM bets")
        cursor.execute("DELETE FROM markets")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('bets','markets','users')")
        print("✅ Soft reset complete — all rows deleted, schema kept.")

    conn.commit()
    conn.close()


def hard_reset():
    """Delete the .db file entirely and let the bot recreate it on next start."""
    if os.path.exists(config.DATABASE_PATH):
        os.remove(config.DATABASE_PATH)
        print(f"✅ Hard reset complete — {config.DATABASE_PATH} deleted.")
    else:
        print("No database file found — nothing to delete.")

    # Recreate schema immediately so the file exists
    from database.db import Database
    Database()
    print("✅ Fresh schema created.")


if __name__ == "__main__":
    guild_arg = None
    for arg in sys.argv[1:]:
        if arg.startswith("--guild="):
            guild_arg = arg.split("=", 1)[1]

    if "--hard" in sys.argv:
        confirm = input(f"⚠️  This will DELETE {config.DATABASE_PATH} entirely. Type 'yes' to confirm: ")
        if confirm.strip().lower() == "yes":
            hard_reset()
        else:
            print("Aborted.")
    else:
        scope = f" for guild {guild_arg}" if guild_arg else ""
        confirm = input(f"⚠️  This will wipe ALL users, markets, and bets{scope}. Type 'yes' to confirm: ")
        if confirm.strip().lower() == "yes":
            soft_reset(guild_arg)
        else:
            print("Aborted.")
