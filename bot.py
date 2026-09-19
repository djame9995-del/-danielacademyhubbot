import os
import re
import logging
import telebot
from telebot import types
from dotenv import load_dotenv

# Load environment variables (for local testing)
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get token from environment
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables.")

bot = telebot.TeleBot(BOT_TOKEN)

# ---------- Helper Functions ----------

def main_menu():
    """Return the main menu inline keyboard."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_test = types.InlineKeyboardButton("🧪 Test Regex", callback_data="test_regex")
    btn_help = types.InlineKeyboardButton("📖 Help", callback_data="help")
    btn_about = types.InlineKeyboardButton("ℹ️ About", callback_data="about")
    markup.add(btn_test, btn_help, btn_about)
    return markup


def back_menu():
    """Return a single 'Back to Menu' button."""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu"))
    return markup


def format_match_result(pattern, text, flags=0):
    """Run regex and format the result as a readable string."""
    try:
        compiled = re.compile(pattern, flags)
    except re.error as e:
        return f"❌ Invalid regex pattern:\n`{e}`", None

    matches = list(compiled.finditer(text))

    if not matches:
        return "🔍 No matches found.", None

    lines = [f"✅ Found {len(matches)} match(es):\n"]

    for i, m in enumerate(matches, 1):
        lines.append(f"*Match {i}*")
        lines.append(f"  Value: `{m.group()}`")
        lines.append(f"  Span:  {m.start()}–{m.end()}")

        if m.groups():
            lines.append("  Groups:")
            for gi, g in enumerate(m.groups(), 1):
                lines.append(f"    {gi}: `{g}`")

        if m.groupdict():
            lines.append("  Named Groups:")
            for name, val in m.groupdict().items():
                lines.append(f"    {name}: `{val}`")

        lines.append("")

    return "\n".join(lines), len(matches)


def parse_input(text):
    """
    Parse user input of the form:
        /regex <pattern> | <text>
    Also supports plain format without command.
    Returns (pattern, text) or (None, None) if parsing fails.
    """
    # Remove /regex command if present
    if text.startswith('/regex'):
        text = text[len('/regex'):].strip()

    if '|' not in text:
        return None, None

    pattern, sample = text.split('|', 1)
    return pattern.strip(), sample.strip()


# ---------- Command Handlers ----------

@bot.message_handler(commands=['start'])
def cmd_start(message):
    welcome = (
        "👋 *Welcome to Regex Tester Bot!*\n\n"
        "I help you test regular expressions quickly.\n\n"
        "*How to use:*\n"
        "Send a message in this format:\n"
        "`<pattern> | <text>`\n\n"
        "*Example:*\n"
        "`\\d{4}-\\d{2}-\\d{2} | Today is 2026-06-01`\n\n"
        "You can also use the `/regex` command:\n"
        "`/regex <pattern> | <text>`"
    )
    bot.send_message(message.chat.id, welcome, parse_mode='Markdown', reply_markup=main_menu())


@bot.message_handler(commands=['help'])
def cmd_help(message):
    help_text = (
        "📖 *Help*\n\n"
        "*Format:*\n"
        "Send `<pattern> | <text>`\n\n"
        "*Examples:*\n"
        "• `\\d+ | Order 123 and 456`\n"
        "• `[A-Z]\\w+ | Hello World`\n"
        "• `(\\w+)@(\\w+)\\.com | mail me at john@example.com`\n\n"
        "*What you get:*\n"
        "• All matches\n"
        "• Capture groups\n"
        "• Named groups\n"
        "• Match positions\n\n"
        "Use `/regex` before your input if you want to be explicit."
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown', reply_markup=back_menu())


@bot.message_handler(commands=['about'])
def cmd_about(message):
    about_text = (
        "ℹ️ *About Regex Tester Bot*\n\n"
        "This bot is an educational tool for developers and students "
        "to test regular expressions directly inside Telegram.\n\n"
        "It shows matches, groups, named groups, and match positions "
        "in real time — no external website needed.\n\n"
        "Built with Python and deployed on Railway."
    )
    bot.send_message(message.chat.id, about_text, parse_mode='Markdown', reply_markup=back_menu())


@bot.message_handler(commands=['regex'])
def cmd_regex(message):
    pattern, text = parse_input(message.text)

    if not pattern:
        bot.reply_to(
            message,
            "⚠️ Please use the format:\n`/regex <pattern> | <text>`\n\n"
            "Example:\n`/regex \\d+ | I have 12 apples and 3 oranges`",
            parse_mode='Markdown'
        )
        return

    result, count = format_match_result(pattern, text)
    bot.reply_to(message, result, parse_mode='Markdown')


# ---------- Callback Query Handlers (buttons) ----------

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        if call.data == "menu":
            bot.edit_message_text(
                "🏠 *Main Menu*\n\nChoose an option below:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='Markdown',
                reply_markup=main_menu()
            )

        elif call.data == "test_regex":
            bot.edit_message_text(
                "🧪 *Test Regex*\n\nSend me a message in this format:\n"
                "`<pattern> | <text>`\n\n"
                "*Example:*\n"
                "`\\d{4} | Year 2026`",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='Markdown',
                reply_markup=back_menu()
            )

        elif call.data == "help":
            bot.edit_message_text(
                "📖 *Help*\n\nFormat: `<pattern> | <text>`\n\n"
                "*Examples:*\n"
                "• `\\d+ | Order 123`\n"
                "• `[A-Z]\\w+ | Hello World`\n"
                "• `(\\w+)@(\\w+)\\.com | john@example.com`",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='Markdown',
                reply_markup=back_menu()
            )

        elif call.data == "about":
            bot.edit_message_text(
                "ℹ️ *About*\n\nEducational regex testing bot built "
                "with Python and deployed on Railway.\n\n"
                "Shows matches, groups, and positions in real time.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='Markdown',
                reply_markup=back_menu()
            )

        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.exception("Callback error")
        bot.answer_callback_query(call.id, text="Something went wrong.")


# ---------- Plain Text Handler (main regex tester) ----------

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    # Ignore messages that are commands
    if message.text.startswith('/'):
        return

    pattern, text = parse_input(message.text)

    if not pattern:
        bot.reply_to(
            message,
            "⚠️ Format not recognized.\n\n"
            "Please send:\n`<pattern> | <text>`\n\n"
            "*Example:*\n`\\d+ | Item 42`",
            parse_mode='Markdown'
        )
        return

    result, count = format_match_result(pattern, text)
    bot.reply_to(message, result, parse_mode='Markdown')


# ---------- Start the Bot ----------

if __name__ == '__main__':
    logger.info("Starting Regex Tester Bot...")
    bot.infinity_polling(timeout=30, long_polling_timeout=30)
