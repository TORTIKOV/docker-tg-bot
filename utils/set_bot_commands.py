from aiogram import types


async def set_default_commands(dp) -> None:
    await dp.bot.set_my_commands([
        types.BotCommand('start', 'Перезапуск бота'),
        types.BotCommand('help', 'Помощь'),
        types.BotCommand('update_info', 'Зарегестрироваться'),
        types.BotCommand('update_username', 'Обновить имя(для доставщиков)'),
        types.BotCommand('main_menu', 'Главное меню')
    ])
