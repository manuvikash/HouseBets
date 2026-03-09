"""Database initialization and connection management."""

import sqlite3
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import config


class Database:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Get a database connection."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database schema."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table — one row per (discord_id, guild_id) pair
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT NOT NULL,
                guild_id TEXT NOT NULL,
                balance REAL DEFAULT 1000.0,
                total_profit REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(discord_id, guild_id)
            )
        """)

        # Markets table — scoped to a guild
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS markets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                creator_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                question TEXT NOT NULL,
                outcomes TEXT NOT NULL,
                liquidity TEXT NOT NULL,
                close_time TIMESTAMP NOT NULL,
                resolved BOOLEAN DEFAULT 0,
                winning_outcome TEXT,
                resolved_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Bets table — market_id already scopes to a guild implicitly
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                guild_id TEXT NOT NULL,
                market_id INTEGER NOT NULL,
                outcome TEXT NOT NULL,
                shares REAL NOT NULL,
                cost REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (market_id) REFERENCES markets(id)
            )
        """)

        conn.commit()
        conn.close()

    # ── User operations ──────────────────────────────────────────────────────

    def get_or_create_user(self, discord_id: str, guild_id: str) -> Dict[str, Any]:
        """Get user in a guild, or create if doesn't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE discord_id = ? AND guild_id = ?",
            (discord_id, guild_id),
        )
        user = cursor.fetchone()

        if user is None:
            cursor.execute(
                "INSERT INTO users (discord_id, guild_id, balance) VALUES (?, ?, ?)",
                (discord_id, guild_id, config.INITIAL_BALANCE),
            )
            conn.commit()
            cursor.execute(
                "SELECT * FROM users WHERE discord_id = ? AND guild_id = ?",
                (discord_id, guild_id),
            )
            user = cursor.fetchone()

        conn.close()
        return dict(user)

    def update_balance(self, discord_id: str, guild_id: str, new_balance: float):
        """Update user balance within a guild."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET balance = ? WHERE discord_id = ? AND guild_id = ?",
            (new_balance, discord_id, guild_id),
        )
        conn.commit()
        conn.close()

    def update_profit(self, discord_id: str, guild_id: str, profit_delta: float):
        """Update user total profit within a guild."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET total_profit = total_profit + ? WHERE discord_id = ? AND guild_id = ?",
            (profit_delta, discord_id, guild_id),
        )
        conn.commit()
        conn.close()

    def get_leaderboard(self, guild_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by total profit within a guild."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE guild_id = ? ORDER BY total_profit DESC LIMIT ?",
            (guild_id, limit),
        )
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users

    # ── Market operations ────────────────────────────────────────────────────

    def create_market(
        self,
        guild_id: str,
        creator_id: str,
        target_id: str,
        question: str,
        outcomes: List[str],
        close_time: datetime,
    ) -> int:
        """Create a new market within a guild."""
        conn = self.get_connection()
        cursor = conn.cursor()

        liquidity = {outcome: config.INITIAL_LIQUIDITY for outcome in outcomes}

        cursor.execute(
            """
            INSERT INTO markets (guild_id, creator_id, target_id, question, outcomes, liquidity, close_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                guild_id,
                creator_id,
                target_id,
                question,
                json.dumps(outcomes),
                json.dumps(liquidity),
                close_time,
            ),
        )

        market_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return market_id

    def get_market(self, market_id: int) -> Optional[Dict[str, Any]]:
        """Get market by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM markets WHERE id = ?", (market_id,))
        market = cursor.fetchone()
        conn.close()

        if market:
            market_dict = dict(market)
            market_dict["outcomes"] = json.loads(market_dict["outcomes"])
            market_dict["liquidity"] = json.loads(market_dict["liquidity"])
            return market_dict
        return None

    def get_active_markets(
        self, guild_id: str, exclude_discord_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all active (unresolved) markets in a guild."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM markets WHERE resolved = 0 AND guild_id = ?"
        params: list = [guild_id]

        if exclude_discord_id:
            query += " AND target_id != ?"
            params.append(exclude_discord_id)

        cursor.execute(query, params)
        markets = [dict(row) for row in cursor.fetchall()]
        conn.close()

        for market in markets:
            market["outcomes"] = json.loads(market["outcomes"])
            market["liquidity"] = json.loads(market["liquidity"])

        return markets

    def get_user_markets(self, creator_id: str, guild_id: str) -> List[Dict[str, Any]]:
        """Get markets created by user in a guild."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM markets WHERE creator_id = ? AND guild_id = ? ORDER BY created_at DESC",
            (creator_id, guild_id),
        )
        markets = [dict(row) for row in cursor.fetchall()]
        conn.close()

        for market in markets:
            market["outcomes"] = json.loads(market["outcomes"])
            market["liquidity"] = json.loads(market["liquidity"])

        return markets

    def update_market_liquidity(self, market_id: int, liquidity: Dict[str, float]):
        """Update market liquidity after a bet."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE markets SET liquidity = ? WHERE id = ?",
            (json.dumps(liquidity), market_id),
        )
        conn.commit()
        conn.close()

    def resolve_market(self, market_id: int, winning_outcome: str):
        """Mark market as resolved."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE markets SET resolved = 1, winning_outcome = ?, resolved_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (winning_outcome, market_id),
        )
        conn.commit()
        conn.close()

    # ── Bet operations ───────────────────────────────────────────────────────

    def place_bet(
        self, user_id: str, guild_id: str, market_id: int, outcome: str, shares: float, cost: float
    ):
        """Record a bet."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO bets (user_id, guild_id, market_id, outcome, shares, cost)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, guild_id, market_id, outcome, shares, cost),
        )
        conn.commit()
        conn.close()

    def get_user_position(self, user_id: str, market_id: int) -> Dict[str, float]:
        """Get user's position in a market (shares per outcome)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT outcome, SUM(shares) as total_shares, SUM(cost) as total_cost
            FROM bets
            WHERE user_id = ? AND market_id = ?
            GROUP BY outcome
            """,
            (user_id, market_id),
        )

        positions = {}
        for row in cursor.fetchall():
            positions[row["outcome"]] = {
                "shares": row["total_shares"],
                "cost": row["total_cost"],
            }

        conn.close()
        return positions

    def get_market_bets(self, market_id: int) -> List[Dict[str, Any]]:
        """Get all bets for a market."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bets WHERE market_id = ?", (market_id,))
        bets = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return bets


# Global database instance
db = Database()
