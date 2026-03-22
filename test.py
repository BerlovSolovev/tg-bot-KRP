
# Автоматический тест для проверки функциональности добавления доходов и расходов
# Связан с тестовым случаем TC-001: "Добавление доходов/расходов"

import pytest
import json
from unittest.mock import MagicMock, patch, call
from datetime import datetime
import uuid
import sys
import os
sys.path.append(os.path.dirname(__file__))
import bot

@pytest.fixture
def mock_ydb(monkeypatch):
    """Мокируем YDB для локального тестирования"""
    mock_driver = MagicMock()
    mock_driver.wait.return_value = None

    class FakeSession:
        def __init__(self):
            self.transaction = MagicMock()
            self.transaction.return_value.execute = self.execute
            self._execute_calls = []

        def execute(self, query, commit_tx=False):
            self._execute_calls.append(query)
            return [MagicMock(rows=[])]

        def execute_scheme(self, query):
            pass

    fake_session = FakeSession()

    def fake_pool(func):
        class FakePool:
            def __init__(self, driver):
                self.driver = driver
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def checkout(self):
                return fake_session
        return FakePool(mock_driver)

    monkeypatch.setattr(bot, 'init_ydb', lambda: mock_driver)
    monkeypatch.setattr(bot, 'SessionPool', fake_pool)
    return fake_session

@pytest.fixture(autouse=True)
def reset_globals():
    bot.bot_token = None
    bot.driver = None

@pytest.mark.issue("TC-001")
def test_add_income(mock_db):
    """Тест добавления дохода"""
    user_id = 12345
    amount = 1000.50
    category = "salary"
    description = "monthly salary"

    result = bot.add_income(user_id, amount, category, description)

    assert result is True
    # Проверяем, что был выполнен INSERT в таблицу incomes
    assert len(mock_db._execute_calls) > 0
    insert_query = mock_db._execute_calls[0]
    assert "INSERT INTO incomes" in insert_query
    assert str(user_id) in insert_query
    assert str(amount) in insert_query
    assert category in insert_query
    assert description in insert_query

@pytest.mark.issue("TC-001")
def test_add_expense(mock_db):
    """Тест добавления расхода"""
    user_id = 12345
    amount = 500.75
    category = "food"
    description = "lunch"

    result = bot.add_expense(user_id, amount, category, description)

    assert result is True
    assert len(mock_db._execute_calls) > 0
    insert_query = mock_db._execute_calls[0]
    assert "INSERT INTO expenses" in insert_query
    assert str(user_id) in insert_query
    assert str(amount) in insert_query
    assert category in insert_query
    assert description in insert_query

@pytest.mark.issue("TC-001")
def test_parse_message_valid():
    """Тест парсинга корректного сообщения"""
    text = "1500 продукты"
    amount, category, description = bot.parse_message(text)
    assert amount == 1500.0
    assert category == "продукты"
    assert description == ""

    text = "500 транспорт такси до работы"
    amount, category, description = bot.parse_message(text)
    assert amount == 500.0
    assert category == "транспорт"
    assert description == "такси до работы"

    text = "3000 развлечения"
    amount, category, description = bot.parse_message(text)
    assert amount == 3000.0
    assert category == "развлечения"
    assert description == ""

@pytest.mark.issue("TC-001")
def test_parse_message_invalid():
    """Тест парсинга некорректного сообщения"""
    text = "не число категория"
    amount, category, description = bot.parse_message(text)
    assert amount is None
    assert category is None
    assert description is None

    text = "1500"
    amount, category, description = bot.parse_message(text)
    assert amount is None
    assert category is None
    assert description is None


@patch('bot.send_telegram_message')
@patch('bot.add_income')
@patch('bot.add_expense')
def test_handler_message_income(mock_add_expense, mock_add_income, mock_send):
    """Тест обработчика сообщения для дохода"""
    # Создаем событие, имитирующее сообщение с доходом
    event = {
        'body': json.dumps({
            'message': {
                'chat': {'id': 12345},
                'text': '50000 зарплата аванс'
            }
        })
    }
    context = {}

    # Вызываем обработчик
    bot.handler(event, context)

    # Проверяем, что вызвана add_income, а не add_expense
    mock_add_income.assert_called_once_with(12345, 50000.0, 'зарплата', 'аванс')
    mock_add_expense.assert_not_called()
    # Проверяем, что отправлено сообщение об успехе
    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    assert args[0] == 12345
    assert "Доход добавлен" in args[1]


@patch('bot.send_telegram_message')
@patch('bot.add_income')
@patch('bot.add_expense')
def test_handler_message_expense(mock_add_expense, mock_add_income, mock_send):
    """Тест обработчика сообщения для расхода"""
    event = {
        'body': json.dumps({
            'message': {
                'chat': {'id': 12345},
                'text': '1500 продукты'
            }
        })
    }
    context = {}

    bot.handler(event, context)

    mock_add_expense.assert_called_once_with(12345, 1500.0, 'продукты', '')
    mock_add_income.assert_not_called()
    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    assert args[0] == 12345
    assert "Расход добавлен" in args[1]


@patch('bot.send_telegram_message')
def test_handler_message_invalid_format(mock_send):
    """Тест обработчика сообщения с некорректным форматом"""
    event = {
        'body': json.dumps({
            'message': {
                'chat': {'id': 12345},
                'text': 'неправильный формат'
            }
        })
    }
    context = {}

    bot.handler(event, context)

    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    assert args[0] == 12345
    assert "Неверный формат" in args[1]


@patch('bot.send_telegram_message')
def test_handler_start_command(mock_send):
    """Тест команды /start"""
    event = {
        'body': json.dumps({
            'message': {
                'chat': {'id': 12345},
                'text': '/start'
            }
        })
    }
    context = {}

    bot.handler(event, context)

    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    assert args[0] == 12345
    assert "Бот учета личных финансов" in args[1]
    # Проверяем, что клавиатура была передана
    assert args[2] is not None  # reply_markup


@patch('bot.send_telegram_message')
def test_handler_help_command(mock_send):
    """Тест команды /help"""
    event = {
        'body': json.dumps({
            'message': {
                'chat': {'id': 12345},
                'text': '/help'
            }
        })
    }
    context = {}

    bot.handler(event, context)

    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    assert args[0] == 12345
    assert "Помощь по использованию бота" in args[1]


# Для запуска тестов
if __name__ == "__main__":
    pytest.main([__file__])