#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2025 Your Name

import sys
from random import shuffle
from time import time

from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)
from PyQt6.QtGui import QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width: float = 5, height: float = 4, dpi: int = 100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        fig.tight_layout()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.alpha2num = {v: k for k, v in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 1)}
        self.answers = list(self.alpha2num.keys())
        shuffle(self.answers)
        self.current_alpha = None
        self.start_time = None
        self.response_times: list[tuple[str, float]] = []
        self.started = False
        self.canvas: MplCanvas | None = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("알파벳을 숫자로 바꾸기")
        self.resize(600, 500)

        font = QFont("Courier New", 16)

        self.time_label = QLabel("이전 문제 풀이에 걸린 시간: -", font=font)
        self.question_label = QLabel("시작하려면 제출 버튼 또는 엔터를 누르세요.", font=font)

        self.input_field = QLineEdit(placeholderText="여기에 입력하세요.")
        self.input_field.setFont(font)
        self.input_field.returnPressed.connect(self.check_answer)

        self.submit_button = QPushButton("제출", font=font)
        self.submit_button.clicked.connect(self.check_answer)

        layout = QVBoxLayout(self)
        layout.addWidget(self.time_label)
        layout.addWidget(self.question_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def next_question(self):
        if not self.answers:
            self.show_result_graph()
            self.question_label.setText("모든 문제가 끝났습니다.")
            self.input_field.setEnabled(False)
            self.submit_button.setEnabled(False)
            return

        self.current_alpha = self.answers.pop()
        self.question_label.setText(f"{self.current_alpha} ⇒ 숫자로 표현하면?")
        self.input_field.clear()
        self.input_field.setFocus()
        self.start_time = time()

    def check_answer(self):
        if not self.started:
            self.input_field.setPlaceholderText("숫자를 입력하세요")
            self.started = True
            self.next_question()
            return

        if not self.current_alpha:
            return

        user_input = self.input_field.text()
        correct_answer = self.alpha2num[self.current_alpha]
        elapsed = time() - self.start_time

        if not user_input.isdecimal():
            QMessageBox.warning(self, "오답", "숫자를 입력해주세요.")
            self.input_field.clear()
            return

        if int(user_input) == correct_answer:
            self.response_times.append((self.current_alpha, elapsed))
            self.time_label.setText(f"이전 문제 풀이에 걸린 시간: {elapsed:.3f}초")
            self.next_question()
            self.input_field.selectAll()
        else:
            QMessageBox.warning(self, "오답", "틀렸습니다! 다시 시도해보세요.")
            self.input_field.clear()

    def show_result_graph(self):
        if not self.response_times:
            return

        self.response_times.sort(key=lambda x: x[0])
        letters = [alpha for alpha, _ in self.response_times]
        times = [t for _, t in self.response_times]

        if self.canvas:
            self.layout().removeWidget(self.canvas)
            self.canvas.setParent(None)

        self.canvas = MplCanvas(self, width=6, height=4, dpi=100)
        ax = self.canvas.axes
        ax.bar(letters, times)

        ax.axhline(sum(times) / len(times), linestyle="--", linewidth=1)
        ax.set_title("Response Time per Alphabet")
        ax.set_xlabel("Alphabet")
        ax.set_ylabel("Response Time (seconds)")
        ax.grid(True, axis="y")
        self.canvas.draw()

        self.layout().addWidget(self.canvas)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
