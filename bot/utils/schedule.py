from datetime import datetime, timedelta
from bot.common import get_current_date, logger


def format_schedule_message(schedule_data: dict, all_schedules: list) -> str:
    def safe_text(text: str) -> str:
        """Убираем все спецсимволы которые могут вызвать проблемы"""
        if not text:
            return ""
        return (
            str(text)
            .translate(str.maketrans('', '', '_*[]~`>#+=|{}<>'))
            .strip()
        )

    TOURNAMENTS = {
        'ФМТ': '📐',
        'ГУТ': '⚗️',
        'БХТ': '🧪'
    }

    EVENING_EVENTS = {
        'ВК': '\n• *ВК*\n{}',
        'Киноклуб': '\n• *Киноклуб*\n{}',
        'Самовар': '\n• *Самовар*\n{}'
    }

    # Блок дежурства
    current_date = get_current_date()  # Функция возвращает дату в формате таблицы (напр. "10.04")

    # Дежурство сегодня
    today_duty = safe_text(schedule_data.get('Дежурство', ''))

    # Дежурство завтра (ищем следующую дату)
    tomorrow_duty = ""
    try:
        # Преобразуем текущую дату в datetime
        current_day = datetime.strptime(current_date, "%d.%m")
        next_day = current_day + timedelta(days=1)
        next_date = next_day.strftime("%d.%m")

        # Ищем запись на следующий день
        tomorrow_schedule = next(
            (item for item in all_schedules
             if item.get('дата', '') == next_date),
            None
        )

        if tomorrow_schedule:
            tomorrow_duty = safe_text(tomorrow_schedule.get('Дежурство', ''))

    except Exception as e:
        logger.error(f"Ошибка поиска дежурства: {str(e)}")

    message = [f"📅 Сегодня {safe_text(schedule_data.get('день школы', ''))}-й день КЛШ!", ""]

    # Обработка ПИВ
    piv_value = schedule_data.get('ПИВ', '0')
    try:
        piv = int(piv_value)
        if piv == 1:
            message.extend([
                "🎓 *ПИВ-1*",
                "Состоится первый ПИВ!",
                "• Школьники и школьницы выбирают сквозные курсы и курсы 1 модуля",
                "• Приноси плакаты своих курсов",
                "• Время: 9:30–11:00",
                ""
            ])
        elif piv == 2:
            message.extend([
                "🎓 *ПИВ-2*",
                "Состоится второй ПИВ!",
                "• Школьники и школьницы выбирают только курсы 2 модуля",
                "• Приноси плакаты своих курсов",
                "• Время: 12:30–13:30",
                ""
            ])
        elif piv == 3:
            message.extend([
                "🎉 *ВИП*",
                "Состоится ВИП!",
                "• Школьники и школьницы показывают свои достижения на курсах",
                "• Они принесут плакаты!",
                "• Время: 11:00–12:30",
                ""
            ])
    except (ValueError, TypeError):
        pass

    # Турниры
    tournament_lines = []
    for key, emoji in TOURNAMENTS.items():
        value = safe_text(schedule_data.get(key, '0'))
        try:
            tournament_num = int(value)
            if tournament_num > 0:
                tournament_lines.append(f"• {key}-{tournament_num}")
        except ValueError:
            if value and value != "0":
                tournament_lines.append(f"• {value} {key}")

    if tournament_lines:
        message.extend([
            "🏆 *Пройдут следующие турниры:*",
            *tournament_lines,
            ""
        ])

    # Факультатив
    facultative = schedule_data.get('Факультатив', '0')
    try:
        fac_num = int(facultative)
        if fac_num > 0:
            message.extend([
                "📚 *Факультатив*",
                f"Состоится {fac_num}-е занятие факультатива!",
                ""
            ])
    except (ValueError, TypeError):
        pass

    # Вечерние мероприятия
    evening_events = []
    for key, template in EVENING_EVENTS.items():
        value = safe_text(schedule_data.get(key, ''))
        if value:
            evening_events.append(template.format(value))

    if evening_events:
        message.extend([
            "🕗 *Вечером:*",
            *evening_events,
            ""
        ])

    # Формируем сообщение о дежурстве
    if today_duty or tomorrow_duty:
        duty_message = []
        if today_duty:
            duty_message.append(f"Сегодня дежурят: {today_duty}")
        if tomorrow_duty:
            duty_message.append(f"К завтрашнему дежурству готовятся: {tomorrow_duty}")

        message.extend([
            "\n🫡 *Дежурство*",
            *duty_message,
            ""
        ])

    # Объявления
    announcements = safe_text(schedule_data.get('Объявления', ''))
    if announcements:
        message.extend([
            "❗️ *Объявления* ❗️",
            announcements,
            ""
        ])

    # Удаление последнего переноса
    if message and message[-1] == "":
        message.pop()

    return "\n".join(message).strip()
