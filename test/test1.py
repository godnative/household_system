import sys
from PyQt5.QtWidgets import *
from openpyxl import load_workbook

class ExcelRichTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XLSX → 富文本表格（导入+导出+合并单元格）")
        self.resize(900, 650)

        # 富文本编辑器（核心）
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("font-size:14px;")

        # 按钮栏
        self.btn_open = QPushButton("📄 打开 XLSX")
        self.btn_export = QPushButton("💾 导出富文本")
        self.btn_import = QPushButton("📂 导入富文本")

        self.btn_open.clicked.connect(self.open_xlsx)
        self.btn_export.clicked.connect(self.export_rich)  # 这里修复了！
        self.btn_import.clicked.connect(self.import_rich)

        # 布局
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.btn_open)
        h_layout.addWidget(self.btn_import)
        h_layout.addWidget(self.btn_export)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.text_edit)

        container = QWidget()
        container.setLayout(v_layout)
        self.setCentralWidget(container)

    # ------------------------------
    # 1. 打开 XLSX → 渲染富文本表格
    # ------------------------------
    def open_xlsx(self):
        path, _ = QFileDialog.getOpenFileName(filter="Excel (*.xlsx)")
        if not path:
            return
        html = self.excel_to_html(path)
        self.text_edit.setHtml(html)

    def excel_to_html(self, file_path):
        wb = load_workbook(file_path)
        sheet = wb.active

        # 读取所有合并单元格
        merged_ranges = sheet.merged_cells.ranges
        merged_set = set()
        merge_info = {}

        for m in merged_ranges:
            mr, mc, Mr, Mc = m.min_row, m.min_col, m.max_row, m.max_col
            rspan = Mr - mr + 1
            cspan = Mc - mc + 1
            merge_info[(mr, mc)] = (rspan, cspan)
            for r in range(mr, Mr+1):
                for c in range(mc, Mc+1):
                    if r != mr or c != mc:
                        merged_set.add((r, c))

        # 生成 HTML
        html = """
        <h3>Excel 富文本表格</h3>
        <table border='1' cellpadding='8' cellspacing='0' style='border-collapse:collapse; width:100%; font-size:14px;'>
        """

        for row_idx, row in enumerate(sheet.iter_rows(), 1):
            html += "<tr>"
            for col_idx, cell in enumerate(row, 1):
                if (row_idx, col_idx) in merged_set:
                    continue
                val = str(cell.value) if cell.value is not None else ""
                rspan, cspan = merge_info.get((row_idx, col_idx), (1, 1))

                if row_idx == 1:
                    html += f'<th rowspan={rspan} colspan={cspan} style="background:#f2f2f2;">{val}</th>'
                else:
                    html += f'<td rowspan={rspan} colspan={cspan}>{val}</td>'
            html += "</tr>"

        html += "</table>"
        wb.close()
        return html

    # ------------------------------
    # 2. 导出当前富文本为 HTML 文件
    # ------------------------------
    def export_rich(self):
        path, _ = QFileDialog.getSaveFileName(filter="富文本文件 (*.html)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text_edit.toHtml())
            QMessageBox.information(self, "成功", "富文本已导出！")

    # ------------------------------
    # 3. 导入富文本 → 直接渲染表格
    # ------------------------------
    def import_rich(self):
        path, _ = QFileDialog.getOpenFileName(filter="富文本文件 (*.html)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                html = f.read()
            self.text_edit.setHtml(html)
            QMessageBox.information(self, "成功", "富文本已导入并渲染！")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ExcelRichTextEditor()
    w.show()
    sys.exit(app.exec_())