#!/usr/bin/env python3
"""HouseBets setup validator - checks if everything is configured correctly."""

import sys
import os


def print_status(message, status):
    """Print a status message with emoji."""
    emoji = "✅" if status else "❌"
    print(f"{emoji} {message}")
    return status


def check_python_version():
    """Check if Python version is 3.8+."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_status(
            f"Python version {version.major}.{version.minor}.{version.micro}", True
        )
        return True
    else:
        print_status(
            f"Python version {version.major}.{version.minor}.{version.micro} (needs 3.8+)",
            False,
        )
        return False


def check_dependencies():
    """Check if required packages are installed."""
    try:
        import discord

        print_status(f"py-cord installed (version {discord.__version__})", True)
        return True
    except ImportError:
        print_status("py-cord not installed", False)
        print("  → Run: pip install -r requirements.txt")
        return False


def check_env_file():
    """Check if .env file exists and has required values."""
    if not os.path.exists(".env"):
        print_status(".env file not found", False)
        print("  → Run: cp .env.example .env")
        return False

    print_status(".env file exists", True)

    # Check if BOT_TOKEN is set
    with open(".env", "r") as f:
        content = f.read()
        if "BOT_TOKEN=your_discord_bot_token_here" in content:
            print_status("BOT_TOKEN needs to be configured", False)
            print("  → Edit .env and add your Discord bot token")
            return False
        elif (
            "BOT_TOKEN=" in content
            and len(content.split("BOT_TOKEN=")[1].split()[0]) > 10
        ):
            print_status("BOT_TOKEN appears to be configured", True)
            return True
        else:
            print_status("BOT_TOKEN not found in .env", False)
            return False


def check_file_structure():
    """Check if all required files exist."""
    required_files = [
        "main.py",
        "config.py",
        "requirements.txt",
        "cogs/markets.py",
        "cogs/betting.py",
        "cogs/leaderboard.py",
        "cogs/resolution.py",
        "database/db.py",
        "ui/modals.py",
        "ui/buttons.py",
        "ui/embeds.py",
        "utils/pricing.py",
        "utils/helpers.py",
    ]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            continue
        else:
            print_status(f"Missing file: {file}", False)
            all_exist = False

    if all_exist:
        print_status("All required files present", True)

    return all_exist


def check_config():
    """Check if config can be loaded."""
    try:
        import config

        print_status("Configuration loads successfully", True)

        # Check important config values
        if hasattr(config, "INITIAL_BALANCE"):
            print(
                f"  → Initial balance: {config.INITIAL_BALANCE} {config.CURRENCY_NAME}"
            )

        return True
    except Exception as e:
        print_status(f"Configuration error: {str(e)}", False)
        return False


def check_database():
    """Check if database can be initialized."""
    try:
        from database import db

        print_status("Database initializes successfully", True)

        # Try to create a test user
        test_user = db.get_or_create_user("test_user_123", "test_guild_123")
        if test_user:
            print("  → Database operations working")

        return True
    except Exception as e:
        print_status(f"Database error: {str(e)}", False)
        return False


def main():
    """Run all checks."""
    print("🎲 HouseBets Setup Validator\n")
    print("=" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("File Structure", check_file_structure),
        ("Configuration", check_config),
        ("Database", check_database),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        try:
            results.append(check_func())
        except Exception as e:
            print_status(f"Unexpected error: {str(e)}", False)
            results.append(False)

    print("\n" + "=" * 50)

    if all(results):
        print("\n✅ All checks passed! Your bot is ready to run.")
        print("\nTo start the bot:")
        print("  ./start.sh")
        print("  or")
        print("  python3 main.py")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        print("\nFor help, see:")
        print("  - SETUP.md for setup instructions")
        print("  - README.md for full documentation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
