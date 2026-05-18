import sys
import time
import hashlib
import os
import fnmatch
import threading
from queue import Queue
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QComboBox, QSystemTrayIcon,
    QMenu, QAction, QTabWidget, QGridLayout, QFileDialog, QMessageBox,
    QTextEdit, QPlainTextEdit, QProgressBar, QListWidget
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtCore import Qt, QTimer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stop_search = False
        self.init_ui()
        self.init_tray()

    def init_ui(self):
        self.setWindowTitle('运维小工具')
        self.setGeometry(100, 100, 564, 434)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        
        self.set_window_icon()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        top_layout = QHBoxLayout()
        self.always_on_top = QPushButton('固定窗口')
        self.always_on_top.setCheckable(True)
        self.always_on_top.clicked.connect(self.toggle_always_on_top)
        top_layout.addWidget(self.always_on_top)

        self.shortcut_buttons = []
        self.top_layout = top_layout
        
        add_shortcut_btn = QPushButton('+')
        add_shortcut_btn.setFixedSize(24, 24)
        add_shortcut_btn.clicked.connect(self.add_shortcut)
        top_layout.addWidget(add_shortcut_btn)
        
        top_layout.addStretch(1)
        layout.addLayout(top_layout)
        
        self.load_shortcuts()

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.status_bar = QLabel('运维小工具 v1.0 | 作者: wei')
        self.status_bar.setStyleSheet('color: gray; font-size: 10px;')
        self.status_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_bar)

        self.create_clipboard_tab()
        self.create_conversion_tab()
        self.create_timestamp_tab()
        self.create_md5_tab()
        self.create_file_search_tab()
        self.create_sql_tools_tab()
        self.create_case_conversion_tab()
        self.create_network_tools_tab()
        self.create_subnet_calculator_tab()
        self.create_api_test_tab()
        self.create_port_forward_tab()
        self.create_remote_download_tab()
        self.create_data_convert_tab()
        self.create_process_manager_tab()
        self.create_service_manager_tab()

    def set_window_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            return
        
        icon_pixmap = QPixmap(32, 32)
        icon_pixmap.fill(Qt.transparent)
        painter = QPainter(icon_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setBrush(Qt.blue)
        painter.drawRect(4, 4, 24, 24)
        
        painter.setBrush(Qt.white)
        painter.drawRect(8, 8, 8, 8)
        painter.drawRect(16, 16, 8, 8)
        
        painter.end()
        
        self.setWindowIcon(QIcon(icon_pixmap))

    def toggle_always_on_top(self, checked):
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.always_on_top.setText('取消固定')
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.always_on_top.setText('固定窗口')
        self.show()

    def load_shortcuts(self):
        import json
        self.shortcuts = []
        try:
            with open('shortcuts.json', 'r', encoding='utf-8') as f:
                self.shortcuts = json.load(f)
        except:
            pass
        
        for name, path in self.shortcuts:
            self.add_shortcut_button(name, path)

    def add_shortcut_button(self, name, path):
        btn = QPushButton(name)
        btn.setFixedSize(60, 24)
        btn.clicked.connect(lambda checked, p=path: self.launch_program(p))
        btn.setContextMenuPolicy(Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(lambda pos, b=btn, p=path: self.show_shortcut_menu(pos, b, p))
        self.shortcut_buttons.append(btn)
        self.top_layout.insertWidget(len(self.shortcut_buttons) + 1, btn)

    def add_shortcut(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择程序', '', '可执行文件 (*.exe);;所有文件 (*.*)')
        if file_path:
            import os
            name = os.path.basename(file_path).replace('.exe', '')
            self.shortcuts.append([name, file_path])
            self.save_shortcuts()
            self.add_shortcut_button(name, file_path)

    def show_shortcut_menu(self, pos, button, path):
        menu = QMenu()
        delete_action = QAction('删除', self)
        delete_action.triggered.connect(lambda: self.delete_shortcut(button, path))
        menu.addAction(delete_action)
        menu.exec_(button.mapToGlobal(pos))

    def delete_shortcut(self, button, path):
        self.shortcuts = [s for s in self.shortcuts if s[1] != path]
        self.save_shortcuts()
        button.deleteLater()
        self.shortcut_buttons.remove(button)

    def save_shortcuts(self):
        import json
        with open('shortcuts.json', 'w', encoding='utf-8') as f:
            json.dump(self.shortcuts, f)

    def launch_program(self, path):
        import subprocess
        try:
            subprocess.Popen([path])
        except Exception as e:
            QMessageBox.warning(self, '错误', f'启动失败: {str(e)}')

    def create_conversion_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)

        layout.addWidget(QLabel('输入数字（每行一个）:'), 0, 0, Qt.AlignLeft)
        self.conv_input = QTextEdit()
        self.conv_input.setPlaceholderText('输入数字')
        self.conv_input.setMaximumHeight(100)
        layout.addWidget(self.conv_input, 0, 1)

        layout.addWidget(QLabel('源进制:'), 1, 0, Qt.AlignLeft)
        self.from_base = QComboBox()
        self.from_base.addItems(['十进制', '二进制', '八进制', '十六进制'])
        layout.addWidget(self.from_base, 1, 1)

        layout.addWidget(QLabel('目标进制:'), 2, 0, Qt.AlignLeft)
        self.to_base = QComboBox()
        self.to_base.addItems(['十进制', '二进制', '八进制', '十六进制'])
        self.to_base.setCurrentIndex(1)
        layout.addWidget(self.to_base, 2, 1)

        convert_btn = QPushButton('转换')
        convert_btn.clicked.connect(self.convert_number)
        layout.addWidget(convert_btn, 3, 1)

        layout.addWidget(QLabel('结果:'), 4, 0, Qt.AlignLeft)
        self.conv_result = QTextEdit()
        self.conv_result.setReadOnly(True)
        self.conv_result.setMaximumHeight(100)
        layout.addWidget(self.conv_result, 4, 1)

        self.tabs.addTab(tab, '进制转换')

    def create_timestamp_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)

        layout.addWidget(QLabel('时间戳（每行一个）:'), 0, 0, Qt.AlignLeft)
        self.ts_input = QTextEdit()
        self.ts_input.setPlaceholderText('输入时间戳（秒或毫秒）')
        self.ts_input.setMaximumHeight(80)
        layout.addWidget(self.ts_input, 0, 1)

        ts_btn = QPushButton('转日期')
        ts_btn.clicked.connect(self.ts_to_date)
        layout.addWidget(ts_btn, 0, 2)

        layout.addWidget(QLabel('日期时间:'), 1, 0, Qt.AlignLeft)
        self.ts_result = QTextEdit()
        self.ts_result.setReadOnly(True)
        self.ts_result.setMaximumHeight(80)
        layout.addWidget(self.ts_result, 1, 1)

        layout.addWidget(QLabel('日期:'), 2, 0, Qt.AlignLeft)
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText('YYYY-MM-DD HH:MM:SS')
        layout.addWidget(self.date_input, 2, 1)

        date_btn = QPushButton('转时间戳')
        date_btn.clicked.connect(self.date_to_ts)
        layout.addWidget(date_btn, 2, 2)

        now_btn = QPushButton('获取当前时间')
        now_btn.clicked.connect(self.get_current_time)
        layout.addWidget(now_btn, 2, 3)

        layout.addWidget(QLabel('时间戳:'), 3, 0, Qt.AlignLeft)
        self.date_result = QLineEdit()
        self.date_result.setReadOnly(True)
        layout.addWidget(self.date_result, 3, 1, 1, 3)

        self.tabs.addTab(tab, '时间戳转换')

    def create_md5_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)

        layout.addWidget(QLabel('输入文本:'), 0, 0, Qt.AlignLeft)
        self.md5_input = QLineEdit()
        self.md5_input.setPlaceholderText('输入要加密的文本')
        layout.addWidget(self.md5_input, 0, 1, 1, 3)

        layout.addWidget(QLabel('位数:'), 1, 0, Qt.AlignLeft)
        self.md5_bits = QComboBox()
        self.md5_bits.addItems(['32位', '16位'])
        layout.addWidget(self.md5_bits, 1, 1)

        btn_layout = QHBoxLayout()
        md5_btn = QPushButton('文本加密')
        md5_btn.setFixedWidth(100)
        md5_btn.clicked.connect(self.calc_md5_text)
        btn_layout.addWidget(md5_btn)

        file_btn = QPushButton('选择文件')
        file_btn.setFixedWidth(100)
        file_btn.clicked.connect(self.calc_md5_file)
        btn_layout.addWidget(file_btn)
        
        layout.addLayout(btn_layout, 1, 2, 1, 2)

        layout.addWidget(QLabel('加密结果:'), 2, 0, Qt.AlignLeft)
        self.md5_result = QLineEdit()
        self.md5_result.setReadOnly(True)
        layout.addWidget(self.md5_result, 2, 1, 1, 3)

        self.tabs.addTab(tab, 'MD5加密')

    def create_case_conversion_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)

        layout.addWidget(QLabel('输入文本:'), 0, 0, Qt.AlignLeft)
        self.case_input = QLineEdit()
        self.case_input.setPlaceholderText('输入要转换的文本')
        layout.addWidget(self.case_input, 0, 1, 1, 2)

        btn_layout = QHBoxLayout()
        
        upper_btn = QPushButton('转大写')
        upper_btn.setFixedWidth(90)
        upper_btn.clicked.connect(self.to_upper)
        btn_layout.addWidget(upper_btn)

        lower_btn = QPushButton('转小写')
        lower_btn.setFixedWidth(90)
        lower_btn.clicked.connect(self.to_lower)
        btn_layout.addWidget(lower_btn)

        swap_btn = QPushButton('大小写互换')
        swap_btn.setFixedWidth(100)
        swap_btn.clicked.connect(self.swap_case)
        btn_layout.addWidget(swap_btn)

        layout.addLayout(btn_layout, 1, 1)

        layout.addWidget(QLabel('转换结果:'), 2, 0, Qt.AlignLeft)
        self.case_result = QLineEdit()
        self.case_result.setReadOnly(True)
        layout.addWidget(self.case_result, 2, 1, 1, 2)

        self.tabs.addTab(tab, '大小写转换')

    def to_upper(self):
        text = self.case_input.text()
        self.case_result.setText(text.upper())

    def to_lower(self):
        text = self.case_input.text()
        self.case_result.setText(text.lower())

    def swap_case(self):
        text = self.case_input.text()
        self.case_result.setText(text.swapcase())

    def create_file_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        group_box = QWidget()
        group_layout = QGridLayout(group_box)

        group_layout.addWidget(QLabel('日志目录:'), 0, 0, Qt.AlignLeft)
        self.search_path = QLineEdit()
        self.search_path.setPlaceholderText('选择文件夹或文件')
        group_layout.addWidget(self.search_path, 0, 1)

        browse_dir_btn = QPushButton('选择目录')
        browse_dir_btn.clicked.connect(self.browse_path)
        group_layout.addWidget(browse_dir_btn, 0, 2)

        browse_file_btn = QPushButton('选择文件')
        browse_file_btn.clicked.connect(self.browse_files)
        group_layout.addWidget(browse_file_btn, 0, 3)

        group_layout.addWidget(QLabel('关键字:'), 1, 0, Qt.AlignLeft)
        self.search_keyword = QLineEdit()
        self.search_keyword.setPlaceholderText('输入搜索关键词')
        group_layout.addWidget(self.search_keyword, 1, 1, 1, 2)

        group_layout.addWidget(QLabel('文件过滤:'), 2, 0, Qt.AlignLeft)
        self.file_filter = QLineEdit()
        self.file_filter.setPlaceholderText('如: *.txt (可选)')
        group_layout.addWidget(self.file_filter, 2, 1, 1, 2)

        self.whole_word_check = QLabel('全词匹配')
        self.whole_word_check.setStyleSheet('color: blue; text-decoration: underline;')
        self.whole_word_check.setToolTip('点击切换全词匹配模式')
        self.whole_word_check.mousePressEvent = self.toggle_whole_word
        self.whole_word_enabled = False
        self.whole_word_check.setCursor(Qt.PointingHandCursor)
        group_layout.addWidget(self.whole_word_check, 3, 0, Qt.AlignLeft)

        layout.addWidget(group_box)

        btn_layout = QHBoxLayout()
        search_btn = QPushButton('开始搜索')
        search_btn.clicked.connect(self.search_files)
        btn_layout.addWidget(search_btn)

        clear_btn = QPushButton('清空条件')
        clear_btn.clicked.connect(self.clear_search)
        btn_layout.addWidget(clear_btn)

        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel('')
        layout.addWidget(self.status_label)

        layout.addWidget(QLabel('搜索结果:'))
        self.search_result = QTextEdit()
        self.search_result.setReadOnly(True)
        layout.addWidget(self.search_result)

        save_btn = QPushButton('保存结果')
        save_btn.clicked.connect(self.save_search_results)
        layout.addWidget(save_btn)

        self.tabs.addTab(tab, '文件搜索')

    def browse_path(self):
        dir_path = QFileDialog.getExistingDirectory(self, '选择文件夹')
        if dir_path:
            self.search_path.setText(dir_path)

    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            '选择文件', 
            '', 
            '所有文件 (*.*);;SQL文件 (*.sql)'
        )
        if files:
            self.search_path.setText('|'.join(files))

    def clear_search(self):
        self.stop_search = True
        self.search_path.clear()
        self.search_keyword.clear()
        self.file_filter.clear()
        self.search_result.clear()
        self.status_label.setText('搜索已停止')
        self.progress_bar.setValue(0)

    def toggle_whole_word(self, event):
        self.whole_word_enabled = not self.whole_word_enabled
        if self.whole_word_enabled:
            self.whole_word_check.setStyleSheet('color: red; text-decoration: underline; font-weight: bold;')
        else:
            self.whole_word_check.setStyleSheet('color: blue; text-decoration: underline;')

    def search_files(self):
        path = self.search_path.text().strip()
        keyword = self.search_keyword.text().strip()
        file_pattern = self.file_filter.text().strip()

        if not path:
            QMessageBox.warning(self, '提示', '请先选择搜索路径')
            return

        if not keyword:
            QMessageBox.warning(self, '提示', '请输入搜索关键词')
            return

        self.stop_search = False
        self.search_result.clear()
        self.progress_bar.setValue(0)
        self.search_results_list = []
        self.search_count = 0
        self.total_files = 0
        self.processed_files = 0

        files = []
        if '|' in path:
            files = path.split('|')
        elif os.path.isfile(path):
            files = [path]
        else:
            import multiprocessing.pool
            all_files = []
            
            def scan_directory(args):
                root, dirs, filenames = args
                result = []
                for filename in filenames:
                    if file_pattern:
                        if fnmatch.fnmatch(filename, file_pattern):
                            result.append(os.path.join(root, filename))
                    else:
                        result.append(os.path.join(root, filename))
                return result
            
            pool = multiprocessing.pool.ThreadPool(processes=4)
            walk_results = []
            
            for root, dirs, filenames in os.walk(path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                walk_results.append((root, dirs, filenames))
            
            results = pool.map(scan_directory, walk_results)
            pool.close()
            pool.join()
            
            for result in results:
                all_files.extend(result)
            
            files = all_files
        
        if '|' in path or os.path.isfile(path):
            file_pattern = ''

        self.total_files = len(files)
        if self.total_files == 0:
            self.status_label.setText('未找到匹配的文件')
            return

        self.status_label.setText('正在搜索...')

        self.result_queue = Queue()
        self.file_queue = Queue()
        for f in files:
            self.file_queue.put(f)

        import os as os_module
        cpu_count = max(4, os_module.cpu_count() or 4)
        self.threads = []
        for _ in range(min(cpu_count, self.total_files)):
            t = threading.Thread(target=self.search_worker, args=(keyword, self.whole_word_enabled))
            t.daemon = True
            t.start()
            self.threads.append(t)

        self.update_display()

    def search_worker(self, keyword, whole_word=False):
        import re
        
        keyword_lower = keyword.lower()
        if whole_word:
            if keyword.isdigit():
                pattern = re.compile(r'(?:^|[^0-9])' + re.escape(keyword) + r'(?:$|[^0-9])', re.IGNORECASE)
            else:
                pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)

        while not self.file_queue.empty() and not self.stop_search:
            try:
                file_path = self.file_queue.get(timeout=1)
            except:
                break

            try:
                content = self.read_file_with_encoding(file_path)
                if content is not None:
                    if whole_word:
                        for line_num, line in enumerate(content.split('\n'), 1):
                            if self.stop_search:
                                return
                            if pattern.search(line):
                                self.result_queue.put(f'{file_path}:{line_num}: {line.rstrip()}')
                    else:
                        for line_num, line in enumerate(content.split('\n'), 1):
                            if self.stop_search:
                                return
                            if keyword_lower in line.lower():
                                self.result_queue.put(f'{file_path}:{line_num}: {line.rstrip()}')
            except Exception as e:
                pass

            self.processed_files += 1

    def update_display(self):
        if self.stop_search:
            self.status_label.setText('搜索已停止')
            self.progress_bar.setValue(100)
            return

        new_results = []
        while not self.result_queue.empty():
            line = self.result_queue.get()
            new_results.append(line)
            self.search_count += 1
        
        if new_results:
            self.search_results_list.extend(new_results)
            if len(self.search_results_list) <= 10000:
                self.search_result.setPlainText('\n'.join(self.search_results_list))

        if self.processed_files < self.total_files:
            self.progress_bar.setValue(int(self.processed_files / self.total_files * 100))
            self.status_label.setText(f'正在搜索... ({self.processed_files}/{self.total_files})')
            QApplication.processEvents()
            QTimer.singleShot(50, self.update_display)
        else:
            self.progress_bar.setValue(100)
            if self.search_results_list:
                if len(self.search_results_list) > 10000:
                    self.status_label.setText(f'搜索完成，找到 {self.search_count} 处匹配（仅显示前10000条）')
                else:
                    self.status_label.setText(f'搜索完成，找到 {self.search_count} 处匹配')
            else:
                self.status_label.setText('搜索完成，未找到匹配')

    def read_file_with_encoding(self, file_path):
        encodings_priority = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030', 'utf-16']
        
        file_path = str(file_path).strip()
        
        if file_path.startswith('/'):
            file_path = file_path[1:]
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return None
        
        try:
            with open(file_path, 'rb') as f:
                binary_content = f.read()
        except Exception:
            return None
        
        if not binary_content:
            return ''
        
        for encoding in encodings_priority:
            try:
                return binary_content.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                continue
        
        try:
            return binary_content.decode('utf-8', errors='replace')
        except Exception:
            return None

    def save_search_results(self):
        if not hasattr(self, 'search_results_list') or not self.search_results_list:
            QMessageBox.warning(self, '提示', '没有可保存的内容')
            return

        keyword = self.search_keyword.text().strip() or '搜索结果'
        default_path = self.search_path.text().strip()
        default_dir = default_path if os.path.isdir(default_path) else os.path.dirname(default_path)

        output_path, _ = QFileDialog.getSaveFileName(
            self, '保存搜索结果',
            os.path.join(default_dir, f'{keyword}.txt') if default_dir else keyword,
            '文本文件 (*.txt)'
        )
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.search_results_list))
            QMessageBox.information(self, '提示', f'结果已保存到 {output_path}')

    def calc_md5_text(self):
        try:
            text = self.md5_input.text().strip()
            if not text:
                self.md5_result.clear()
                return

            md5_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            if self.md5_bits.currentText() == '16位':
                md5_hash = md5_hash[8:-8]
            self.md5_result.setText(md5_hash)
        except Exception:
            self.md5_result.setText('加密失败')

    def calc_md5_file(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, '选择文件')
            if not file_path:
                return

            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    md5_hash.update(chunk)
            
            result = md5_hash.hexdigest()
            if self.md5_bits.currentText() == '16位':
                result = result[8:-8]
            self.md5_result.setText(result)
        except Exception as e:
            QMessageBox.warning(self, '错误', f'文件加密失败: {str(e)}')
            self.md5_result.setText('加密失败')

    def convert_number(self):
        try:
            input_text = self.conv_input.toPlainText().strip()
            if not input_text:
                self.conv_result.clear()
                return

            bases = [10, 2, 8, 16]
            from_base = bases[self.from_base.currentIndex()]
            to_base = bases[self.to_base.currentIndex()]

            lines = input_text.split('\n')
            results = []
            for num_str in lines:
                num_str = num_str.strip()
                if not num_str:
                    results.append('')
                    continue
                
                try:
                    if from_base == 10:
                        num = int(num_str)
                    elif from_base == 2:
                        num = int(num_str, 2)
                    elif from_base == 8:
                        num = int(num_str, 8)
                    elif from_base == 16:
                        num = int(num_str, 16)

                    if to_base == 10:
                        result = str(num)
                    elif to_base == 2:
                        result = bin(num)[2:]
                    elif to_base == 8:
                        result = oct(num)[2:]
                    elif to_base == 16:
                        result = hex(num)[2:].upper()
                    
                    results.append(result)
                except:
                    results.append('转换失败')

            self.conv_result.setText('\n'.join(results))
        except Exception:
            self.conv_result.setText('输入无效')

    def ts_to_date(self):
        try:
            input_text = self.ts_input.toPlainText().strip()
            if not input_text:
                self.ts_result.clear()
                return

            lines = input_text.split('\n')
            results = []
            for ts_str in lines:
                ts_str = ts_str.strip()
                if not ts_str:
                    results.append('')
                    continue
                
                try:
                    ts = float(ts_str)
                    if ts > 1e12:
                        ts = ts / 1000
                    date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
                    results.append(date_str)
                except:
                    results.append('转换失败')

            self.ts_result.setText('\n'.join(results))
        except Exception:
            self.ts_result.setText('输入无效')

    def date_to_ts(self):
        try:
            date_str = self.date_input.text().strip()
            if not date_str:
                self.date_result.clear()
                return

            ts = int(time.mktime(time.strptime(date_str, '%Y-%m-%d %H:%M:%S')))
            self.date_result.setText(str(ts))
        except Exception:
            self.date_result.setText('格式错误')

    def get_current_time(self):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.date_input.setText(current_time)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            icon = QPixmap(32, 32)
            icon.fill(Qt.blue)
            self.tray_icon.setIcon(QIcon(icon))

        self.tray_menu = QMenu()

        show_action = QAction('显示窗口', self)
        show_action.triggered.connect(self.show_window)
        self.tray_menu.addAction(show_action)

        quit_action = QAction('退出', self)
        quit_action.triggered.connect(QApplication.quit)
        self.tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_activated)

    def show_window(self):
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
        self.show()
        self.activateWindow()
        self.raise_()

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()

    def create_network_tools_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        ping_group = QWidget()
        ping_layout = QGridLayout(ping_group)
        ping_layout.addWidget(QLabel('目标地址:'), 0, 0)
        self.ping_host = QLineEdit()
        self.ping_host.setPlaceholderText('输入IP地址或域名')
        ping_layout.addWidget(self.ping_host, 0, 1)
        self.ping_button = QPushButton('Ping')
        self.ping_button.clicked.connect(self.ping_hosts)
        ping_layout.addWidget(self.ping_button, 0, 2)
        layout.addWidget(ping_group)
        
        self.ping_result = QTextEdit()
        self.ping_result.setReadOnly(True)
        self.ping_result.setMaximumHeight(100)
        layout.addWidget(self.ping_result)
        
        port_group = QWidget()
        port_layout = QGridLayout(port_group)
        port_layout.addWidget(QLabel('目标地址:'), 0, 0)
        self.port_host = QLineEdit()
        self.port_host.setPlaceholderText('输入IP地址或域名')
        port_layout.addWidget(self.port_host, 0, 1)
        port_layout.addWidget(QLabel('端口范围:'), 1, 0)
        self.port_range = QLineEdit()
        self.port_range.setPlaceholderText('例如: 1-1000')
        port_layout.addWidget(self.port_range, 1, 1)
        self.port_button = QPushButton('端口扫描')
        self.port_button.clicked.connect(self.scan_ports)
        port_layout.addWidget(self.port_button, 1, 2)
        layout.addWidget(port_group)
        
        self.port_result = QTextEdit()
        self.port_result.setReadOnly(True)
        self.port_result.setMaximumHeight(100)
        layout.addWidget(self.port_result)
        
        ip_group = QWidget()
        ip_layout = QHBoxLayout(ip_group)
        self.get_ip_button = QPushButton('获取本机IP')
        self.get_ip_button.clicked.connect(self.get_local_ip)
        ip_layout.addWidget(self.get_ip_button)
        self.ip_result = QLineEdit()
        self.ip_result.setReadOnly(True)
        ip_layout.addWidget(self.ip_result)
        layout.addWidget(ip_group)
        
        layout.addStretch(1)
        self.tabs.addTab(tab, '网络工具')

    def ping_hosts(self):
        host = self.ping_host.text().strip()
        if not host:
            QMessageBox.warning(self, '提示', '请输入目标地址')
            return
        
        self.ping_result.clear()
        self.ping_result.setText('正在Ping...')
        self.ping_button.setEnabled(False)
        
        def ping_thread():
            try:
                import subprocess
                result = subprocess.run(['ping', '-n', '4', host], capture_output=True, timeout=30)
                output = result.stdout.decode('gbk', errors='replace') + result.stderr.decode('gbk', errors='replace')
                QTimer.singleShot(0, lambda: self.ping_result.setText(output))
            except Exception as e:
                QTimer.singleShot(0, lambda: self.ping_result.setText(f'Ping失败: {str(e)}'))
            finally:
                QTimer.singleShot(0, lambda: self.ping_button.setEnabled(True))
        
        threading.Thread(target=ping_thread, daemon=True).start()

    def scan_ports(self):
        host = self.port_host.text().strip()
        port_range = self.port_range.text().strip()
        
        if not host:
            QMessageBox.warning(self, '提示', '请输入目标地址')
            return
        if not port_range:
            QMessageBox.warning(self, '提示', '请输入端口范围')
            return
        
        try:
            start_port, end_port = map(int, port_range.split('-'))
        except:
            QMessageBox.warning(self, '提示', '端口范围格式错误，应为: start-end')
            return
        
        self.port_result.clear()
        self.port_result.setText('正在扫描...')
        self.port_button.setEnabled(False)
        
        open_ports = []
        port_queue = Queue()
        for port in range(start_port, min(end_port + 1, start_port + 200)):
            port_queue.put(port)
        
        def scan_worker():
            import socket
            while not port_queue.empty():
                port = port_queue.get()
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.2)
                    result = sock.connect_ex((host, port))
                    if result == 0:
                        open_ports.append(port)
                    sock.close()
                except:
                    pass
        
        threads = []
        for _ in range(10):
            t = threading.Thread(target=scan_worker, daemon=True)
            t.start()
            threads.append(t)
        
        def wait_and_show_result():
            for t in threads:
                t.join()
            
            if open_ports:
                open_ports.sort()
                self.port_result.setText(f'开放端口: {", ".join(map(str, open_ports))}')
            else:
                self.port_result.setText('未找到开放端口')
            self.port_button.setEnabled(True)
        
        threading.Thread(target=wait_and_show_result, daemon=True).start()

    def get_local_ip(self):
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            self.ip_result.setText(ip)
        except Exception as e:
            self.ip_result.setText(f'获取失败: {str(e)}')

    def create_sql_tools_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        input_group = QWidget()
        input_layout = QVBoxLayout(input_group)
        input_layout.addWidget(QLabel('输入数据（每行一个）:'))
        self.sql_input = QTextEdit()
        self.sql_input.setPlaceholderText('1872542xx\n133277xx7\n1872xx40')
        self.sql_input.setMaximumHeight(120)
        input_layout.addWidget(self.sql_input)
        layout.addWidget(input_group)
        
        button_group = QWidget()
        button_layout = QHBoxLayout(button_group)
        self.sql_format_button = QPushButton('格式化为IN条件')
        self.sql_format_button.clicked.connect(self.format_sql_in)
        button_layout.addWidget(self.sql_format_button)
        self.sql_copy_button = QPushButton('复制结果')
        self.sql_copy_button.clicked.connect(self.copy_sql_result)
        button_layout.addWidget(self.sql_copy_button)
        self.sql_clear_button = QPushButton('清空')
        self.sql_clear_button.clicked.connect(self.clear_sql)
        button_layout.addWidget(self.sql_clear_button)
        layout.addWidget(button_group)
        
        output_group = QWidget()
        output_layout = QVBoxLayout(output_group)
        output_layout.addWidget(QLabel('输出结果:'))
        self.sql_output = QTextEdit()
        self.sql_output.setReadOnly(True)
        self.sql_output.setMaximumHeight(120)
        output_layout.addWidget(self.sql_output)
        layout.addWidget(output_group)
        
        layout.addStretch(1)
        self.tabs.addTab(tab, 'SQL工具')

    def format_sql_in(self):
        input_text = self.sql_input.toPlainText().strip()
        if not input_text:
            QMessageBox.warning(self, '提示', '请输入数据')
            return
        
        lines = input_text.split('\n')
        values = [line.strip() for line in lines if line.strip()]
        quoted_values = [f"'{v}'" for v in values]
        result = ','.join(quoted_values)
        
        self.sql_output.setText(result)

    def copy_sql_result(self):
        result = self.sql_output.toPlainText()
        if not result:
            QMessageBox.warning(self, '提示', '没有可复制的内容')
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(result)
        QMessageBox.information(self, '提示', '已复制到剪贴板')

    def clear_sql(self):
        self.sql_input.clear()
        self.sql_output.clear()

    def create_subnet_calculator_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)

        layout.addWidget(QLabel('IP地址:'), 0, 0, Qt.AlignLeft)
        self.subnet_ip = QLineEdit()
        self.subnet_ip.setPlaceholderText('192.168.1.100')
        layout.addWidget(self.subnet_ip, 0, 1)

        layout.addWidget(QLabel('子网掩码:'), 1, 0, Qt.AlignLeft)
        self.subnet_mask = QLineEdit()
        self.subnet_mask.setPlaceholderText('255.255.255.0 或 /24')
        layout.addWidget(self.subnet_mask, 1, 1)

        calc_btn = QPushButton('计算')
        calc_btn.clicked.connect(self.calculate_subnet)
        layout.addWidget(calc_btn, 2, 0, 1, 2)

        self.subnet_results = QTextEdit()
        self.subnet_results.setReadOnly(True)
        self.subnet_results.setMaximumHeight(150)
        layout.addWidget(self.subnet_results, 3, 0, 1, 2)

        self.tabs.addTab(tab, 'IP子网计算')

    def calculate_subnet(self):
        ip = self.subnet_ip.text().strip()
        subnet = self.subnet_mask.text().strip()

        if not ip:
            QMessageBox.warning(self, '提示', '请输入IP地址')
            return

        if not subnet:
            QMessageBox.warning(self, '提示', '请输入子网掩码')
            return

        try:
            ip_parts = list(map(int, ip.split('.')))
            if len(ip_parts) != 4 or any(not 0 <= p <= 255 for p in ip_parts):
                raise ValueError('无效的IP地址')

            if subnet.startswith('/'):
                cidr = int(subnet[1:])
                if not 0 <= cidr <= 32:
                    raise ValueError('无效的CIDR')
                mask_bits = cidr
            else:
                mask_parts = list(map(int, subnet.split('.')))
                if len(mask_parts) != 4 or any(not 0 <= p <= 255 for p in mask_parts):
                    raise ValueError('无效的子网掩码')
                mask_bits = sum(bin(p).count('1') for p in mask_parts)

            network = []
            broadcast = []
            for i in range(4):
                bits_in_octet = min(8, max(0, mask_bits - i * 8))
                network.append(ip_parts[i] & ((0xFF << (8 - bits_in_octet)) & 0xFF))
                broadcast.append(network[i] | ((0xFF >> bits_in_octet) & 0xFF))

            network_str = '.'.join(map(str, network))
            broadcast_str = '.'.join(map(str, broadcast))

            if mask_bits >= 31:
                first_usable = network_str
                last_usable = broadcast_str
            else:
                first_usable = '.'.join(map(str, network[:3] + [network[3] + 1]))
                last_usable = '.'.join(map(str, broadcast[:3] + [broadcast[3] - 1]))

            total_ips = 2 ** (32 - mask_bits)
            usable_ips = max(0, total_ips - 2)

            wildcard = [255 - network[i] ^ broadcast[i] for i in range(4)]
            wildcard_str = '.'.join(map(str, wildcard))

            mask_octets = []
            for i in range(4):
                bits = min(8, max(0, mask_bits - i * 8))
                mask_octets.append((0xFF << (8 - bits)) & 0xFF)
            mask_str = '.'.join(map(str, mask_octets))

            result = f"""网络地址: {network_str}
子网掩码: {mask_str} (/ {mask_bits})
广播地址: {broadcast_str}
可用IP范围: {first_usable} - {last_usable}
总IP数: {total_ips}
可用IP数: {usable_ips}
通配符掩码: {wildcard_str}
网关地址: {network_str.rsplit('.', 1)[0]}.1"""

            self.subnet_results.setText(result)

        except Exception as e:
            QMessageBox.warning(self, '错误', str(e))

    def create_api_test_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)

        layout.addWidget(QLabel('请求方法:'), 0, 0, Qt.AlignLeft)
        self.api_method = QComboBox()
        self.api_method.addItems(['GET', 'POST', 'PUT', 'DELETE'])
        layout.addWidget(self.api_method, 0, 1)

        layout.addWidget(QLabel('URL:'), 1, 0, Qt.AlignLeft)
        self.api_url = QLineEdit()
        self.api_url.setPlaceholderText('https://api.example.com/test')
        layout.addWidget(self.api_url, 1, 1, 1, 3)

        layout.addWidget(QLabel('请求头（每行一个，格式: key:value）:'), 2, 0, Qt.AlignLeft)
        self.api_headers = QTextEdit()
        self.api_headers.setPlaceholderText('Content-Type: application/json\nAuthorization: Bearer token')
        self.api_headers.setMaximumHeight(60)
        layout.addWidget(self.api_headers, 2, 1, 1, 3)

        layout.addWidget(QLabel('请求体:'), 3, 0, Qt.AlignLeft)
        self.api_body = QTextEdit()
        self.api_body.setPlaceholderText('{"key": "value"}')
        self.api_body.setMaximumHeight(80)
        layout.addWidget(self.api_body, 3, 1, 1, 3)

        send_btn = QPushButton('发送请求')
        send_btn.clicked.connect(self.send_api_request)
        layout.addWidget(send_btn, 4, 1, 1, 3)

        layout.addWidget(QLabel('响应结果:'), 5, 0, Qt.AlignLeft)
        self.api_response = QTextEdit()
        self.api_response.setReadOnly(True)
        self.api_response.setMaximumHeight(120)
        layout.addWidget(self.api_response, 5, 1, 1, 3)

        self.tabs.addTab(tab, 'API测试')

    def send_api_request(self):
        import requests

        url = self.api_url.text().strip()
        method = self.api_method.currentText()
        headers_text = self.api_headers.toPlainText().strip()
        body_text = self.api_body.toPlainText().strip()

        if not url:
            QMessageBox.warning(self, '提示', '请输入URL')
            return

        try:
            headers = {}
            if headers_text:
                for line in headers_text.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip()] = value.strip()

            data = None
            if body_text:
                import json
                try:
                    data = json.loads(body_text)
                except:
                    data = body_text

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if isinstance(data, dict) else None,
                data=data if not isinstance(data, dict) else None,
                timeout=30
            )

            result = f"""状态码: {response.status_code}
响应时间: {response.elapsed.total_seconds():.3f}秒
响应头:
{json.dumps(dict(response.headers), indent=2, ensure_ascii=False)}

响应体:
{response.text}"""

            self.api_response.setText(result)

        except Exception as e:
            self.api_response.setText(f'请求失败: {str(e)}')

    def create_port_forward_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)

        layout.addWidget(QLabel('本地地址:'), 0, 0, Qt.AlignLeft)
        self.local_host = QLineEdit()
        self.local_host.setPlaceholderText('127.0.0.1')
        self.local_host.setText('127.0.0.1')
        layout.addWidget(self.local_host, 0, 1)

        layout.addWidget(QLabel('本地端口:'), 1, 0, Qt.AlignLeft)
        self.local_port = QLineEdit()
        self.local_port.setPlaceholderText('8080')
        layout.addWidget(self.local_port, 1, 1)

        swap_btn = QPushButton('↔')
        swap_btn.setFixedSize(30, 24)
        swap_btn.clicked.connect(self.swap_forward)
        layout.addWidget(swap_btn, 0, 2, 2, 1)

        layout.addWidget(QLabel('目标地址:'), 0, 3, Qt.AlignLeft)
        self.target_host = QLineEdit()
        self.target_host.setPlaceholderText('192.168.1.100')
        layout.addWidget(self.target_host, 0, 4)

        layout.addWidget(QLabel('目标端口:'), 1, 3, Qt.AlignLeft)
        self.target_port = QLineEdit()
        self.target_port.setPlaceholderText('80')
        layout.addWidget(self.target_port, 1, 4)

        self.forward_btn = QPushButton('启动转发')
        self.forward_btn.clicked.connect(self.toggle_port_forward)
        layout.addWidget(self.forward_btn, 2, 0, 1, 5)

        self.forward_log = QTextEdit()
        self.forward_log.setReadOnly(True)
        self.forward_log.setMaximumHeight(150)
        layout.addWidget(self.forward_log, 3, 0, 1, 5)

        self.forward_running = False
        self.forward_thread = None

        self.tabs.addTab(tab, '端口转发')

    def swap_forward(self):
        local_host = self.local_host.text()
        local_port = self.local_port.text()
        target_host = self.target_host.text()
        target_port = self.target_port.text()

        self.local_host.setText(target_host)
        self.local_port.setText(target_port)
        self.target_host.setText(local_host)
        self.target_port.setText(local_port)

    def toggle_port_forward(self):
        if self.forward_running:
            self.stop_port_forward()
        else:
            self.start_port_forward()

    def start_port_forward(self):
        try:
            local_host = self.local_host.text().strip()
            local_port = int(self.local_port.text().strip())
            target_host = self.target_host.text().strip()
            target_port = int(self.target_port.text().strip())

            if not local_host or not target_host:
                QMessageBox.warning(self, '提示', '请输入本地地址和目标地址')
                return

            self.forward_running = True
            self.forward_btn.setText('停止转发')
            self.forward_log.clear()
            self.forward_log.append(f'开始端口转发: {local_host}:{local_port} -> {target_host}:{target_port}')

            import threading
            self.forward_thread = threading.Thread(
                target=self.port_forward_worker,
                args=(local_host, local_port, target_host, target_port),
                daemon=True
            )
            self.forward_thread.start()

        except ValueError:
            QMessageBox.warning(self, '提示', '端口号必须是数字')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'启动失败: {str(e)}')

    def stop_port_forward(self):
        self.forward_running = False
        self.forward_btn.setText('启动转发')
        self.forward_log.append('端口转发已停止')

    def port_forward_worker(self, local_host, local_port, target_host, target_port):
        import socket
        import threading

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server_socket.bind(('0.0.0.0', local_port))
            server_socket.listen(5)
            self.forward_log.append(f'本地服务已启动，监听 {local_host}:{local_port}')

            while self.forward_running:
                server_socket.settimeout(1)
                try:
                    client_socket, addr = server_socket.accept()
                    t = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, target_host, target_port),
                        daemon=True
                    )
                    t.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.forward_running:
                        self.forward_log.append(f'错误: {str(e)}')
        except Exception as e:
            self.forward_log.append(f'绑定失败: {str(e)}')
            self.stop_port_forward()
        finally:
            server_socket.close()

    def handle_client(self, client_socket, target_host, target_port):
        import socket

        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            target_socket.connect((target_host, target_port))
            self.forward_log.append(f'连接建立: {client_socket.getpeername()} -> {target_host}:{target_port}')

            def forward(src, dst):
                while self.forward_running:
                    src.settimeout(1)
                    try:
                        data = src.recv(4096)
                        if not data:
                            break
                        dst.sendall(data)
                    except socket.timeout:
                        continue
                    except Exception:
                        break

            import threading
            t1 = threading.Thread(target=forward, args=(client_socket, target_socket), daemon=True)
            t2 = threading.Thread(target=forward, args=(target_socket, client_socket), daemon=True)
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        except Exception as e:
            self.forward_log.append(f'连接目标失败: {str(e)}')
        finally:
            client_socket.close()
            target_socket.close()

    def create_remote_download_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)

        layout.addWidget(QLabel('远程主机:'), 0, 0, Qt.AlignLeft)
        self.remote_host = QLineEdit()
        self.remote_host.setPlaceholderText('192.168.1.100')
        layout.addWidget(self.remote_host, 0, 1)

        layout.addWidget(QLabel('共享目录:'), 1, 0, Qt.AlignLeft)
        self.remote_share = QLineEdit()
        self.remote_share.setPlaceholderText('share')
        layout.addWidget(self.remote_share, 1, 1)

        layout.addWidget(QLabel('用户名:'), 2, 0, Qt.AlignLeft)
        self.remote_user = QLineEdit()
        self.remote_user.setPlaceholderText('可选')
        layout.addWidget(self.remote_user, 2, 1)

        layout.addWidget(QLabel('密码:'), 3, 0, Qt.AlignLeft)
        self.remote_pass = QLineEdit()
        self.remote_pass.setEchoMode(QLineEdit.Password)
        self.remote_pass.setPlaceholderText('可选')
        layout.addWidget(self.remote_pass, 3, 1)

        self.remote_file_list = QListWidget()
        layout.addWidget(self.remote_file_list, 4, 0, 1, 2)

        browse_btn = QPushButton('浏览远程文件')
        browse_btn.clicked.connect(self.browse_remote_files)
        layout.addWidget(browse_btn, 5, 0)

        layout.addWidget(QLabel('本地保存路径:'), 6, 0, Qt.AlignLeft)
        self.local_save_path = QLineEdit()
        layout.addWidget(self.local_save_path, 6, 1)

        save_browse_btn = QPushButton('浏览')
        save_browse_btn.clicked.connect(self.browse_local_path)
        layout.addWidget(save_browse_btn, 6, 2)

        download_btn = QPushButton('下载文件')
        download_btn.clicked.connect(self.download_remote_file)
        layout.addWidget(download_btn, 7, 0, 1, 3)

        self.download_log = QTextEdit()
        self.download_log.setReadOnly(True)
        self.download_log.setMaximumHeight(100)
        layout.addWidget(self.download_log, 8, 0, 1, 3)

        self.tabs.addTab(tab, '远程下载')

    def browse_remote_files(self):
        host = self.remote_host.text().strip()
        share = self.remote_share.text().strip()
        user = self.remote_user.text().strip()
        password = self.remote_pass.text().strip()

        if not host or not share:
            QMessageBox.warning(self, '提示', '请输入远程主机和共享目录')
            return

        try:
            import subprocess
            import os

            self.download_log.clear()
            self.remote_file_list.clear()

            smb_path = f'\\\\{host}\\{share}'
            
            if user and password:
                subprocess.run(
                    f'net use "{smb_path}" /user:{user} {password}',
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=30
                )
            else:
                subprocess.run(
                    f'net use "{smb_path}"',
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=30
                )

            try:
                files = os.listdir(smb_path)
                for f in files:
                    if f and f not in ('.', '..'):
                        self.remote_file_list.addItem(f)
                
                self.download_log.append(f'成功连接到 {smb_path}')
                self.download_log.append(f'发现 {len(files)} 个文件/目录')
            except Exception as e:
                self.download_log.append(f'列出文件失败: {str(e)}')

        except Exception as e:
            self.download_log.append(f'连接失败: {str(e)}')
            QMessageBox.warning(self, '错误', f'连接失败: {str(e)}')

    def browse_local_path(self):
        path, _ = QFileDialog.getSaveFileName(self, '选择保存路径')
        if path:
            self.local_save_path.setText(path)

    def download_remote_file(self):
        host = self.remote_host.text().strip()
        share = self.remote_share.text().strip()
        user = self.remote_user.text().strip()
        password = self.remote_pass.text().strip()
        local_path = self.local_save_path.text().strip()

        selected_items = self.remote_file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '提示', '请选择要下载的文件')
            return

        remote_file = selected_items[0].text()

        if not host or not share or not local_path:
            QMessageBox.warning(self, '提示', '请填写完整信息')
            return

        try:
            import subprocess
            import shutil

            self.download_log.append(f'开始下载: {remote_file}')

            smb_path = f'\\\\{host}\\{share}'
            remote_file_path = f'{smb_path}\\{remote_file}'
            
            if user and password:
                subprocess.run(
                    f'net use "{smb_path}" /user:{user} {password}',
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=30
                )
            else:
                subprocess.run(
                    f'net use "{smb_path}"',
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=30
                )

            shutil.copy(remote_file_path, local_path)

            subprocess.run(f'net use "{smb_path}" /delete /y', capture_output=True, shell=True)

            self.download_log.append(f'下载完成: {local_path}')
            QMessageBox.information(self, '成功', '文件下载完成！')

        except Exception as e:
            self.download_log.append(f'下载失败: {str(e)}')
            QMessageBox.warning(self, '错误', f'下载失败: {str(e)}')

    def create_data_convert_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)

        layout.addWidget(QLabel('输入格式:'), 0, 0, Qt.AlignLeft)
        self.data_input_format = QComboBox()
        self.data_input_format.addItems(['JSON', 'XML', 'YAML'])
        layout.addWidget(self.data_input_format, 0, 1)

        layout.addWidget(QLabel('输出格式:'), 0, 2, Qt.AlignLeft)
        self.data_output_format = QComboBox()
        self.data_output_format.addItems(['JSON', 'XML', 'YAML'])
        layout.addWidget(self.data_output_format, 0, 3)

        layout.addWidget(QLabel('输入:'), 1, 0, Qt.AlignLeft)
        self.data_input = QTextEdit()
        self.data_input.setPlaceholderText('请输入JSON/XML/YAML数据')
        layout.addWidget(self.data_input, 2, 0, 1, 4)

        convert_btn = QPushButton('转换')
        convert_btn.clicked.connect(self.convert_data)
        layout.addWidget(convert_btn, 3, 0, 1, 4)

        layout.addWidget(QLabel('输出:'), 4, 0, Qt.AlignLeft)
        self.data_output = QTextEdit()
        self.data_output.setReadOnly(True)
        layout.addWidget(self.data_output, 5, 0, 1, 4)

        self.tabs.addTab(tab, '数据转换')

    def convert_data(self):
        input_text = self.data_input.toPlainText().strip()
        input_format = self.data_input_format.currentText()
        output_format = self.data_output_format.currentText()

        if not input_text:
            QMessageBox.warning(self, '提示', '请输入数据')
            return

        try:
            data = None

            if input_format == 'JSON':
                import json
                data = json.loads(input_text)
            elif input_format == 'XML':
                import xmltodict
                data = xmltodict.parse(input_text)
            elif input_format == 'YAML':
                import yaml
                data = yaml.safe_load(input_text)

            if output_format == 'JSON':
                import json
                result = json.dumps(data, indent=2, ensure_ascii=False)
            elif output_format == 'XML':
                import xmltodict
                if isinstance(data, list):
                    data = {'root': {'item': data}}
                elif not isinstance(data, dict):
                    data = {'root': {'value': data}}
                elif not data:
                    data = {'root': {}}
                result = xmltodict.unparse(data, pretty=True, encoding='utf-8').decode('utf-8')
            elif output_format == 'YAML':
                import yaml
                result = yaml.dump(data, default_flow_style=False, allow_unicode=True)

            self.data_output.setText(result)

        except Exception as e:
            self.data_output.setText(f'转换失败: {str(e)}')
            QMessageBox.warning(self, '错误', f'转换失败: {str(e)}')

    def create_process_manager_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        search_layout = QHBoxLayout()
        search_label = QLabel('搜索:')
        self.process_search = QLineEdit()
        self.process_search.setPlaceholderText('按名称或PID搜索')
        self.process_search.textChanged.connect(self.refresh_process_list)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.process_search)
        layout.addLayout(search_layout)

        self.process_table = QListWidget()
        self.process_table.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self.process_table)

        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.refresh_process_list)
        btn_layout.addWidget(refresh_btn)

        kill_btn = QPushButton('结束进程')
        kill_btn.clicked.connect(self.kill_process)
        btn_layout.addWidget(kill_btn)

        layout.addLayout(btn_layout)

        self.tabs.addTab(tab, '进程管理')
        self.refresh_process_list()

    def refresh_process_list(self):
        self.process_table.clear()
        try:
            import psutil
            search_text = self.process_search.text().lower()
            
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    pid = str(proc.info['pid'])
                    name = proc.info['name']
                    memory = proc.info['memory_info']
                    
                    if memory:
                        memory_mb = memory.rss / (1024 * 1024)
                        memory_str = f'{memory_mb:.2f} MB'
                    else:
                        memory_str = 'N/A'
                    
                    display_text = f'{pid} - {name} - {memory_str}'
                    
                    if search_text in name.lower() or search_text in pid:
                        self.process_table.addItem(display_text)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            QMessageBox.warning(self, '错误', f'获取进程列表失败: {str(e)}')

    def kill_process(self):
        selected_items = self.process_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '提示', '请选择要结束的进程')
            return

        try:
            import psutil
            success_count = 0
            fail_count = 0
            
            for item in selected_items:
                item_text = item.text()
                pid = int(item_text.split(' - ')[0])
                try:
                    proc = psutil.Process(pid)
                    proc.kill()
                    success_count += 1
                except Exception as e:
                    fail_count += 1
            
            message = f'成功结束 {success_count} 个进程'
            if fail_count > 0:
                message += f'，失败 {fail_count} 个进程'
            QMessageBox.information(self, '完成', message)
            self.refresh_process_list()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'结束进程失败: {str(e)}')

    def create_service_manager_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        search_layout = QHBoxLayout()
        search_label = QLabel('搜索:')
        self.service_search = QLineEdit()
        self.service_search.setPlaceholderText('按服务名称搜索')
        self.service_search.textChanged.connect(self.refresh_service_list)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.service_search)
        layout.addLayout(search_layout)

        self.service_table = QListWidget()
        layout.addWidget(self.service_table)

        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.refresh_service_list)
        btn_layout.addWidget(refresh_btn)

        start_btn = QPushButton('启动')
        start_btn.clicked.connect(self.start_service)
        btn_layout.addWidget(start_btn)

        stop_btn = QPushButton('停止')
        stop_btn.clicked.connect(self.stop_service)
        btn_layout.addWidget(stop_btn)

        restart_btn = QPushButton('重启')
        restart_btn.clicked.connect(self.restart_service)
        btn_layout.addWidget(restart_btn)

        layout.addLayout(btn_layout)

        self.tabs.addTab(tab, '服务管理')
        self.refresh_service_list()

    def refresh_service_list(self):
        self.service_table.clear()
        try:
            import subprocess
            
            search_text = self.service_search.text().lower()
            
            result = subprocess.run(
                ['sc', 'query', 'type=', 'service', 'state=', 'all'],
                capture_output=True,
                text=True,
                encoding='gbk',
                timeout=30
            )
            
            output = result.stdout
            services = []
            current_service = {}
            
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('SERVICE_NAME:'):
                    if current_service:
                        services.append(current_service)
                    current_service = {'name': line.split(':')[1].strip()}
                elif line.startswith('DISPLAY_NAME:'):
                    current_service['display_name'] = line.split(':', 1)[1].strip()
                elif line.startswith('STATE:'):
                    state_code = line.split(':')[1].strip().split()[0]
                    if state_code == '1':
                        current_service['state'] = '已停止'
                    elif state_code == '4':
                        current_service['state'] = '运行中'
                    else:
                        current_service['state'] = '未知'
            
            if current_service:
                services.append(current_service)
            
            for service in services:
                display_name = service.get('display_name', service['name'])
                name = service['name']
                state = service.get('state', '未知')
                
                if search_text in display_name.lower() or search_text in name.lower():
                    self.service_table.addItem(f'{display_name} ({name}) - {state}')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'获取服务列表失败: {str(e)}')

    def get_selected_service(self):
        selected_items = self.service_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '提示', '请选择服务')
            return None
        
        item_text = selected_items[0].text()
        # 提取服务名称 (service_name)
        start = item_text.find('(') + 1
        end = item_text.find(')')
        service_name = item_text[start:end]
        return service_name

    def start_service(self):
        service_name = self.get_selected_service()
        if not service_name:
            return
        
        try:
            import subprocess
            result = subprocess.run(
                ['sc', 'start', service_name],
                capture_output=True,
                text=True,
                encoding='gbk',
                timeout=30
            )
            
            if 'SUCCESS' in result.stdout or result.returncode == 0:
                QMessageBox.information(self, '成功', '服务已启动')
            else:
                QMessageBox.warning(self, '错误', f'启动服务失败: {result.stderr or result.stdout}')
            
            self.refresh_service_list()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'启动服务失败: {str(e)}')

    def stop_service(self):
        service_name = self.get_selected_service()
        if not service_name:
            return
        
        try:
            import subprocess
            result = subprocess.run(
                ['sc', 'stop', service_name],
                capture_output=True,
                text=True,
                encoding='gbk',
                timeout=30
            )
            
            if 'SUCCESS' in result.stdout or result.returncode == 0:
                QMessageBox.information(self, '成功', '服务已停止')
            else:
                QMessageBox.warning(self, '错误', f'停止服务失败: {result.stderr or result.stdout}')
            
            self.refresh_service_list()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'停止服务失败: {str(e)}')

    def restart_service(self):
        service_name = self.get_selected_service()
        if not service_name:
            return
        
        try:
            import subprocess
            
            subprocess.run(
                ['sc', 'stop', service_name],
                capture_output=True,
                text=True,
                encoding='gbk',
                timeout=30
            )
            
            result = subprocess.run(
                ['sc', 'start', service_name],
                capture_output=True,
                text=True,
                encoding='gbk',
                timeout=30
            )
            
            if 'SUCCESS' in result.stdout or result.returncode == 0:
                QMessageBox.information(self, '成功', '服务已重启')
            else:
                QMessageBox.warning(self, '错误', f'重启服务失败: {result.stderr or result.stdout}')
            
            self.refresh_service_list()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'重启服务失败: {str(e)}')

    def create_clipboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.clipboard_text = QPlainTextEdit()
        self.clipboard_text.setPlaceholderText('剪贴板内容将显示在这里...')
        layout.addWidget(self.clipboard_text)

        btn_layout = QHBoxLayout()
        
        copy_btn = QPushButton('复制到剪贴板')
        copy_btn.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(copy_btn)

        paste_btn = QPushButton('粘贴剪贴板')
        paste_btn.clicked.connect(self.paste_from_clipboard)
        btn_layout.addWidget(paste_btn)

        clear_btn = QPushButton('清空剪贴板')
        clear_btn.clicked.connect(self.clear_clipboard)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)

        self.tabs.addTab(tab, '剪贴板')

    def copy_to_clipboard(self):
        text = self.clipboard_text.toPlainText()
        if not text:
            QMessageBox.warning(self, '提示', '请输入要复制的内容')
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, '成功', '已复制到剪贴板')

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.clipboard_text.setPlainText(text)
        else:
            QMessageBox.information(self, '提示', '剪贴板为空')

    def clear_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.clear()
        self.clipboard_text.clear()
        QMessageBox.information(self, '成功', '剪贴板已清空')

    

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage('运维小工具', '已最小化到托盘', QSystemTrayIcon.Information, 2000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())