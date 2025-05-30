import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox, QComboBox
)


class AcademicEntry:

    def __init__(self, date: str, time: str, teacher_name: str):
        self.date = datetime.strptime(date, '%Y.%m.%d').date()
        self.time = datetime.strptime(time, '%H:%M').time()
        self.teacher_name = teacher_name

    def to_string(self) -> str:
        return f"{self.date.strftime('%Y.%m.%d')}, {self.time.strftime('%H:%M')}, \"{self.teacher_name}\""

    def __str__(self) -> str:
        return f"AcademicEntry(date={self.date}, time={self.time}, teacher_name='{self.teacher_name}')"


class LiteraryWork(AcademicEntry):

    def __init__(self, date: str, time: str, teacher_name: str, work_title: str):
        super().__init__(date, time, teacher_name)
        self.work_title = work_title

    def to_string(self) -> str:
        base_str = super().to_string()
        return f"{base_str}, \"{self.work_title}\""

    def __str__(self) -> str:
        return (f"LiteraryWork(date={self.date}, time={self.time}, "
                f"teacher_name='{self.teacher_name}', work_title='{self.work_title}')")


class MathTopic(AcademicEntry):

    def __init__(self, date: str, time: str, teacher_name: str, topic_name: str):
        super().__init__(date, time, teacher_name)
        self.topic_name = topic_name

    def to_string(self) -> str:
        base_str = super().to_string()
        return f"{base_str}, \"{self.topic_name}\""

    def __str__(self) -> str:
        return (f"MathTopic(date={self.date}, time={self.time}, "
                f"teacher_name='{self.teacher_name}', topic_name='{self.topic_name}')")


def create_entry(entry_type: str, date: str, time: str, teacher: str, title: str) -> AcademicEntry:
    if entry_type == 'literature':
        return LiteraryWork(date, time, teacher, title)
    elif entry_type == 'math':
        return MathTopic(date, time, teacher, title)
    raise ValueError(f"Неизвестный тип записи: {entry_type}")


def parse_entry_description(description: str) -> tuple:
    parts = [part.strip() for part in description.split(',')]
    if len(parts) != 4:
        raise ValueError("Некорректный формат описания")
    
    date, time, teacher, title = parts
    return date, time, teacher.strip('"'), title.strip('"')


class AcademicJournal:
    def __init__(self):
        self.entries = []
        self.save_path = r"C:\Users\Pital\Desktop\Pr2\journal_entries.txt"

    def add_entry(self, entry: AcademicEntry) -> None:
        self.entries.append(entry)
        self._save_to_file()

    def get_all_entries(self) -> list:
        return self.entries.copy()

    def clear_entries(self) -> None:
        self.entries.clear()
        self._save_to_file()

    def _save_to_file(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            with open(self.save_path, 'w', encoding='utf-8') as f:
                for entry in self.entries:
                    f.write(entry.to_string() + "\n")
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.journal = AcademicJournal()
        self._setup_ui()
        self.setWindowTitle("Академический журнал")
        self.resize(600, 400)

    def _setup_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Тип записи
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Тип записи:"))
        
        self.entry_type_combo = QComboBox()
        self.entry_type_combo.addItem("Литературное произведение", 'literature')
        self.entry_type_combo.addItem("Тема по математике", 'math')
        type_layout.addWidget(self.entry_type_combo)
        
        layout.addLayout(type_layout)

        # Поле ввода
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText(
            'Введите описание: "YYYY.MM.DD, HH:MM, "Преподаватель", "Название""'
        )
        layout.addWidget(self.description_input)

        # Кнопки
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Добавить запись")
        add_button.clicked.connect(self._handle_add_entry)
        buttons_layout.addWidget(add_button)
        
        clear_button = QPushButton("Очистить журнал")
        clear_button.clicked.connect(self._handle_clear_entries)
        buttons_layout.addWidget(clear_button)
        
        save_button = QPushButton("Сохранить в файл")
        save_button.clicked.connect(self._handle_save_to_file)
        buttons_layout.addWidget(save_button)
        
        layout.addLayout(buttons_layout)

        # Список записей
        self.entries_list = QListWidget()
        layout.addWidget(self.entries_list)

    def _handle_add_entry(self) -> None:
        description = self.description_input.text().strip()
        if not description:
            self._show_warning("Описание не может быть пустым")
            return

        try:
            date, time, teacher, title = parse_entry_description(description)
            entry_type = self.entry_type_combo.currentData()
            entry = create_entry(entry_type, date, time, teacher, title)
            self.journal.add_entry(entry)
            self._update_entries_list()
            self.description_input.clear()
        except ValueError as e:
            self._show_warning(f"Ошибка формата: {e}")

    def _handle_clear_entries(self) -> None:
        if not self.journal.get_all_entries():
            return

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

    def _handle_save_to_file(self) -> None:
        """Обрабатывает явный запрос на сохранение в файл."""
        try:
            self.journal._save_to_file()
            QMessageBox.information(self, "Сохранено", f"Данные успешно сохранены в файл:\n{self.journal.save_path}")
        except Exception as e:
            self._show_warning(f"Ошибка при сохранении: {e}")

    def _update_entries_list(self) -> None:
        self.entries_list.clear()
        for entry in self.journal.get_all_entries():
            self.entries_list.addItem(str(entry))

    def _show_warning(self, message: str) -> None:
        QMessageBox.warning(self, "Ошибка", message)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
