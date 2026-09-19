# Regex Tester Bot

An educational Telegram bot that tests regular expressions and shows
matches, capture groups, named groups, and match positions in real time.

## Features

- Test any regex pattern with sample text
- See all matches with their positions
- Display numbered and named capture groups
- No external links — everything works inside Telegram

## Usage

Send a message in this format:

    <pattern> | <text>

Example:

    \d{4}-\d{2}-\d{2} | Today is 2026-06-01

Or use the command form:

    /regex <pattern> | <text>

## Commands

- `/start` — Welcome and main menu
- `/help` — Usage instructions
- `/about` — Bot information
- `/regex` — Explicit regex test command

## Tech Stack

- Python 3.11
- pyTelegramBotAPI
- Deployed on Railway
