import sys
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QListWidget, QMessageBox, QComboBox)


class AcademicEntry:
    """Базовый класс для академических записей."""

    def __init__(self, description: str):
        """Инициализирует объект AcademicEntry из строки описания.
        
        Args:
            description: Строка с описанием записи в формате 'YYYY.MM.DD, HH:MM, "Teacher", ...'
        """
        parts = description.split(maxsplit=3)
        self.date = datetime.strptime(parts[0], '%Y.%m.%d,').date()
        self.time = datetime.strptime(parts[1], '%H:%M,').time()
        self.teacher_name = parts[2].strip('",')
        self.parts = parts

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return (f"AcademicEntry(date={self.date}, time={self.time}, "
                f"teacher_name='{self.teacher_name}')")


class LiteraryWork(AcademicEntry):
    """Класс для представления литературных произведений."""

    def __init__(self, description: str):
        """Инициализирует объект LiteraryWork."""
        super().__init__(description)
        self.work_title = self.parts[3].strip('"')

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return (f"LiteraryWork(date={self.date}, time={self.time}, "
                f"teacher_name='{self.teacher_name}', work_title='{self.work_title}')")


class MathTopic(AcademicEntry):
    """Класс для представления тем по математике."""

    def __init__(self, description: str):
        """Инициализирует объект MathTopic."""
        super().__init__(description)
        self.topic_name = self.parts[3].strip('"')

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return (f"MathTopic(date={self.date}, time={self.time}, "
                f"teacher_name='{self.teacher_name}', topic_name='{self.topic_name}')")


class EntryFactory:
    """Фабрика для создания объектов академических записей."""

    @staticmethod
    def create_entry(entry_type: str, description: str) -> AcademicEntry:
        """Создает объект академической записи заданного типа.
        
        Args:
            entry_type: Тип записи ('literature' или 'math')
            description: Описание записи
            
        Returns:
            Объект AcademicEntry или его подкласса
            
        Raises:
            ValueError: Если тип записи неизвестен или описание некорректно
        """
        if entry_type == 'literature':
            return LiteraryWork(description)
        elif entry_type == 'math':
            return MathTopic(description)
        else:
            raise ValueError(f"Unknown entry type: {entry_type}")


class AcademicJournal:
    """Класс для управления коллекцией академических записей."""

    def __init__(self):
        """Инициализирует пустой журнал записей."""
        self.entries = []

    def add_entry(self, entry: AcademicEntry) -> None:
        """Добавляет запись в журнал.
        
        Args:
            entry: Объект академической записи
        """
        self.entries.append(entry)

    def get_all_entries(self) -> list[AcademicEntry]:
        """Возвращает список всех записей.
        
        Returns:
            Список объектов AcademicEntry
        """
        return self.entries.copy()

    def clear_entries(self) -> None:
        """Очищает журнал записей."""
        self.entries.clear()


class AcademicJournalApp(QMainWindow):
    """Главное окно приложения академического журнала."""

    def __init__(self):
        """Инициализирует главное окно приложения."""
        super().__init__()
        self.journal = AcademicJournal()
        self.init_ui()
        self.setWindowTitle("Академический журнал")
        self.resize(600, 400)

    def init_ui(self) -> None:
        """Инициализирует пользовательский интерфейс."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Выбор типа записи
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Тип записи:"))
        
        self.entry_type_combo = QComboBox()
        self.entry_type_combo.addItem("Литературное произведение", 'literature')
        self.entry_type_combo.addItem("Тема по математике", 'math')
        type_layout.addWidget(self.entry_type_combo)
        
        main_layout.addLayout(type_layout)

        # Поле ввода описания
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText(
            'Введите описание в формате: "YYYY.MM.DD, HH:MM, "Преподаватель", "Название"'
        )
        main_layout.addWidget(self.description_input)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Добавить запись")
        self.add_button.clicked.connect(self.add_entry)
        buttons_layout.addWidget(self.add_button)
        
        self.clear_button = QPushButton("Очистить журнал")
        self.clear_button.clicked.connect(self.clear_entries)
        buttons_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(buttons_layout)

        # Список записей
        self.entries_list = QListWidget()
        main_layout.addWidget(self.entries_list)

    def add_entry(self) -> None:
        """Добавляет новую запись в журнал."""
        description = self.description_input.text().strip()
        if not description:
            QMessageBox.warning(self, "Ошибка", "Описание не может быть пустым")
            return

        entry_type = self.entry_type_combo.currentData()
        
        try:
            entry = EntryFactory.create_entry(entry_type, description)
            self.journal.add_entry(entry)
            self.update_entries_list()
            self.description_input.clear()
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Ошибка",
                f"Некорректный формат описания: {e}\n"
                "Правильный формат: YYYY.MM.DD, HH:MM, \"Преподаватель\", \"Название\""
            )

    def clear_entries(self) -> None:
        """Очищает журнал записей."""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы действительно хотите очистить журнал?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.journal.clear_entries()
            self.entries_list.clear()

    def update_entries_list(self) -> None:
        """Обновляет список отображаемых записей."""
        self.entries_list.clear()
        for entry in self.journal.get_all_entries():
            self.entries_list.addItem(str(entry))


def main() -> None:
    """Точка входа в приложение."""
    app = QApplication(sys.argv)
    window = AcademicJournalApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
