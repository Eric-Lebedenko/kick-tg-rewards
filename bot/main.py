import os
from dataclasses import dataclass, field
from typing import Dict, List

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Provide it via environment or .env file.")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:8001")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


@dataclass
class Stats:
    total_prizes: int = 0
    total_amount_usd: float = 0.0
    monthly_prizes: int = 0


@dataclass
class Profile:
    username: str
    twitch_username: str = "realericlmorgan"
    twitch_handle: str = "@realericlmorgan"
    steam_trade_url: str | None = "https://steamcommunity.com/tradeoffer/new/?partner=891699708..."
    participation_active: bool = True
    followed_streamers: List[str] = field(default_factory=lambda: ["Signaturk4"])
    streamers_followers: Dict[str, int] = field(default_factory=lambda: {"Signaturk4": 352})
    stats: Stats = field(default_factory=Stats)
    prizes: List[str] = field(default_factory=list)


profiles: Dict[int, Profile] = {}


def _https_or_none(url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith("https://"):
        return url
    # Telegram inline button не принимает http — вернем None и покажем текстовую ссылку
    return None


def get_profile(user_id: int, username: str | None) -> Profile:
    if user_id not in profiles:
        profiles[user_id] = Profile(username=username or f"user_{user_id}")
    return profiles[user_id]


def action_keyboard() -> InlineKeyboardMarkup | None:
    open_url = _https_or_none(FRONTEND_URL)
    kick_url = _https_or_none(f"{BACKEND_URL}/auth/kick/start")
    buttons = []
    if open_url:
        buttons.append(InlineKeyboardButton(text="Открыть", url=open_url))
    if kick_url:
        buttons.append(InlineKeyboardButton(text="Авторизоваться в Kick", url=kick_url))
    if not buttons:
        return None
    return InlineKeyboardMarkup([buttons])


def profile_keyboard(profile: Profile) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                "Отключить участие" if profile.participation_active else "Активировать участие",
                callback_data="toggle_participation",
            )
        ],
        [InlineKeyboardButton("Отвязать Twitch", callback_data="unlink_twitch")],
        [
            InlineKeyboardButton("Изменить Steam ссылку", callback_data="edit_steam"),
            InlineKeyboardButton("Удалить", callback_data="delete_steam"),
        ],
        [
            InlineKeyboardButton("Показать стримеров", callback_data="show_streamers"),
            InlineKeyboardButton("Показать призы", callback_data="show_prizes"),
        ],
        [
            InlineKeyboardButton("Настройки", callback_data="settings"),
            InlineKeyboardButton("Техподдержка", callback_data="support"),
            InlineKeyboardButton("Начать стримить", callback_data="start_streaming"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def profile_message(profile: Profile) -> str:
    status_text = "Активно" if profile.participation_active else "Выключено"
    steam_text = profile.steam_trade_url or "Не указана"
    streamer_lines = "\n".join(
        f"• {name} — {profile.streamers_followers.get(name, 0)} подписчиков" for name in profile.followed_streamers
    )
    if not streamer_lines:
        streamer_lines = "• Нет отслеживаемых стримеров"
    prizes_text = "Нет призов" if not profile.prizes else "\n".join(f"• {p}" for p in profile.prizes)
    stats = profile.stats
    return (
        "<b>Профиль</b>\n"
        f"Участие в розыгрышах: <b>{status_text}</b>\n\n"
        "<b>Twitch аккаунт</b>\n"
        f"{profile.twitch_username} ({profile.twitch_handle})\n\n"
        "<b>Ссылка обмена Steam</b>\n"
        f"<code>{steam_text}</code>\n\n"
        "<b>Статистика</b>\n"
        f"Призов: {stats.total_prizes} | "
        f"Суммарно: ${stats.total_amount_usd:0.2f} | "
        f"За месяц: {stats.monthly_prizes}\n\n"
        "<b>Отслеживаемые стримеры</b>\n"
        f"{streamer_lines}\n\n"
        "<b>Мои призы</b>\n"
        f"{prizes_text}"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    profile = get_profile(user.id, user.username)
    markup = action_keyboard()
    text_intro = "Привет! Это минимальный бот для наград. Используй /profile для просмотра профиля."
    if not markup:
        text_intro += "\n\n⚠️ Задай публичные https ссылки в переменных FRONTEND_URL и BACKEND_URL, чтобы кнопки работали."
    await update.message.reply_text(text_intro, reply_markup=markup)
    await send_profile(update, context, profile)


async def send_profile(update: Update, context: ContextTypes.DEFAULT_TYPE, profile: Profile) -> None:
    message_func = update.effective_message.reply_html if update.effective_message else update.callback_query.edit_message_text
    markup = action_keyboard()
    await message_func(
        profile_message(profile),
        reply_markup=markup,
    )


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    profile = get_profile(user.id, user.username)
    await send_profile(update, context, profile)


async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    profile = get_profile(user.id, user.username)

    if query.data == "toggle_participation":
        profile.participation_active = not profile.participation_active
    elif query.data == "unlink_twitch":
        profile.twitch_username = "Не привязан"
        profile.twitch_handle = "@not-set"
    elif query.data == "delete_steam":
        profile.steam_trade_url = None
    elif query.data == "edit_steam":
        context.user_data["awaiting_steam"] = True
        await query.edit_message_text(
            "Отправьте новую ссылку обмена Steam. Формат: https://steamcommunity.com/tradeoffer/new/?partner=...",
        )
        return
    elif query.data == "show_streamers":
        await query.edit_message_text(
            "<b>Отслеживаемые стримеры</b>\n" + "\n".join(profile.followed_streamers),
            parse_mode="HTML",
        )
        return
    elif query.data == "show_prizes":
        prizes = "Нет призов" if not profile.prizes else "\n".join(profile.prizes)
        await query.edit_message_text(f"<b>Мои призы</b>\n{prizes}", parse_mode="HTML")
        return
    elif query.data == "settings":
        await query.edit_message_text("Настройки пока заглушка.", parse_mode="HTML")
        return
    elif query.data == "support":
        await query.edit_message_text("Техподдержка: напишите @support.", parse_mode="HTML")
        return
    elif query.data == "start_streaming":
        await query.edit_message_text("Гайд для стримеров появится позже.", parse_mode="HTML")
        return

    await query.edit_message_text(
        profile_message(profile),
        reply_markup=profile_keyboard(profile),
        parse_mode="HTML",
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    profile = get_profile(user.id, user.username)
    if context.user_data.get("awaiting_steam"):
        text = update.message.text.strip()
        profile.steam_trade_url = text
        context.user_data["awaiting_steam"] = False
        await update.message.reply_html(
            "Ссылка обновлена.\n\n" + profile_message(profile),
            reply_markup=profile_keyboard(profile),
        )
    else:
        await update.message.reply_text("Используй /profile чтобы открыть профиль.")


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("profile", show_profile))
    application.add_handler(CallbackQueryHandler(handle_callbacks))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    application.run_polling()


if __name__ == "__main__":
    main()
