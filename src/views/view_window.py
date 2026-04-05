from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QComboBox
from PyQt5.QtCore import Qt
from qfluentwidgets import ComboBox, FlowLayout, ElevatedCardWidget, BodyLabel, CaptionLabel, TitleLabel
from src.services.village_service import VillageService
from src.services.household_service import HouseholdService
from src.services.member_service import MemberService
from src.models import SessionLocal

class MemberCard(ElevatedCardWidget):
    """ 成员卡片 """

    def __init__(self, member, parent=None):
        super().__init__(parent)
        self.member = member
        
        self.nameLabel = BodyLabel(member.name, self)
        self.idNumberLabel = CaptionLabel(member.id_number, self)
        
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.nameLabel, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.idNumberLabel, 0, Qt.AlignCenter)
        
        self.setFixedSize(168, 120)

class ViewWindow(QWidget):
    """ 查看子窗口 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_villages()
    
    def showEvent(self, event):
        """ 窗口显示时刷新数据 """
        super().showEvent(event)
        self.refresh()
    
    def refresh(self):
        """ 刷新所有数据 """
        self.load_villages()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = TitleLabel('村庄-家庭-成员查看')
        layout.addWidget(title_label)
        
        # 村庄选择
        village_layout = QHBoxLayout()
        village_label = QLabel('选择村庄:')
        self.village_combo = ComboBox()
        self.village_combo.currentIndexChanged.connect(self.on_village_changed)
        village_layout.addWidget(village_label)
        village_layout.addWidget(self.village_combo)
        village_layout.addStretch()
        layout.addLayout(village_layout)
        
        # 左右双列布局
        main_layout = QHBoxLayout()
        
        # 左边家庭列表
        left_layout = QVBoxLayout()
        household_label = QLabel('家庭列表')
        self.household_list = QListWidget()
        self.household_list.itemClicked.connect(self.on_household_clicked)
        left_layout.addWidget(household_label)
        left_layout.addWidget(self.household_list)
        main_layout.addLayout(left_layout, 1)
        
        # 右边成员卡片
        right_layout = QVBoxLayout()
        member_label = QLabel('成员列表')
        self.member_container = QWidget()
        self.member_layout = FlowLayout(self.member_container)
        right_layout.addWidget(member_label)
        right_layout.addWidget(self.member_container)
        self.right_layout = right_layout
        main_layout.addLayout(right_layout, 2)
        
        layout.addLayout(main_layout)
    
    def load_villages(self):
        """ 加载村庄数据 """
        db = SessionLocal()
        try:
            villages = VillageService.get_all_villages(db)
            self.village_combo.clear()
            for village in villages:
                self.village_combo.addItem(village.name)
                self.village_combo.setItemData(self.village_combo.count() - 1, village.id)
            if villages:
                self.on_village_changed(0)
        finally:
            db.close()
    
    def on_village_changed(self, index):
        """ 村庄选择变化时的处理 """
        village_id = self.village_combo.currentData()
        if village_id:
            self.load_households(village_id)
    
    def load_households(self, village_id):
        """ 加载家庭数据 """
        db = SessionLocal()
        try:
            households = HouseholdService.get_all_households(db, village_id=village_id)
            self.household_list.clear()
            for household in households:
                item = QListWidgetItem(household.household_code)
                item.setData(Qt.UserRole, household.id)
                self.household_list.addItem(item)
            if households:
                self.household_list.setCurrentRow(0)
                self.on_household_clicked(self.household_list.item(0))
            else:
                self.clear_member_cards()
        finally:
            db.close()
    
    def on_household_clicked(self, item):
        """ 家庭选择变化时的处理 """
        household_id = item.data(Qt.UserRole)
        if household_id:
            self.load_members(household_id)
    
    def clear_member_cards(self):
        """ 清空成员卡片 """
        # 移除旧的容器
        if hasattr(self, 'member_container'):
            self.right_layout.removeWidget(self.member_container)
            self.member_container.deleteLater()
        
        # 创建新的空容器
        self.member_container = QWidget()
        self.member_layout = FlowLayout(self.member_container)
        self.right_layout.addWidget(self.member_container)
    
    def load_members(self, household_id):
        """ 加载成员数据 """
        db = SessionLocal()
        try:
            members = MemberService.get_all_members(db, household_id=household_id)
            
            # 移除旧的容器
            if hasattr(self, 'member_container'):
                self.right_layout.removeWidget(self.member_container)
                self.member_container.deleteLater()
            
            # 创建新的容器和布局
            self.member_container = QWidget()
            self.member_layout = FlowLayout(self.member_container)
            
            # 添加成员卡片
            for member in members:
                card = MemberCard(member)
                self.member_layout.addWidget(card)
            
            # 添加新容器到布局
            self.right_layout.addWidget(self.member_container)
        finally:
            db.close()