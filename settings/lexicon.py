START_TEXT = '''
<b>
Добро пожаловать в бот для розыгрышей! 🌟
</b>

Бот умеет запускать розыгрыши среди участников одного или нескольких каналов Телеграма и самостоятельно выбирать победителей в назначенное время.

Выбери действие:
'''



EVENT_TEXT = """
💎 Название розыгрыша:
    <b>{name}</b>

📜 Описание:
    {description}

Участников: <b>{users_count}</b>
Призовых мест: <b>{win_count}</b>
Дата окончания розыгрыша: <b>{raffle_date}</b> MSK
"""

EVENT_WIN_TEXT = """
🚀 Результаты розыгрыша:
    <b>{name}</b>

📜 Победители:
    {winners}

Участников: <b>{users_count}</b>
Призовых мест: <b>{win_count}</b>
Дата окончания розыгрыша: <b>{raffle_date}</b> MSK
"""






ADMIN_ADD_TICKETS_TEXT = '''

Счастливые билеты:

{tickets}

Подтвердите правильность
'''
