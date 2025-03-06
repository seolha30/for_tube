from bs4 import BeautifulSoup
import tempfile
import zipfile
import glob
import platform
from pathlib import Path
import requests 

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from googleapiclient.discovery import build  # YouTube API
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QWidget, QMessageBox, QScrollArea  # UI 컴포넌트
from PyQt6.QtCore import QThread, pyqtSignal  # 스레드 처리
import logging
from datetime import datetime
from yt_dlp import YoutubeDL
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

def get_resource_path(relative_path):
        try:
            base_path = sys._MEIPASS  # PyInstaller의 임시 디렉토리
        except Exception:
            base_path = os.path.abspath(".")
        
        if getattr(sys, 'frozen', False):
            # 실행파일로 패키징된 경우
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            # 일반 Python 스크립트로 실행되는 경우
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
    

# 로그 폴더 생성 (AppData 내 안전한 위치)
app_data = os.path.join(os.path.expandvars('%LOCALAPPDATA%'), 'TubeLens')
log_dir = os.path.join(app_data, 'tubelens_log')
os.makedirs(log_dir, exist_ok=True)

# 로그 파일 설정
log_filename = os.path.join(log_dir, f"tubelens_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
# 3일 이상 된 로그 파일 삭제
current_time = datetime.now()
for old_log in os.listdir(log_dir):
    if old_log.endswith('.log'):
        log_path = os.path.join(log_dir, old_log)
        file_time = datetime.fromtimestamp(os.path.getctime(log_path))
        if (current_time - file_time).days > 3:
            try:
                os.remove(log_path)
            except:
                pass
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
import os.path
from cryptography.fernet import Fernet
from historymanager import HistoryManager
# 기존 임포트문들 아래에 추가
import importlib
import importlib.util
import shutil
import base64
import firebase_admin
import asyncio
import aiohttp
import shutil
import tempfile
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QTabWidget, QRadioButton
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from io import BytesIO
from firebase_admin import credentials
from firebase_admin import db
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QFileDialog, QProgressBar, QWidget, QHBoxLayout
from functools import partial
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle

def collect_single_subtitle(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcript_list.find_transcript(['ko'])
        except:
            try:
                transcript = transcript_list.find_transcript(['en'])
            except:
                transcript = transcript_list.find_generated_transcript(['ko', 'en'])
        
        return "\n".join([line['text'] for line in transcript.fetch()])
    except Exception as e:
        return "자막 없음"

def process_subtitle(video_data):
    i, video_url = video_data
    video_id = video_url.split('v=')[1]
    return i, collect_single_subtitle(video_id)

# Firebase 초기화
if not firebase_admin._apps:
    from cryptography.fernet import Fernet
    import json
    import os
    import sys
    import subprocess
    import winreg
    import yt_dlp
    import threading

    
    # 키와 암호화된 설정 파일 읽기
    with open(get_resource_path('firebase_key.key'), 'rb') as key_file:
        key = key_file.read()
    with open(get_resource_path('firebase_config.enc'), 'rb') as config_file:
        encrypted_data = config_file.read()

    # 복호화
    f = Fernet(key)
    config_str = f.decrypt(encrypted_data).decode()
    config = json.loads(config_str)

    cred = credentials.Certificate(config)
    firebase_admin.initialize_app(cred, {
        
        'databaseURL': 'https://seol-license-manager-default-rtdb.asia-southeast1.firebasedatabase.app'
    })

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLineEdit, QDateEdit, QLabel, QComboBox, QTextEdit,
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
                            QFrame, QCheckBox, QGroupBox, QProgressBar, QDialog, QInputDialog, QCalendarWidget,
                            QSplashScreen)
from PyQt6.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal, QDir, QDate, QUrl, QEvent, QPoint, QRect
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPainterPath, QDesktopServices, QCursor  # QCursor 추가
from PyQt6.QtGui import QAction
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PyQt6.QtWidgets import QMenu
from PyQt6.QtWidgets import QToolTip
from PyQt6.QtGui import QIcon
import tempfile
import re
import sys
import os
import json
import pandas as pd
from datetime import datetime, timedelta, timezone
import ntplib
import urllib.request
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled
import hashlib

import json

from pathlib import Path

class RealtimeSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("시그널 실시간 검색어")
        self.setStyleSheet("QDialog { background-color: #f5f5f5; } QLabel { color: black; }")
        self.setFixedSize(1000, 500)
        
        # 메인 레이아웃
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(15, 5, 15, 5)

                # 상단 영역을 포함할 컨테이너 위젯
        top_container = QWidget()
        top_container.setFixedHeight(120)  # 높이만 증가
        top_container.setStyleSheet("""
            QWidget {
                background: #f5f5f5;
                margin: 0;
                padding: 0;
            }
        """)
        
        top_layout = QVBoxLayout(top_container)
        top_layout.setSpacing(15)  # 간격만 증가
        top_layout.setContentsMargins(15, 15, 15, 15)  # 여백 추가

        # 모든 헤더 내용을 top_container에 추가
        header_layout = QVBoxLayout()
        header_layout.setSpacing(12)  # 간격만 증가
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 제목 (기존 스타일 유지)
        title = QLabel("🔍 실시간 검색어 TOP 10")
        title.setStyleSheet("""
            QLabel {
                color: #4a9eff;  /* 튜브렌즈의 메인 컬러 */
                font-size: 24px;
                font-weight: bold;
                padding: 0;
                margin: 0;
                background-color: transparent;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬 추가
        
        # 설명 (기존 스타일 유지)
        desc = QLabel("현재 기준 사용자가 가장 많이 검색하는 키워드입니다")
        desc.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 14px;
                padding: 0;
                margin: 0;
                font-weight: normal;
                line-height: 1.0;
            }
        """)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬 추가

        # 시간 표시 (기존 스타일 유지)
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                font-size: 13px;
                margin: 0;
                padding: 0;
                font-weight: bold;  /* 글씨 굵게 설정 */
                line-height: 1.0;
            }
        """)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬 추가

        # 라벨들의 높이를 강제로 설정
        desc.setFixedHeight(20)  # 15에서 20으로 증가
        self.time_label.setFixedHeight(20)  # 15에서 20으로 증가

        header_layout.addWidget(title)
        header_layout.addWidget(desc)
        header_layout.addWidget(self.time_label)
        
        top_layout.addLayout(header_layout)
        layout.addWidget(top_container)

        # 검색어 랭킹 컨테이너
        ranks_container = QWidget()
        ranks_layout = QHBoxLayout(ranks_container)
        ranks_layout.setContentsMargins(0, 0, 0, 0)  # 모든 여백 제거
        ranks_layout.setSpacing(10)  # 좌우 간격 줄임

        # 상단과 랭킹 사이 간격 최소화
        layout.addWidget(ranks_container)
        layout.setSpacing(0)  # 위젯 사이 간격 제거

        # 왼쪽/오른쪽 컬럼
        self.left_column = QVBoxLayout()
        self.right_column = QVBoxLayout()
        
        for col in [self.left_column, self.right_column]:
            col.setContentsMargins(0, 0, 0, 0)
            col.setSpacing(8)  # 랭킹 아이템 간 간격

        ranks_layout.addLayout(self.left_column)
        ranks_layout.addLayout(self.right_column)
        layout.addWidget(ranks_container)
        
        # 데이터 로드 및 자동 새로고침
        self.refresh_data()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(300000)  # 5분마다 새로고침
    
    
    def create_rank_item(self, rank, keyword, state):
        # 검색어 아이템 컨테이너
        item = QWidget()
        item.setCursor(Qt.CursorShape.PointingHandCursor)
        item.setStyleSheet("""
            QWidget {
                background-color: #B2CCFF;
                border-radius: 10px;
                padding: 15px;
            }
            QWidget:hover {
                background-color: #6799FF;
            }
        """)
        layout = QHBoxLayout(item)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # 순위 컨테이너 위젯 생성
        rank_container = QWidget()
        rank_container.setStyleSheet("""
            QWidget {
                background-color: #3CAEA3;
                border-radius: 5px;
                padding: 5px;
            }
            QWidget:hover {
                background-color: #4FDFCF;
            }
        """)
        rank_container_layout = QHBoxLayout(rank_container)
        rank_container_layout.setContentsMargins(5, 5, 5, 5)
        
        # 순위 레이블
        rank_label = QLabel(f"{rank}")
        rank_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
                min-width: 30px;
            }
        """)
        rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rank_container_layout.addWidget(rank_label)
        layout.addWidget(rank_container)
        
        # 검색어
        keyword_text = QTextEdit(keyword)
        keyword_text.setReadOnly(True)  # 읽기 전용
        keyword_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        keyword_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        keyword_text.setStyleSheet("""
            QTextEdit {
                color: #333333;
                font-size: 18px;
                font-weight: bold;
                border: none;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
        """)
        # 높이 자동 조정
        keyword_text.setFixedHeight(30)
        layout.addWidget(keyword_text, 1)  # stretch factor 1
        
        
        
        # 클릭 이벤트
        item.mousePressEvent = lambda e: self.open_search(keyword)
        
        return item

    def open_search(self, keyword):
        # 네이버 검색 페이지로 이동 (실제 작동하는 URL로 수정)
        search_url = f"https://search.naver.com/search.naver?where=news&query={keyword}"
        QDesktopServices.openUrl(QUrl(search_url))

    def refresh_data(self):
        try:
            # API 호출
            url = 'https://api.signal.bz/news/realtime'
            response = requests.get(url)
            if not response.ok:
                raise Exception("데이터를 가져올 수 없습니다.")
                
            data = response.json()
            if not data.get('top10'):
                raise Exception("검색어 데이터가 없습니다.")
            
            # 기존 아이템들 제거
            self.clear_layouts([self.left_column, self.right_column])
            
            # 새 데이터로 아이템 추가
            for idx, item in enumerate(data['top10'], 1):
                rank_item = self.create_rank_item(
                    idx,
                    item['keyword'],
                    item.get('state', '-')  
                )
                
                if idx <= 5:  # 1-5위는 왼쪽
                    self.left_column.addWidget(rank_item)
                else:        # 6-10위는 오른쪽
                    self.right_column.addWidget(rank_item)
            
            # 현재 시간 업데이트
            current_time = datetime.now()
            weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
            weekday = weekday_names[current_time.weekday()]
            formatted_time = f"{current_time.strftime('%Y년 %m월 %d일')} {weekday} {current_time.strftime('%p').replace('PM', '오후').replace('AM', '오전')} {current_time.strftime('%I:%M')}"
            self.time_label.setText(f"{formatted_time}")
            
        except Exception as e:
            self.time_label.setText(f"업데이트 실패: {str(e)}")
            
    def clear_layouts(self, layouts):
        """레이아웃 내의 모든 위젯 제거"""
        for layout in layouts:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

class TubeLens(QMainWindow):
    # 1. 기본 영상 정보
    def get_video_title(self):
        try:
            row = self.table.currentRow()
            return self.table.item(row, 1).text() if row >= 0 else None
        except:
            return None

    def get_thumbnail_url(self):
        try:
            row = self.table.currentRow()
            return self.video_data[row]['thumbnail_url'] if row >= 0 else None
        except:
            return None

    def get_video_duration(self):
        try:
            row = self.table.currentRow()
            return self.table.item(row, 3).text() if row >= 0 else None
        except:
            return None

    def get_publish_date(self):
        try:
            row = self.table.currentRow()
            return self.video_data[row]['publishedAt'] if row >= 0 else None
        except:
            return None

    def get_view_count(self):
        try:
            row = self.table.currentRow()
            return self.table.item(row, 4).text() if row >= 0 else None
        except:
            return None

    def get_like_count(self):
        try:
            row = self.table.currentRow()
            return self.video_data[row]['likeCount'] if row >= 0 else None
        except:
            return None

    def get_comment_count(self):
        try:
            row = self.table.currentRow()
            return self.video_data[row]['commentCount'] if row >= 0 else None
        except:
            return None

    # 2. 채널 정보
    def get_channel_name(self):
        try:
            row = self.table.currentRow()
            return self.table.item(row, 2).text() if row >= 0 else None
        except:
            return None

    def get_subs(self):
        try:
            row = self.table.currentRow()
            return self.video_data[row]['subscriberCount'] if row >= 0 else None
        except:
            return None

    def get_total_videos(self):
        try:
            row = self.table.currentRow()
            channel_id = self.video_data[row]['channelId']
            return self.channel_stats.get(channel_id, {}).get('videoCount')
        except:
            return None

    # 3. 분석 데이터
    def get_contribution(self):
        try:
            row = self.table.currentRow()
            return self.table.item(row, 7).text() if row >= 0 else None
        except:
            return None

    def get_performance(self):
        try:
            row = self.table.currentRow()
            return self.table.item(row, 8).text() if row >= 0 else None
        except:
            return None

    def get_cii(self):
        try:
            row = self.table.currentRow()
            return self.table.item(row, 9).text() if row >= 0 else None
        except:
            return None

    def get_engagement(self):
        try:
            row = self.table.currentRow()
            return self.calculate_engagement(row) if row >= 0 else None
        except:
            return None

    # 4. 댓글 데이터
    def get_best_comments(self):
        try:
            row = self.table.currentRow()
            video_id = self.video_data[row]['videoId']
            return self.comment_cache.get(video_id, [])
        except:
            return []

    def get_all_comments(self):
        try:
            row = self.table.currentRow()
            video_id = self.video_data[row]['videoId']
            return self.fetch_all_comments(video_id)
        except:
            return []

    # 5. 자막 데이터
    def get_subtitles(self):
        try:
            row = self.table.currentRow()
            video_id = self.video_data[row]['videoId']
            return self.subtitle_cache.get(video_id, "")
        except:
            return ""

    # 6. 채널 상세 정보
    def get_channel_description(self):
        try:
            row = self.table.currentRow()
            channel_id = self.video_data[row]['channelId']
            return self.channel_stats.get(channel_id, {}).get('description')
        except:
            return None

    def get_channel_views(self):
        try:
            row = self.table.currentRow()
            channel_id = self.video_data[row]['channelId']
            return self.channel_stats.get(channel_id, {}).get('viewCount')
        except:
            return None

    def get_channel_join_date(self):
        try:
            row = self.table.currentRow()
            channel_id = self.video_data[row]['channelId']
            return self.channel_stats.get(channel_id, {}).get('publishedAt')
        except:
            return None

    def get_monthly_earnings(self):
        try:
            row = self.table.currentRow()
            return self.calculate_monthly_earnings(row) if row >= 0 else None
        except:
            return None

    def get_monthly_views(self):
        try:
            row = self.table.currentRow()
            return self.calculate_monthly_views(row) if row >= 0 else None
        except:
            return None

    def get_average_views(self):
        try:
            row = self.table.currentRow()
            channel_id = self.video_data[row]['channelId']
            return self.channel_stats.get(channel_id, {}).get('averageViews')
        except:
            return None

    def get_top_videos(self):
        try:
            row = self.table.currentRow()
            channel_id = self.video_data[row]['channelId']
            return self.channel_stats.get(channel_id, {}).get('topVideos', [])
        except:
            return []

    def get_channel_tags(self):
        try:
            row = self.table.currentRow()
            channel_id = self.video_data[row]['channelId']
            return self.channel_stats.get(channel_id, {}).get('tags', [])
        except:
            return []

    def get_channel_links(self):
        try:
            row = self.table.currentRow()
            channel_id = self.video_data[row]['channelId']
            return self.channel_stats.get(channel_id, {}).get('links', [])
        except:
            return []

    def get_channel_banner(self):
        try:
            row = self.table.currentRow()
            channel_id = self.video_data[row]['channelId']
            return self.channel_stats.get(channel_id, {}).get('bannerUrl')
        except:
            return None

    def get_channel_profile(self):
        try:
            row = self.table.currentRow()
            channel_id = self.video_data[row]['channelId']
            return self.channel_stats.get(channel_id, {}).get('profileUrl')
        except:
            return None

    # 7. 보관 상태
    def is_saved(self):
        try:
            row = self.table.currentRow()
            video_id = self.video_data[row]['videoId']
            return video_id in self.saved_videos
        except:
            return False
    
    def __init__(self):
        super().__init__()
        self.undo_stack = []
        self.downloading_type = None
        self.download_workers = []
        self.credentials = None
        self.token_file = 'token.pickle'
        self.selected_urls = []
        # 다크모드 호환성 스타일 적용
        self.apply_compatibility_styles()
        
        # 1. 인증 매니저 먼저 초기화 (필수)
        self.auth_manager = AuthManager()
        
        # 2. auth_info.json 확인 및 인증키 입력 처리 (필수)
        if (not os.path.exists('auth_info.json')) or (not self.auth_manager.is_authenticated()):
            key, ok = QInputDialog.getText(
                self, 
                '인증키 입력', 
                '프로그램을 사용하려면 인증키가 필요합니다.\n인증키를 입력해주세요:',
                QLineEdit.EchoMode.Normal
            )
            if not ok or not key:
                sys.exit()
            self.validate_and_set_auth_key(key)
        
        # 3. 만료 임박 확인 (필수)
        expiry_date_str = self.auth_manager.get_expiry_date()
        if expiry_date_str:
            try:
                expiry_date = datetime.fromisoformat(expiry_date_str).date()
                current_date = datetime.now().date()
                days_left = (expiry_date - current_date).days
                
                if 0 < days_left <= 7:
                    self._show_expiry_dialog(days_left)
                    
                # 타이틀 설정
                title = f"Tube Lens - 만료일: {expiry_date_str[:10]} (남은 기간: {days_left}일)"
                self.setWindowTitle(title)
                self.setStyleSheet("QDialog { background-color: #f5f5f5; } QLabel { color: black; }")
            except Exception as e:
                print(f"만료일 확인 중 오류: {str(e)}")

        # 4. 나머지 초기화는 지연 로드
        QTimer.singleShot(0, self._delayed_init)
        
        # 5. UI 초기화
        self.init_ui()
        
        # 프로그램 아이콘 설정
        try:
            app_icon = QIcon(get_resource_path("images/tubelens.png"))
            self.setWindowIcon(app_icon)
        except Exception as e:
            print(f"아이콘 로딩 오류: {str(e)}")

    def apply_compatibility_styles(self):
        """다크모드 호환성을 위한 스타일 적용"""
        compatibility_style = """
            QMessageBox {
                background-color: #f5f5f5;
                color: #333333;
            }
            QMessageBox QLabel {
                color: #333333;
            }
            QMessageBox QPushButton {
                background-color: #4a9eff;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QMenu {
                background-color: white;
                color: black;
            }
            QMenu::item {
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #4a9eff;
                color: white;
            }
            QToolTip {
                background-color: #f0f0f0;
                color: black;
                border: 1px solid #767676;
            }
            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #cccccc;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #4a9eff;
                selection-color: white;
            }
        """
        self.setStyleSheet(compatibility_style)

    def _delayed_init(self):
        # API 매니저 초기화
        self.api_manager = APIKeyManager()
        self.gemini_api_manager = GeminiAPIKeyManager()
        
        # 지연 로딩 관리자 초기화 
        self.lazy_load_manager = LazyLoadManager()

        # 비디오 링크 초기화
        self.video_links = get_video_links()
        
        
        
    
    
    def get_youtube_service(self):
        SCOPES = [
            'https://www.googleapis.com/auth/youtube.readonly',
            
            'https://www.googleapis.com/auth/youtube.force-ssl'
        ]
        
        logging.info("YouTube API 서비스 연결 시도")
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secrets.json',
                        SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            youtube = build('youtube', 'v3', credentials=self.credentials)
            logging.info("YouTube API 서비스 인증 성공")
            return youtube
            
        except Exception as e:
            logging.error(f"""
    YouTube API 서비스 인증 실패:
    오류 메시지: {str(e)}
    Credentials 상태: {'있음' if self.credentials else '없음'}
    Token 파일 존재: {os.path.exists(self.token_file)}
    """)
            return None

class TitleMakerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.selected_videos = []
        self.analyzed_data = {}
        
        # 고급 설정 기본값 정의
        self.advanced_settings = {
            'tone': '신뢰감 있는',
            'age': '전연령',            
            'structure': '이모티콘 + 핵심키워드 + 호기심유발',
            'banned_words': ''
        }
        
        # trends_text 속성 초기화
        self.trends_text = QTextEdit()
        self.trends_text.setReadOnly(True)
        
        # 선택된 영상들 데이터 수집
        self.collect_selected_videos()
        
        # UI 초기화
        self.setup_ui()
    
    def setup_ui(self):
        """UI 초기화 - 프리미엄 디자인"""
        # trends_text 속성 초기화
        self.trends_text = QTextEdit()
        self.trends_text.setReadOnly(True)
        
        self.setWindowTitle("✨ 타이틀 메이커")
        self.setMinimumSize(900, 750)  # 너비를 1000에서 900으로 줄임
        
        # 창을 화면 중앙에 배치
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(
            (screen.width() - 1000) // 2,
            (screen.height() - 750) // 2,
            1000, 750
        )
        
        # 고급 스타일시트 설정
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                color: #333333;
            }
            QLabel {
                color: #333333;
                font-size: 13px;
            }
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #1976d2;
                border: none;
                margin-top: 10px;
                padding: 10px;
                background-color: white;
            }
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 10px;
                color: #333333;
                font-size: 14px;
                selection-background-color: #bbdefb;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 2px solid #4a9eff;
            }
            QTextEdit {
                background-color: #f8f9fa;
                line-height: 1.5;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f0f0f0;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #bbdefb;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a9eff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 헤더 영역 - 현대적인 디자인
        header_container = QWidget()
        header_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(15)
        
        # 아이콘과 타이틀 
        title_icon = QLabel("✨")
        title_icon.setStyleSheet("font-size: 32px; color: gold;")
        
        title_content = QWidget()
        title_layout = QVBoxLayout(title_content)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        title_label = QLabel("타이틀 메이커")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1976d2;")
        
        description_label = QLabel("선택한 영상들을 분석하여 최적의 제목을 추천해드립니다.")
        description_label.setStyleSheet("font-size: 14px; color: #555; margin-top: 5px;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(description_label)
        
        # 통계 정보 (세로 배치로 변경)
        stats_container = QWidget()
        stats_container.setStyleSheet("background-color: transparent;")
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setContentsMargins(5, 0, 5, 0)
        stats_layout.setSpacing(3)

        # 분석 영상 정보
        video_count_info = QWidget()
        video_count_layout = QHBoxLayout(video_count_info)
        video_count_layout.setContentsMargins(0, 0, 0, 0)
        video_count_layout.setSpacing(5)

        video_count_label = QLabel("분석 영상:")
        video_count_label.setStyleSheet("color: #555; font-size: 12px;")

        self.video_count_label = QLabel("0개")
        self.video_count_label.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #1976d2;
            background-color: #e3f2fd;
            padding: 3px 10px;
            border-radius: 10px;
        """)

        video_count_layout.addWidget(video_count_label)
        video_count_layout.addWidget(self.video_count_label)
        video_count_layout.addStretch()

        # 평균 조회수 정보
        avg_views_info = QWidget()
        avg_views_layout = QHBoxLayout(avg_views_info)
        avg_views_layout.setContentsMargins(0, 0, 0, 0)
        avg_views_layout.setSpacing(5)

        avg_views_label = QLabel("평균 조회수:")
        avg_views_label.setStyleSheet("color: #555; font-size: 12px;")

        self.avg_views_label = QLabel("0회")
        self.avg_views_label.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #2e7d32;
            background-color: #e8f5e9;
            padding: 3px 10px;
            border-radius: 10px;
        """)

        avg_views_layout.addWidget(avg_views_label)
        avg_views_layout.addWidget(self.avg_views_label)
        avg_views_layout.addStretch()

        # 레이아웃에 추가
        stats_layout.addWidget(video_count_info)
        stats_layout.addWidget(avg_views_info)

        header_layout.addWidget(title_icon)
        header_layout.addWidget(title_content, 1)
        header_layout.addWidget(stats_container)
        
        main_layout.addWidget(header_container)
        
        # 스크롤 영역 (메인 컨텐츠)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # 가로 배치 섹션 (키워드 분석, 영상 태그, 연관 태그)
        horizontal_sections_container = QWidget()
        horizontal_layout = QHBoxLayout(horizontal_sections_container)
        horizontal_layout.setSpacing(8)  # 섹션 간 간격 더 줄임
        horizontal_layout.setContentsMargins(0, 0, 0, 0)

        # 공통 스타일 설정
        section_style = """
            QWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """

        # 헤더 스타일 (각 섹션마다 다른 배경색 사용)
        keyword_header_style = """
            font-size: 13px;
            font-weight: bold;
            color: #ffffff;
            background-color: #64b5f6;  /* 파스텔 파란색 */
            padding: 6px 10px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin: 0;
        """

        video_tag_header_style = """
            font-size: 13px;
            font-weight: bold;
            color: #ffffff;
            background-color: #81c784;  /* 파스텔 녹색 */
            padding: 6px 10px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin: 0;
        """

        related_tag_header_style = """
            font-size: 13px;
            font-weight: bold;
            color: #ffffff;
            background-color: #ffb74d;  /* 파스텔 주황색 */
            padding: 6px 10px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin: 0;
        """

        textedit_style = """
            border: none;
            background-color: #f9f9f9;
            border-radius: 5px;
            padding: 5px;
            font-size: 12px;
        """

        # 1. 키워드 분석 섹션
        keywords_section = QWidget()
        keywords_section.setStyleSheet(section_style)
        keywords_layout = QVBoxLayout(keywords_section)
        keywords_layout.setContentsMargins(10, 10, 10, 10)
        keywords_layout.setSpacing(5)

        keywords_header = QLabel("🔍 제목 핵심 키워드 TOP 10")
        keywords_header.setStyleSheet(keyword_header_style)
        keywords_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_keywords_label = QTextEdit()
        self.title_keywords_label.setReadOnly(True)
        self.title_keywords_label.setPlaceholderText("아직 분석되지 않음")
        self.title_keywords_label.setStyleSheet(textedit_style)
        self.title_keywords_label.setFixedHeight(200)  # 높이 증가

        keywords_layout.addWidget(keywords_header)
        keywords_layout.addWidget(self.title_keywords_label)

        # 2. 태그 섹션 (영상 내 태그)
        tags_section = QWidget()
        tags_section.setStyleSheet(section_style)
        tags_layout = QVBoxLayout(tags_section)
        tags_layout.setContentsMargins(10, 10, 10, 10)
        tags_layout.setSpacing(5)

        tags_header = QLabel("🏷️ 영상 내 태그 순위")
        tags_header.setStyleSheet(video_tag_header_style)
        tags_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.video_tags_label = QTextEdit()
        self.video_tags_label.setReadOnly(True)
        self.video_tags_label.setPlaceholderText("아직 분석되지 않음")
        self.video_tags_label.setStyleSheet(textedit_style)
        self.video_tags_label.setFixedHeight(200)  # 높이 증가

        tags_layout.addWidget(tags_header)
        tags_layout.addWidget(self.video_tags_label)

        # 3. 연관 태그 섹션
        related_tags_section = QWidget()
        related_tags_section.setStyleSheet(section_style)
        related_tags_layout = QVBoxLayout(related_tags_section)
        related_tags_layout.setContentsMargins(10, 10, 10, 10)
        related_tags_layout.setSpacing(5)

        related_tags_header = QLabel("🔗 연관 태그")
        related_tags_header.setStyleSheet(related_tag_header_style)
        related_tags_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.related_tags_label = QTextEdit()
        self.related_tags_label.setReadOnly(True)
        self.related_tags_label.setPlaceholderText("아직 분석되지 않음")
        self.related_tags_label.setStyleSheet(textedit_style)
        self.related_tags_label.setFixedHeight(200)  # 높이 증가

        # 태그 복사 버튼
        self.copy_all_tags_btn = QPushButton("📋 전체 태그 복사")
        self.copy_all_tags_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
                padding: 3px 8px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.copy_all_tags_btn.clicked.connect(self.copy_all_tags)

        related_tags_layout.addWidget(related_tags_header)
        related_tags_layout.addWidget(self.related_tags_label)
        related_tags_layout.addWidget(self.copy_all_tags_btn, 0, Qt.AlignmentFlag.AlignRight)

        # 세 섹션을 수평 레이아웃에 추가 (동일한 크기)
        horizontal_layout.addWidget(keywords_section, 1)  # 가중치 1
        horizontal_layout.addWidget(tags_section, 1)      # 가중치 1
        horizontal_layout.addWidget(related_tags_section, 1)  # 가중치 1
        
        # 제목 생성 섹션
        title_generator_section = QWidget()
        title_generator_section.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
        """)
        title_generator_layout = QVBoxLayout(title_generator_section)
        title_generator_layout.setContentsMargins(15, 15, 15, 15)
        title_generator_layout.setSpacing(10)
        
        title_generator_header = QLabel("✨ 제목 생성")
        title_generator_header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #1976d2;
            padding-bottom: 5px;
            border-bottom: 2px solid #e3f2fd;
        """)
        
        # 영상 주제 입력
        topic_label = QLabel("영상 주제를 입력해주세요 (자세할수록 더 좋은 제목이 생성됩니다)")
        topic_label.setStyleSheet("font-size: 13px; color: #555; margin-top: 5px;")
        
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("예) 초보자도 쉽게 따라할 수 있는 홈트레이닝 루틴")
        self.topic_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bbdefb;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4a9eff;
            }
        """)
        self.topic_input.setMinimumHeight(40)
        self.topic_input.returnPressed.connect(self.generate_title)
        
        # 제어 버튼 영역
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 5, 0, 5)
        buttons_layout.setSpacing(10)

        # 제목 생성 버튼 (프리미엄 디자인)
        self.generate_btn = QPushButton("✨ 제목 생성하기")
        self.generate_btn.clicked.connect(self.generate_title)
        self.generate_btn.setFixedSize(130, 34)  # 크기 조정
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5252;
                color: white;
                border: none;
                border-radius: 17px;  /* 버튼 높이의 절반으로 설정하여 완전한 라운드 모양 */
                font-size: 12px;
                font-weight: bold;
                text-align: center;
                letter-spacing: 0.5px;
                padding: 0 16px;  /* 내부 여백을 좌우로만 설정 */
            }
            QPushButton:hover {
                background-color: #FF1744;
            }
            QPushButton:pressed {
                background-color: #D50000;  /* 클릭 시 더 어두운 색상 */
            }
        """)

        # 고급 설정 버튼 (프리미엄 디자인)
        self.advanced_btn = QPushButton("⚙️ 고급 설정")
        self.advanced_btn.clicked.connect(self.show_advanced_settings)
        self.advanced_btn.setFixedSize(110, 34)  # 크기 조정
        self.advanced_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;  /* 세련된 청회색 */
                color: white;
                border: none;
                border-radius: 17px;  /* 버튼 높이의 절반으로 설정하여 완전한 라운드 모양 */
                font-size: 12px;
                font-weight: bold;
                text-align: center;
                letter-spacing: 0.5px;
                padding: 0 16px;  /* 내부 여백을 좌우로만 설정 */
            }
            QPushButton:hover {
                background-color: #455A64;
            }
            QPushButton:pressed {
                background-color: #37474F;  /* 클릭 시 더 어두운 색상 */
            }
        """)

        buttons_layout.addWidget(self.generate_btn)
        buttons_layout.addWidget(self.advanced_btn)
        
        # 생성된 제목 영역
        title_results_label = QLabel("생성된 제목")
        title_results_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #1976d2;
            margin-top: 10px;
        """)
        
        # 제목 결과 표시 영역
        self.results_area = QWidget()
        self.results_area_layout = QVBoxLayout(self.results_area)
        self.results_area_layout.setSpacing(10)
        self.results_area_layout.setContentsMargins(0, 0, 0, 0)
        
        # 결과가 없을 때 표시할 메시지
        self.no_results_label = QLabel("제목을 생성하면 여기에 표시됩니다.")
        self.no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_results_label.setStyleSheet("""
            font-size: 14px;
            color: #757575;
            padding: 20px;
            background-color: #f5f8fa;
            border-radius: 8px;
            margin: 10px 0;
        """)
        self.results_area_layout.addWidget(self.no_results_label)
        
        # tabs 초기화
        self.tabs = QTabWidget()
        # 트렌드 분석 탭 추가
        trends_tab = QWidget()
        trends_layout = QVBoxLayout(trends_tab)
        trends_layout.addWidget(self.trends_text)
        self.tabs.addTab(trends_tab, "시청자 트렌드")
        
        # 상태 표시 영역
        status_bar = QWidget()
        status_bar_layout = QHBoxLayout(status_bar)
        status_bar_layout.setContentsMargins(0, 5, 0, 0)
        status_bar_layout.setSpacing(10)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            color: #1976d2;
            font-weight: bold;
            font-size: 13px;
            padding: 5px;
        """)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        
        status_bar_layout.addWidget(self.status_label)
        status_bar_layout.addWidget(self.progress_bar)
        status_bar_layout.addStretch()
        
        # 모든 섹션을 메인 레이아웃에 추가
        title_generator_layout.addWidget(title_generator_header)
        title_generator_layout.addWidget(topic_label)
        title_generator_layout.addWidget(self.topic_input)
        title_generator_layout.addWidget(buttons_container)
        title_generator_layout.addWidget(title_results_label)
        title_generator_layout.addWidget(self.results_area)
        title_generator_layout.addWidget(status_bar)
        
        # 스크롤 영역에 모든 섹션 추가 (가로 배치된 섹션과 제목 생성 섹션)
        scroll_layout.addWidget(horizontal_sections_container)
        scroll_layout.addWidget(title_generator_section)
        
        # 스크롤 영역 설정
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # 하단 버튼 (프리미엄 디자인)
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.close)
        close_btn.setFixedSize(100, 34)  # 크기 설정
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #78909C;  /* 세련된 청회색 */
                color: white;
                border: none;
                border-radius: 17px;  /* 완전한 라운드 모양 */
                font-size: 13px;
                font-weight: bold;
                text-align: center;
                letter-spacing: 0.5px;
                padding: 0 16px;  /* 내부 여백을 좌우로만 설정 */
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
            QPushButton:pressed {
                background-color: #455A64;  /* 클릭 시 더 어두운 색상 */
            }
        """)
        
        close_container = QWidget()
        close_layout = QHBoxLayout(close_container)
        close_layout.setContentsMargins(0, 0, 0, 0)
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        
        main_layout.addWidget(close_container)
        
        # 초기 데이터 분석 수행
        self.analyze_data()
    
    def collect_selected_videos(self):
        """메인 창에서 선택된 영상 데이터 수집"""
        self.selected_videos = []
        main_window = self.parent
        
        # 메인 윈도우에서 선택된 영상들의 데이터 수집
        for row in range(main_window.table.rowCount()):
            item = main_window.table.item(row, 0)  # N열 체크
            if item and item.background().color() == QColor("#FF5D5D"):
                if row < len(main_window.search_results):
                    data = main_window.search_results[row]
                    # 검색어도 함께 저장
                    search_data = {
                        'title': data['title'],
                        'description': data.get('description', ''),
                        'views': int(data['view_count']),
                        'search_keyword': main_window.search_input.text() if hasattr(main_window, 'search_input') else ''
                    }
                    self.selected_videos.append(search_data)
    
    def analyze_data(self):
        """수집된 영상 데이터 분석"""
        if not self.selected_videos:
            return
        
        video_count = len(self.selected_videos)
        self.video_count_label.setText(f"{video_count}개")
        
        try:
            # 평균 조회수 계산 및 표시
            total_views = sum(video['views'] for video in self.selected_videos)
            avg_views = total_views // video_count
            self.avg_views_label.setText(f"{avg_views:,}회")
            
            # 제목 키워드 분석
            title_keywords = self.analyze_keywords([v['title'] for v in self.selected_videos])
            title_keywords_text = "\n".join([f"🔍 {kw} ({cnt}회)" for kw, cnt in title_keywords])
            self.title_keywords_label.setText(title_keywords_text)
            
            # 태그 분석 결과 가져오기
            tags_data = self.analyze_tags(self.selected_videos)
            
            # 영상 내 태그 순위 표시
            video_tags_text = "\n".join([f"{tag} ({count}회)" for tag, count in tags_data['frequency']])
            self.video_tags_label.setText(video_tags_text)
            
            # 연관 태그 표시
            related_tags_text = "\n".join(tags_data['related'])
            self.related_tags_label.setText(related_tags_text)
            
        except Exception as e:
            print(f"데이터 분석 중 오류 발생: {str(e)}")
    
    def analyze_keywords(self, texts):
        """텍스트 목록에서 주요 키워드 추출"""
        from collections import Counter
        import re
        
        # 불용어 정의 - 조사, 어미, 의미없는 단어들
        stop_words = {
            '있다', '없다', '되다', '이다', '하다', '같다', '때', '및', '이', '그', '저',
            '것', '들', '등', '을', '를', '이런', '그런', '와', '과', '에', '더', '왜',
            '가지', '하기', '하는', '된다', '하면', '해서', '에서', '으로', '만의', '위한',
            '중', '후', '전', '말', '내', '집', '요즘', '끝', '답'
        }
        
        # 해시태그 제외하고 텍스트 결합
        combined_text = ' '.join([text for text in texts if not text.startswith('#')])
        # 텍스트 중간의 해시태그도 제거
        combined_text = re.sub(r'#\w+', '', combined_text)
        keywords = []
        
        # 1. 숫자+단위 키워드 추출 (예: "3가지", "5단계" 등)
        number_unit_matches = re.finditer(r'\d+[가지|단계|위|등|번|개|년|분|시간|일|주]+', combined_text)
        for match in number_unit_matches:
            keywords.append(match.group())
        
        # 2. 일반 단어 추출 (2글자 이상)
        words = re.findall(r'[가-힣]{2,}|[a-zA-Z]{2,}', combined_text)
        filtered_words = [w for w in words if w not in stop_words]
        
        # 숫자+단위 키워드와 일반 단어를 합쳐서 카운트
        all_keywords = keywords + filtered_words    
        word_counts = Counter(all_keywords)
        
        # 빈도수 2회 이상 & 상위 10개 반환
        return [(word, count) for word, count in word_counts.most_common(10) if count >= 2]
    
    def analyze_tags(self, videos_data):
        """제목과 설명에서 실제 해시태그 추출"""
        from collections import Counter
        import re
        
        # 실제 해시태그만 추출 (제목과 설명)
        hashtags = []
        search_keyword = ""  # 검색 키워드 저장용
        
        for idx, data in enumerate(videos_data):
            if idx == 0:  # 첫 번째 데이터의 원본 검색어 저장
                search_keyword = data.get('search_keyword', '')
                
            if 'title' in data:
                tags = re.findall(r'#[^\s#]+', data['title'])
                hashtags.extend(tags)
                
            if 'description' in data:
                desc_tags = re.findall(r'#[^\s#]+', data['description'])
                hashtags.extend(desc_tags)
        
        hashtags = [tag for tag in hashtags if len(tag) > 1]  # '#' 만 있는 경우 제외
        
        # 빈도수 계산 및 정렬
        tag_counts = Counter(hashtags)
        frequency_tags = tag_counts.most_common(10)  # 상위 10개
        
        # 유튜브 연관 검색어 가져오기
        try:
            # 원본 검색어로 연관 검색어 가져오기
            if search_keyword:
                related_tags = self.get_youtube_suggestions(search_keyword)
            else:
                # 검색어가 없으면 가장 많이 나온 해시태그에서 # 제외하고 검색
                if frequency_tags:
                    most_common_tag = frequency_tags[0][0].replace('#', '')
                    related_tags = self.get_youtube_suggestions(most_common_tag)
                else:
                    related_tags = []
                    
        except Exception as e:
            print(f"연관 검색어 가져오기 실패: {str(e)}")
            related_tags = []
        
        return {
            'frequency': frequency_tags,
            'related': related_tags
        }
    
    def get_youtube_suggestions(self, keyword):
        """YouTube 검색어 자동완성 데이터 가져오기"""
        try:
            import urllib.request
            import urllib.parse
            import json
            
            # 검색어 전처리 (공백 및 특수문자 처리)
            keyword = keyword.strip()
            
            # 검색어 인코딩
            encoded_query = urllib.parse.quote(keyword)
            
            # YouTube 자동완성 API 호출
            url = f"http://suggestqueries.google.com/complete/search?client=youtube&ds=yt&client=firefox&q={encoded_query}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            request = urllib.request.Request(url, headers=headers)
            
            response = urllib.request.urlopen(request)
            data = response.read().decode('utf-8')
            suggestions = json.loads(data)[1]  # 두 번째 요소가 추천 검색어 리스트
            
            # 태그 형식으로 변환
            return [f"#{suggestion}" for suggestion in suggestions if suggestion != keyword][:10]            
       
        except Exception as e:
            print(f"자동완성 데이터 가져오기 실패: {str(e)}")
            return []
    
    def copy_all_tags(self):
        """모든 섹션의 태그 복사 (# 제거, 콤마로 구분)"""
        try:
            # 영상 내 빈도 태그와 연관 태그 모두 가져오기
            frequency_tags = self.video_tags_label.toPlainText()
            related_tags = self.related_tags_label.toPlainText()
            
            # 태그 추출
            tags = []
            
            # 영상 내 빈도 태그 처리
            for line in frequency_tags.split('\n'):
                if '(' in line:  # 빈도수 정보가 있는 경우
                    tag = line.split('(')[0].strip()
                    if tag.startswith('#'):
                        # '#' 제거하고 추가
                        tags.append(tag[1:])
            
            # 연관 태그 처리
            for line in related_tags.split('\n'):
                if line.startswith('#'):
                    # '#' 제거하고 추가
                    tags.append(line.strip()[1:])
            
            if tags:
                # 중복 제거
                unique_tags = list(dict.fromkeys(tags))
                # 콤마와 공백으로 구분
                all_tags = ', '.join(unique_tags)
                
                QApplication.clipboard().setText(all_tags)
                
                # 복사 완료 표시
                self.status_label.setText("태그가 클립보드에 복사되었습니다!")
                QTimer.singleShot(2000, lambda: self.status_label.setText(""))
                
        except Exception as e:
            print(f"태그 복사 중 오류 발생: {str(e)}")
            self.status_label.setText("태그 복사 중 오류가 발생했습니다.")
            QTimer.singleShot(2000, lambda: self.status_label.setText(""))
    
    def show_advanced_settings(self):
        """고급 설정 다이얼로그 표시"""
        dialog = QDialog(self)
        dialog.setWindowTitle("고급 설정")
        dialog.setFixedSize(500, 520)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-size: 14px;
                color: #1976d2;
                border: 1px solid #bbdefb;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
                background-color: white;
            }
            QLabel {
                color: #333333;
                font-size: 13px;
            }
            QLineEdit, QComboBox {
                background-color: white;
                border: 1px solid #bbdefb;
                border-radius: 5px;
                padding: 8px;
                color: #333333;
                min-height: 20px;
            }
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #ff4da6;
            }
            QPushButton[text="취소"] {
                background-color: #757575;
            }
            QPushButton[text="취소"]:hover {
                background-color: #616161;
            }
        """)

        # 메인 레이아웃
        main_layout = QVBoxLayout(dialog)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 1. 톤앤매너 설정
        tone_group = QGroupBox("톤앤매너")
        tone_layout = QVBoxLayout(tone_group)
        
        self.tone_combo = QComboBox()
        self.tone_combo.addItems([
            "신뢰감 있는",
            "전문적인", 
            "친근한",
            "충격적인",
            "호기심 자극"
        ])
        self.tone_combo.setCurrentText(self.advanced_settings.get('tone', '신뢰감 있는'))
        tone_layout.addWidget(self.tone_combo)

        # 2. 타겟 시청자 설정 
        target_group = QGroupBox("타겟 시청자")
        target_layout = QVBoxLayout(target_group)
        
        self.age_combo = QComboBox()
        self.age_combo.addItems([
            "10대",
            "20대",
            "30대", 
            "40대 이상",
            "전연령"
        ])
        self.age_combo.setCurrentText(self.advanced_settings.get('age', '전연령'))
        target_layout.addWidget(self.age_combo)

        # 3. 제목 구조 설정
        structure_group = QGroupBox("제목 구조")
        structure_layout = QVBoxLayout(structure_group)
        
        self.structure_combo = QComboBox()
        self.structure_combo.addItems([
            "이모티콘 + 핵심키워드 + 호기심유발 (기본)",
            "HOW TO + 혜택 + 키워드 (예: 하루 만에 배우는 엑셀 실무)",
            "TOP N + 키워드 + 혜택 (예: 40대가 꼭 먹어야 할 5가지 음식)",
            "문제 + 솔루션 + 차별점 (예: 목아픈데 병원갈 시간이 없다면?)",
            "비교 + 핵심키워드 + 결론 (예: 아이폰15 vs 갤럭시23 최종결론)", 
            "즉각효과 + 방법 + 검증 (예: 유튜브 전문가가 알려주는 30초 꿀팁)"
        ])
        self.structure_combo.setCurrentText(self.advanced_settings.get('structure', '이모티콘 + 핵심키워드 + 호기심유발'))
        structure_layout.addWidget(self.structure_combo)

        # 4. 금지어 설정
        banned_group = QGroupBox("금지어 설정")
        banned_layout = QVBoxLayout(banned_group)
        
        banned_description = QLabel("제목에 포함하지 않을 단어를 쉼표로 구분하여 입력하세요.")
        banned_layout.addWidget(banned_description)
        
        self.banned_input = QLineEdit()
        self.banned_input.setPlaceholderText("예: 충격, 경악, 놀라운")
        self.banned_input.setText(self.advanced_settings.get('banned_words', ''))
        banned_layout.addWidget(self.banned_input)

        # 모든 그룹박스를 메인 레이아웃에 추가
        main_layout.addWidget(tone_group)
        main_layout.addWidget(target_group)
        main_layout.addWidget(structure_group)
        main_layout.addWidget(banned_group)

        # 버튼 영역
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        save_btn = QPushButton("저장")
        save_btn.clicked.connect(lambda: [self.save_advanced_settings(dialog), dialog.accept()])
        
        cancel_btn = QPushButton("취소")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        main_layout.addLayout(button_layout)

        dialog.exec()
    
    def save_advanced_settings(self, dialog=None):
        """고급 설정 저장"""
        try:
            if hasattr(self, 'tone_combo'):
                # 현재 설정 값 저장
                self.advanced_settings = {
                    'tone': self.tone_combo.currentText(),
                    'age': self.age_combo.currentText(),
                    'structure': self.structure_combo.currentText(),
                    'banned_words': self.banned_input.text()
                }
                
                self.status_label.setText("고급 설정이 저장되었습니다.")
                QTimer.singleShot(2000, lambda: self.status_label.setText(""))
                
        except Exception as e:
            print(f"고급 설정 저장 중 오류: {str(e)}")
            if dialog:
                QMessageBox.warning(
                    dialog,
                    "오류",
                    f"설정 저장 중 오류가 발생했습니다: {str(e)}"
                )
            else:
                self.status_label.setText("설정 저장 중 오류가 발생했습니다.")
                QTimer.singleShot(2000, lambda: self.status_label.setText(""))
    
    def generate_title(self):
        """AI를 사용하여 제목 생성"""
        # 입력값 확인
        topic = self.topic_input.text().strip()
        if not topic:
            QMessageBox.warning(self, "경고", "영상 주제를 입력해주세요!")
            return
        
        # 버튼 상태 변경 (로딩 표시)
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("제목 생성 중...")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5252;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.status_label.setText("제목 생성 중...")
        QApplication.processEvents()
        
        try:
            print("API 키 확인 중...")
            # API 키 확인
            api_key = None
            
            # 1. parent.gemini_api_manager에서 키 찾기
            if hasattr(self.parent, 'gemini_api_manager') and self.parent.gemini_api_manager:
                gemini_api_manager = self.parent.gemini_api_manager
                current_key = next((k for k in gemini_api_manager.keys if k.is_current), None)
                if current_key and current_key.status == 'active':
                    api_key = current_key.key
                    print(f"현재 선택된 API 키 사용: {current_key.last_five}")
            
            # 2. 없으면 settings.json에서 키 찾기
            if not api_key:
                try:
                    with open('settings.json', 'r') as f:
                        settings = json.load(f)
                        api_key = settings.get('google_ai_api_key')
                        if api_key:
                            print("settings.json에서 API 키 불러옴")
                except Exception as e:
                    print(f"settings.json 읽기 실패: {e}")
            
            # 3. 그래도 없으면 오류 메시지
            if not api_key:
                QMessageBox.warning(self, "경고", "유효한 Gemini API 키가 없습니다. 설정에서 API 키를 추가해주세요.")
                self.reset_ui_state()
                return
            
            # Gemini API 설정
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')
            
            # 프롬프트 구성
            self.progress_bar.setValue(20)
            QApplication.processEvents()
            
            title_keywords_text = self.title_keywords_label.toPlainText()
            video_tags_text = self.video_tags_label.toPlainText()
            related_tags_text = self.related_tags_label.toPlainText()
            
            prompt = f"""당신은 수백만 조회수를 기록하는 유튜브 제목 생성 전문가입니다.
            주어진 규칙을 모두 준수하면서, 아래 10가지 유형의 독창적인 제목을 생성해주세요.

            === 데이터 기반 패턴 분석 ===
            현재 트렌드 키워드: {title_keywords_text}
            영상 내 태그: {video_tags_text}
            연관 태그: {related_tags_text}

            === 필수 제목 규칙 ===
            - 글자수: 반드시 15~40자 이내로 작성
            - 말줄임표(...) 사용 금지
            - 주제 "{topic}"에 정확히 부합
            - 호기심 유발 요소 포함
            - 실제 콘텐츠 관련성 유지

            === 사용자 설정 ===
            - 톤앤매너: {self.advanced_settings['tone']}
            - 타겟 연령: {self.advanced_settings['age']}            
            - 제목 구조: {self.advanced_settings['structure']}
            - 금지어: {self.advanced_settings['banned_words'] if self.advanced_settings['banned_words'] else '없음'}

            각 유형별로 다음 형식으로 제목을 생성하세요:
            - 추천이유는 "반드시 공백포함 95자 이내"로 작성하세요.

            [일반형 제목]
            제목: (기본적이고 직관적인 제목)
            추천이유: (핵심 내용을 담은 깔끔한 설명)

            [극단적 반전 유형]
            제목: (예: "이거 왜 샀지...? 반응 보고 후회했습니다 (feat. 10만원짜리 선택)")
            추천이유: (극적인 반전 요소의 효과 설명)

            [자극적&도발 유형]
            제목: (예: "이거 안 사면 당신만 손해! 필수템 TOP3 (feat. 내돈내산 솔직 리뷰)")
            추천이유: (강력한 구매 욕구를 자극하는 포인트 설명)

            [궁금증 폭발 유형]
            제목: (예: "이 캣타워, 가격이 미쳤어요... 후기 보면 더 충격적입니다")
            추천이유: (궁금증을 최대한 자극하는 요소 설명)

            [강력추천형 제목]
            제목: (강력한 추천이 담긴 호소력있는 제목)
            추천이유: (최상급 표현의 근거 포인트 설명)

            [인생팁형 제목]
            제목: (인생의 중요한 조언을 담은 제목)
            추천이유: (실용적 조언의 가치 포인트 설명)

            [시간효율형 제목]
            제목: (빠른 해결책을 제시하는 제목)
            추천이유: (시간 절약 가치 포인트 설명)

            [검증실험형 제목]
            제목: (직접 검증한 실험 결과를 담은 제목)
            추천이유: (검증 과정의 신뢰도 포인트 설명)

            [비교분석형 제목]
            제목: (명확한 비교와 차이점을 담은 제목)
            추천이유: (비교 분석의 핵심 가치 설명)

            [꿀팁&정보]
            제목: (예: "고양이 용품 '잘' 고르는 법! 집사가 100번 실수하고 얻은 꿀팁 대방출")
            추천이유: (전문성과 실용적 정보 제공 포인트 설명)

            추가로 시청자 트렌드 분석도 함께 제공해주세요:
            
            [시청자 트렌드 분석]
            - 지금 시청자들이 가장 관심 있어하는 주제 (핵심만 간략히)
            - 시청자의 주요 질문 또는 요청사항 (반드시 3개 이상 작성)
            - 시청자가 가장 긍정적으로 반응하는 콘텐츠 특징 (간결하게)
            """
            
            # API 호출
            self.progress_bar.setValue(40)
            QApplication.processEvents()
            
            print("Gemini API 호출 시작")
            response = model.generate_content(prompt)
            response_text = response.text
            print(f"API 응답 성공: {len(response_text)} 글자")
            
            self.progress_bar.setValue(60)
            QApplication.processEvents()
            
            # 제목 추출 및 표시
            titles_data = []
            
            # 제목 형식 파싱
            response_lines = response_text.split('\n')
            current_title = None
            current_reason = None
            current_type = None
            
            for line in response_lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 유형 라인
                if line.startswith('[') and ']' in line:
                    # 이전 항목 저장
                    if current_title and current_reason:
                        titles_data.append({
                            'type': current_type,
                            'title': current_title,
                            'reason': current_reason
                        })
                        current_title = None
                        current_reason = None
                    
                    # 새 유형 시작
                    current_type = line.strip('[]')
                    
                elif line.startswith('제목:'):
                    if current_title and current_reason and current_type:
                        titles_data.append({
                            'type': current_type,
                            'title': current_title,
                            'reason': current_reason
                        })
                        
                    current_title = line.replace('제목:', '').strip()
                    current_reason = None
                    
                elif line.startswith('추천이유:'):
                    current_reason = line.replace('추천이유:', '').strip()
                    
                    # 항목 완성 - 저장
                    if current_title and current_reason and current_type:
                        titles_data.append({
                            'type': current_type,
                            'title': current_title,
                            'reason': current_reason
                        })
                        current_title = None
                        current_reason = None
            
            # 마지막 항목 추가
            if current_title and current_reason and current_type:
                titles_data.append({
                    'type': current_type,
                    'title': current_title,
                    'reason': current_reason
                })
            
            self.progress_bar.setValue(80)
            QApplication.processEvents()
            
            # 시청자 트렌드 분석 부분 처리
            trend_section = ""
            if "[시청자 트렌드 분석]" in response_text:
                trend_parts = response_text.split("[시청자 트렌드 분석]")
                if len(trend_parts) > 1:
                    trend_section = trend_parts[1].strip()
                    # 다음 섹션 제목이 있으면 그 앞까지만 추출
                    if "[" in trend_section:
                        trend_section = trend_section.split("[")[0].strip()
            
            print("트렌드 분석 내용:", trend_section[:100] + "..." if trend_section and len(trend_section) > 100 else "없음")
            
            # 결과 표시 (최대 10개)
            print(f"추출된 제목 수: {len(titles_data)}")
            if not titles_data:
                # 제목 파싱 실패 시 다른 방법으로 다시 시도
                print("제목 파싱 실패. 다른 방법으로 추출 시도...")
                # 정규식으로 제목 추출 시도
                import re
                title_matches = re.findall(r'제목:\s*(.+?)[\n\r]', response_text)
                reason_matches = re.findall(r'추천이유:\s*(.+?)[\n\r]', response_text)
                
                # 유형 추출 시도
                type_matches = re.findall(r'\[(.*?)\]', response_text)
                title_types = [t for t in type_matches if '제목' in t or '유형' in t]
                
                print(f"정규식 추출 결과: 제목 {len(title_matches)}개, 이유 {len(reason_matches)}개, 유형 {len(title_types)}개")
                
                # 추출 성공했으면 데이터 구성
                for i in range(min(len(title_matches), len(reason_matches))):
                    title_type = title_types[i] if i < len(title_types) else f"유형 {i+1}"
                    titles_data.append({
                        'type': title_type,
                        'title': title_matches[i],
                        'reason': reason_matches[i]
                    })
            
            # 부족한 경우 기본값으로 채우기
            while len(titles_data) < 10:
                titles_data.append({
                    'type': f"유형 {len(titles_data)+1}",
                    'title': '제목 생성에 실패했습니다',
                    'reason': '다시 시도해주세요'
                })
            
            # 결과 표시 (최대 10개)
            self.display_generated_titles(titles_data[:10])
            
            self.progress_bar.setValue(100)
            self.status_label.setText("제목 생성 완료!")
            
            # 알림음 재생
            try:
                import winsound
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            except:
                pass
                
            # 2초 후 상태 메시지와 프로그레스 바 숨기기
            QTimer.singleShot(2000, lambda: self.progress_bar.hide())
            QTimer.singleShot(2000, lambda: self.status_label.setText(""))
            
        except Exception as e:
            print(f"제목 생성 중 오류 발생: {str(e)}")
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                QMessageBox.warning(self, "API 할당량 초과", 
                    "API 키의 할당량이 초과되었습니다.\n"
                    "1. 설정에서 다른 API 키를 선택하거나\n"
                    "2. 잠시 후 다시 시도해주세요.")
            else:
                QMessageBox.critical(self, "오류", f"제목 생성 중 오류가 발생했습니다: {str(e)}")
            
            self.reset_ui_state()
        
        
    def reset_ui_state(self):
        """UI 상태 초기화"""
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("✨ 제목 생성하기")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5252;
                color: white;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #ff4da6;
            }
        """)
        self.progress_bar.hide()
        self.status_label.setText("")
    
    def display_generated_titles(self, titles_data):
        """생성된 제목 UI에 표시 - 프리미엄 디자인"""
        # 기존 위젯 모두 제거
        while self.results_area_layout.count():
            item = self.results_area_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 결과 스크롤 영역
        scroll_container = QScrollArea()
        scroll_container.setWidgetResizable(True)
        scroll_container.setFrameShape(QFrame.Shape.NoFrame)
        scroll_container.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f0f0f0;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #bbdefb;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a9eff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
        # 결과 컨테이너
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        results_layout.setSpacing(12)
        results_layout.setContentsMargins(0, 0, 0, 0)
        
        # 색상 팔레트 (세로 카드에 맞게 조정)
        colors = [
            {"bg": "#f3e5f5", "accent": "#9c27b0"},  # 보라색
            {"bg": "#e3f2fd", "accent": "#2196f3"},  # 파란색
            {"bg": "#e8f5e9", "accent": "#4caf50"},  # 초록색
            {"bg": "#fff3e0", "accent": "#ff9800"},  # 주황색
            {"bg": "#ffebee", "accent": "#f44336"}   # 빨간색
        ]
        
        # 타입 레이블
        type_labels = [
            "🎯 일반형", "💥 극단적 반전", "🔥 자극적&도발", "❓ 궁금증 폭발", 
            "⭐ 강력추천형", "💡 인생팁형", "⏰ 시간효율형", "🧪 검증실험형", 
            "🔍 비교분석형", "📚 꿀팁&정보"
        ]
        
        # 각 제목 카드 생성
        for i, title_info in enumerate(titles_data):
            if i >= 10:  # 최대 10개만 표시
                break
                
            color = colors[i % len(colors)]
            
            # 카드 컨테이너
            card = QWidget()
            card.setStyleSheet(f"""
                QWidget {{
                    background-color: white;
                    border-radius: 8px;
                    border-left: 4px solid {color["accent"]};
                }}
            """)
            
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 12, 15, 12)
            card_layout.setSpacing(8)
            
            # 제목 유형
            type_label = QLabel(type_labels[i] if i < len(type_labels) else f"유형 {i+1}")
            type_label.setStyleSheet(f"""
                font-size: 13px;
                font-weight: bold;
                color: {color["accent"]};
            """)
            
            # 제목 텍스트
            title_text = QLabel(title_info['title'])
            title_text.setWordWrap(True)
            title_text.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                padding: 5px 0;
            """)
            
            # 추천 이유
            reason_container = QWidget()
            reason_container.setStyleSheet(f"""
                background-color: {color["bg"]};
                border-radius: 5px;
            """)
            
            reason_layout = QVBoxLayout(reason_container)
            reason_layout.setContentsMargins(10, 8, 10, 8)
            reason_layout.setSpacing(3)
            
            reason_header = QLabel("💡 추천 이유")
            reason_header.setStyleSheet(f"""
                font-size: 12px;
                font-weight: bold;
                color: {color["accent"]};
            """)
            
            reason_text = QLabel(title_info['reason'])
            reason_text.setWordWrap(True)
            reason_text.setStyleSheet("""
                font-size: 12px;
                color: #333333;
                line-height: 1.3;
            """)
            
            reason_layout.addWidget(reason_header)
            reason_layout.addWidget(reason_text)
            
            # 복사 버튼
            copy_btn = QPushButton("복사")
            copy_btn.setFixedWidth(80)
            copy_btn.setFixedHeight(28)
            copy_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color["accent"]};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                    min-height: 28px;
                }}
                QPushButton:hover {{
                    opacity: 0.9;
                }}
            """)
            
            # 복사 기능
            def make_copy_function(button, text):
                def copy_text():
                    QApplication.clipboard().setText(text)
                    original_text = button.text()
                    button.setText("복사 완료!")
                    QTimer.singleShot(1500, lambda: button.setText(original_text))
                return copy_text
            
            copy_btn.clicked.connect(make_copy_function(copy_btn, title_info['title']))
            
            # 카드에 요소 추가
            card_layout.addWidget(type_label)
            card_layout.addWidget(title_text)
            card_layout.addWidget(reason_container)
            
            # 버튼 컨테이너 (오른쪽 정렬)
            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.addStretch()
            button_layout.addWidget(copy_btn)
            
            card_layout.addWidget(button_container)
            
            # 결과 영역에 카드 추가
            results_layout.addWidget(card)
        
        # 스크롤 영역 설정
        scroll_container.setWidget(results_widget)
        
        # 최대 높이 설정 (스크롤 가능하게)
        scroll_container.setMaximumHeight(500)
        
        # 결과 영역에 추가
        self.results_area_layout.addWidget(scroll_container)
    
          
                  
                  

def get_client_config():
    try:
        config_path = get_resource_path('client_secrets.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logging.error("client_secrets.json 파일을 찾을 수 없습니다.")
            QMessageBox.critical(None, "오류", "client_secrets.json 파일을 찾을 수 없습니다.\n프로그램 폴더에 파일이 있는지 확인해주세요.")
            return None
    except Exception as e:
        error_msg = str(e)
        logging.error(f"설정 파일 로드 중 오류: {error_msg}")
        QMessageBox.critical(None, "오류", f"설정 파일 읽기 오류: {error_msg}")
        return None

import subprocess 


class AuthManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthManager, cls).__new__(cls)
            cls._instance.auth_file = 'auth_info.json'
            cls._instance.token_file = 'token.json'  # 구글 토큰 파일 추가
            cls._instance.ntp_client = ntplib.NTPClient()
            cls._instance._load_auth_info()
            cls._instance._load_google_token()  # 구글 토큰 로드 추가
        return cls._instance

    def __init__(self):
        pass

    # 구글 토큰 관리 함수들 추가
    def _load_google_token(self):
        """구글 토큰 로드"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    self.google_token = json.load(f)
            else:
                self.google_token = None
        except Exception as e:
            print(f"토큰 로드 오류: {str(e)}")
            self.google_token = None

    def save_google_token(self, token_info):
        """구글 토큰 저장"""
        try:
            with open(self.token_file, 'w') as f:
                json.dump(token_info, f)
            self.google_token = token_info
        except Exception as e:
            print(f"토큰 저장 오류: {str(e)}")

    def clear_google_token(self):
        """구글 로그아웃"""
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
            self.google_token = None
        except Exception as e:
            print(f"토큰 삭제 오류: {str(e)}")

    def is_google_logged_in(self):
        """구글 로그인 상태 확인"""
        return self.google_token is not None
    
    def get_google_credentials(self):
        """구글 OAuth 자격증명 가져오기"""
        if not self.google_token:
            return None
        try:
            # 필요한 모든 스코프 정의
            required_scopes = [
                'https://www.googleapis.com/auth/youtube.readonly',
                'https://www.googleapis.com/auth/youtube.force-ssl'
            ]
            
            # 현재 스코프 가져오기
            current_scopes = self.google_token.get('scopes', [])
            
            # 필요한 스코프 추가
            for scope in required_scopes:
                if scope not in current_scopes:
                    current_scopes.append(scope)
            
            credentials = Credentials(
                token=self.google_token['token'],
                refresh_token=self.google_token['refresh_token'],
                token_uri=self.google_token['token_uri'],
                client_id=self.google_token['client_id'],
                client_secret=self.google_token['client_secret'],
                scopes=current_scopes  # 업데이트된 스코프 사용
            )

            # 토큰이 만료되었는지 확인하고 필요시 갱신
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                # 갱신된 토큰 저장
                self.save_google_token({
                    'token': credentials.token,
                    'refresh_token': credentials.refresh_token,
                    'token_uri': credentials.token_uri,
                    'client_id': credentials.client_id,
                    'client_secret': credentials.client_secret,
                    'scopes': current_scopes
                })

            return credentials
        except Exception as e:
            print(f"Credentials 생성 오류: {str(e)}")
            return None

    def __init__(self):
        # __new__에서 초기화하므로 여기서는 pass
        pass


    def generate_computer_id(self):
        try:
            # CPU ID
            cpu_info = os.popen('wmic cpu get ProcessorId').read()
            cpu_id = cpu_info.split('\n')[1].strip()
            
            # 메인보드 ID
            board_info = os.popen('wmic baseboard get SerialNumber').read()
            board_id = board_info.split('\n')[1].strip()
            
            # MAC 주소
            mac_info = os.popen('wmic nic where PhysicalAdapter=True get MACAddress').read()
            mac_addresses = [line.strip() for line in mac_info.split('\n') if line.strip() and 'MACAddress' not in line]
            mac_id = mac_addresses[0] if mac_addresses else "NO_MAC"
            
            # 모든 정보 조합
            combined = f"{cpu_id}_{board_id}_{mac_id}"
            
            # SHA-256 해시 생성
            return hashlib.sha256(combined.encode()).hexdigest()
        except Exception as e:
            print(f"컴퓨터 ID 생성 중 오류: {str(e)}")
            return "ERROR_GENERATING_ID"

    def _load_auth_info(self):
        try:
            # 저장된 라이센스 키 읽기
            try:
                with open(self.auth_file, 'r') as f:
                    data = json.load(f)
                    current_computer_id = self.generate_computer_id()
                    
                    # 기본 정보 로드
                    self.auth_info = {
                        'auth_key': data.get('auth_key'),
                        'signature': data.get('signature', '')
                    }
                    
                    # signature가 있으면 검증
                    if self.auth_info['signature']:
                        try:
                            # signature 복호화
                            stored_data = self.decrypt_signature(self.auth_info['signature'])
                            date_str, computer_id, license_key = stored_data.split('_')
                            
                            # 컴퓨터ID와 라이센스키 검증
                            if (computer_id != current_computer_id or 
                                license_key != self.auth_info['auth_key']):
                                self.auth_info['signature'] = ''  # 검증 실패시 초기화
                                
                        except Exception:
                            self.auth_info['signature'] = ''  # 복호화 실패시 초기화
                            
            except FileNotFoundError:
                self.auth_info = {'auth_key': None, 'signature': ''}
                self._save_auth_info()
                    
        except Exception as e:
            print(f"라이센스 정보 로드 중 오류: {str(e)}")
            self.auth_info = {'auth_key': None, 'signature': ''}

    def _save_auth_info(self):
        if self.auth_info['auth_key']:
            # 인증 정보가 있을 때만 signature 생성
            try:
                # 현재 시간 (NTP 서버에서 가져옴)
                current_time = self.get_network_time().strftime('%Y-%m-%d')
                computer_id = self.generate_computer_id()
                
                # signature 생성 및 암호화
                signature_data = f"{current_time}_{computer_id}_{self.auth_info['auth_key']}"
                self.auth_info['signature'] = self.encrypt_signature(signature_data)
                
            except Exception as e:
                print(f"Signature 생성 중 오류: {str(e)}")
                self.auth_info['signature'] = ''
        
        # 인증 정보 저장
        try:
            with open(self.auth_file, 'w') as f:
                # expiry_date는 저장하지 않음
                save_data = {
                    'auth_key': self.auth_info['auth_key'],
                    'signature': self.auth_info.get('signature', '')
                }
                json.dump(save_data, f)
        except Exception as e:
            print(f"인증 정보 저장 중 오류: {str(e)}")

    def encrypt_signature(self, data):
        try:
            # 암호화 키 생성 (컴퓨터ID의 해시값 사용)
            key = hashlib.sha256(self.generate_computer_id().encode()).digest()[:32]
            cipher = Fernet(base64.b64encode(key))
            return cipher.encrypt(data.encode()).decode()
        except Exception:
            return ''

    def decrypt_signature(self, encrypted_data):
        try:
            # 암호화 키 생성 (컴퓨터ID의 해시값 사용)
            key = hashlib.sha256(self.generate_computer_id().encode()).digest()[:32]
            cipher = Fernet(base64.b64encode(key))
            return cipher.decrypt(encrypted_data.encode()).decode()
        except Exception:
            return ''
        
    def get_expiry_date(self):
        if not self.auth_info['auth_key']:
            return None

        try:
            # Firebase에서 만료일 확인
            ref = db.reference('/라이센스')
            licenses = ref.get()
            computer_id = self.generate_computer_id()
            
            if licenses:
                auth_key = self.auth_info['auth_key'].replace("-", "")
                
                for license_data in licenses.values():
                    if (license_data['라이센스키'] == auth_key and 
                        license_data.get('컴퓨터ID') == computer_id):
                        return license_data['만료일']
                        
        except Exception as e:
            print(f"만료일 확인 중 오류: {str(e)}")
            
            # Firebase 연결 실패시 signature에서 확인
            if self.auth_info['signature']:
                try:
                    stored_data = self.decrypt_signature(self.auth_info['signature'])
                    date_str = stored_data.split('_')[0]
                    return date_str
                except Exception:
                    pass
            
        return None    

    def get_network_time(self):
        try:
            # 여러 NTP 서버 시도
            servers = [
                'time.google.com',
                'time.windows.com',
                'pool.ntp.org',
                'time.nist.gov'
            ]
            
            for server in servers:
                try:
                    response = self.ntp_client.request(server, timeout=2)  # 타임아웃 2초로 감소
                    return datetime.fromtimestamp(response.tx_time, timezone.utc)
                except:
                    continue
                    
            # 모든 서버 실패시 로컬 시간 사용
            print("NTP 서버 연결 실패, 로컬 시간 사용")
            return datetime.now(timezone.utc)
            
        except Exception as e:
            print(f"시간 확인 실패: {str(e)}")
            return datetime.now(timezone.utc)

    def set_auth_key(self, key, expiry_date):
        if isinstance(expiry_date, datetime):
            expiry_date = expiry_date.strftime("%Y-%m-%d")
        self.auth_info = {
            'auth_key': key,
            'expiry_date': expiry_date
        }
        self._save_auth_info()


    def is_authenticated(self):
        if not self.auth_info['auth_key']:
            return False

        try:
            current_computer_id = self.generate_computer_id()
            need_firebase_check = True
            
            # signature 검증
            if self.auth_info['signature']:
                try:
                    # signature 복호화
                    stored_data = self.decrypt_signature(self.auth_info['signature'])
                    date_str, computer_id, license_key = stored_data.split('_')
                    
                    # 컴퓨터ID, 라이센스키, 날짜 검증
                    if (computer_id == current_computer_id and 
                        license_key == self.auth_info['auth_key']):
                        stored_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        current_date = self.get_network_time().date()
                        
                        # 하루 이내면 Firebase 체크 스킵
                        if (current_date - stored_date).days < 1:
                            need_firebase_check = False
                except Exception:
                    pass  # 검증 실패시 Firebase 체크 진행
            
            # Firebase 체크가 필요한 경우
            if need_firebase_check:
                ref = db.reference('/라이센스')
                licenses = ref.get()
                
                if licenses:
                    auth_key = self.auth_info['auth_key'].replace("-", "")
                    
                    for license_data in licenses.values():
                        if (license_data['라이센스키'] == auth_key and 
                            license_data.get('컴퓨터ID') == current_computer_id):
                            
                            # 만료일 체크
                            expiry_date = datetime.strptime(license_data['만료일'], "%Y-%m-%d").date()
                            current_date = self.get_network_time().date()
                            
                            if current_date > expiry_date:
                                return False
                            
                            # 체크 성공시 signature 업데이트
                            self._save_auth_info()
                            return True
                    
                    return False
                
            return not need_firebase_check  # Firebase 체크 스킵시 True 반환
                    
        except Exception as e:
            print(f"인증 확인 중 오류: {str(e)}")
            return False

    def days_until_expiry(self):
        expiry_date = self.get_expiry_date()
        if not expiry_date:
            return 0
        
        # 현재 시간과 만료일을 날짜로만 변환 (시간 제외)
        try:
            current_time = self.get_network_time().date()
            expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
            
            # 만료일에서 현재 날짜를 빼서 차이를 계산
            difference = (expiry - current_time).days
            return difference if difference >= 0 else 0
        except Exception as e:
            print(f"만료일 계산 중 오류: {str(e)}")
            return 0

    
    def get_auth_key(self):
        return self.auth_info['auth_key']


def get_video_links():
    try:
        ref = db.reference('/program_info/videos')
        videos = ref.get()
        if videos:
            return {
                'api_guide': videos.get('api_guide', 'https://youtu.be/Vt3Yt7TXvlI'),
                'program_guide': videos.get('program_guide', ''),
                'tube_tip': videos.get('tube_tip', 'https://www.youtube.com/@튜브렌즈')
            }
        return {'api_guide': 'https://youtu.be/Vt3Yt7TXvlI', 'program_guide': '', 'tube_tip': 'https://www.youtube.com/@튜브렌즈'}
    except Exception as e:
        print(f"비디오 링크 로드 오류: {str(e)}")
        return {'api_guide': 'https://youtu.be/Vt3Yt7TXvlI', 'program_guide': '', 'tube_tip': 'https://www.youtube.com/@튜브렌즈'}


import firebase_admin
import asyncio
import aiohttp
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from io import BytesIO
from firebase_admin import credentials
from firebase_admin import db
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from functools import partial

def collect_single_subtitle(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcript_list.find_transcript(['ko'])
        except:
            try:
                transcript = transcript_list.find_transcript(['en'])
            except:
                transcript = transcript_list.find_generated_transcript(['ko', 'en'])
        
        return "\n".join([line['text'] for line in transcript.fetch()])
    except Exception as e:
        return "자막 없음"

def process_subtitle(video_data):
    i, video_url = video_data
    video_id = video_url.split('v=')[1]
    return i, collect_single_subtitle(video_id)

# Firebase 초기화
if not firebase_admin._apps:
    from cryptography.fernet import Fernet
    import json
    import os
    import sys

    
    # 키와 암호화된 설정 파일 읽기
    with open(get_resource_path('firebase_key.key'), 'rb') as key_file:
        key = key_file.read()
    with open(get_resource_path('firebase_config.enc'), 'rb') as config_file:
        encrypted_data = config_file.read()

    # 복호화
    f = Fernet(key)
    config_str = f.decrypt(encrypted_data).decode()
    config = json.loads(config_str)

    cred = credentials.Certificate(config)
    firebase_admin.initialize_app(cred, {
        
        'databaseURL': 'https://seol-license-manager-default-rtdb.asia-southeast1.firebasedatabase.app'
    })


class LazyLoadManager:
    def __init__(self):
        self.cache = {}
        self.loading = set()
        self.visible_range = (0, 0)

    def set_visible_range(self, start, end):
        self.visible_range = (max(0, start-5), end+5)  # 버퍼 추가

    def is_in_visible_range(self, index):
        return self.visible_range[0] <= index <= self.visible_range[1]

    def get_cached_thumbnail(self, url):
        return self.cache.get(url)

    def add_to_cache(self, url, pixmap):
        self.cache[url] = pixmap
        if url in self.loading:
            self.loading.remove(url)

    def is_loading(self, url):
        return url in self.loading

    def mark_as_loading(self, url):
        self.loading.add(url)

    def clear_old_cache(self, visible_urls):
        # 현재 보이는 항목 + 약간의 버퍼만 유지
        urls_to_remove = set(self.cache.keys()) - set(visible_urls)
        for url in urls_to_remove:
            if url not in visible_urls:
                self.cache.pop(url, None)


class ThumbnailWorker(QThread):
    thumbnail_loaded = pyqtSignal(QPixmap, int)
    
    def __init__(self, url, video_url, row):
        super().__init__()
        self.url = url
        self.video_url = video_url
        self.row = row
        self._is_running = True
        
    def stop(self):
        self._is_running = False
        self.wait()  # 스레드가 완전히 종료될 때까지 대기
        
    def run(self):
        if not self._is_running:
            return
                
        try:
            response = urllib.request.urlopen(self.url)
            data = response.read()
            if not self._is_running:
                return
            pixmap = QPixmap()
            if pixmap.loadFromData(data):
                self.thumbnail_loaded.emit(pixmap, self.row)
            else:
                # 이미지 로드 실패시 기본 이미지 생성
                default_pixmap = QPixmap(120, 90)  # 썸네일 크기와 동일하게
                default_pixmap.fill(Qt.GlobalColor.gray)  # 회색으로 채우기
                self.thumbnail_loaded.emit(default_pixmap, self.row)
        except Exception as e:
            print(f"Thumbnail error for row {self.row}: {str(e)}")
            if self._is_running:
                # 에러 발생시에도 기본 이미지 생성
                default_pixmap = QPixmap(120, 90)
                default_pixmap.fill(Qt.GlobalColor.gray)
                self.thumbnail_loaded.emit(default_pixmap, self.row)

    def __del__(self):
        self.stop()  # 객체가 삭제될 때 스레드 정리

class APIKey:
    def __init__(self, key, id=None):
        self.id = id
        self.key = key
        self.last_five = key[-5:]
        self.status = 'active'  # active, quotaExceeded
        self.last_used = None
        self.quota_exceeded_time = None
        self.is_current = False

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'last_five': self.last_five,
            'status': self.status,
            'last_used': self.last_used,
            'quota_exceeded_time': self.quota_exceeded_time,
            'is_current': self.is_current
        }

    @classmethod
    def from_dict(cls, data):
        api_key = cls(data['key'], data['id'])
        api_key.status = data['status']
        api_key.last_used = data['last_used']
        api_key.quota_exceeded_time = data['quota_exceeded_time']
        api_key.is_current = data['is_current']
        return api_key

class APIKeyManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIKeyManager, cls).__new__(cls)
            cls._instance.keys = []
            cls._instance.current_key_index = 0
            cls._instance.load_keys()
        return cls._instance

    def __init__(self):
        # __new__에서 초기화하므로 여기서는 pass
        pass

    def add_key(self, key):
        # 중복 키 확인
        for existing_key in self.keys:
            if existing_key.key == key:
                return None  # 중복된 키인 경우 None 반환
        
        try:
            # YouTube API 연결 테스트
            youtube = build('youtube', 'v3', developerKey=key)
            
            # 실제 API 호출 테스트 (가장 적은 할당량을 사용하는 호출)
            youtube.search().list(
                part='snippet',
                q='test',
                maxResults=1
            ).execute()
            
            # 테스트 통과하면 키 추가
            new_id = max([k.id for k in self.keys], default=0) + 1
            api_key = APIKey(key, new_id)
            if not self.keys:  # 첫 번째 키라면 현재 키로 설정
                api_key.is_current = True
            self.keys.append(api_key)
            self.save_keys()
            return api_key
            
        except Exception as e:
            error_str = str(e).lower()
            if 'api key not valid' in error_str:
                raise Exception("유효하지 않은 API 키입니다.")
            elif 'quota' in error_str:
                raise Exception("API 키의 할당량이 초과되었습니다.")
            else:
                raise Exception("API 키 확인 중 오류가 발생했습니다. 키를 확인해주세요.")

    def remove_key(self, key_id):
        self.keys = [k for k in self.keys if k.id != key_id]
        if self.keys and not any(k.is_current for k in self.keys):
            self.keys[0].is_current = True
        self.save_keys()

    def set_current_key(self, key_id):
        for key in self.keys:
            key.is_current = (key.id == key_id)
        self.save_keys()

    def get_next_available_key(self):
        if not self.keys:
            return None
            
        current = next((k for k in self.keys if k.is_current), None)
        start_index = self.keys.index(current) if current else 0
        checked_count = 0
        
        while checked_count < len(self.keys):
            idx = (start_index + checked_count) % len(self.keys)
            key = self.keys[idx]
            
            if key.status == 'active':
                if not key.is_current:
                    self.set_current_key(key.id)
                return key
                
            elif key.status == 'quotaExceeded' and self.check_reset_time(key):
                key.status = 'active'
                key.quota_exceeded_time = None
                if not key.is_current:
                    self.set_current_key(key.id)
                self.save_keys()
                return key
                
            checked_count += 1
        
        return None  # 모든 키가 사용 불가능한 상태

    def check_reset_time(self, key):
        if not key.quota_exceeded_time:
            return True
            
        exceeded_time = datetime.fromisoformat(key.quota_exceeded_time)
        # 한국시간 오후 5시(17시) 기준으로 리셋
        current_time = datetime.now()
        reset_time = exceeded_time.replace(hour=17, minute=0, second=0, microsecond=0)
        
        # 초과 시점이 그날 오후 5시 이후라면 다음날 오후 5시가 리셋 시간
        if exceeded_time.hour >= 17:
            reset_time = reset_time + timedelta(days=1)
            
        return current_time >= reset_time

    def get_reset_time_remaining(self, key):
        """API 키 리셋까지 남은 시간 계산"""
        if not key.quota_exceeded_time:
            return "0:00:00"
            
        try:
            exceeded_time = datetime.fromisoformat(key.quota_exceeded_time)
            current_time = datetime.now()
            
            # 리셋 시간 계산 (한국시간 오후 5시)
            reset_time = exceeded_time.replace(hour=17, minute=0, second=0, microsecond=0)
            
            # 초과 시점이 그날 오후 5시 이후라면 다음날 오후 5시가 리셋 시간
            if exceeded_time.hour >= 17:
                reset_time = reset_time + timedelta(days=1)
                
            # 남은 시간 계산
            remaining = reset_time - current_time
            
            # 이미 지났으면 0 반환
            if remaining.total_seconds() <= 0:
                return "0:00:00"
                
            # 시간 형식 변환
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            seconds = int(remaining.total_seconds() % 60)
            
            # 24시간 이상 남은 경우 날짜 표시 추가
            if hours >= 24:
                days = hours // 24
                hours = hours % 24
                return f"{days}일 {hours:02d}:{minutes:02d}:{seconds:02d}"
            
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
        except Exception as e:
            print(f"시간 계산 오류: {str(e)}")  # 디버깅용
            return "계산 오류"
    
    def update_key_status(self, key_id, status):
        key = next((k for k in self.keys if k.id == key_id), None)
        if key:
            key.status = status
            if status == 'quotaExceeded':
                key.quota_exceeded_time = datetime.now().isoformat()
            self.save_keys()

    def save_keys(self):
        data = [k.to_dict() for k in self.keys]
        with open('api_keys.json', 'w') as f:
            json.dump(data, f)

    def load_keys(self):
        try:
            with open('api_keys.json', 'r') as f:
                data = json.load(f)
                self.keys = [APIKey.from_dict(k) for k in data]
        except FileNotFoundError:
            self.keys = []

class GeminiAPIKeyManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiAPIKeyManager, cls).__new__(cls)
            cls._instance.keys = []
            cls._instance.current_key_index = 0
            cls._instance.load_keys()
        return cls._instance

    def get_reset_time_remaining(self, key):
        """API 키 리셋까지 남은 시간 계산"""
        if not key.quota_exceeded_time:
            return "0:00:00"
            
        try:
            exceeded_time = datetime.fromisoformat(key.quota_exceeded_time)
            current_time = datetime.now()
            
            # 구글 AI 스튜디오는 하루 단위로 리셋 (다음날 0시 기준)
            reset_time = exceeded_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            
            # 남은 시간 계산
            remaining = reset_time - current_time
            
            # 이미 지났으면 0 반환
            if remaining.total_seconds() <= 0:
                return "0:00:00"
                
            # 시간 형식 변환
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            seconds = int(remaining.total_seconds() % 60)
            
            # 24시간 이상 남은 경우 날짜 표시 추가
            if hours >= 24:
                days = hours // 24
                hours = hours % 24
                return f"{days}일 {hours:02d}:{minutes:02d}:{seconds:02d}"
            
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
        except Exception as e:
            print(f"Gemini API 시간 계산 오류: {str(e)}")
            return "계산 오류"

    def __init__(self):
        # __new__에서 초기화하므로 여기서는 pass
        pass

    def add_key(self, key):
        # 중복 키 확인
        for existing_key in self.keys:
            if existing_key.key == key:
                return None  # 중복된 키인 경우 None 반환
        
        try:
            # Gemini API 연결 테스트
            import google.generativeai as genai
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')
            
            # 실제 API 호출 테스트
            response = model.generate_content("test")
            if not response.text:
                raise Exception("API 응답이 올바르지 않습니다.")
            
            # 테스트 통과하면 키 추가
            new_id = max([k.id for k in self.keys], default=0) + 1
            api_key = APIKey(key, new_id)
            if not self.keys:  # 첫 번째 키라면 현재 키로 설정
                api_key.is_current = True
            self.keys.append(api_key)
            self.save_keys()
            return api_key
            
        except Exception as e:
            error_str = str(e).lower()
            if 'invalid' in error_str or 'error' in error_str:
                raise Exception("유효하지 않은 API 키입니다.")
            elif 'quota' in error_str or 'exceeded' in error_str:
                raise Exception("API 키의 할당량이 초과되었습니다.")
            else:
                raise Exception(f"API 키 확인 중 오류가 발생했습니다: {str(e)}")

    def remove_key(self, key_id):
        self.keys = [k for k in self.keys if k.id != key_id]
        if self.keys and not any(k.is_current for k in self.keys):
            self.keys[0].is_current = True
        self.save_keys()

    def set_current_key(self, key_id):
        for key in self.keys:
            key.is_current = (key.id == key_id)
        self.save_keys()

    def get_next_available_key(self):
        if not self.keys:
            return None
            
        current = next((k for k in self.keys if k.is_current), None)
        start_index = self.keys.index(current) if current else 0
        checked_count = 0
        
        while checked_count < len(self.keys):
            idx = (start_index + checked_count) % len(self.keys)
            key = self.keys[idx]
            
            if key.status == 'active':
                if not key.is_current:
                    self.set_current_key(key.id)
                return key
                
            elif key.status == 'quotaExceeded' and self.check_reset_time(key):
                key.status = 'active'
                key.quota_exceeded_time = None
                if not key.is_current:
                    self.set_current_key(key.id)
                self.save_keys()
                return key
                
            checked_count += 1
        
        return None  # 모든 키가 사용 불가능한 상태

    def check_reset_time(self, key):
        if not key.quota_exceeded_time:
            return True
            
        exceeded_time = datetime.fromisoformat(key.quota_exceeded_time)
        # 한국시간 오후 5시(17시) 기준으로 리셋
        current_time = datetime.now()
        reset_time = exceeded_time.replace(hour=17, minute=0, second=0, microsecond=0)
        
        # 초과 시점이 그날 오후 5시 이후라면 다음날 오후 5시가 리셋 시간
        if exceeded_time.hour >= 17:
            reset_time = reset_time + timedelta(days=1)
            
        return current_time >= reset_time

    def update_key_status(self, key_id, status):
        key = next((k for k in self.keys if k.id == key_id), None)
        if key:
            key.status = status
            if status == 'quotaExceeded':
                key.quota_exceeded_time = datetime.now().isoformat()
            self.save_keys()

    def get_current_key(self):
        current_key = next((k for k in self.keys if k.is_current), None)
        return current_key.key if current_key else None

    def save_keys(self):
        data = [k.to_dict() for k in self.keys]
        with open('gemini_api_keys.json', 'w') as f:
            json.dump(data, f)

    def load_keys(self):
        try:
            with open('gemini_api_keys.json', 'r') as f:
                data = json.load(f)
                self.keys = [APIKey.from_dict(k) for k in data]
        except FileNotFoundError:
            self.keys = []
            
            # 기존에 settings.json에 저장된 API 키가 있으면 마이그레이션
            try:
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    if 'google_ai_api_key' in settings and settings['google_ai_api_key']:
                        self.add_key(settings['google_ai_api_key'])
            except:
                pass

def get_video_links():
    try:
        ref = db.reference('/program_info/videos')
        videos = ref.get()
        if videos:
            return {
                'api_guide': videos.get('api_guide', 'https://youtu.be/Vt3Yt7TXvlI'),
                'program_guide': videos.get('program_guide', ''),
                'tube_tip': videos.get('tube_tip', 'https://www.youtube.com/@튜브렌즈')
            }
        return {'api_guide': 'https://youtu.be/Vt3Yt7TXvlI', 'program_guide': '', 'tube_tip': 'https://www.youtube.com/@튜브렌즈'}
    except Exception as e:
        print(f"비디오 링크 로드 오류: {str(e)}")
        return {'api_guide': 'https://youtu.be/Vt3Yt7TXvlI', 'program_guide': '', 'tube_tip': 'https://www.youtube.com/@튜브렌즈'}

class APIKeyDialog(QDialog):

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # 엔터키 이벤트를 여기서 소비
            event.accept()
        else:
            super().keyPressEvent(event)
            
    def reset_auth_key(self):
        def try_another_key():
            reply = QMessageBox.critical(
                self, 
                "인증 실패", 
                "다른 인증키를 입력하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.reset_auth_key()
            return
                
        key, ok = QInputDialog.getText(
            self, 
            '인증키 재설정', 
            '새로운 인증키를 입력해주세요:',
            QLineEdit.EchoMode.Normal
        )
            
        if not ok or not key:
            return
                
        try:
            # Firebase에서 라이센스 키 확인
            ref = db.reference('/라이센스')
            licenses = ref.get()

            if not licenses:
                QMessageBox.critical(self, "오류", "라이센스 정보를 찾을 수 없습니다.")
                return

            input_key = key.replace('-', '')  # 하이픈 제거
            current_computer_id = self.parent().auth_manager.generate_computer_id()

            # 라이센스 정보 확인
            license_info = None
            license_id = None

            for lid, data in licenses.items():
                if data['라이센스키'] == input_key:
                    license_info = data
                    license_id = lid
                    break

            if not license_info:
                QMessageBox.critical(self, "오류", "유효하지 않은 인증키입니다.")
                try_another_key()
                return

            # 컴퓨터 ID 검증
            if '컴퓨터ID' in license_info and license_info['컴퓨터ID']:
                stored_computer_id = license_info['컴퓨터ID']
                if stored_computer_id != current_computer_id:
                    try:
                        with open('auth_info.json', 'r') as f:
                            previous_auth = json.load(f)
                        # 이전에 이 컴퓨터에서 사용하던 인증키인지 확인
                        if previous_auth.get('auth_key') == key:
                            # 이전에 사용하던 컴퓨터면 재사용 허용
                            pass
                        else:
                            QMessageBox.critical(
                                self, 
                                "오류", 
                                "이 라이센스 키는 이미 다른 컴퓨터에서 사용 중입니다.\n"
                                "라이센스 키는 하나의 컴퓨터에서만 사용할 수 있습니다."
                            )
                            try_another_key()
                            return
                    except FileNotFoundError:
                        # auth_info.json이 없는 경우
                        QMessageBox.critical(
                            self, 
                            "오류", 
                            "이 라이센스 키는 이미 다른 컴퓨터에서 사용 중입니다.\n"
                            "라이센스 키는 하나의 컴퓨터에서만 사용할 수 있습니다."
                        )
                        try_another_key()
                        return
            
            # 만료일 검증
            expiry_date = datetime.strptime(license_info['만료일'], "%Y-%m-%d").date()
            current_date = datetime.now().date()
            
            if current_date > expiry_date:
                QMessageBox.critical(self, "오류", "만료된 인증키입니다.")
                try_another_key()
                return
                
            # 모든 검증을 통과한 경우에만 업데이트 진행
            ref.child(license_id).update({
                '컴퓨터ID': current_computer_id,
                '활성화상태': "사용중"
            })
            
            # 인증키 설정
            days_left = (expiry_date - current_date).days
            self.parent().auth_manager.set_auth_key(key, expiry_date.strftime("%Y-%m-%d"))
            
            QMessageBox.information(
                self, 
                "인증 성공",
                f"인증키가 재설정되었습니다.\n만료일: {expiry_date.strftime('%Y-%m-%d')}\n남은 기간: {days_left}일"
            )

            # UI 업데이트
            self.setup_ui()
            
            # 메인 창 타이틀 업데이트
            main_window = self.parent()
            expiry_date_str = main_window.auth_manager.get_expiry_date()
            if expiry_date_str:
                title = f"Tube Lens - 만료일 : {expiry_date_str[:10]} (남은 기간 : {days_left}일)"
                main_window.setWindowTitle(title)
                    
        except Exception as e:
            QMessageBox.critical(self, "오류", f"인증키 확인 중 오류가 발생했습니다: {str(e)}")
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_manager = parent.api_manager  # 부모의 api_manager 사용
        self.setup_ui()
        
        # 타이머 초기화
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_and_update)
        self.update_timer.start(1000)  # 매 초마다 업데이트
        
        # 다이얼로그가 닫힐 때 타이머 정지
        self.finished.connect(self.cleanup)

    def setup_ui(self):
        self.setWindowTitle("설정")
        # 부모로부터 video_links 가져오기
        self.setStyleSheet("QDialog { background-color: #f5f5f5; } QLabel { color: black; }")
        self.video_links = self.parent().video_links
        self.setMinimumWidth(700)  # 너비 증가
        self.setMinimumHeight(700)  # 높이 설정
        
        # 기존 레이아웃이 있다면 제거
        if self.layout():
            QWidget().setLayout(self.layout())
            
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 상단 타이틀
        title_label = QLabel("TubeLens 설정")
        title_label.setStyleSheet("""
            QLabel {
                color: #4a9eff;
                font-size: 24px;
                font-weight: bold;
                padding-bottom: 10px;
                border-bottom: 2px solid #4a9eff;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 스크롤 영역 추가
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #f0f0f0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(25)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        
        # 1. 인증키 섹션 ===================================
        auth_section = QWidget()
        auth_section.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
        """)
        auth_layout = QVBoxLayout(auth_section)
        auth_layout.setSpacing(15)
        auth_layout.setContentsMargins(20, 20, 20, 20)
        
        # 섹션 헤더
        auth_header = QWidget()
        auth_header_layout = QHBoxLayout(auth_header)
        auth_header_layout.setContentsMargins(0, 0, 0, 3)
        
        auth_icon = QLabel("🔑")
        auth_icon.setStyleSheet("font-size: 24px;")
        auth_title = QLabel("인증키 관리")
        auth_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
        """)
        
        auth_header_layout.addWidget(auth_icon)
        auth_header_layout.addWidget(auth_title)
        auth_header_layout.addStretch()
        
        # 버튼 컨테이너 (비어있는 상태로 유지)
        auth_buttons = QWidget()
        auth_buttons_layout = QHBoxLayout(auth_buttons)
        auth_buttons_layout.setContentsMargins(0, 0, 0, 0)
        auth_buttons_layout.setSpacing(10)
        
        # 인증키 정보 패널
        auth_info_panel = QWidget()
        auth_info_panel.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        auth_info_layout = QVBoxLayout(auth_info_panel)
        auth_info_layout.setSpacing(15)
        
        # 현재 인증키 표시
        current_auth = self.parent().auth_manager.get_auth_key()
        if current_auth:
            # 인증키 표시
            key_container = QWidget()
            key_layout = QHBoxLayout(key_container)
            key_layout.setContentsMargins(0, 0, 0, 0)
            
            key_label = QLabel("<b>인증키:</b>")
            key_label.setStyleSheet("color: #555;")
            key_value = QLabel(current_auth)
            key_value.setStyleSheet("""
                color: #4a9eff;
                font-weight: bold;
                background-color: #e9f5ff;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 14px;
            """)
            
            # 인증키 재설정 버튼 생성
            reset_auth_button = QPushButton("🔄 인증키 재설정")
            reset_auth_button.setFixedWidth(125)
            reset_auth_button.setStyleSheet("""
                QPushButton {
                    background-color: #4a9eff;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3d8ae0;
                }
            """)
            reset_auth_button.clicked.connect(self.reset_auth_key)

            key_layout.addWidget(key_label)
            key_layout.addWidget(key_value, 1)
            key_layout.addWidget(reset_auth_button)
            auth_info_layout.addWidget(key_container)
            
            # 만료일 표시
            expiry_date = self.parent().auth_manager.get_expiry_date()
            if expiry_date:
                date_container = QWidget()
                date_layout = QHBoxLayout(date_container)
                date_layout.setContentsMargins(0, 0, 0, 0)
                
                date_label = QLabel("<b>만료일:</b>")
                date_label.setStyleSheet("color: #555;")
                
                current_date = datetime.now().date()
                expiry = datetime.strptime(expiry_date[:10], "%Y-%m-%d").date()
                days_left = (expiry - current_date).days
                
                date_value = QLabel(f"{expiry_date[:10]} (남은 기간: {days_left}일)")
                
                # 남은 일수에 따라 색상 변경
                if days_left <= 7:
                    bg_color = "#fff3cd"  # 노랑색 배경
                    text_color = "#856404"  # 어두운 노랑색 텍스트
                elif days_left <= 30:
                    bg_color = "#e9f5ff"  # 파란색 배경
                    text_color = "#004085"  # 어두운 파란색 텍스트
                else:
                    bg_color = "#d4edda"  # 초록색 배경  
                    text_color = "#155724"  # 어두운 초록색 텍스트
                    
                date_value.setStyleSheet(f"""
                    color: {text_color};
                    font-weight: bold;
                    background-color: {bg_color};
                    padding: 5px 10px;
                    border-radius: 4px;
                """)
                
                date_layout.addWidget(date_label)
                date_layout.addWidget(date_value, 1)
                auth_info_layout.addWidget(date_container)
        else:
            no_auth_label = QLabel("등록된 인증키가 없습니다")
            no_auth_label.setStyleSheet("""
                color: #721c24;
                font-weight: bold;
                background-color: #f8d7da;
                padding: 10px;
                border-radius: 4px;
                text-align: center;
            """)
            no_auth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            auth_info_layout.addWidget(no_auth_label)
        
        # 섹션 구성 완료
        auth_layout.addWidget(auth_header)
        auth_layout.addWidget(auth_info_panel)
        
        # 2. Google AI Studio API 섹션 ===============================
        ai_section = QWidget()
        ai_section.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
        """)
        ai_layout = QVBoxLayout(ai_section)
        ai_layout.setSpacing(15)
        ai_layout.setContentsMargins(20, 20, 20, 20)
        
        # 섹션 헤더
        ai_header = QWidget()
        ai_header_layout = QHBoxLayout(ai_header)
        ai_header_layout.setContentsMargins(0, 0, 0, 3)
        
        ai_icon = QLabel("🤖")
        ai_icon.setStyleSheet("font-size: 24px;")
        ai_title = QLabel("Google AI Studio API")
        ai_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
        """)
        
        ai_header_layout.addWidget(ai_icon)
        ai_header_layout.addWidget(ai_title)
        ai_header_layout.addStretch()
        
        # 설명 추가
        ai_description = QLabel("AI 추천 기능을 사용하려면 Google AI Studio API 키가 필요합니다.")
        ai_description.setStyleSheet("""
            color: #666;
            padding: 5px 0;
        """)
        ai_description.setWordWrap(True)
        
        # AI API 키 입력 영역
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)

        self.ai_key_input = QLineEdit()
        self.ai_key_input.setPlaceholderText("새로운 Google AI Studio API 키 입력")
        self.ai_key_input.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                color: black;
                border: 1px solid #dddddd;
                border-radius: 5px;
                padding: 10px;
                selection-background-color: #4a9eff;
            }
            QLineEdit:focus {
                border: 1px solid #9b59b6;
            }
        """)
        
        add_button = QPushButton("추가")
        add_button.setFixedWidth(80)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        add_button.clicked.connect(self.add_ai_key)

        # 키 발급받기 버튼 추가
        get_key_button = QPushButton("🔑 키 발급받기")
        get_key_button.setFixedWidth(115)
        get_key_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        get_key_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://aistudio.google.com/apikey")))
        
        input_layout.addWidget(self.ai_key_input)
        input_layout.addWidget(add_button)
        input_layout.addWidget(get_key_button)
        
        # API 키 테이블
        self.ai_table = QTableWidget()
        self.ai_table.setColumnCount(4)
        self.ai_table.setHorizontalHeaderLabels(["API 키", "상태", "남은 시간", "작업"])
        self.ai_table.setStyleSheet("""
            QTableWidget {
                background-color: #f8f9fa;
                border-radius: 5px;
                border: none;
                gridline-color: #ddd;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f9e4ff;
                color: #333;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #f3e5f5;
            }
        """)
        self.ai_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ai_table.setMinimumHeight(200)
        
        # 섹션 구성 완료
        ai_layout.addWidget(ai_header)
        ai_layout.addWidget(ai_description)
        ai_layout.addWidget(input_container)
        ai_layout.addWidget(self.ai_table)
        
        # 3. YouTube API 키 섹션 =======================================
        api_section = QWidget()
        api_section.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
        """)
        api_layout = QVBoxLayout(api_section)
        api_layout.setSpacing(15)
        api_layout.setContentsMargins(20, 20, 20, 20)
        
        # 섹션 헤더
        api_header = QWidget()
        api_header_layout = QHBoxLayout(api_header)
        api_header_layout.setContentsMargins(0, 0, 0, 3)
        api_header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 왼쪽 정렬로 설정

        api_icon = QLabel("📊")
        api_icon.setStyleSheet("font-size: 24px;")
        api_title = QLabel("YouTube API 키 관리")
        api_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
        """)

        # API키 받는법 버튼
        guide_button = QPushButton("📖 API키 받는 법")
        guide_button.setFixedSize(115, 30)  # 너비와 높이 동시 설정
        guide_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5252;
                color: white;
                border: none;
                padding: 3px 8px;  /* 패딩 줄임 */
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
            }
        """)
        guide_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.parent().video_links['api_guide'])))

        # 모든 위젯을 왼쪽에 차례대로 배치
        api_header_layout.addWidget(api_icon)
        api_header_layout.addWidget(api_title)
        api_header_layout.addSpacing(10)  # 아이콘과 버튼 사이 간격
        api_header_layout.addWidget(guide_button)
        api_header_layout.addStretch(1)  # 나머지 공간을 채워서 모든 요소가 왼쪽에 붙도록 함
        
        # 설명 추가
        api_description = QLabel("YouTube 데이터 검색을 위해 API 키를 추가하거나 구글 계정을 사용할 수 있습니다.")
        api_description.setStyleSheet("""
            color: #666;
            padding: 5px 0;
        """)
        api_description.setWordWrap(True)
        
        # API 키 입력 영역
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)

        self.key_input = QLineEdit()
        self.key_input.returnPressed.connect(lambda: self.add_key())
        self.key_input.setPlaceholderText("새로운 YouTube API 키 입력")
        self.key_input.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                color: black;
                border: 1px solid #dddddd;
                border-radius: 5px;
                padding: 10px;
                selection-background-color: #4a9eff;
            }
            QLineEdit:focus {
                border: 1px solid #4a9eff;
            }
        """)

        add_button = QPushButton("추가")
        add_button.setFixedWidth(80)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
        """)
        add_button.clicked.connect(self.add_key)

        # 키 발급받기 버튼 추가
        get_youtube_key_button = QPushButton("🔑 키 발급받기")
        get_youtube_key_button.setFixedWidth(115)
        get_youtube_key_button.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
        """)
        get_youtube_key_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("http://console.cloud.google.com/apis/library/youtube.googleapis.com?project=aaaa-434404&inv=1&invt=AbkQAw")))

        input_layout.addWidget(self.key_input)
        input_layout.addWidget(add_button)
        input_layout.addWidget(get_youtube_key_button)
        
        # API 키 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["API 키", "상태", "남은 시간", "작업"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #f8f9fa;
                border-radius: 5px;
                border: none;
                gridline-color: #ddd;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #e6f3ff;
                color: #333;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setMinimumHeight(200)
        
        # 섹션 구성 완료
        api_layout.addWidget(api_header)
        api_layout.addWidget(api_description)
        api_layout.addWidget(input_container)
        api_layout.addWidget(self.table)
        
        # 모든 섹션을 스크롤 영역에 추가
        scroll_layout.addWidget(auth_section)
        scroll_layout.addWidget(api_section)
        scroll_layout.addWidget(ai_section)
        
        # 스크롤 영역을 메인 레이아웃에 추가
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # 버튼들을 담을 컨테이너
        bottom_buttons = QWidget()
        bottom_layout = QHBoxLayout(bottom_buttons)
        bottom_layout.setSpacing(15)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # 프로그램 사용법 버튼
        usage_button = QPushButton("📝 프로그램 사용법")
        usage_button.setFixedWidth(160)  # 여기에 고정 너비 추가
        usage_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 7px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        usage_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.parent().video_links['program_guide'] if self.parent().video_links['program_guide'] else self.parent().video_links['api_guide'])))

        # 닫기 버튼
        close_button = QPushButton("닫기")
        close_button.setFixedWidth(160)  # 동일한 너비로 설정
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 10px 7px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        close_button.clicked.connect(self.close)

        bottom_layout.addWidget(usage_button)
        bottom_layout.addWidget(close_button)

        main_layout.addWidget(bottom_buttons, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 테이블 데이터 업데이트
        self.update_table()
        self.update_ai_table() 
    
    def add_ai_key(self):
        key = self.ai_key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "경고", "API 키를 입력해주세요.")
            return
            
        try:
            # 부모의 gemini_api_manager 사용 (안전하게 확인)
            if not hasattr(self.parent(), 'gemini_api_manager'):
                QMessageBox.warning(self, "경고", "API 관리자가 초기화되지 않았습니다.")
                return
                
            gemini_api_manager = self.parent().gemini_api_manager
            result = gemini_api_manager.add_key(key)
            
            if result is None:
                QMessageBox.warning(
                    self,
                    "중복된 API 키",
                    "이미 등록된 API 키입니다.",
                    QMessageBox.StandardButton.Ok
                )
            else:
                self.ai_key_input.clear()
                self.update_ai_table()
                QMessageBox.information(
                    self,
                    "성공",
                    "Gemini API 키가 성공적으로 등록되었습니다.",
                    QMessageBox.StandardButton.Ok
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "오류",
                str(e),
                QMessageBox.StandardButton.Ok
            )
    
    def update_ai_table(self):
        """Gemini API 키 테이블 업데이트"""
        try:
            # 부모 객체가 gemini_api_manager 속성을 가지고 있는지 확인
            if not hasattr(self.parent(), 'gemini_api_manager'):
                print("부모 객체에 gemini_api_manager가 없습니다")
                return
                
            gemini_api_manager = self.parent().gemini_api_manager
            if not hasattr(self, 'ai_table'):
                print("ai_table이 초기화되지 않았습니다")
                return
                
            self.ai_table.setRowCount(len(gemini_api_manager.keys))
            # 행 높이 설정 (각 행의 높이를 45로 설정)
            for row in range(len(gemini_api_manager.keys)):
                self.ai_table.setRowHeight(row, 40)
            
            
            for i, key in enumerate(gemini_api_manager.keys):
                # API 키 (마지막 5자리만)
                key_item = QTableWidgetItem(f"...{key.last_five}")
                key_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # 현재 선택된 키는 보라색 배경, 할당량 초과된 키는 연한 빨간색 배경
                if key.is_current and key.status == 'active':
                    key_item.setBackground(QColor("#9b59b6"))
                    key_item.setForeground(QColor("white"))
                elif key.status == 'quotaExceeded':
                    key_item.setBackground(QColor("#ffebee"))  # 연한 빨간색
                self.ai_table.setItem(i, 0, key_item)

                # 상태
                status_text = "활성" if key.status == 'active' else "할당량 초과"
                status_item = QTableWidgetItem(status_text)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                if key.status == 'quotaExceeded':
                    status_item.setBackground(QColor("#ff4a4a"))
                    status_item.setForeground(QColor("white"))
                else:
                    status_item.setBackground(QColor("#98FB98"))
                self.ai_table.setItem(i, 1, status_item)

                # 남은 시간 - 여기서 gemini_api_manager의 함수 사용
                time_remaining = "-"
                if key.status == 'quotaExceeded':
                    time_remaining = gemini_api_manager.get_reset_time_remaining(key)  # ← 수정된 부분
                    if time_remaining == "0:00:00":
                        # 리셋 시간이 지난 경우 자동으로 상태 업데이트
                        gemini_api_manager.update_key_status(key.id, 'active')
                        time_remaining = "-"
                        
                remaining_item = QTableWidgetItem(time_remaining)
                remaining_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if key.status == 'quotaExceeded':
                    remaining_item.setForeground(QColor("#ff4a4a"))
                    remaining_item.setBackground(QColor("#ffebee"))
                self.ai_table.setItem(i, 2, remaining_item)

                # 버튼 컨테이너
                button_container = QWidget()
                button_layout = QHBoxLayout(button_container)
                button_layout.setContentsMargins(5, 0, 5, 0)
                button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                button_layout.setSpacing(10)  # 버튼 사이 간격 조정

                if not key.is_current:
                    use_button = QPushButton("사용")
                    use_button.setFixedSize(57, 23)  # 버튼 크기 조정
                    use_button.setEnabled(key.status == 'active')
                    if key.status == 'active':
                        use_button.setStyleSheet("""
                            QPushButton {
                                background-color: #9b59b6;
                                color: white;
                                border: none;
                                border-radius: 4px;
                                font-size: 12px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: #8e44ad;
                            }
                            QPushButton:disabled {
                                background-color: #cccccc;
                            }
                        """)
                    def on_use_button_clicked(key_id):
                        import winsound
                        winsound.PlaySound("SystemHand", winsound.SND_ALIAS)  # Windows 기본 효과음
                        gemini_api_manager.set_current_key(key_id)
                        self.update_ai_table()  # 테이블 즉시 업데이트

                    use_button.clicked.connect(lambda x, kid=key.id: on_use_button_clicked(kid))
                    button_layout.addWidget(use_button)

                delete_button = QPushButton("삭제")
                delete_button.setFixedSize(57, 23)  # 버튼 크기 조정
                delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #da190b;
                    }
                """)
                delete_button.clicked.connect(lambda x, kid=key.id: self.delete_ai_key(kid))
                button_layout.addWidget(delete_button)

                self.ai_table.setCellWidget(i, 3, button_container)

                # 툴팁 추가
                if key.status == 'quotaExceeded':
                    tooltip_text = f"할당량 초과\n리셋까지 남은 시간: {time_remaining}"
                    if time_remaining == "-":
                        tooltip_text += "\n(리셋 시간이 지났습니다. 다시 사용해보세요.)"
                    for col in range(self.ai_table.columnCount()):
                        item = self.ai_table.item(i, col)
                        if item:
                            item.setToolTip(tooltip_text)
        except Exception as e:
            print(f"AI 테이블 업데이트 오류: {str(e)}")
    
    def delete_ai_key(self, key_id):
        """Gemini API 키 삭제"""
        reply = QMessageBox.question(
            self, '확인',
            'Gemini API 키를 삭제하시겠습니까?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            gemini_api_manager = self.parent().gemini_api_manager
            gemini_api_manager.remove_key(key_id)
            self.update_ai_table()
    
    def cleanup(self):
        """다이얼로그가 닫힐 때 타이머를 정리"""
        self.update_timer.stop()

    def check_and_update(self):
        """API 키 상태를 확인하고 필요한 경우 업데이트"""
        try:
            # YouTube API 키 확인
            need_update = False
            for key in self.api_manager.keys:
                if key.status == 'quotaExceeded':
                    # 리셋 시간 확인
                    time_remaining = self.api_manager.get_reset_time_remaining(key)
                    print(f"YouTube 키 (...{key.last_five}) 남은 시간: {time_remaining}")  # 디버깅용
                    
                    if time_remaining == "0:00:00":
                        # 리셋 시간이 지났으면 상태 업데이트
                        self.api_manager.update_key_status(key.id, 'active')
                        need_update = True
                        
                        # 상태가 리셋되었음을 사용자에게 알림
                        QToolTip.showText(
                            self.mapToGlobal(self.pos()),
                            f"YouTube API 키 (...{key.last_five})가 리셋되어 다시 사용 가능합니다.",
                            self,
                            self.rect(),
                            2000  # 2초 동안 표시
                        )
            
            # Gemini API 키 확인
            if hasattr(self.parent(), 'gemini_api_manager'):
                gemini_api_manager = self.parent().gemini_api_manager
                for key in gemini_api_manager.keys:
                    if key.status == 'quotaExceeded':
                        # 리셋 시간 확인 - 이 부분 수정
                        time_remaining = gemini_api_manager.get_reset_time_remaining(key)  # 변경된 부분
                        print(f"Gemini 키 (...{key.last_five}) 남은 시간: {time_remaining}")
                        
                        if time_remaining == "0:00:00":
                            # 리셋 시간이 지났으면 상태 업데이트
                            gemini_api_manager.update_key_status(key.id, 'active')
                            need_update = True
                            
                            # 상태가 리셋되었음을 사용자에게 알림
                            QToolTip.showText(
                                self.mapToGlobal(self.pos()),
                                f"Gemini API 키 (...{key.last_five})가 리셋되어 다시 사용 가능합니다.",
                                self,
                                self.rect(),
                                2000
                            )
            
            if need_update:
                self.update_table()
                if hasattr(self, 'update_ai_table'):
                    self.update_ai_table()
            else:
                # 카운트다운만 업데이트
                for i, key in enumerate(self.api_manager.keys):
                    if key.status == 'quotaExceeded':
                        time_remaining = self.api_manager.get_reset_time_remaining(key)
                        
                        # 구글 계정 행이 있으면 인덱스 조정
                        row_offset = 1 if self.parent().auth_manager.is_google_logged_in() else 0
                        row_index = i + row_offset
                        
                        remaining_item = self.table.item(row_index, 2)
                        if remaining_item:
                            remaining_item.setText(time_remaining)
                            # 툴팁 업데이트
                            tooltip_text = f"할당량 초과\n리셋까지 남은 시간: {time_remaining}"
                            remaining_item.setToolTip(tooltip_text)
                            
                            # 붉은색으로 강조
                            remaining_item.setForeground(QColor("#ff4a4a"))
                
                # Gemini API 키 카운트다운 업데이트
                if hasattr(self.parent(), 'gemini_api_manager'):
                    gemini_api_manager = self.parent().gemini_api_manager
                    for i, key in enumerate(gemini_api_manager.keys):
                        if key.status == 'quotaExceeded':
                            time_remaining = gemini_api_manager.get_reset_time_remaining(key)  # 변경된 부분
                            
                            if hasattr(self, 'ai_table'):
                                remaining_item = self.ai_table.item(i, 2)
                                if remaining_item:
                                    remaining_item.setText(time_remaining)
                                    # 툴팁 업데이트
                                    tooltip_text = f"할당량 초과\n리셋까지 남은 시간: {time_remaining}"
                                    remaining_item.setToolTip(tooltip_text)
                                    
                                    # 붉은색으로 강조
                                    remaining_item.setForeground(QColor("#ff4a4a"))
        except Exception as e:
            print(f"check_and_update 오류: {str(e)}")
    
    

    def update_table(self):
        # 여기서부터 새로운 코드 시작
        # 구글 계정도 포함한 전체 행 수 계산
        total_rows = len(self.api_manager.keys) + (1 if self.parent().auth_manager.is_google_logged_in() else 0)
        self.table.setRowCount(total_rows)

        current_row = 0
        # 구글 계정이 있으면 첫 번째 행에 추가
        if self.parent().auth_manager.is_google_logged_in():
            # 행 높이 설정 (40으로 증가)
            self.table.setRowHeight(current_row, 35)
            
            # API 키 열
            key_item = QTableWidgetItem("Google 계정")
            key_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # 현재 선택된 API 키가 없으면 구글 계정이 현재 사용 중임을 표시
            if not any(k.is_current for k in self.api_manager.keys):
                key_item.setBackground(QColor("#4a9eff"))
                key_item.setForeground(QColor("white"))
            self.table.setItem(current_row, 0, key_item)

            # 상태 열
            status_item = QTableWidgetItem("활성")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setBackground(QColor("#98FB98"))
            self.table.setItem(current_row, 1, status_item)

            # 남은 시간 열
            remaining_item = QTableWidgetItem("-")
            remaining_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(current_row, 2, remaining_item)

            # 작업 버튼 열
            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            button_layout.setContentsMargins(5, 0, 5, 0)
            button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 다른 API 키가 사용 중일 때만 '사용' 버튼 표시
            if any(k.is_current for k in self.api_manager.keys):
                use_button = QPushButton("사용")
                use_button.setFixedSize(60, 23)  # 버튼 크기 조정
                use_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                use_button.clicked.connect(lambda: self.use_google_account())
                button_layout.addWidget(use_button)

            self.table.setCellWidget(current_row, 3, button_container)
            current_row += 1
        
        # API 키 목록 표시
        row_start = 1 if self.parent().auth_manager.is_google_logged_in() else 0
        for i, key in enumerate(self.api_manager.keys, start=row_start):
            # 행 높이 설정 (40으로 증가)
            self.table.setRowHeight(i, 35)
            
            # API 키 (마지막 5자리만)
            key_item = QTableWidgetItem(f"...{key.last_five}")
            key_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 현재 선택된 키는 파란색 배경, 할당량 초과된 키는 연한 빨간색 배경
            if key.is_current and key.status == 'active':
                key_item.setBackground(QColor("#4a9eff"))
                key_item.setForeground(QColor("white"))
            elif key.status == 'quotaExceeded':
                key_item.setBackground(QColor("#ffebee"))  # 연한 빨간색
            self.table.setItem(i, 0, key_item)

            # 상태
            status_text = "활성" if key.status == 'active' else "할당량 초과"
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if key.status == 'quotaExceeded':
                status_item.setBackground(QColor("#ff4a4a"))
                status_item.setForeground(QColor("white"))
            else:
                status_item.setBackground(QColor("#98FB98"))
            self.table.setItem(i, 1, status_item)

            # 남은 시간
            time_remaining = "-"
            if key.status == 'quotaExceeded':
                time_remaining = self.api_manager.get_reset_time_remaining(key)
                if time_remaining == "0:00:00":
                    # 리셋 시간이 지난 경우 자동으로 상태 업데이트
                    self.api_manager.update_key_status(key.id, 'active')
                    time_remaining = "-"
                    
            remaining_item = QTableWidgetItem(time_remaining)
            remaining_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if key.status == 'quotaExceeded':
                remaining_item.setForeground(QColor("#ff4a4a"))
                remaining_item.setBackground(QColor("#ffebee"))
            self.table.setItem(i, 2, remaining_item)

            # 버튼 컨테이너
            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            button_layout.setContentsMargins(5, 0, 5, 0)
            button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button_layout.setSpacing(10)  # 버튼 사이 간격 조정

            if not key.is_current:
                use_button = QPushButton("사용")
                use_button.setFixedSize(57, 23)  # 버튼 크기 조정
                use_button.setEnabled(key.status == 'active')
                if key.status == 'active':
                    use_button.setStyleSheet("""
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            font-size: 12px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #45a049;
                        }
                        QPushButton:disabled {
                            background-color: #cccccc;
                        }
                    """)
                def on_use_button_clicked(key_id):
                    import winsound
                    winsound.PlaySound("SystemHand", winsound.SND_ALIAS)  # Windows 기본 효과음
                    self.api_manager.set_current_key(key_id)
                    self.update_table()  # 테이블 즉시 업데이트

                use_button.clicked.connect(lambda x, kid=key.id: on_use_button_clicked(kid))
                button_layout.addWidget(use_button)

            delete_button = QPushButton("삭제")
            delete_button.setFixedSize(57, 23)  # 버튼 크기 조정
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            delete_button.clicked.connect(lambda x, kid=key.id: self.delete_key(kid))
            button_layout.addWidget(delete_button)

            self.table.setCellWidget(i, 3, button_container)

            # 툴팁 추가
            if key.status == 'quotaExceeded':
                tooltip_text = f"할당량 초과\n리셋까지 남은 시간: {time_remaining}"
                if time_remaining == "-":
                    tooltip_text += "\n(리셋 시간이 지났습니다. 다시 사용해보세요.)"
                for col in range(self.table.columnCount()):
                    item = self.table.item(i, col)
                    if item:
                        item.setToolTip(tooltip_text)
    
    def add_key(self):
        key = self.key_input.text().strip()
        if not key:
            return
            
        try:
            result = self.api_manager.add_key(key)
            if result is None:
                QMessageBox.warning(
                    self,
                    "중복된 API 키",
                    "이미 등록된 API 키입니다.",
                    QMessageBox.StandardButton.Ok
                )
            else:
                self.key_input.clear()
                self.update_table()
                QMessageBox.information(
                    self,
                    "성공",
                    "API 키가 성공적으로 등록되었습니다.",
                    QMessageBox.StandardButton.Ok
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "오류",
                str(e),
                QMessageBox.StandardButton.Ok
            )

    def delete_key(self, key_id):
        reply = QMessageBox.question(
            self, '확인',
            'API 키를 삭제하시겠습니까?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.api_manager.remove_key(key_id)
            self.update_table()
            
    def use_google_account(self):
        # Windows 기본 효과음 재생
        import winsound
        winsound.PlaySound("SystemHand", winsound.SND_ALIAS)  # Windows 기본 효과음
            # 모든 API 키의 is_current를 False로 설정
        for key in self.api_manager.keys:
            key.is_current = False
        self.api_manager.save_keys()
        self.update_table()        

class YouTubeSearchWorker(QThread):
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str, int)

    def __init__(self, youtube, search_params):
        super().__init__()
        self.youtube = youtube
        self.search_params = search_params
        self.is_running = True
        self.results = []
        self.thumbnail_semaphore = asyncio.Semaphore(5)

    def process_video_data(self, search_result, video_info, channel_info):
        # 기본 정보 추출
        video_id = search_result['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        try:
            duration_str = video_info['contentDetails']['duration']
            duration = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
            duration_formatted = ""
            hours = 0
            minutes = 0
            seconds = 0
            
            if duration:
                hours = int(duration.group(1) or 0)
                minutes = int(duration.group(2) or 0)
                seconds = int(duration.group(3) or 0)
                
                if hours > 0:
                    duration_formatted = f"{hours}:{minutes:02d}:{seconds:02d}"
                else:
                    duration_formatted = f"{minutes}:{seconds:02d}"
            else:
                duration_formatted = "0:00"
                hours = 0
                minutes = 0
                seconds = 0
                
        except:
            duration_formatted = "0:00"
            hours = 0
            minutes = 0
            seconds = 0
                
        # 쇼츠 여부 판단 (1분 이하 영상)
        total_seconds = hours * 3600 + minutes * 60 + seconds
        is_shorts = total_seconds <= 60
        
        # 통계 정보
        statistics = video_info.get('statistics', {})
        view_count = int(statistics.get('viewCount', 0))
        like_count = int(statistics.get('likeCount', 0))
        comment_count = int(statistics.get('commentCount', 0))
        
        # 채널 통계
        channel_stats = channel_info.get('statistics', {})
        subscriber_count = int(channel_stats.get('subscriberCount', 0))
        total_videos = int(channel_stats.get('videoCount', 0))
        total_views = int(channel_stats.get('viewCount', 0))
        
        import math

        # 채널 기여도 계산 (30%)
        contribution_value = (view_count/total_views*100) if total_views > 0 else 0
        contribution_score = min(contribution_value, 100)

        # 성과도 계산 (70%) - 구독자 대비 조회수 배율
        performance_value = (view_count/subscriber_count) if subscriber_count > 0 else 0
        performance_score = min(performance_value * 10, 100)  # 10배까지는 기존과 동일

        # 최종 CII 점수 계산 (채널 기여도 30% + 성과 점수 70%)
        cii_score = (contribution_score * 0.3) + (performance_score * 0.7)

        # 참여율 계산
        engagement_rate = ((like_count + comment_count) / view_count * 100) if view_count > 0 else 0
        
        
        # CII 등급 판정
        if cii_score >= 70:
            cii = "Great!!"
        elif cii_score >= 50:
            cii = "Good"
        elif cii_score >= 30:
            cii = "Soso"
        elif cii_score >= 10:
            cii = "Not bad"
        else:
            cii = "Bad"

        # performance_value도 반환 데이터에 포함
        return {
            'video_url': video_url,
            'thumbnail_url': search_result['snippet']['thumbnails']['default']['url'],
            'channel_title': search_result['snippet']['channelTitle'],
            'title': search_result['snippet']['title'].replace('&#39;', "'").replace('&quot;', '"'),
            'published_at': search_result['snippet']['publishedAt'],
            'duration': duration_formatted,
            'is_shorts': is_shorts,
            'view_count': view_count,
            'like_count': like_count,
            'comment_count': comment_count,
            'subscriber_count': subscriber_count,
            'total_videos': total_videos,
            'contribution_value': contribution_value,
            'performance_value': performance_value,  # 배율 값 추가
            'cii_score': cii_score,
            'cii': cii,
            'engagement_rate': engagement_rate,
            'transcript': "자막수집" ,
            'description': video_info['snippet']['description']
        }

               
        

    async def fetch_thumbnail(self, session, url):
        try:
            async with self.thumbnail_semaphore:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
                    return None
        except Exception as e:
            print(f"Thumbnail error: {str(e)}")
            return None

    async def process_video_batch(self, session, video_ids, channel_ids):
        try:
            # 비디오 ID를 50개씩 나누기 (YouTube API 제한)
            video_id_chunks = [video_ids[i:i + 50] for i in range(0, len(video_ids), 50)]
            channel_id_chunks = [list(set(channel_ids))[i:i + 50] for i in range(0, len(set(channel_ids)), 50)]
            
            # 비디오 정보 가져오기
            videos_responses = []
            for chunk in video_id_chunks:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.youtube.videos().list(
                        part="statistics,contentDetails,player,snippet",
                        id=','.join(chunk),
                        maxResults=50
                    ).execute()
                )
                videos_responses.extend(response.get('items', []))
            
            # 채널 정보 가져오기
            channels_responses = []
            for chunk in channel_id_chunks:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.youtube.channels().list(
                        part="statistics,snippet",
                        id=','.join(chunk),
                        maxResults=50
                    ).execute()
                )
                channels_responses.extend(response.get('items', []))
            
            return {'items': videos_responses}, {'items': channels_responses}
                
        except Exception as e:
            if 'quotaExceeded' in str(e):
                self.error.emit("API_QUOTA_EXCEEDED", 0)
            raise e

    def run(self):
        async def main():
            try:
                results = []
                next_page_token = None
                current_count = 0
                total_expected = self.search_params.get('total_results', 100)
                
                async with aiohttp.ClientSession() as session:
                    while current_count < total_expected and self.is_running:
                        if next_page_token:
                            self.search_params['pageToken'] = next_page_token
                            
                        search_params_copy = {k: v for k, v in self.search_params.items() if k != 'total_results'}
                        try:
                            print("검색 시도:", search_params_copy)  # 임시 디버깅용
                            search_response = self.youtube.search().list(**search_params_copy).execute()
                        except Exception as e:
                            print(f"검색 중 에러 발생: {str(e)}")  # 임시 디버깅용
                            if 'quotaExceeded' in str(e):
                                self.error.emit("API_QUOTA_EXCEEDED", 0)
                                return
                            self.error.emit(f"검색 중 오류: {str(e)}", 0)
                            return

                        items = search_response.get('items', [])
                        if not items:
                            break
                            
                        # ID 수집
                        video_ids = []
                        channel_ids = []
                        for item in items:
                            if current_count >= total_expected:
                                break
                            video_ids.append(item['id']['videoId'])
                            channel_ids.append(item['snippet']['channelId'])
                            current_count += 1
                            
                        # 비디오와 채널 정보 가져오기
                        try:
                            videos_response, channels_response = await self.process_video_batch(session, video_ids, channel_ids)
                        except Exception as e:
                            print(f"비디오/채널 정보 가져오기 실패: {str(e)}")  # 디버깅용
                            error_str = str(e).lower()
                            if 'quota' in error_str and 'exceeded' in error_str:
                                self.error.emit("API_QUOTA_EXCEEDED", 0)
                            else:
                                self.error.emit(f"데이터 수집 중 오류: {str(e)}", 0)
                            return

                        # 채널 정보를 딕셔너리로 변환
                        channels_dict = {
                            channel['id']: channel
                            for channel in channels_response.get('items', [])
                        }
                        
                        # 썸네일 다운로드 작업 준비
                        thumbnail_tasks = []
                        for item in items:
                            thumb = item['snippet']['thumbnails'].get('default', 
                                    item['snippet']['thumbnails'].get('high'))
                            if thumb:
                                task = self.fetch_thumbnail(session, thumb['url'])
                                thumbnail_tasks.append(task)
                        
                        # 썸네일 병렬 다운로드
                        thumbnail_results = await asyncio.gather(*thumbnail_tasks)
                        
                        # 결과 처리
                        for idx, search_result in enumerate(items):
                            if current_count > total_expected:
                                break
                                
                            video_id = search_result['id']['videoId']
                            channel_id = search_result['snippet']['channelId']
                            
                            video_info = next((v for v in videos_response['items'] if v['id'] == video_id), None)
                            channel_info = channels_dict.get(channel_id)
                            
                            if video_info and channel_info:
                                result = self.process_video_data(search_result, video_info, channel_info)
                                result['thumbnail_data'] = thumbnail_results[idx]
                                results.append(result)
                                
                                progress = min(98, int((len(results) / total_expected) * 98))
                                self.progress.emit(f"데이터 수집 중... ({len(results)}/{total_expected})", progress)
                        
                        next_page_token = search_response.get('nextPageToken')
                        if not next_page_token or len(results) >= total_expected:
                            break
                            
                if self.is_running:
                    self.progress.emit("데이터 처리 중...", 99)
                    self.finished.emit(results[:total_expected])
                    
            except Exception as e:
                if 'quotaExceeded' in str(e):
                    self.error.emit("API_QUOTA_EXCEEDED", 0)
                else:
                    self.error.emit(f"예상치 못한 오류: {str(e)}", 0)

        # Windows에서 이벤트 루프 실행
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
        except Exception as e:
            self.error.emit(str(e), 0)
        finally:
            loop.close()
    
    def stop(self):
        self.is_running = False
        
class YouTubeAnalyzer(QMainWindow):    
        
    def on_header_clicked(self, section):
        if section == 0:  # N열 클릭시
            # 현재 선택 상태 확인
            any_selected = False
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item and item.background().color() == QColor("#FF5D5D"):
                    any_selected = True
                    break
            
            # 상태에 따라 전체 선택/해제
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item:
                    item.setBackground(QColor("#f5f5f5") if any_selected else QColor("#FF5D5D"))
                    item.setForeground(QColor("black") if any_selected else QColor("white"))
            
            # URL 목록 업데이트
            self.selected_urls = []
            if not any_selected:  # 전체 선택 시
                for row in range(self.table.rowCount()):
                    if row < len(self.search_results):
                        self.selected_urls.append(self.search_results[row]['video_url'])
            
            
    
    def toggle_column(self, column, checked):
        self.table.setColumnHidden(column, not checked)
        # 설정 즉시 저장
        settings = {}
        for i in range(self.table.columnCount()):
            settings[str(i)] = not self.table.isColumnHidden(i)
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"설정 저장 실패: {str(e)}")
            
    def toggle_all_columns(self, show):
        # 모든 컬럼을 순회하면서 표시/숨김 처리
        # 0번 컬럼(N)은 제외하고 처리
        for i in range(1, len(self.headers)):
            self.table.setColumnHidden(i, not show)
    
       
    def show_thumbnail_dialog(self, video_url, current_thumbnail):
        dialog = QDialog(self)
        dialog.setWindowTitle("썸네일 상세보기")
        dialog.setFixedSize(800, 600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
        """)

        layout = QVBoxLayout(dialog)

        # 썸네일 표시 영역
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 고화질 썸네일 로드
        video_id = video_url.split('v=')[1]
        qualities = [
            'maxresdefault.jpg',  # 최고화질
            'sddefault.jpg',      # 표준화질
            'hqdefault.jpg'       # 고화질
        ]

        loaded = False
        loaded_url = None  # 성공적으로 로드된 URL 저장
        for quality in qualities:
            try:
                url = f"https://img.youtube.com/vi/{video_id}/{quality}"
                response = urllib.request.urlopen(url)
                data = response.read()
                pixmap = QPixmap()
                if pixmap.loadFromData(data):
                    # 다이얼로그 크기에 맞게 스케일링
                    scaled_pixmap = pixmap.scaled(
                        760, 480,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    image_label.setPixmap(scaled_pixmap)
                    loaded = True
                    loaded_url = url  # 성공한 URL 저장
                    break
            except Exception:
                continue

        if not loaded:
            image_label.setPixmap(current_thumbnail)

        layout.addWidget(image_label)

        # 버튼 컨테이너
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)

        # URL 복사 버튼
        copy_url_btn = QPushButton("영상 URL 복사")
        def copy_url():
            QApplication.clipboard().setText(video_url)
            copy_url_btn.setText("복사 완료!")
            QTimer.singleShot(1500, lambda: copy_url_btn.setText("영상 URL 복사"))
        copy_url_btn.clicked.connect(copy_url)

        # 원본 이미지 저장 버튼
        save_btn = QPushButton("원본 이미지 저장")
        def save_image():
            if loaded_url:  # 고화질 이미지 URL이 있는 경우
                try:
                    # 이미지 다운로드
                    response = urllib.request.urlopen(loaded_url)
                    original_data = response.read()
                    
                    file_name, _ = QFileDialog.getSaveFileName(
                        dialog,
                        "원본 썸네일 저장",
                        f"thumbnail_{video_id}.jpg",
                        "Images (*.jpg *.png)"
                    )
                    if file_name:
                        with open(file_name, 'wb') as f:
                            f.write(original_data)
                        save_btn.setText("저장 완료!")
                        QTimer.singleShot(1500, lambda: save_btn.setText("원본 이미지 저장"))
                except Exception as e:
                    QMessageBox.warning(dialog, "저장 오류", f"이미지 저장 중 오류가 발생했습니다: {str(e)}")
            else:
                QMessageBox.warning(dialog, "저장 오류", "원본 이미지를 불러올 수 없습니다.")
        save_btn.clicked.connect(save_image)

        # 닫기 버튼
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(dialog.close)

        # 버튼 추가
        button_layout.addWidget(copy_url_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(close_btn)

        layout.addWidget(button_container)
        dialog.exec()
    def format_transcript_text(self, text):
        if not text or text == "자막 없음":
            return text

        # 줄 단위로 처리
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            # 앞뒤 공백 제거
            line = line.strip()
            
            # 빈 줄 스킵
            if not line:
                continue
                
            # 불필요한 여러 공백을 하나로
            line = ' '.join(line.split())
            
            # 문장 부호로 끝나지 않는 경우 처리
            if line and not line[-1] in '.!?':
                line += '.'
                
            formatted_lines.append(line)
        
        # 적절한 간격으로 문장들 결합
        return '\n\n'.join(formatted_lines)
    def __init__(self):
        super().__init__()
        self.history_manager = HistoryManager()
        
        # 다운로드 설정 초기화
        self.download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        
        # 검색 관련 변수들 먼저 초기화
        self.search_results = []
        self.original_results = []
        self.search_worker = None
        
        # API 키 매니저 초기화
        self.api_manager = APIKeyManager()
        self.gemini_api_manager = GeminiAPIKeyManager()
        
        # 지연 로딩 관리자 초기화
        self.lazy_load_manager = LazyLoadManager()

        # 인증 매니저 초기화
        self.auth_manager = AuthManager()        
        
        
        # 비디오 링크 초기화
        self.video_links = get_video_links()        
        
        self.selected_urls = []     
        
        
                
        
        
        
                                
        # auth_info.json이 없거나 인증되지 않은 경우에만 인증키 입력 요청
        if (not os.path.exists('auth_info.json')) or (not self.auth_manager.is_authenticated()):
            key, ok = QInputDialog.getText(
                self, 
                '인증키 입력', 
                '프로그램을 사용하려면 인증키가 필요합니다.\n인증키를 입력해주세요:',
                QLineEdit.EchoMode.Normal
            )
            if not ok or not key:
                sys.exit()
                
            self.validate_and_set_auth_key(key)
        
        # 만료 임박 확인
        expiry_date_str = self.auth_manager.get_expiry_date()
        if expiry_date_str:
            try:
                expiry_date = datetime.fromisoformat(expiry_date_str).date()
                current_date = datetime.now().date()
                days_left = (expiry_date - current_date).days
                
                if 0 < days_left <= 7:
                    dialog = QDialog(self)
                    dialog.setWindowTitle("만료 예정")
                    dialog.setFixedSize(400, 180)
                    dialog.setStyleSheet("""
                        QDialog {
                            background-color: #1a1a1a;
                            color: white;
                            border-radius: 10px;
                        }
                        QLabel {
                            color: white;
                            font-size: 13px;
                        }
                        QPushButton {
                            color: white;
                            border: none;
                            padding: 8px 20px;
                            border-radius: 5px;
                            font-weight: bold;
                            font-size: 13px;
                            min-width: 100px;
                        }
                        QPushButton#homeButton {
                            background-color: #4a9eff;
                        }
                        QPushButton#homeButton:hover {
                            background-color: #3d8ae0;
                        }
                        QPushButton#confirmButton {
                            background-color: #666666;
                        }
                        QPushButton#confirmButton:hover {
                            background-color: #555555;
                        }
                    """)

                    # 메인 레이아웃 생성
                    layout = QVBoxLayout()
                    dialog.setLayout(layout)
                    layout.setSpacing(15)
                    layout.setContentsMargins(20, 20, 20, 20)

                    # 메시지 레이블
                    message = QLabel(f"프로그램 기한이 {days_left}일 남았습니다.\n계속 사용하시려면 새로운 인증키를\n아래 홈페이지에서 발급받으세요.")
                    message.setWordWrap(True)
                    message.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    message.setStyleSheet("font-weight: bold;")
                    layout.addWidget(message)

                    # 버튼 컨테이너
                    button_container = QWidget()
                    button_layout = QVBoxLayout(button_container)
                    button_layout.setSpacing(10)
                    button_layout.setContentsMargins(0, 0, 0, 0)

                    # 홈페이지 버튼
                    home_button = QPushButton("TUBE LENS 홈페이지 바로가기")
                    home_button.setObjectName("homeButton")
                    home_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://tubelens-0o0opqa.gamma.site/")))
                    button_layout.addWidget(home_button)

                    # 확인 버튼
                    confirm_button = QPushButton("확인")
                    confirm_button.setObjectName("confirmButton")
                    confirm_button.clicked.connect(dialog.accept)
                    button_layout.addWidget(confirm_button)

                    layout.addWidget(button_container)

                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                    dialog.exec()

            except Exception as e:
                print(f"만료일 확인 중 오류: {str(e)}")

        # 타이틀 설정
        title = "Tube Lens"
        if expiry_date_str:
            expiry_date = datetime.fromisoformat(expiry_date_str).date()
            current_date = datetime.now().date()
            days_left = (expiry_date - current_date).days
            title += f" - 만료일: {expiry_date_str[:10]} (남은 기간: {days_left}일)"
        self.setWindowTitle(title)
        
        # 프로그램 아이콘 설정
        try:
            app_icon = QIcon(get_resource_path("images/tubelens.png"))
            self.setWindowIcon(app_icon)
        except Exception as e:
            print(f"아이콘 로딩 오류: {str(e)}")
        self.setGeometry(100, 100, 1820, 800)
        
        # 화면 중앙에 위치시키기
        screen = QApplication.primaryScreen().availableGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.setGeometry(x, y, 1650, 800)
        
        # 설정 파일 경로 (프로그램 디렉토리의 config.json 사용)
        self.settings_file = 'config.json'
        
        # UI 초기화 (마지막에)
        self.init_ui()
        
        # 구글 로그인 상태 확인
        if hasattr(self, 'google_login_button'):
            self.google_login_button.setText("로그아웃" if self.auth_manager.is_google_logged_in() else "구글 로그인")
            
    def validate_and_set_auth_key(self, key):
        try:
            # Firebase에서 라이센스 키 확인
            ref = db.reference('/라이센스')
            licenses = ref.get()
            
            if not licenses:
                QMessageBox.critical(self, "오류", "라이센스 정보를 찾을 수 없습니다.")
                return False
            
            input_key = key.replace('-', '')  # 하이픈 제거
            current_computer_id = self.auth_manager.generate_computer_id()
            
            # 라이센스 확인
            license_info = None
            license_id = None
            
            for lid, data in licenses.items():
                if data['라이센스키'] == input_key:
                    license_info = data
                    license_id = lid
                    break
                    
            if not license_info:
                reply = QMessageBox.critical(
                    self, 
                    "오류",
                    "유효하지 않은 인증키입니다.\n새로운 인증키를 입력하시겠습니까?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    key, ok = QInputDialog.getText(
                        self, 
                        '인증키 입력', 
                        '새로운 인증키를 입력해주세요:',
                        QLineEdit.EchoMode.Normal
                    )
                    if ok and key:
                        return self.validate_and_set_auth_key(key)
                sys.exit()
                return False
            
            # 컴퓨터 ID 검증
            if '컴퓨터ID' in license_info and license_info['컴퓨터ID']:
                stored_computer_id = license_info['컴퓨터ID']
                if stored_computer_id != current_computer_id:
                    reply = QMessageBox.critical(
                        self, 
                        "오류", 
                        "이 라이센스 키는 이미 다른 컴퓨터에서 사용 중입니다.\n"
                        "새로운 인증키를 입력하시겠습니까?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        key, ok = QInputDialog.getText(
                            self, 
                            '인증키 입력', 
                            '새로운 인증키를 입력해주세요:',
                            QLineEdit.EchoMode.Normal
                        )
                        if ok and key:
                            return self.validate_and_set_auth_key(key)
                    sys.exit()
                    return False
            
            # 만료일 검증
            expiry_date = datetime.strptime(license_info['만료일'], "%Y-%m-%d").date()
            current_date = datetime.now().date()
            
            if current_date > expiry_date:
                reply = QMessageBox.critical(
                    self, 
                    "오류",
                    "만료된 인증키입니다.\n새로운 인증키를 입력하시겠습니까?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    key, ok = QInputDialog.getText(
                        self, 
                        '인증키 입력', 
                        '새로운 인증키를 입력해주세요:',
                        QLineEdit.EchoMode.Normal
                    )
                    if ok and key:
                        return self.validate_and_set_auth_key(key)
                sys.exit()
                return False
            
            # 모든 검증을 통과한 경우 Firebase 업데이트
            ref.child(license_id).update({
                '컴퓨터ID': current_computer_id,
                '활성화상태': "사용중"
            })
            
            # 인증키 설정
            days_left = (expiry_date - current_date).days
            self.auth_manager.set_auth_key(key, expiry_date.strftime("%Y-%m-%d"))
            
            QMessageBox.information(
                self, 
                "인증 성공",
                f"인증이 완료되었습니다.\n만료일: {expiry_date.strftime('%Y-%m-%d')}\n남은 기간: {days_left}일"
            )
            
            return True
                    
        except Exception as e:
            QMessageBox.critical(self, "오류", f"인증키 확인 중 오류가 발생했습니다: {str(e)}")
            return False
    def init_ui(self):
        self.undo_stack = []
        self.downloading_type = None  # 여기에 추가
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
            }
            QTableWidget {
                background-color: white;
            }
        """)
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        
        # 왼쪽 사이드바 설정
        self.setup_sidebar()
        
        # 테이블 영역 설정
        self.setup_table_area()
        
    def setup_sidebar(self):
        sidebar = QWidget()
        screen = QApplication.primaryScreen().availableGeometry()

        # 기본 사이드바 설정
        default_width = 300
        default_height = 800

        # 화면 크기에 따른 스케일 계산
        scale_factor = min(screen.height() / default_height, 1.0)

        # 스케일된 크기 계산
        scaled_width = int(default_width * scale_factor)

        # 사이드바 크기 설정
        sidebar.setFixedWidth(scaled_width)

        # 전역 스타일 설정을 위한 글로벌 변수 저장
        self.ui_scale = scale_factor  # 클래스의 멤버 변수로 저장

        base_height = 36  # 기본 높이값
        scaled_height = int(base_height * scale_factor)  # 스케일된 높이

        style = f"""
            QWidget#sidebar {{
                background-color: #1a1a1a;
            }}
            QPushButton, QComboBox, QLineEdit, QDateEdit {{
                min-height: {scaled_height}px; 
                max-height: {scaled_height}px;
            }}
            QGroupBox {{
                margin-top: {int(10*scale_factor)}px;
                padding: {int(5*scale_factor)}px;
            }}
            * {{
                font-size: {int(12*scale_factor)}px;
            }}
        """
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(style)

        # 레이아웃 설정
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(int(4 * scale_factor))
        sidebar_layout.setContentsMargins(
            int(5*scale_factor),
            int(5*scale_factor),
            int(5*scale_factor),
            int(5*scale_factor)
        )
        
        # 기본 스타일 정의
        label_style = """
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 4px;
            }
        """
        
        button_style = """
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 8px;
                min-height: 36px;
                border-radius: 5px;
                border: none;
            }
        """
        
        input_style = """
            QLineEdit, QDateEdit {
                font-size: 12px;
                padding: 8px;
                min-height: 36px;
                background-color: #2d2d2d;
                color: white;
                border: none;
                border-radius: 5px;
            }

            QDateEdit::drop-down {
                border: none;
                width: 30px;
                background-color: transparent;
            }

            QDateEdit::down-arrow {
                background-color: transparent;
                image: none;
                font-size: 14px;
                padding: 0;
                margin: 0;
                border-top: 8px solid white;
                border-right: 5px solid transparent;
                border-left: 5px solid transparent;
            }

            QCalendarWidget {
                background-color: white;
            }

            /* 달력 위쪽 툴바 */
            QCalendarWidget QToolBar {
                background-color: white;
                color: black;
            }

            /* 달력 테이블 */
            QCalendarWidget QTableView {
                alternate-background-color: white;
                background-color: white;
                selection-background-color: #4a9eff;
                selection-color: white;
                color: black;
            }

            /* 달력 셀 */
            QCalendarWidget QTableView::item {
                color: black;
                background: white;
            }

            /* 달력 상단 네비게이션 바 */
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: white;
            }

            /* 달력 상단 버튼들 */
            QCalendarWidget QToolButton {
                background-color: white;
                color: black;
            }

            /* 요일 헤더 */
            QCalendarWidget QHeaderView {
                background-color: white;
                color: black;
            }

            /* 날짜 선택 */
            QCalendarWidget QTableView::item:selected {
                background-color: #4a9eff;
                color: white;
            }

            /* 이전/다음 달의 날짜 */
            QCalendarWidget QTableView::item:alternate {
                color: #808080;
            }
        """

        combobox_style = """
            QComboBox {
                font-size: 12px;
                padding: 4px;
                min-height: 36px;
                background-color: #2d2d2d;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid white;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: white;
                selection-background-color: #404040;
            }
            QComboBox::item {
                color: white;
                padding: 5px;
            }
            QComboBox::item:selected {
                background-color: #4a9eff;
            }
        """

        checkbox_style = """
            QCheckBox {
                color: white;
                font-size: 12px;
                padding: 4px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2d2d2d;
                border: 2px solid #4a9eff;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #4a9eff;
                border: 2px solid #4a9eff;
                border-radius: 3px;
                image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'%3E%3C/polyline%3E%3C/svg%3E");
            }
        """
        
        groupbox_style = f"""
            QGroupBox {{
                font-size: {int(13*self.ui_scale)}px;
                font-weight: bold;
                color: white;
                border: 1px solid #4a9eff;
                border-radius: {int(5*self.ui_scale)}px;
                margin-top: {int(8*self.ui_scale)}px;
                padding-top: {int(10*self.ui_scale)}px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1f1f1f, stop:1 #1a1a1a);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 {int(10*self.ui_scale)}px;
                color: #4a9eff;
            }}
        """
        
        # API 키 관리와 추가기능 버튼을 위한 컨테이너
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(8, 0, 8, 8)
                
        # API 키 관리 버튼
        api_key_button = QPushButton("⚙️ 설정")
        api_key_button.setFixedWidth(140)
        api_key_button.setFixedHeight(20)
        api_key_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #4a9eff;
                color: white;
                margin-left: 4px;
                margin-right: 4px;
                font-size: 14px;
                width: 100%;
                min-height: 15px !important;
                max-height: px !important;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
        """)
        api_key_button.clicked.connect(self.show_api_key_dialog)
        
        # 인증키 업데이트 시 설정 창의 API 키 목록도 새로고침
        def refresh_api_keys():
            self.update_table()
        api_key_button.clicked.connect(refresh_api_keys)

        # 실시간 검색어 버튼
        realtime_trend_button = QPushButton("🔍 실시간 검색어")
        realtime_trend_button.setFixedWidth(140)
        realtime_trend_button.setFixedHeight(20)
        realtime_trend_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                margin-left: 4px;
                margin-right: 4px;
                font-size: 14px;
                width: 100%;
                min-height: 15px !important;
                max-height: px !important;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        realtime_trend_button.clicked.connect(self.show_realtime_trends)

        button_layout.addWidget(api_key_button)
        button_layout.addWidget(realtime_trend_button)
        sidebar_layout.addWidget(button_container)
        sidebar_layout.addSpacing(10)

        def setup_combobox(combobox):
            combobox.setStyleSheet("""
                QComboBox {
                    background-color: #2d2d2d;
                    color: white;
                    border-radius: 5px;
                    border: none;
                    padding: 4px;
                    min-height: 30px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 4px solid white;
                    margin-right: 8px;
                }
                QComboBox QAbstractItemView {
                    background-color: #2d2d2d;
                    color: white;
                }
                QComboBox::item {
                    color: white;
                    padding: 5px;
                }
                QComboBox::item:selected {
                    background-color: #4a9eff;
                }
            """)
        
        # 검색 설정 그룹
        search_group = QGroupBox("[검색 설정]")
        search_group.setStyleSheet(f"""
            QGroupBox {{
                color: white;
                font-weight: bold;
                border: 1px solid #4a9eff;
                border-radius: 5px;
                margin-top: {int(8*self.ui_scale)}px;
                padding: {int(5*self.ui_scale)}px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1f1f1f, stop:1 #1a1a1a);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                color: #4a9eff;
            }}
        """)
        search_layout = QVBoxLayout(search_group)
        search_layout.setSpacing(int(8 * self.ui_scale))

        # 정렬 버튼들을 담을 컨테이너
        sort_container = QWidget()
        sort_layout = QHBoxLayout(sort_container)
        sort_layout.setSpacing(int(5 * self.ui_scale))
        sort_layout.setContentsMargins(0, 0, 0, 0)

        # 정렬 버튼 생성
        self.sort_latest = QPushButton("최신순")
        self.sort_views = QPushButton("조회수순")

        # 버튼 설정 및 스타일 적용
        for btn in [self.sort_latest, self.sort_views]:
            btn.setCheckable(True)
            btn.setMinimumHeight(30)  # 최소 높이만 설정
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #2d2d2d;
                    color: white;
                    border-radius: {int(3*self.ui_scale)}px;
                    border: none;
                    font-size: {int(11*self.ui_scale)}px;
                    padding: {int(2*self.ui_scale)}px;
                    min-width: {int(120*self.ui_scale)}px;
                }}
                QPushButton:checked {{
                    background-color: #4a9eff;
                }}
            """)
            sort_layout.addWidget(btn)

        search_layout.addWidget(sort_container)
        
        # 조회수순을 기본값으로 설정
        self.sort_views.setChecked(True)
        
        # 버튼 클릭 시 동작
        def on_sort_button_clicked():
            sender = self.sender()
            for btn in [self.sort_latest, self.sort_views]:
                btn.setChecked(btn == sender)

        # 버튼 클릭 이벤트 연결
        self.sort_latest.clicked.connect(on_sort_button_clicked)
        self.sort_views.clicked.connect(on_sort_button_clicked)
        

        search_layout.addWidget(sort_container)
        search_layout.addSpacing(5)
        
        

        # 영상 수집 수
        video_count_label = QLabel("영상 수집 수")
        video_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        video_count_label.setStyleSheet("color: white;")
        self.video_count = QComboBox()
        self.video_count.addItems(["50개", "100개", "200개", "500개"])
        self.video_count.setCurrentText("100개")
        search_layout.addWidget(video_count_label)
        search_layout.addWidget(self.video_count)
        search_layout.addSpacing(5)

        # 기간 선택
        time_frame_label = QLabel("기간 선택")
        time_frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_frame_label.setStyleSheet("color: white;")
        self.time_frame = QComboBox()
        self.time_frame.addItems([
            "모든 기간", "1년 이내", "6개월 이내", "3개월 이내", 
            "1개월 이내", "7일 이내", "날짜 직접 선택"
        ])
        self.time_frame.setCurrentText("1개월 이내")
        self.time_frame.currentTextChanged.connect(self.on_time_frame_changed)
        search_layout.addWidget(time_frame_label)
        search_layout.addWidget(self.time_frame)
        search_layout.addSpacing(5)

        # 날짜 선택 컨테이너
        self.date_input_container = QWidget()
        date_input_layout = QHBoxLayout(self.date_input_container)
        date_input_layout.setSpacing(10)  # 간격 늘림
        date_input_layout.setContentsMargins(5, 5, 5, 5)  # 여백 추가

        # 시작일 부분
        start_container = QWidget()
        start_layout = QHBoxLayout(start_container)
        start_layout.setSpacing(5)
        start_layout.setContentsMargins(0, 0, 0, 0)

        self.start_date = QLineEdit()
        self.start_date.setPlaceholderText("시작일")
        self.start_date.setFixedWidth(120)  # 너비 조정
        self.start_date.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
        """)

        start_calendar_btn = QPushButton("📅")
        start_calendar_btn.setFixedSize(30, 30)
        start_calendar_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #404040;
                border-radius: 5px;
            }
        """)
        start_calendar_btn.clicked.connect(lambda: self.show_calendar(self.start_date))

        start_layout.addWidget(self.start_date)
        start_layout.addWidget(start_calendar_btn)

        # 종료일 부분
        end_container = QWidget()
        end_layout = QHBoxLayout(end_container)
        end_layout.setSpacing(5)
        end_layout.setContentsMargins(0, 0, 0, 0)

        self.end_date = QLineEdit()
        self.end_date.setPlaceholderText("종료일")
        self.end_date.setFixedWidth(120)  # 너비 조정
        self.end_date.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
        """)

        end_calendar_btn = QPushButton("📅")
        end_calendar_btn.setFixedSize(30, 30)
        end_calendar_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #404040;
                border-radius: 5px;
            }
        """)
        end_calendar_btn.clicked.connect(lambda: self.show_calendar(self.end_date))

        end_layout.addWidget(self.end_date)
        end_layout.addWidget(end_calendar_btn)

        # 전체 레이아웃에 추가
        date_input_layout.addWidget(start_container)
        date_input_layout.addWidget(end_container)

        # date_input_container를 메인 레이아웃에 추가하고 숨김
        search_layout.addWidget(self.date_input_container)
        self.date_input_container.hide()

        # 검색어 입력
        search_label = QLabel("검색어 입력")
        search_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_label.setStyleSheet("color: white;")
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.start_search)
        self.search_input.setPlaceholderText("검색어를 입력하세요")
        self.search_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #f0f0f0;
                color: #333333;
                font-size: {int(13*self.ui_scale)}px;
                font-weight: bold;
                border: 2px solid #4a9eff;
                border-radius: 5px;
                padding: {int(4*self.ui_scale)}px;
                min-height: {int(30*self.ui_scale)}px;
            }}
            QLineEdit::placeholder {{
                color: #666666;
            }}
        """)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addSpacing(10)  # 버튼과의 간격 조정

        # 검색/Clear 버튼 레이아웃
        button_layout = QHBoxLayout()
        button_layout.setSpacing(int(5 * self.ui_scale))  # 버튼 사이 간격 조정

        search_button = QPushButton("검색")
        search_button.setFixedHeight(int(35 * self.ui_scale))  # 버튼 높이 조정
        search_button.clicked.connect(self.start_search)
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #ff69b4;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4da6;
            }
        """)

        clear_button = QPushButton("Clear")
        clear_button.setFixedHeight(int(35 * self.ui_scale))  # 버튼 높이 조정
        clear_button.clicked.connect(self.clear_results)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)

        button_layout.addWidget(search_button)
        button_layout.addWidget(clear_button)
        search_layout.addLayout(button_layout)

        sidebar_layout.addWidget(search_group)
        
        # 구분선
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #333;")
        sidebar_layout.addWidget(line)
        
        # 필터 설정 그룹
        filter_group = QGroupBox("[필터 설정]")
        filter_group.setStyleSheet(f"""
            QGroupBox {{
                color: white;
                font-weight: bold;
                border: 1px solid #4a9eff;
                border-radius: 5px;
                margin-top: {int(8*self.ui_scale)}px;
                padding: {int(5*self.ui_scale)}px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1f1f1f, stop:1 #1a1a1a);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                color: #4a9eff;
            }}
        """)

        filter_layout = QVBoxLayout(filter_group)
        filter_layout.setSpacing(int(8 * self.ui_scale))

        # 체크박스 버튼 스타일
        shortslong_style = f"""
            QPushButton {{
                background-color: #2d2d2d;
                color: white;
                min-width: {int(100*self.ui_scale)}px;
                border-radius: 5px;
                border: none;
                padding: {int(5*self.ui_scale)}px;
            }}
            QPushButton:checked {{
                background-color: #4a9eff;
            }}
        """

        # CII 버튼 스타일
        cii_style = f"""
            QPushButton {{
                background-color: #2d2d2d;
                color: white;
                min-width: {int(70*self.ui_scale)}px;
                max-width: {int(70*self.ui_scale)}px;
                border-radius: 5px;
                border: none;
                padding: {int(5*self.ui_scale)}px;
            }}
            QPushButton:checked {{
                background-color: #4a9eff;
            }}
        """

        # 체크박스 버튼 생성
        self.shorts_checkbox = QPushButton("쇼츠")
        self.shorts_checkbox.setCheckable(True)
        self.shorts_checkbox.setStyleSheet(shortslong_style)

        self.longform_checkbox = QPushButton("롱폼")
        self.longform_checkbox.setCheckable(True)
        self.longform_checkbox.setStyleSheet(shortslong_style)

        # CII 버튼 생성
        self.cii_great = QPushButton("Great!!")
        self.cii_great.setCheckable(True)
        self.cii_great.setStyleSheet(cii_style)

        self.cii_good = QPushButton("Good")
        self.cii_good.setCheckable(True)
        self.cii_good.setStyleSheet(cii_style)

        self.cii_soso = QPushButton("Soso")
        self.cii_soso.setCheckable(True)
        self.cii_soso.setStyleSheet(cii_style)

        # 조회수 필터
        self.view_count = QComboBox()
        self.view_count.setStyleSheet(combobox_style)
        self.view_count.addItems([
            "선택 안함", "1만 이상", "5만 이상",
            "10만 이상", "50만 이상", "100만 이상"
        ])
        self.view_count.setFixedWidth(140)

        # 구독자 수 필터
        self.subscriber_count = QComboBox()
        self.subscriber_count.setStyleSheet(combobox_style)
        self.subscriber_count.addItems([
            "선택 안함", "1천명 이하", "5천명 이하",
            "1만명 이하", "5만명 이하", "10만명 이하"
        ])
        self.subscriber_count.setFixedWidth(140)
        
        # 클릭 이벤트 처리 함수 추가
        def on_video_type_clicked():
            sender = self.sender()  # 클릭된 버튼 확인
            if sender == self.shorts_checkbox:
                if self.shorts_checkbox.isChecked():
                    self.longform_checkbox.setChecked(False)
            elif sender == self.longform_checkbox:
                if self.longform_checkbox.isChecked():
                    self.shorts_checkbox.setChecked(False)

        # 버튼 클릭 이벤트 연결
        self.shorts_checkbox.clicked.connect(on_video_type_clicked)
        self.longform_checkbox.clicked.connect(on_video_type_clicked)

        # 비디오 유형 버튼 레이아웃
        video_type_layout = QHBoxLayout()
        video_type_layout.setSpacing(int(5 * self.ui_scale))
        video_type_layout.addWidget(self.shorts_checkbox)
        video_type_layout.addWidget(self.longform_checkbox)
        filter_layout.addLayout(video_type_layout)

        # CII 레이아웃
        cii_label = QLabel("콘텐츠 영향력 지수")
        cii_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cii_label.setStyleSheet("color: white;")
        filter_layout.addWidget(cii_label)

        cii_layout = QHBoxLayout()
        cii_layout.setSpacing(int(2 * self.ui_scale))
        cii_layout.addWidget(self.cii_great)
        cii_layout.addWidget(self.cii_good)
        cii_layout.addWidget(self.cii_soso)
        filter_layout.addLayout(cii_layout)

        # 조회수와 구독자 수를 담을 수평 컨테이너 (가운데 정렬을 위해 전체를 감싸는 컨테이너)
        counts_row = QWidget()
        counts_layout = QHBoxLayout(counts_row)
        counts_layout.setContentsMargins(0, 0, 0, 0)  # 좌우 여백 10씩 추가하여 가운데 정렬 효과
        counts_layout.setSpacing(6)  # 조회수와 구독자 수 사이 간격
        counts_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 전체 내용 가운데 정렬

        # 조회수 필터 컨테이너 설정
        view_container = QWidget()
        view_layout = QVBoxLayout(view_container)
        view_layout.setContentsMargins(0, 0, 0, 0)  # 컨테이너 내부 여백 제거
        view_layout.setSpacing(2)  # 라벨과 콤보박스 사이 간격
        view_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 내부 내용 가운데 정렬

        # 조회수 라벨 설정
        view_count_label = QLabel("조회수")
        view_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        view_count_label.setStyleSheet("""
            color: white;
            font-size: 12px;
            padding: 2px;
        """)
        view_layout.addWidget(view_count_label)

        # 조회수 콤보박스 크기 및 스타일 설정
        self.view_count.setFixedSize(126, 30)  # 가로 110, 세로 30으로 고정
        self.view_count.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
                min-height: 30px;
            }
        """)
        view_layout.addWidget(self.view_count)

        # 구독자 수 필터 컨테이너 설정 (조회수와 동일한 구조)
        sub_container = QWidget()
        sub_layout = QVBoxLayout(sub_container)
        sub_layout.setContentsMargins(0, 0, 0, 0)
        sub_layout.setSpacing(2)
        sub_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 구독자 수 라벨 설정
        subscriber_count_label = QLabel("구독자 수")
        subscriber_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subscriber_count_label.setStyleSheet("""
            color: white;
            font-size: 12px;
            padding: 2px;
        """)
        sub_layout.addWidget(subscriber_count_label)

        # 구독자 수 콤보박스 크기 및 스타일 설정 (조회수와 완전히 동일하게)
        self.subscriber_count.setFixedSize(126, 30)  # 조회수와 동일한 크기
        self.subscriber_count.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
                min-height: 28px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid white;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: white;
                selection-background-color: #404040;
            }
            QComboBox::item {
                color: white;
                padding: 5px;
            }
            QComboBox::item:selected {
                background-color: #4a9eff;
            }
        """)
        sub_layout.addWidget(self.subscriber_count)

        # 컨테이너들을 수평 레이아웃에 추가
        counts_layout.addWidget(view_container)
        counts_layout.addWidget(sub_container)

        # 전체를 필터 레이아웃에 추가
        filter_layout.addWidget(counts_row)

        # 필터 버튼 스타일
        filter_btn_style = f"""
            QPushButton {{
                padding: {int(4*self.ui_scale)}px;
                border-radius: 5px;
                border: none;
                color: white;
                font-weight: bold;
            }}
        """

        # 필터 적용/해제 버튼
        filter_button_layout = QHBoxLayout()
        filter_button_layout.setSpacing(int(5 * self.ui_scale))

        apply_filter_button = QPushButton("필터 적용")
        apply_filter_button.clicked.connect(self.apply_filter)        
        apply_filter_button.setStyleSheet(filter_btn_style + """
                                          
            QPushButton {
                background-color: #ff69b4;
            }
            QPushButton:hover {
                background-color: #ff4da6;
            }
        """)

        clear_filter_button = QPushButton("필터 해제")
        clear_filter_button.clicked.connect(self.clear_filter)
        clear_filter_button.setStyleSheet(filter_btn_style + """
            QPushButton {
                background-color: #4CAF50;
            }
            QPushButton:hover {
                background-color: #43a047;
            }
        """)

        filter_button_layout.addWidget(apply_filter_button)
        filter_button_layout.addWidget(clear_filter_button)
        filter_layout.addLayout(filter_button_layout)

        # 자막 수집 버튼
        self.collect_subtitle_btn = QPushButton("자막 수집")
        self.collect_subtitle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #4a9eff;
                color: white;
                margin: {int(2*self.ui_scale)}px {int(1*self.ui_scale)}px;
                border-radius: 5px;
                border: none;
                min-height: {int(30*self.ui_scale)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #3d8ae0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """)
        self.collect_subtitle_btn.clicked.connect(self.collect_subtitles)
        filter_layout.addWidget(self.collect_subtitle_btn) 
                
        
        sidebar_layout.addWidget(filter_group)
        
        # 상태 표시 영역
        status_container = QWidget()
        status_layout = QVBoxLayout(status_container)
        
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                margin: 10px;
            }
        """)
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                background-color: #2d2d2d;
            }
            QProgressBar::chunk {
                background-color: #4a9eff;
                border-radius: 5px;
            }
        """)
        
        status_layout.addWidget(self.progress_bar)
        sidebar_layout.addWidget(status_container)
        self.main_layout.addWidget(sidebar)

        # 각 콤보박스에 스타일 적용
        setup_combobox(self.video_count)
        setup_combobox(self.time_frame)
        setup_combobox(self.view_count)
    
    def download_from_url(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "경고", "URL을 입력해주세요.")
            return
                
        # 저장 경로 선택
        save_path = QFileDialog.getExistingDirectory(
            self,
            "저장 위치 선택",
            os.path.join(os.path.expanduser('~'), 'Desktop'),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if save_path:
            try:
                ffmpeg_path = os.path.expandvars(r'%LOCALAPPDATA%\Programs\ffmpeg\bin\ffmpeg.exe')
                if not os.path.exists(ffmpeg_path):
                    QMessageBox.information(self, "정보", "FFmpeg 설치가 필요합니다. 설치를 시작합니다.")
                    self.install_ffmpeg()
                    if not os.path.exists(ffmpeg_path):
                        QMessageBox.warning(self, "경고", "FFmpeg 설치에 실패했습니다.")
                        return
                
                self.progress_bar.show()
                self.progress_bar.setValue(0)
                self.status_label.setText("다운로드 준비 중...")
                
                if not hasattr(self, 'download_workers'):
                    self.download_workers = []
                
                quality = self.quality_combo.currentText()
                worker = DownloadWorker(url, 'mp4', save_path, quality)
                
                worker.progress_signal.connect(lambda s, p: (
                    self.progress_bar.setValue(p),
                    self.status_label.setText(s)
                ))
                worker.finished_signal.connect(lambda: (
                    self.progress_bar.hide(),
                    self.status_label.setText(""),
                    QMessageBox.information(self, "완료", "다운로드가 완료되었습니다."),
                    QDesktopServices.openUrl(QUrl.fromLocalFile(save_path))
                ))
                worker.error_signal.connect(lambda e: (
                    QMessageBox.warning(self, "오류", f"다운로드 중 오류가 발생했습니다: {e}"),
                    self.progress_bar.hide(),
                    self.status_label.setText("")
                ))
                
                self.download_workers.append(worker)
                worker.start()
                    
            except Exception as e:
                QMessageBox.critical(self, "오류", f"다운로드 초기화 중 오류가 발생했습니다: {str(e)}")
                self.progress_bar.hide()
                self.status_label.setText("")
    
    def show_script_generator(self):
        """대본 생성기 다이얼로그 표시"""
        try:
            # API 키 확인
            try:
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    api_key = settings.get('google_ai_api_key')
                    if not api_key:
                        raise Exception("API 키가 설정되지 않았습니다.")
            except Exception as e:
                QMessageBox.warning(self, "경고", "Google AI Studio API 키를 설정에서 먼저 입력해주세요.")
                return

            # 선택된 행 확인
            selected_videos = []
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)  # N열 체크
                if item and item.background().color() == QColor("#FF5D5D"):
                    if row < len(self.search_results):
                        selected_videos.append(self.search_results[row])

            # 선택된 영상이 없으면 표시된 모든 영상 사용
            if not selected_videos:
                for row in range(self.table.rowCount()):
                    if not self.table.isRowHidden(row) and row < len(self.search_results):
                        selected_videos.append(self.search_results[row])

            if not selected_videos:
                QMessageBox.warning(self, "경고", "분석할 영상이 없습니다.")
                return

            # 대본 생성기 다이얼로그 표시
            dialog = ScriptGeneratorDialog(selected_videos, self)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "오류", f"대본 생성기 실행 중 오류가 발생했습니다: {str(e)}")

    
    def clear_results(self):
        # 결과 초기화
        if hasattr(self, 'search_results'):
            self.search_results = []
        if hasattr(self, 'original_results'):
            self.original_results = []
        
        # UI 초기화    
        if hasattr(self, 'table'):
            self.table.setRowCount(0)
        if hasattr(self, 'search_input'):
            self.search_input.clear()
        if hasattr(self, 'status_label'):
            self.status_label.setText("")
                    
        
        # 필터 초기화
        if hasattr(self, 'shorts_checkbox'):
            self.shorts_checkbox.setChecked(False)
        if hasattr(self, 'longform_checkbox'):
            self.longform_checkbox.setChecked(False)
        if hasattr(self, 'cii_great'):
            self.cii_great.setChecked(False)
        if hasattr(self, 'cii_good'):
            self.cii_good.setChecked(False)
        if hasattr(self, 'cii_soso'):
            self.cii_soso.setChecked(False)
        if hasattr(self, 'view_count'):
            self.view_count.setCurrentText("선택 안함")
        if hasattr(self, 'subscriber_count'):
            self.subscriber_count.setCurrentText("선택 안함")
            
        # 선택된 URL 초기화
        self.selected_urls = []

        
                    
        # 워터마크 투명도 설정
        for widget in self.findChildren(QLabel):
            if hasattr(widget, 'graphicsEffect') and isinstance(widget.graphicsEffect(), QGraphicsOpacityEffect):
                widget.graphicsEffect().setOpacity(0.8)
    
    def setup_table_area(self):
        # 바깥쪽 컨테이너 (진한 회색 배경)
        outer_container = QWidget()
        outer_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
            }
        """)
        outer_layout = QVBoxLayout(outer_container)
        
        # 테이블 컨테이너 (하얀색 배경)
        table_container = QWidget()
        table_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
            QTableWidget {
                background-color: white;
                color: black;
            }
            /* 개별 셀 배경색을 유지하기 위해 ::item 스타일 제거 */
            QHeaderView::section {
                background-color: #e6f3ff;
                color: black;
            }
            QTableCornerButton::section {
                background-color: #e6f3ff;
            }
        """)
        
        self.table_layout = QVBoxLayout(table_container)                
                
        # 컨트롤+F로 "# 버튼 컨테이너 추가" 라는 줄을 찾으세요.
# 그 아래의 button_container = QWidget() 부터
# button_layout.addWidget(mp3_button)  # MP3 버튼 추가 까지의 코드를 모두 지우고
# 아래 코드를 넣으세요.

        # 버튼 컨테이너 추가
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 5, 10, 5) #N열쪽 왼쪽정렬 첫번째꺼 숫자
        button_layout.setSpacing(5) #버튼사이 간격

        # 섹션 1: 보관 관련 버튼들 (하늘색 배경)
        section1 = QWidget()
        section1.setStyleSheet("background-color: #E3F2FD; border-radius: 5px; padding: 5px;")
        section1_layout = QHBoxLayout(section1)
        section1_layout.setSpacing(5)

        # 보관 버튼
        save_button = QPushButton("💾 보관")
        save_button.setFixedSize(80, 30)
        save_button.clicked.connect(self.save_current_state)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
        """)

        # 보관함 버튼
        history_button = QPushButton("📥 보관함")
        history_button.setFixedSize(80, 30)
        history_button.clicked.connect(self.show_history)
        history_button.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
        """)

        section1_layout.addWidget(save_button)
        section1_layout.addWidget(history_button)

        # 섹션 2: 다운로드 관련 버튼들 (연한 녹색 배경)
        section2 = QWidget()
        section2.setStyleSheet("background-color: #E8F5E9; border-radius: 5px; padding: 5px;")
        section2_layout = QHBoxLayout(section2)
        section2_layout.setSpacing(5)

        # MP4, MP3 다운로드 버튼 생성
        mp4_button = QPushButton("📺 MP4 다운")
        mp4_button.setFixedSize(100, 30)
        mp4_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        mp4_button.clicked.connect(lambda: self.start_download('mp4'))

        mp3_button = QPushButton("🎵 MP3 다운")
        mp3_button.setFixedSize(100, 30)
        mp3_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        mp3_button.clicked.connect(lambda: self.start_download('mp3'))

        # URL 입력창과 다운로드 버튼
        url_container = QWidget()
        url_layout = QHBoxLayout(url_container)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(5)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("YouTube URL 입력")
        self.url_input.setFixedWidth(200)
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
        """)
        self.url_input.returnPressed.connect(self.download_from_url)

        # 화질 선택 콤보박스 추가
        self.quality_combo = QComboBox()
        self.quality_combo.setFixedWidth(110)  # 너비를 조금 늘림
        self.quality_combo.setStyleSheet("""
            QComboBox {
                background-color: #f8f9fa;
                border: 2px solid #4a9eff;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 12px;
                font-weight: bold;
                color: #333;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #4a9eff;
                margin-right: 8px;
            }
            QComboBox:hover {
                background-color: #e9ecef;
                border-color: #3d8ae0;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #4a9eff;
                border-radius: 5px;
                selection-background-color: #4a9eff;
                selection-color: white;
            }
            QComboBox QAbstractItemView::item {
                padding: 5px 10px;
                min-height: 25px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e3f2fd;
            }
        """)

        # 아이콘과 함께 아이템 추가
        self.quality_combo.addItems([
            "⚡ 최고화질",
            "🎥 1080p",
            "📺 720p", 
            "📱 480p",
            "💻 360p"
        ])

        url_download_btn = QPushButton("URL 다운")
        url_download_btn.setFixedSize(80, 30)
        url_download_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        url_download_btn.clicked.connect(self.download_from_url)

        section2_layout.addWidget(mp4_button)
        section2_layout.addWidget(mp3_button)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(url_download_btn)
        url_layout.addWidget(self.quality_combo)
        section2_layout.addWidget(url_container)

        # 섹션 3: AI 추천과 실시간 검색어 버튼 (연한 보라색 배경)
        section3 = QWidget()
        section3.setStyleSheet("background-color: #F3E5F5; border-radius: 5px; padding: 5px;")
        section3_layout = QHBoxLayout(section3)
        section3_layout.setSpacing(5)

        # AI 추천 버튼
        ai_recommend_btn = QPushButton("🤖 AI 추천 아이디어")
        ai_recommend_btn.setFixedSize(125, 30)
        ai_recommend_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        ai_recommend_btn.clicked.connect(self.show_ai_recommendations)
        section3_layout.addWidget(ai_recommend_btn)

        # 타이틀 메이커 버튼 
        title_maker_btn = QPushButton("✏️ 타이틀 메이커")
        title_maker_btn.setFixedSize(125, 30)
        title_maker_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        title_maker_btn.clicked.connect(self.show_title_maker)
        section3_layout.addWidget(title_maker_btn)
        
        # 대본 생성기 버튼
        script_generator_btn = QPushButton("📝 분석 및 대본생성")
        script_generator_btn.setFixedSize(125, 30)
        script_generator_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        script_generator_btn.clicked.connect(self.show_script_generator)
        section3_layout.addWidget(script_generator_btn)

        # 모든 섹션을 메인 레이아웃에 추가
        button_layout.addWidget(section1)
        button_layout.addWidget(section2)
        button_layout.addWidget(section3)
        button_layout.addStretch()  # 남은 공간을 채움

        # 버튼 컨테이너를 테이블 레이아웃에 추가
        self.table_layout.addWidget(button_container)
        
        # 테이블 설정
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # 키보드 포커스 활성화
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)  # 셀 단위 선택
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)  # 드래그 선택 가능

        # 키 이벤트와 셀 클릭 이벤트 연결
        self.table.installEventFilter(self)
        self.table.cellClicked.connect(self.handle_cell_click)

        def handle_cell_click(self, row, col):
            if col == 0:  # N열(번호열)을 클릭했을 때만 처리
                item = self.table.item(row, col)
                if item:
                    current_color = item.background().color()
                    if current_color == QColor("#FF5D5D"):  # 이미 선택된 상태면
                        item.setBackground(QColor("white"))  # 선택 해제
                    else:
                        item.setBackground(QColor("#FF5D5D"))  # 선택

        # 헤더 클릭 이벤트 처리
        def header_clicked(column):
            tooltips = {
                7: "이 영상이 채널의 전체 조회수에서 차지하는 비중입니다. (예: 전체 조회수의 5%를 차지)",
                8: "구독자 수 대비 조회수의 비율입니다. (예: 구독자의 2배가 시청)",
                9: "채널 기여도와 성과도 배율을 종합한 점수입니다.\n\nGreat!! (70점 이상)\nGood (50-69점)\nSoso (30-49점)\nNot bad (10-29점)\nBad (9점 이하)",
                13: "조회수 대비 좋아요와 댓글 참여도를 나타냅니다."
            }
            
            if column in tooltips:
                header = self.table.horizontalHeader()
                pos = header.mapToGlobal(QPoint(header.sectionPosition(column), header.height()))
                QToolTip.showText(
                    pos,
                    tooltips[column],
                    header,
                    QRect(),
                    5000  # 5초 동안 표시
                )

        # 헤더 클릭 이벤트 연결
        self.table.horizontalHeader().sectionClicked.connect(header_clicked)
        # 헤더 우클릭 메뉴 연결
        self.table.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self.show_header_menu)
        
        self.headers = ["N", "썸네일", "채널명", "제목", "게시일", "구독자 수", "조회수", 
                "채널 기여도", "성과도 배율", "CII", "영상 길이", 
                "좋아요 수", "댓글 수", "참여율", "총 영상 수", "자막", "설명"]
        
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        # 저장된 컬럼 설정 로드
        self.load_column_settings()
        
        # 컬럼 너비 설정
        column_widths = [
            30,   # 번호
            120,  # 썸네일
            90,  # 채널명
            100,  # 제목
            80,   # 게시일
            80,   # 구독자 수
            80,   # 조회수
            80,   # 채널 기여도
            80,   # 성과도 배율
            80,   # CII
            70,   # 영상 길이
            70,   # 좋아요 수
            70,   # 댓글 수
            70,   # 참여율
            70,   # 총 영상 수
            90,   # 자막     
            150,  # 설명      
        ]

        header = self.table.horizontalHeader()
        for i, width in enumerate(column_widths):
            self.table.setColumnWidth(i, width)
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)

        # 헤더 스타일 설정
        header.setStyleSheet("QHeaderView::section { background-color: #e6f3ff !important; padding: 6; border: 1px solid #cccccc; font-weight: bold; font-size: 12px; }")
        # N열 헤더 클릭 이벤트 연결
        header.sectionClicked.connect(self.on_header_clicked)
                
        self.table_layout.addWidget(self.table)
        
        # 테이블 컨테이너를 외부 레이아웃에 추가
        outer_layout.addWidget(table_container)
        
        # 2. 워터마크 레이블 생성
        watermark_label = QLabel(table_container)
        watermark_label.setFixedSize(800, 400)  # 레이블 크기를 더 크게 설정
        watermark_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        watermark_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        watermark_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                margin: 0;
                padding: 0;
                min-width: 800px;
                min-height: 400px;
            }
        """)
        
        

        try:
            logo_path = get_resource_path("images/TubeLensword.png")
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(600, 300,
                                        Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
                watermark_label.setPixmap(scaled_pixmap)
                watermark_label.setMinimumSize(800, 400)
                watermark_label.setMaximumSize(1200, 600)
        except Exception as e:
            print(f"로고 로딩 오류: {str(e)}")

        # 3. 투명도 설정
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.8)
        watermark_label.setGraphicsEffect(opacity_effect)

        # 4. 워터마크를 정중앙에 배치하는 함수
        def center_watermark():
            # 테이블 컨테이너의 중앙 좌표 계산
            container_center_x = table_container.width() // 2
            container_center_y = table_container.height() // 2
            
            # 워터마크의 왼쪽 상단 좌표 계산
            watermark_x = container_center_x - (watermark_label.width() // 2)
            watermark_y = container_center_y - (watermark_label.height() // 2) + 10
            
            watermark_label.move(watermark_x, watermark_y)
            watermark_label.raise_()  # 항상 최상단에 표시

        # 5. 리사이즈 이벤트 연결
        table_container.resizeEvent = lambda e: center_watermark()

        # 6. 초기 위치 설정
        QTimer.singleShot(100, center_watermark)
        
        # 테이블 컨테이너를 외부 컨테이너에 추가
        outer_layout.addWidget(table_container)

        # 7. 버튼 컨테이너 추가
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        button_layout.setSpacing(5)

        save_button = QPushButton("Excel로 저장")
        save_button.clicked.connect(self.save_to_excel)
        save_button.setFixedWidth(100)
        save_button.setFixedHeight(40)
        save_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                background-color: #1d6f42;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(save_button)

        tip_button = QPushButton("렌즈tip")
        tip_button.setFixedWidth(100)
        tip_button.setFixedHeight(40)
        tip_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.video_links['tube_tip'])))
        tip_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                background-color: #ff5252;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
            }
        """)
        button_layout.addWidget(tip_button)

        about_button = QPushButton("About")
        about_button.setFixedWidth(100)
        about_button.setFixedHeight(40)
        about_button.clicked.connect(self.show_developer_info)
        about_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
        """)
        button_layout.addWidget(about_button)
        
        # 구글 로그인 버튼 생성
        self.google_login_button = QPushButton("구글 로그인")
        self.google_login_button.setFixedWidth(120)  # 가로 길이를 120으로 늘림
        self.google_login_button.setFixedHeight(40)
        self.google_login_button.clicked.connect(self.handle_google_login)

        # 아이콘 설정
        icon = QIcon(get_resource_path("images/google.ico"))
        self.google_login_button.setIcon(icon)
        self.google_login_button.setIconSize(QSize(24, 24))

        # 스타일 설정
        self.google_login_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                background-color: white;
                color: black;
                border: none;  /* 테두리 제거 */
                padding: 5px;
                border-radius: 3px;
                min-height: 30px;
                text-align: center;
                padding-left: 5px;
                padding-right: 5px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)

        # 아이콘과 텍스트 사이 간격 설정
        self.google_login_button.setStyleSheet(self.google_login_button.styleSheet() + """
            QPushButton {
                qproperty-iconSize: 30px;  /* 아이콘 크기 설정 */
                padding-right: 10px;  /* 오른쪽 여백 */
            }
        """)

        button_layout.addWidget(self.google_login_button)
        # 버튼 컨테이너를 외부 컨테이너에 추가
        outer_layout.addWidget(button_container)
        
        # 최종적으로 외부 컨테이너를 메인 레이아웃에 추가
        self.main_layout.addWidget(outer_container)

    
    def save_current_state(self):
        """현재 검색 상태를 저장"""
        selected_rows = []
        filtered_results = []
        
        # 선택된 행 확인
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)  # N열 체크
            if item and item.background().color() == QColor("#FF5D5D"):
                selected_rows.append(row)
        
        print("\n=== 저장 시작 ===")
        print(f"subtitle_data 존재 여부: {hasattr(self, 'subtitle_data')}")
        print(f"선택된 행 수: {len(selected_rows)}")
        
        print("\n=== 검색 결과 데이터 구조 ===")
        if self.search_results and len(self.search_results) > 0:
            print(f"첫 번째 항목의 키들: {list(self.search_results[0].keys())}")
        
        # 선택된 행이 있으면 선택된 것만, 없으면 전체 저장
        rows_to_process = selected_rows if selected_rows else range(self.table.rowCount())
        for row in rows_to_process:
            data = self.search_results[row].copy()
            
            # bytes 타입인 thumbnail_data 제거
            if 'thumbnail_data' in data:
                data.pop('thumbnail_data')
            
            # transcript 데이터 확인 및 디버깅
            print(f"\n=== 행 {row} 데이터 ===")
            print(f"Video URL: {data.get('video_url', 'URL 없음')}")
            print(f"Transcript 존재: {'transcript' in data}")
            if 'transcript' in data:
                print(f"Transcript 길이: {len(data['transcript'])}")
                print(f"Transcript 일부: {data['transcript'][:100] if data['transcript'] else '내용 없음'}")
            
            filtered_results.append(data)
        
        save_data = {
            "search_query": self.search_input.text() if hasattr(self, 'search_input') else "",
            "filtered_results": filtered_results,
            "total_count": len(filtered_results)
        }
        
        print("\n=== 저장 데이터 확인 ===")
        print(f"총 저장 항목 수: {len(filtered_results)}")
        print(f"자막 있는 항목 수: {sum(1 for item in filtered_results if 'transcript' in item and item['transcript'] != '자막 없음')}")
        
        print("\n=== 저장 완료 ===\n")
        
        if self.history_manager.save_current_state(save_data):
            QMessageBox.information(self, "저장 완료", f"현재 검색 결과 {len(filtered_results)}개가 보관되었습니다.")
        else:
            QMessageBox.warning(self, "저장 실패", "저장 중 오류가 발생했습니다.")
    
    
    def show_history(self):
        """보관함 다이얼로그 표시"""
        if not hasattr(self, 'history_manager'):
            self.history_manager = HistoryManager()
        dialog = QDialog(self)
        dialog.setWindowTitle("📥 보관함")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 보관된 항목 목록
        list_widget = QListWidget()
        list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
                padding: 5px;
                font-size: 14px;  /* 기본 글자 크기 */
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #f0f0f0;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        
        # 저장된 항목들 표시
        history = self.history_manager.load_history()
        for state in history:
            item = QListWidgetItem()
            check_symbol = "⬜"  # 더 큰 체크박스 문자 사용
            item_text = (f"{check_symbol}  검색어: {state['search_query']}\n"
                        f"      ⏰ 저장시간: {state['timestamp']}\n"
                        f"      📊 저장 수: {state['total_count']}개")
            item.setText(item_text)
            item.setData(Qt.ItemDataRole.UserRole, {'id': state["id"], 'checked': False})
            list_widget.addItem(item)
        
        def on_item_clicked(item):
            data = item.data(Qt.ItemDataRole.UserRole)
            data['checked'] = not data['checked']
            item.setData(Qt.ItemDataRole.UserRole, data)
            
            check_symbol = "✅" if data['checked'] else "⬜"
            text = item.text().replace("⬜", "").replace("✅", "")
            item.setText(f"{check_symbol}{text}")
            
            # 선택된 항목 수 확인
            checked_count = sum(1 for i in range(list_widget.count()) 
                            if list_widget.item(i).data(Qt.ItemDataRole.UserRole)['checked'])
            
            # 버튼 상태 업데이트
            load_button.setEnabled(checked_count == 1)
            delete_button.setEnabled(checked_count > 0)
        
        list_widget.itemClicked.connect(on_item_clicked)
        layout.addWidget(list_widget)
        
        # 버튼 컨테이너
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)
        
        # 버튼 스타일
        button_style = """
            QPushButton {
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
        """
        
        # 불러오기 버튼
        load_button = QPushButton("불러오기")
        load_button.setEnabled(False)
        load_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        # 선택 삭제 버튼
        delete_button = QPushButton("선택 삭제")
        delete_button.setEnabled(False)
        delete_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
            }
        """)
        
        # 전체 삭제 버튼
        clear_button = QPushButton("전체 삭제")
        clear_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #ff5722;
                color: white;
                border: none;
            }
        """)
        
        # 닫기 버튼
        close_button = QPushButton("닫기")
        close_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
            }
        """)
        
        # 버튼 이벤트 연결
        def load_selected():
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                data = item.data(Qt.ItemDataRole.UserRole)
                if data['checked']:
                    state_id = data['id']
                    if self.history_manager.restore_state(self, state_id):
                        dialog.accept()
                    break
        
        def delete_selected():
            selected_items = []
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                if item.data(Qt.ItemDataRole.UserRole)['checked']:
                    selected_items.append(item)
            
            if not selected_items:
                return
                
            if QMessageBox.question(dialog, '삭제 확인',
                                f'선택한 {len(selected_items)}개의 항목을 삭제하시겠습니까?',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                for item in selected_items:
                    state_id = item.data(Qt.ItemDataRole.UserRole)['id']
                    if self.history_manager.delete_state(state_id):
                        list_widget.takeItem(list_widget.row(item))
        
        def clear_all():
            if not list_widget.count():
                return
                
            if QMessageBox.question(dialog, '전체 삭제 확인',
                                '모든 보관된 항목을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self.history_manager.clear_all_states()
                list_widget.clear()
        
        load_button.clicked.connect(load_selected)
        delete_button.clicked.connect(delete_selected)
        clear_button.clicked.connect(clear_all)
        close_button.clicked.connect(dialog.close)
        
        button_layout.addWidget(load_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(close_button)
        layout.addWidget(button_container)
        
        dialog.exec()
    
    def toggle_all_checkboxes(self, state):
        """전체 체크박스 선택/해제"""
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(state == Qt.CheckState.Checked)
    
    
    
    def show_ai_recommendations(self):
        try:
            # API 키 확인
            try:
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    api_key = settings.get('google_ai_api_key')
                    if not api_key:
                        raise Exception("API 키가 설정되지 않았습니다.")
            except Exception as e:
                QMessageBox.warning(self, "경고", "Google AI Studio API 키를 설정에서 먼저 입력해주세요.")
                return

            # 테이블에 표시된 영상 수집
            visible_videos = []
            for row in range(self.table.rowCount()):
                if not self.table.isRowHidden(row):
                    video_data = self.search_results[row].copy()
                    visible_videos.append(video_data)

            if not visible_videos:
                QMessageBox.warning(self, "경고", "분석할 영상이 없습니다.")
                return

            # 조회수 기준으로 정렬하여 상위 10개 선택
            top_videos = sorted(visible_videos, key=lambda x: int(x['view_count']), reverse=True)[:10]

            # 분석 작업 시작
            self.progress_bar.show()
            self.status_label.setText("AI 분석 준비 중...")
            self.progress_bar.setValue(0)

            # 분석 워커 생성 및 시작
            self.ai_worker = AIAnalysisWorker(api_key, top_videos)
            self.ai_worker.progress_signal.connect(self.update_ai_progress)
            self.ai_worker.finished_signal.connect(lambda results: AIRecommendationDialog(results, self).exec())
            self.ai_worker.error_signal.connect(self.handle_ai_error)
            self.ai_worker.start()

        except Exception as e:
            QMessageBox.critical(self, "오류", f"AI 분석 준비 중 오류가 발생했습니다: {str(e)}")
            self.progress_bar.hide()
            self.status_label.setText("")
    
    def show_title_maker(self):
        """타이틀 메이커 다이얼로그 표시"""
        dialog = TitleMakerDialog(self)
        dialog.exec()
    
    def show_realtime_trends(self):
        dialog = RealtimeSearchDialog(self)
        dialog.exec()
    
    def update_ai_progress(self, message, progress):
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)

    def handle_ai_error(self, error_message):
        self.progress_bar.hide()
        self.status_label.setText("")
        QMessageBox.critical(self, "오류", f"AI 분석 중 오류가 발생했습니다: {error_message}")

    
    def show_developer_info(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.setFixedSize(600, 700)  # 높이를 늘렸어요
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                padding: 20px;
            }
            QLabel {
                color: #333333;
                margin: 0px;
            }
            QLabel[cssClass="title"] {
                font-size: 20px;
                font-weight: bold;
                color: #4a9eff;
                margin: 0px 0px;
                padding: 0px;
            }
            QLabel[cssClass="dev-name"] {
                font-size: 10px;
                color: #333333;
                font-weight: bold;
                margin: 5px 0px;
            }
            QLabel[cssClass="section-title"] {
                font-size: 16px;
                color: #4a9eff;
                font-weight: bold;
                margin-top: 20px;
            }
            QLabel[cssClass="stats"] {
                font-size: 14px;
                background-color: #e3f2fd;
                border: 1px solid #bbdefb;
                border-radius: 5px;
                padding: 8px;
                margin: 2px 0px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # 로고 이미지
        logo_label = QLabel()
        try:
            logo_path = get_resource_path("images/tubelens.png")
            logo_pixmap = QPixmap(logo_path)
            if not logo_pixmap.isNull():
                scaled_pixmap = logo_pixmap.scaled(180, 180,
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except Exception as e:
            print(f"로고 로딩 오류: {str(e)}")

        scaled_pixmap = logo_pixmap.scaled(180, 180,
                                        Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                margin: 10px;
            }
        """)
        layout.addWidget(logo_label)
        
        # 프로그램 정보
        title = QLabel("TUBE LENS")
        title.setProperty('cssClass', 'title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 30px;")
        layout.addWidget(title)

        dev_name = QLabel("Developer: SEOL")
        dev_name.setProperty('cssClass', 'dev-name')
        dev_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev_name.setStyleSheet("font-size: 20px;")
        layout.addWidget(dev_name)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #4a9eff;")
        layout.addWidget(line)
        
        # Support & Help 섹션
        support_title = QLabel("Support & Help")
        support_title.setProperty('cssClass', 'section-title')
        support_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(support_title)

        
        
        # 이메일 정보
        email_container = QWidget()
        email_layout = QHBoxLayout(email_container)
        email_label = QLabel("Email:")
        email_text = QLineEdit("tubelens24@gmail.com")
        email_text.setReadOnly(True)
        email_text.setFixedWidth(350)  # 이메일 텍스트 길이
        email_text.setStyleSheet("background-color: #f5f5f5; border: 1px solid #dddddd;")
        copy_button = QPushButton("복사")

        # 이 부분을 추가해주세요
        email_layout.setSpacing(5)  # 요소들 사이 간격
        email_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 전체 중앙 정렬
        email_label.setFixedWidth(30)  # Email: 라벨 width
        copy_button.setFixedWidth(60)  # 복사 버튼 width

        # 각 요소를 중앙 정렬로 추가
        email_layout.addWidget(email_label, 0, Qt.AlignmentFlag.AlignVCenter)
        email_layout.addWidget(email_text, 0, Qt.AlignmentFlag.AlignVCenter)
        email_layout.addWidget(copy_button, 0, Qt.AlignmentFlag.AlignVCenter)


        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
        """)
        
        def copy_email():
            email_text.selectAll()
            email_text.copy()
            QToolTip.showText(
                copy_button.mapToGlobal(QPoint(0, 0)),
                "복사되었습니다!",
                copy_button,
                QRect(),
                1500
            )
        
        copy_button.clicked.connect(copy_email)
        email_layout.addWidget(email_label)
        email_layout.addWidget(email_text)
        email_layout.addWidget(copy_button)
        layout.addWidget(email_container)

        # 오류제보 버튼
        report_button = QPushButton("📧 오류제보 및 문의")
        report_button.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                margin: 10px 50px;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
        """)
        report_button.clicked.connect(self.show_error_report_section)
        layout.addWidget(report_button)
        
        # 버전 정보
        version_label = QLabel("Version: 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # 저작권 정보
        copyright_label = QLabel("© 2024 SEOL. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)
        
        # 닫기 버튼
        close_button = QPushButton("닫기")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
        """)
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        dialog.exec()

    
    def handle_google_login(self):
        """구글 로그인/로그아웃 처리"""
        print("[DEBUG] 함수 시작")
        
        import random
        
        # 이미 진행 중인 로그인 작업이 있는지 확인
        if hasattr(self, 'login_worker') and self.login_worker is not None:
            print("[DEBUG] 이전 로그인 작업 존재")
            self.login_worker.disconnect()  # 시그널 연결 해제
            self.login_worker = None        # 참조 제거
            self.progress_bar.hide()
            self.status_label.setText("")
            print("[DEBUG] 이전 작업 정리 완료")
        
        try:
            if self.auth_manager.is_google_logged_in():
                print("[DEBUG] 로그아웃 시도")
                # 로그아웃 처리
                reply = QMessageBox.question(
                    self, 
                    '로그아웃 확인',
                    '구글 계정에서 로그아웃 하시겠습니까?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.auth_manager.clear_google_token()
                    self.google_login_button.setText("구글 로그인")
                    QMessageBox.information(self, "알림", "로그아웃되었습니다.")
                    print("[DEBUG] 로그아웃 완료")
            else:
                print("[DEBUG] 로그인 시도")
                # 로그인 처리
                client_config = get_client_config()
                if not client_config:
                    QMessageBox.critical(self, "오류", "구글 인증 설정을 불러올 수 없습니다.")
                    return
                
                client_secrets_file = get_resource_path("client_secrets.json")
                if not os.path.exists(client_secrets_file):
                    QMessageBox.critical(self, "오류", "client_secrets.json 파일을 찾을 수 없습니다.")
                    return

                # UI 업데이트
                self.status_label.setText("구글 로그인 진행 중...")
                self.progress_bar.show()
                self.progress_bar.setValue(30)

                # 인증 시도 전 디버그 메시지
                print("[DEBUG] 인증 시도 시작")
                
                try:
                    client_id = client_config['installed']['client_id']
                    client_secret = client_config['installed']['client_secret']
                    port = random.randint(8000, 9000)  # 랜덤 포트 사용
                    
                    # 인증 흐름 초기화
                    flow = InstalledAppFlow.from_client_secrets_file(
                        client_secrets_file,
                        scopes=[
                            'https://www.googleapis.com/auth/youtube.readonly',
                            'https://www.googleapis.com/auth/youtube.force-ssl'
                        ]
                    )
                    
                    # 인증 프로세스 시작
                    self.status_label.setText("브라우저에서 로그인을 완료해주세요...")
                    credentials = flow.run_local_server(
                        port=port, 
                        timeout_seconds=120,
                        success_message="인증이 완료되었습니다. 이 창은 닫아주세요."
                    )
                    
                    # 토큰 정보 저장
                    token_info = {
                        'token': credentials.token,
                        'refresh_token': credentials.refresh_token,
                        'token_uri': credentials.token_uri,
                        'client_id': client_id,
                        'client_secret': client_secret,
                        'scopes': credentials.scopes
                    }
                    
                    # 인증 정보 저장
                    self.auth_manager.save_google_token(token_info)
                    
                    # UI 업데이트
                    self.google_login_button.setText("로그아웃")
                    QMessageBox.information(self, "성공", "구글 로그인이 완료되었습니다.")
                    
                except Exception as e:
                    print("[DEBUG] 인증 오류:", str(e))
                    QMessageBox.critical(self, "오류", f"로그인 중 오류가 발생했습니다: {str(e)}")
                
                finally:
                    self.progress_bar.hide()
                    self.status_label.setText("")

        except Exception as e:
            print("[DEBUG] 최상위 예외:", str(e))
            self.progress_bar.hide()
            self.status_label.setText("")
            if hasattr(self, 'login_worker'):
                self.login_worker = None
    def show_error_report_section(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("오류제보 및 문의")
        dialog.setFixedSize(500, 600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #D2E9E1;
            }
            QLabel {
                color: #1A365D;
                font-size: 13px;
                font-weight: bold;
            }
            QTextEdit, QLineEdit {
                background-color: white;
                border: 1px solid #1A365D;
                border-radius: 5px;
                padding: 8px;
                color: #1A365D;
            }
            QPushButton {
                background-color: #1A365D;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        
        # 이메일 입력
        email_label = QLabel("회신받을 이메일:")
        email_input = QLineEdit()
        email_input.setPlaceholderText("답변받으실 이메일을 입력해주세요")
        
        # 피드백 내용 입력
        content_label = QLabel("내용:")
        content_input = QTextEdit()
        content_input.setPlaceholderText("오류 내용이나 개선사항 또는 문의사항을 자세히 적어주세요")
        content_input.setMinimumHeight(300)
        
        # 현재 상태는 자동으로 포함됨을 알리는 메시지
        status_label = QLabel("※ 프로그램의 현재 상태가 자동으로 포함됩니다")
        status_label.setStyleSheet("color: #666; font-size: 12px;")
        
        # 보내기 버튼
        send_button = QPushButton("보내기")
        
        def send_feedback():
            email = email_input.text().strip()
            content = content_input.toPlainText().strip()
            
            if not email or not content:
                QMessageBox.warning(dialog, "입력 오류", "이메일과 내용을 모두 입력해주세요.")
                return
            
            # 이메일 형식 검증
            if not '@' in email or not '.' in email:
                QMessageBox.warning(dialog, "입력 오류", "올바른 이메일 형식이 아닙니다.")
                return
                
            try:
                # Firebase에 저장할 데이터 준비
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                feedback_data = {
                    'user_info': self.auth_manager.generate_computer_id(),
                    'license_key': self.auth_manager.get_auth_key(),
                    'email': email,
                    'content': content,
                    'date': current_time,
                    'status_report': self.generate_error_report()
                }
                
                # Firebase에 저장
                ref = db.reference('/feedback')
                ref.push(feedback_data)
                
                QMessageBox.information(dialog, "전송 완료", "피드백이 성공적으로 전송되었습니다.")
                dialog.accept()
                
            except Exception as e:
                QMessageBox.critical(dialog, "오류", f"피드백 전송 중 오류가 발생했습니다: {str(e)}")
        
        send_button.clicked.connect(send_feedback)
        
        # 위젯 배치
        layout.addWidget(email_label)
        layout.addWidget(email_input)
        layout.addWidget(content_label)
        layout.addWidget(content_input)
        layout.addWidget(status_label)
        layout.addWidget(send_button)
        
        dialog.exec()

    def start_search(self):
        logging.info(f"""
    검색 시작:
    검색어: {self.search_input.text()}
    수집 수: {self.video_count.currentText()}
    정렬: {'최신순' if self.sort_latest.isChecked() else '조회수순'}
    기간: {self.time_frame.currentText()}
    """)
        if self.search_worker is not None and self.search_worker.isRunning():
            self.search_worker.stop()
            self.search_worker.wait()
            return
        
        

        # 검색어 확인
        search_term = self.search_input.text()
        if not search_term:
            QMessageBox.warning(self, "경고", "검색어를 입력해주세요!")
            return

        # 인증 상태 확인
        current_key = next((k for k in self.api_manager.keys if k.is_current), None)
        is_google_logged_in = self.auth_manager.is_google_logged_in()
        
        if not current_key and not is_google_logged_in:
            QMessageBox.warning(self, "경고", "API 키를 추가하거나 구글 로그인을 해주세요.")
            return

        # 선택된 수집 수 가져오기
        video_count_text = self.video_count.currentText()
        max_results = int(video_count_text.replace('개', ''))
                    
        search_params = {
            "part": "snippet",
            "q": search_term,
            "type": "video",
            "maxResults": min(50, max_results),
            "fields": "items(id/videoId,snippet),nextPageToken"
        }

        # 정렬 순서 설정
        if self.sort_latest.isChecked():
            search_params["order"] = "date"
        elif self.sort_views.isChecked():
            search_params["order"] = "viewCount"
        elif self.sort_rating.isChecked():
            search_params["order"] = "rating"
        
        # 기간 필터
        time_frame = self.time_frame.currentText()
        if time_frame != "모든 기간":
            if time_frame == "날짜 직접 선택":
                try:
                    start_date = datetime.strptime(self.start_date.text(), "%Y-%m-%d")
                    end_date = datetime.strptime(self.end_date.text(), "%Y-%m-%d")
                    if start_date > end_date:
                        QMessageBox.warning(self, "경고", "시작일이 종료일보다 늦을 수 없습니다.")
                        return
                    search_params["publishedAfter"] = start_date.isoformat() + "Z"
                    search_params["publishedBefore"] = (end_date + timedelta(days=1)).isoformat() + "Z"
                except ValueError:
                    QMessageBox.warning(self, "경고", "올바른 날짜 형식을 입력해주세요 (YYYY-MM-DD)")
                    return
            else:
                now = datetime.utcnow()
                delta = {
                    "1년 이내": 365,
                    "6개월 이내": 180,
                    "3개월 이내": 90,
                    "1개월 이내": 30,
                    "7일 이내": 7
                }[time_frame]
                past_date = (now - timedelta(days=delta)).isoformat() + "Z"
                search_params["publishedAfter"] = past_date

        search_params['total_results'] = max_results

        try:
            # API 키나 구글 인증으로 YouTube 객체 생성
            if current_key and current_key.status != 'quotaExceeded':
                logging.info("API 키로 검색 시작")
                youtube = build('youtube', 'v3', developerKey=current_key.key)
            elif is_google_logged_in:
                logging.info("구글 계정으로 검색 시작")
                credentials = self.auth_manager.get_google_credentials()
                youtube = build('youtube', 'v3', credentials=credentials)
            else:
                QMessageBox.warning(self, "경고", "사용 가능한 인증 수단이 없습니다.")
                return

            # 검색 워커 시작
            self.search_worker = YouTubeSearchWorker(youtube=youtube, search_params=search_params)
            self.search_worker.progress.connect(self.update_status)
            self.search_worker.finished.connect(self.handle_search_results)
            self.search_worker.error.connect(self.handle_api_error)
            self.search_worker.start()
            
            self.progress_bar.show()
            self.status_label.setText("검색 시작...")
            logging.info("검색 워커 시작됨")

        except Exception as e:
            logging.error(f"검색 시작 중 오류 발생: {str(e)}")
            QMessageBox.critical(self, "오류", f"검색 시작 중 오류가 발생했습니다: {str(e)}")
   
   
    def handle_api_error(self, error_message):
        print(f"에러 메시지: {error_message}")  # 디버깅용
        if error_message == "API_QUOTA_EXCEEDED":
            # 현재 API 키의 상태를 할당량 초과로 변경
            current_key = next((k for k in self.api_manager.keys if k.is_current), None)
            if current_key:
                # API 키 상태 업데이트
                self.api_manager.update_key_status(current_key.id, 'quotaExceeded')
                # API 키 관리 창이 열려있다면 즉시 업데이트
                for dialog in self.findChildren(APIKeyDialog):
                    dialog.update_table()
                
                # 다음 사용 가능한 API 키 확인
                next_key = self.api_manager.get_next_available_key()
                
                if next_key:
                    QMessageBox.information(
                        self,
                        "알림",
                        f"현재 API 키의 할당량이 초과되어 다음 API 키로 전환합니다."
                    )
                    QTimer.singleShot(1000, self.start_search)
                elif self.auth_manager.is_google_logged_in():
                    QMessageBox.information(
                        self,
                        "알림",
                        "API 키 할당량이 모두 초과되어 구글 계정 할당량을 사용합니다."
                    )
                    QTimer.singleShot(1000, self.start_search)
                else:
                    QMessageBox.warning(
                        self,
                        "오류",
                        "모든 API 할당량이 초과되었습니다. 다른 API 키를 추가하거나 내일 다시 시도해주세요."
                    )
            # 구글 계정을 사용 중일 때
            elif self.auth_manager.is_google_logged_in():
                QMessageBox.warning(
                    self,
                    "오류",
                    "구글 계정의 API 할당량이 초과되었습니다. 내일 다시 시도해주세요."
                )
        else:
            QMessageBox.critical(self, "오류", error_message)
        
        self.progress_bar.hide()
        self.status_label.setText("검색 실패")

    def handle_search_results(self, results):
        self.search_results = results
        self.original_results = results.copy()
        
        # 필터가 설정되어 있는지 확인
        filters_active = (
            self.shorts_checkbox.isChecked() or 
            self.longform_checkbox.isChecked() or
            self.cii_great.isChecked() or 
            self.cii_good.isChecked() or 
            self.cii_soso.isChecked() or
            self.view_count.currentText() != "선택 안함" or
            self.subscriber_count.currentText() != "선택 안함"
        )
        
        # 필터가 설정되어 있다면 자동으로 필터 적용
        if filters_active:
            self.apply_filter()
        else:
            self.update_table()
        
        if filters_active:
            filtered_count = len([row for row in range(self.table.rowCount()) if not self.table.isRowHidden(row)])
            self.update_status(f"검색된 {len(results)}개의 동영상 중 {filtered_count}개가 필터 적용되어 표시됩니다.", 100)
        else:
            self.update_status(f"{len(results)}개의 동영상이 수집되었습니다.", 100)
        
        # 검색 결과가 있을 때는 워터마크를 더 투명하게
        for widget in self.findChildren(QLabel):
            if hasattr(widget, 'graphicsEffect') and isinstance(widget.graphicsEffect(), QGraphicsOpacityEffect):
                widget.graphicsEffect().setOpacity(0.1)

    
    def calculate_duration(self, duration_str):
        # "1:23" 형식의 문자열을 초 단위로 변환
        parts = duration_str.split(':')
        if len(parts) == 2:  # 분:초 형식
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:  # 시:분:초 형식
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        return 0

    def handle_error(self, error_message):
        QMessageBox.critical(self, "오류", error_message)
        self.progress_bar.hide()
        self.status_label.setText("검색 실패")

    def update_status(self, message, progress=None):
        self.status_label.setText(message)
        if progress is not None:
            self.progress_bar.setValue(progress)
            if progress >= 100:
                QTimer.singleShot(1000, self.progress_bar.hide)


    

    def update_table(self):
        self.table.setRowCount(len(self.search_results))
        visible_rect = self.table.viewport().rect()
        first_row = self.table.rowAt(visible_rect.top())
        last_row = self.table.rowAt(visible_rect.bottom())
        
        if first_row == -1: first_row = 0
        if last_row == -1: 
            visible_height = visible_rect.height()
            row_height = 90  # 행 높이
            last_row = min((visible_height // row_height) + 2, len(self.search_results))
        
        self.lazy_load_manager.set_visible_range(first_row, last_row)
        
        # 기본 데이터 먼저 표시
        for row, data in enumerate(self.search_results):
            # 번호
            row_num = QTableWidgetItem(str(row + 1))
            row_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row_num.setFlags(row_num.flags() & ~Qt.ItemFlag.ItemIsSelectable)  # 선택 불가능하게
            self.table.setItem(row, 0, row_num)
            
            # 썸네일 자리 표시자
            if self.lazy_load_manager.is_in_visible_range(row):
                self.load_thumbnail_for_row(row, data)
            else:
                placeholder = QTableWidgetItem("Loading...")
                placeholder.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 1, placeholder)
            
            # 나머지 데이터
            items = [
                data['channel_title'],
                data['title'],
                datetime.fromisoformat(data['published_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %I:%M:%S %p'),
                (f"{int(data['subscriber_count']):,}명", int(data['subscriber_count'])),
                (f"{int(data['view_count']):,}회", int(data['view_count'])),
                ("0%" if abs(data['contribution_value']) < 0.0001 else (f"{data['contribution_value']:.1f}%" if data['contribution_value'] < 1 else f"{round(data['contribution_value'])}%"), data['contribution_value'], "gauge_progress"),
                ("0배" if abs(data['performance_value']) < 0.0001 else (f"{data['performance_value']:.1f}배" if data['performance_value'] < 1 else f"{round(data['performance_value'])}배"), data['performance_value']),
                data['cii'],
                data['duration'],
                (f"{int(data['like_count']):,}개", int(data['like_count'])),
                (f"{int(data['comment_count']):,}개", int(data['comment_count'])),
                ("0%" if abs(data['engagement_rate']) < 0.0001 else (f"{data['engagement_rate']:.1f}%" if data['engagement_rate'] < 1 else f"{round(data['engagement_rate'])}%"), data['engagement_rate']),
                (f"{int(data['total_videos']):,}개", int(data['total_videos'])),
                data.get('transcript', '자막수집'),
                (data.get('description', '')[:100] + ('...' if len(data.get('description', '')) > 100 else ''), data.get('description', ''))
            ]
            
            for col, item in enumerate(items, 2):
                if isinstance(item, tuple):
                    if len(item) == 3 and item[2] == "gauge_progress":
                        display_value, value, _ = item
                        
                        # 컨테이너 위젯 생성
                        container = QWidget()
                        layout = QHBoxLayout(container)
                        layout.setContentsMargins(5, 0, 5, 0)  # 상하 여백 제거
                        
                        # 프로그레스 바 생성
                        progress = QProgressBar()
                        progress.setFixedHeight(90)  # 셀 높이와 동일하게 설정
                        progress.setMaximum(100)
                        progress.setValue(min(int(value), 100))
                        progress.setFormat(display_value)
                        progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        
                        # 색상 설정
                        value = float(value)
                        if value <= 30:
                            color = "#FF5252"  # 빨간색
                        elif value <= 60:
                            color = "#FFD700"  # 노란색
                        elif value <= 90:
                            color = "#4A9EFF"  # 파란색
                        else:
                            color = "#4CAF50"  # 초록색
                            
                        # 프로그레스 바 스타일 설정
                        progress.setStyleSheet(f"""
                            QProgressBar {{
                                background-color: transparent;
                                border: none;
                                text-align: center;
                            }}
                            QProgressBar::chunk {{
                                background-color: {color};
                                opacity: 0.4;
                            }}
                        """)
                        
                        layout.addWidget(progress)
                        self.table.setCellWidget(row, col, container)
                        
                        # 정렬을 위한 더미 아이템 생성
                        table_item = QTableWidgetItem()
                        table_item.setData(Qt.ItemDataRole.UserRole, value)
                        
                    else:
                        display_value, sort_value = item
                        table_item = QTableWidgetItem()
                        table_item.setData(Qt.ItemDataRole.DisplayRole, display_value)
                        table_item.setData(Qt.ItemDataRole.UserRole, sort_value)
                else:
                    table_item = QTableWidgetItem(str(item))
                
                table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                if col == 16:  # 설명 컬럼인 경우
                    display_value, full_text = item
                    table_item = QTableWidgetItem(display_value)
                    table_item.setData(Qt.ItemDataRole.UserRole, full_text)
                    table_item.setToolTip(full_text)
                
                # 스타일 설정
                if col in [2, 3]:  # 채널명과 제목
                    table_item.setBackground(QColor("#f5f5f5"))
                elif col in [5, 6]:  # 구독자 수와 조회수
                    table_item.setBackground(QColor("#ffffd4"))
                elif col == 9:  # CII 컬럼
                    if str(item) == "Great!!":
                        cii_score = self.search_results[row]['cii_score']
                        if cii_score >= 70:
                            # 70~100점 사이에서 초록색 농도 결정
                            ratio = (cii_score - 70) / 30  # 70~100 범위를 0~1로 정규화
                            r = int(144 - (144 * ratio))
                            g = int(238 - (138 * ratio))
                            b = int(144 - (144 * ratio))
                            color = QColor(r, g, b)
                            # 배경색의 밝기에 따라 글자색 결정
                            if g < 200:  # 진한 초록일 때만 흰색 글자
                                table_item.setForeground(QColor("white"))
                            else:  # 연한 초록일 때는 검은색 글자
                                table_item.setForeground(QColor("black"))
                        else:
                            color = QColor("#90EE90")  # 기본 연한 초록
                            table_item.setForeground(QColor("black"))
                        table_item.setBackground(color)
                    elif str(item) == "Good":
                        table_item.setBackground(QColor("#87CEEB"))  # 하늘색으로 변경
                    elif str(item) == "Soso":
                        table_item.setBackground(QColor("#FFFF99"))
                    elif str(item) == "Not bad":
                        table_item.setBackground(QColor("#FFCCCB"))
                    elif str(item) == "Bad":
                        table_item.setBackground(QColor("#FF0000"))
                        table_item.setForeground(QColor("white"))
                
                self.table.setItem(row, col, table_item)
            
            
            self.table.setRowHeight(row, 90)

        # 스크롤 이벤트 연결
        self.table.verticalScrollBar().valueChanged.connect(self.handle_scroll)
     
    def delete_selected_rows(self):
        """선택된 행들을 삭제"""
        rows_to_delete = []
        
        # 선택된 행 찾기
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.background().color() == QColor("#FF5D5D"):
                rows_to_delete.append(row)
        
        # 뒤에서부터 삭제
        for row in sorted(rows_to_delete, reverse=True):
            self.table.removeRow(row)
            if row < len(self.search_results):
                self.search_results.pop(row)
    
    def handle_scroll(self):
        visible_rect = self.table.viewport().rect()
        first_row = self.table.rowAt(visible_rect.top())
        last_row = self.table.rowAt(visible_rect.bottom())
        
        if first_row == -1: first_row = 0
        if last_row == -1: last_row = min(20, len(self.search_results))
        
        self.lazy_load_manager.set_visible_range(first_row, last_row)
        
        for row in range(first_row, last_row + 1):
            if row < len(self.search_results):
                data = self.search_results[row]
                self.load_thumbnail_for_row(row, data)


    def load_thumbnail_for_row(self, row, data):
        url = data['thumbnail_url']
        video_url = data['video_url']
        
        if not self.lazy_load_manager.is_loading(url):
            cached_thumbnail = self.lazy_load_manager.get_cached_thumbnail(url)
            if cached_thumbnail:
                label = QLabel()
                label.setPixmap(cached_thumbnail)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setCursor(Qt.CursorShape.PointingHandCursor)
                
                # 좌클릭: URL 열기
                def handle_mouse_press(e):
                    if e.button() == Qt.MouseButton.LeftButton:
                        QDesktopServices.openUrl(QUrl(video_url))

                # 우클릭: 썸네일 다이얼로그 표시
                def handle_mouse_release(e):
                    if e.button() == Qt.MouseButton.RightButton:
                        self.show_thumbnail_dialog(video_url, label.pixmap())

                label.mousePressEvent = handle_mouse_press
                label.mouseReleaseEvent = handle_mouse_release
                self.table.setCellWidget(row, 1, label)
            else:
                self.lazy_load_manager.mark_as_loading(url)
                # 로딩 표시
                loading_item = QTableWidgetItem("Loading...")
                loading_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 1, loading_item)
                
                # 비동기로 썸네일 로드
                if not hasattr(self, '_thumbnail_workers'):
                    self._thumbnail_workers = []
                    
                worker = ThumbnailWorker(url, video_url, row)
                worker.thumbnail_loaded.connect(lambda px, r: self.on_thumbnail_loaded(px, r, url, video_url))
                self._thumbnail_workers.append(worker)
                worker.finished.connect(lambda: self._thumbnail_workers.remove(worker))
                worker.start()

    def on_thumbnail_loaded(self, pixmap, row, url, video_url):
        if pixmap and row < self.table.rowCount():
            scaled_pixmap = pixmap.scaled(120, 90, Qt.AspectRatioMode.KeepAspectRatio)
            self.lazy_load_manager.add_to_cache(url, scaled_pixmap)
            
            if self.lazy_load_manager.is_in_visible_range(row):
                label = QLabel()
                label.setPixmap(scaled_pixmap)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setCursor(Qt.CursorShape.PointingHandCursor)
                
                # 좌클릭: URL 열기
                def handle_mouse_press(e):
                    if e.button() == Qt.MouseButton.LeftButton:
                        QDesktopServices.openUrl(QUrl(video_url))

                # 우클릭: 썸네일 다이얼로그 표시
                def handle_mouse_release(e):
                    if e.button() == Qt.MouseButton.RightButton:
                        self.show_thumbnail_dialog(video_url, label.pixmap())

                label.mousePressEvent = handle_mouse_press
                label.mouseReleaseEvent = handle_mouse_release
                self.table.setCellWidget(row, 1, label)
    
    def sort_table(self, column, order):
        if order == "reset":
            # 원본 데이터 순서로 복원
            self.search_results = self.original_results.copy()
            self.update_table()
            return
            
        self.search_results.sort(
            key=lambda x: (
                int(x['subscriber_count']) if column == 5 else
                int(x['view_count']) if column == 6 else
                float(x['contribution_value']) if column == 7 else
                float(x['performance_value']) if column == 8 else
                float(x['cii_score']) if column == 9 else  # CII 점수로 정렬
                int(x['like_count']) if column == 11 else
                int(x['comment_count']) if column == 12 else
                float(x['engagement_rate']) if column == 13 else
                int(x['total_videos']) if column == 14 else
                x['published_at'] if column == 4 else 0
            ),
            reverse=(order == "desc")
        )
        self.update_table()


    def show_header_menu(self, pos):
        header = self.table.horizontalHeader()
        column = header.logicalIndexAt(pos)
        
        if column != 0:  # N열이 아닌 경우 기존 메뉴 표시
            menu = QMenu(self)
            if column in [5, 6, 7, 8, 9, 11, 12, 13, 14]:  # 구독자, 조회수 등
                menu.addAction("큰 순서대로", lambda: self.sort_table(column, "desc"))
                menu.addAction("작은 순서대로", lambda: self.sort_table(column, "asc"))
                menu.addSeparator()
                menu.addAction("정렬 해제", lambda: self.sort_table(column, "reset"))
            elif column == 4:  # 게시일 열
                menu.addAction("최신순", lambda: self.sort_table(column, "desc"))
                menu.addAction("오래된순", lambda: self.sort_table(column, "asc"))
                menu.addSeparator()
                menu.addAction("정렬 해제", lambda: self.sort_table(column, "reset"))
            menu.exec(header.mapToGlobal(pos))
            return
            
        # N열 클릭시 모든 컬럼 표시/숨김 메뉴
        self.header_menu = QMenu(self)
        
        # 전체 선택/해제 액션 추가
        select_all = QAction("전체 선택", self)
        select_all.triggered.connect(lambda checked: self.show_header_menu_with_state(pos, True))
        self.header_menu.addAction(select_all)
        
        deselect_all = QAction("전체 해제", self)
        deselect_all.triggered.connect(lambda checked: self.show_header_menu_with_state(pos, False))
        self.header_menu.addAction(deselect_all)
        
        self.header_menu.addSeparator()
        
        # 개별 컬럼 메뉴 추가
        for i, header_text in enumerate(self.headers):
            if i == 0:  # N열은 건너뛰기
                continue
            action = QAction(header_text, self)
            action.setCheckable(True)
            action.setChecked(not self.table.isColumnHidden(i))
            
            def make_toggle_func(col):
                def toggle(checked):
                    self.toggle_column(col, checked)
                    QTimer.singleShot(1, lambda: self.show_header_menu_with_state(pos))
                return toggle
                
            action.triggered.connect(make_toggle_func(i))
            self.header_menu.addAction(action)
        
        self.header_menu.exec(header.mapToGlobal(pos))

    def show_header_menu_with_state(self, pos, all_state=None):
        if all_state is not None:
            self.toggle_all_columns(all_state)
        self.show_header_menu(pos)
    
    def save_to_excel(self):
        # 선택된 행이 있는지 먼저 확인
        selected_rows = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)  # N열 체크
            if item and item.background().color() == QColor("#FF5D5D"):
                selected_rows.append(row)

        # 저장할 데이터 결정
        rows_to_process = selected_rows if selected_rows else range(self.table.rowCount())
        if not rows_to_process:
            QMessageBox.warning(self, "경고", "저장할 검색 결과가 없습니다.")
            return

        # 파일 저장 경로 설정
        try:
            filename = f"youtube_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            desktop_path = os.path.expanduser("~/Desktop")
            
            # 바탕화면 경로가 존재하는지 확인
            if not os.path.exists(desktop_path):
                desktop_path = os.path.expanduser("~")  # 홈 디렉토리로 대체
                
            default_path = os.path.join(desktop_path, filename)
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "엑셀 파일 저장",
                default_path,
                "Excel Files (*.xlsx)"
            )
            
            if not file_path:  # 취소 버튼 눌렀을 경우
                self.progress_bar.hide()
                self.status_label.setText("")
                return
                
            # 저장 경로가 유효한지 확인
            save_dir = os.path.dirname(file_path)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)  # 경로가 없으면 생성
                
            # 파일 쓰기 권한 확인
            try:
                with open(file_path, 'a') as test_file:
                    pass
                os.remove(file_path)
            except Exception as e:
                QMessageBox.critical(self, "오류", f"선택한 경로에 파일을 저장할 수 없습니다.\n다른 경로를 선택해주세요.\n\n오류: {str(e)}")
                return

            # 진행 상태 표시 초기화
            self.progress_bar.show()
            self.status_label.setText("엑셀 파일 생성 준비 중...")
            self.progress_bar.setValue(0)
            QApplication.processEvents()  # UI 업데이트

            try:
                # API 키 또는 구글 로그인 확인
                try:
                    current_key = next((k for k in self.api_manager.keys if k.is_current), None)
                    if current_key:
                        youtube = build('youtube', 'v3', developerKey=current_key.key)
                    elif self.auth_manager.is_google_logged_in():
                        credentials = self.auth_manager.get_google_credentials()
                        youtube = build('youtube', 'v3', credentials=credentials)
                    else:
                        QMessageBox.warning(self, "경고", "API 키를 추가하거나 구글 로그인을 해주세요.")
                        return
                except Exception as e:
                    QMessageBox.warning(self, "경고", f"YouTube API 연결 실패: {str(e)}")
                    return

                excel_data = []
                image_data = []
                
                total_rows = len(rows_to_process)
                
                for idx, row in enumerate(rows_to_process):
                    # 진행률 업데이트
                    progress = int((idx / total_rows) * 50)
                    self.progress_bar.setValue(progress)
                    self.status_label.setText(f"댓글 수집 중... ({idx+1}/{total_rows})")
                    QApplication.processEvents()  # UI 업데이트
                    
                    try:
                        data = self.search_results[row]
                        # video_id 추출
                        video_id = data['video_url'].split('v=')[1]  # URL에서 video_id 추출
                        
                        # 댓글 가져오기
                        comments_response = youtube.commentThreads().list(
                            part='snippet',
                            videoId=video_id,
                            order='relevance',
                            maxResults=10
                        ).execute()
                        
                        # 댓글 추출
                        comments = []
                        for item in comments_response.get('items', []):
                            comment = item['snippet']['topLevelComment']['snippet']
                            comments.append(comment['textDisplay'])
                    except Exception as e:
                        print(f"댓글 수집 오류: {str(e)}")
                        comments = []

                    # 나머지 데이터 처리
                    contribution = "0%" if abs(data['contribution_value']) < 0.0001 else (
                        f"{data['contribution_value']:.1f}%" if data['contribution_value'] < 1 
                        else f"{round(data['contribution_value'])}%"
                    )
                    
                    performance = "0배" if abs(data['performance_value']) < 0.0001 else (
                        f"{data['performance_value']:.1f}배" if data['performance_value'] < 1 
                        else f"{round(data['performance_value'])}배"
                    )
                    
                    row_data = {
                        '썸네일': "",
                        '채널명': data['channel_title'],
                        '제목': data['title'],
                        '게시일': datetime.fromisoformat(data['published_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S'),
                        '구독자 수': f"{int(data['subscriber_count']):,}명",
                        '조회수': f"{int(data['view_count']):,}회",
                        '채널 기여도': contribution,
                        '성과도 배율': performance,
                        'CII': data['cii'],
                        '영상 길이': data['duration'],
                        '좋아요 수': f"{int(data['like_count']):,}개",
                        '댓글 수': f"{int(data['comment_count']):,}개",
                        '베스트댓글': "\n\n".join([f"{i+1}위: {comment}" for i, comment in enumerate(comments[:10])]),
                        '참여율': f"{data['engagement_rate']:.1f}%",
                        '총 영상 수': f"{int(data['total_videos']):,}개",
                        '자막': data['transcript'],
                        '설명': data['description']  # 설명 열 추가
                    }
                    excel_data.append(row_data)
                    image_data.append((data['thumbnail_url'], data['video_url']))

                self.status_label.setText("엑셀 파일 생성 중...")
                QApplication.processEvents()  # UI 업데이트
                
                df = pd.DataFrame(excel_data)
                writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
                df.to_excel(writer, index=False, sheet_name='검색결과')
                
                workbook = writer.book
                worksheet = writer.sheets['검색결과']
                
                # 기본 셀 포맷
                cell_format = workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'text_wrap': True
                })
                
                # 헤더 포맷
                header_format = workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'bold': True,
                    'text_wrap': True,
                    'bg_color': '#D9D9D9'
                })
                
                # 구독자수, 조회수 포맷
                stats_format = workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'text_wrap': True,
                    'bg_color': '#ffffd4'
                })
                
                # CII 포맷
                cii_formats = {
                    "Great!!": workbook.add_format({
                        'align': 'center', 'valign': 'vcenter',
                        'bg_color': '#008000', 'font_color': 'white'
                    }),
                    "Good": workbook.add_format({
                        'align': 'center', 'valign': 'vcenter',
                        'bg_color': '#90EE90', 'font_color': 'black'
                    }),
                    "Soso": workbook.add_format({
                        'align': 'center', 'valign': 'vcenter',
                        'bg_color': '#FFFF99', 'font_color': 'black'
                    }),
                    "Not bad": workbook.add_format({
                        'align': 'center', 'valign': 'vcenter',
                        'bg_color': '#FFCCCB', 'font_color': 'black'
                    }),
                    "Bad": workbook.add_format({
                        'align': 'center', 'valign': 'vcenter',
                        'bg_color': '#FF0000', 'font_color': 'white'
                    })
                }

                
                # 열 너비 설정
                column_widths = {
                    '썸네일': 20.5,
                    '채널명': 10,
                    '제목': 30,
                    '게시일': 12,
                    '구독자 수': 12,
                    '조회수': 12,
                    '채널 기여도': 12,
                    '성과도 배율': 12,
                    'CII': 10,
                    '영상 길이': 10,
                    '좋아요 수': 12,
                    '댓글 수': 10,
                    '베스트댓글': 30,
                    '참여율': 10,
                    '총 영상 수': 12,
                    '자막': 30,
                    '설명': 30
                }

                # 열 포맷 적용
                for idx, (col, width) in enumerate(column_widths.items()):
                    worksheet.set_column(idx, idx, width, cell_format)
                    worksheet.write(0, idx, col, header_format)
                
                # 자동 필터 추가
                worksheet.autofilter(0, 0, len(excel_data), len(column_widths) - 1)
                
                # 행 높이 설정
                ROW_HEIGHT = 90
                worksheet.set_default_row(ROW_HEIGHT)
                worksheet.set_row(0, 30)

                # 설명 열도 가운데 정렬
                description_format = workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'text_wrap': True,
                    'bg_color': '#D9D9D9'
                })
                worksheet.write(0, len(column_widths)-1, '설명', header_format)
                # 각 행에 데이터 포맷 적용
                for row_idx, data in enumerate(excel_data, start=1):
                    worksheet.write(row_idx, 4, data['구독자 수'], stats_format)
                    worksheet.write(row_idx, 5, data['조회수'], stats_format)
                    worksheet.write(row_idx, 8, data['CII'], cii_formats[data['CII']])

                # 채널명에 하이퍼링크 추가
                for idx, (row_idx, data) in enumerate(zip(rows_to_process, excel_data), start=1):
                    try:
                        video_id = self.search_results[row_idx]['video_url'].split('v=')[1]
                        video_response = youtube.videos().list(
                            part='snippet',
                            id=video_id
                        ).execute()
                        
                        if video_response['items']:
                            channel_id = video_response['items'][0]['snippet']['channelId']
                            channel_url = f"https://www.youtube.com/channel/{channel_id}"
                            
                            url_format = workbook.add_format({
                                'font_color': 'blue',
                                'underline': True,
                                'align': 'center',
                                'valign': 'vcenter'
                            })
                            
                            worksheet.write_url(f'B{idx+1}', channel_url, url_format, data['채널명'])
                        else:
                            worksheet.write(f'B{idx+1}', data['채널명'])
                    except Exception as e:
                        worksheet.write(f'B{idx+1}', data['채널명'])
                        print(f"Channel URL error for index {idx}: {str(e)}")
                
                # 베스트댓글 열 자동 줄바꿈 설정
                wrap_format = workbook.add_format({'text_wrap': True, 'align': 'left', 'valign': 'top'})
                worksheet.set_column('M:M', 50, wrap_format)
                
                # 임시 디렉토리 생성
                temp_dir = Path(tempfile.gettempdir()) / 'youtube_thumbnails'
                temp_dir.mkdir(exist_ok=True, parents=True)

                try:
                    # 썸네일 이미지 삽입
                    for idx, (img_url, video_url) in enumerate(image_data, start=1):
                        try:
                            progress = int((idx / len(image_data)) * 90)
                            self.progress_bar.setValue(progress)
                            self.status_label.setText(f"엑셀로 저장 중... ({idx}/{len(image_data)})")
                            QApplication.processEvents()  # UI 업데이트
                            
                            response = urllib.request.urlopen(img_url)
                            img_data = response.read()
                            temp_path = temp_dir / f'temp_img_{idx}.jpg'
                            
                            with open(temp_path, 'wb') as f:
                                f.write(img_data)
                            
                            worksheet.insert_image(
                                f'A{idx+1}',
                                str(temp_path),
                                {
                                    'x_scale': 1.2,
                                    'y_scale': 1.2,
                                    'url': video_url,
                                    'positioning': 1,
                                    'x_offset': 5,
                                    'y_offset': 5,
                                    'object_position': 1
                                }
                            )
                        except Exception as e:
                            print(f"Image error for index {idx}: {str(e)}")
                            continue

                    # 워크북 닫기
                    writer.close()

                    self.progress_bar.setValue(100)
                    self.status_label.setText("엑셀 파일 저장 완료!")
                    msg = "선택된 " if selected_rows else "전체 "
                    QMessageBox.information(self, "알림", f"{msg}검색 결과가 저장되었습니다.\n저장 위치: {file_path}")

                    # 저장된 파일이 있는 폴더 열기
                    saved_folder = os.path.dirname(file_path)
                    QDesktopServices.openUrl(QUrl.fromLocalFile(saved_folder))

                finally:
                    # 임시 파일 정리
                    try:
                        for file in temp_dir.glob('*.jpg'):
                            file.unlink(missing_ok=True)
                        temp_dir.rmdir()
                    except Exception as e:
                        print(f"Cleanup error: {str(e)}")

            except Exception as e:
                self.progress_bar.hide()
                self.status_label.setText("저장 실패")
                QMessageBox.critical(self, "오류", f"파일 저장 중 오류 발생: {str(e)}")
                
        except Exception as e:
            self.progress_bar.hide()
            self.status_label.setText("저장 실패")
            QMessageBox.critical(self, "오류", f"파일 처리 중 오류 발생: {str(e)}")
        
    def apply_filter(self):
        if not self.original_results:
            QMessageBox.warning(self, "경고", "필터를 적용할 검색 결과가 없습니다.")
            return
                
        filtered_results = []
        for result in self.original_results:
            should_include = True
                
            # 비디오 타입 필터 (쇼츠/롱폼)
            if self.shorts_checkbox.isChecked() or self.longform_checkbox.isChecked():
                is_shorts = result['is_shorts']
                    
                if self.shorts_checkbox.isChecked() and not self.longform_checkbox.isChecked():
                    if not is_shorts:
                        should_include = False
                elif self.longform_checkbox.isChecked() and not self.shorts_checkbox.isChecked():
                    if is_shorts:
                        should_include = False
                
            # CII 필터
            if self.cii_great.isChecked() or self.cii_good.isChecked() or self.cii_soso.isChecked():
                if not (
                    (self.cii_great.isChecked() and result['cii'] == "Great!!") or
                    (self.cii_good.isChecked() and result['cii'] == "Good") or
                    (self.cii_soso.isChecked() and result['cii'] == "Soso")
                ):
                    should_include = False
                
            # 조회수 필터
            selected_view_count = self.view_count.currentText()
            if selected_view_count != "선택 안함":
                min_views = {
                    "1만 이상": 10000,
                    "5만 이상": 50000,
                    "10만 이상": 100000,
                    "50만 이상": 500000,
                    "100만 이상": 1000000
                }
                if int(result['view_count']) < min_views[selected_view_count]:
                    should_include = False

            # 구독자 수 필터
            selected_subscriber_count = self.subscriber_count.currentText()
            if selected_subscriber_count != "선택 안함":
                max_subscribers = {
                    "1천명 이하": 1000,
                    "5천명 이하": 5000,
                    "1만명 이하": 10000,
                    "5만명 이하": 50000,
                    "10만명 이하": 100000
                }
                if int(result['subscriber_count']) > max_subscribers[selected_subscriber_count]:
                    should_include = False
                
            if should_include:
                filtered_results.append(result)
            
        self.search_results = filtered_results
        self.update_table()
        
        # 필터 적용 후 보이는 행만 선택된 상태 유지
        visible_selected_urls = []
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                item = self.table.item(row, 0)  # N열 체크
                if item and item.background().color() == QColor("#FF5D5D"):
                    visible_selected_urls.append(self.search_results[row]['video_url'])
        
        # 선택된 URL 업데이트
        self.selected_urls = visible_selected_urls
        
       
        
        self.update_status(f"필터 적용됨: {len(self.search_results)}개의 동영상이 표시됩니다.")

    def clear_filter(self):
        self.shorts_checkbox.setChecked(False)  # 쇼츠 체크박스 해제
        self.longform_checkbox.setChecked(False)  # 롱폼 체크박스 해제
        self.cii_great.setChecked(False)
        self.cii_good.setChecked(False)
        self.cii_soso.setChecked(False)
        self.view_count.setCurrentText("선택 안함")
        self.subscriber_count.setCurrentText("선택 안함")
        self.search_results = self.original_results.copy()
        self.update_table()
        
        # 필터 해제 후 모든 선택 초기화
        self.selected_urls = []
        
        
        
        self.update_status(f"필터가 해제되었습니다: {len(self.search_results)}개의 동영상이 표시됩니다.")
    
    def generate_error_report(self):
        """오류 제보를 위한 현재 상태 리포트 생성"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 최근 로그 파일 찾기
        log_files = sorted(Path('logs').glob('*.log'), key=lambda x: x.stat().st_mtime, reverse=True)
        recent_logs = []
        if log_files:
            try:
                with open(log_files[0], 'r', encoding='utf-8') as f:
                    # 최근 50줄만 가져오기
                    recent_logs = f.readlines()[-50:]
            except Exception as e:
                recent_logs = [f"로그 파일 읽기 실패: {str(e)}"]

        report = ["[오류 제보 리포트]", f"생성 시간: {current_time}\n"]
        
        # 시스템 정보
        report.append("[시스템 정보]")
        report.append(f"운영체제: {platform.system()} {platform.release()}")
        report.append(f"Python 버전: {platform.python_version()}")
        report.append(f"프로그램 실행 경로: {os.path.abspath('.')}")
        report.append("")
        
        # API 상태
        report.append("[API 상태]")
        current_key = next((k for k in self.api_manager.keys if k.is_current), None)
        report.append(f"API 키 등록 수: {len(self.api_manager.keys)}개")
        report.append(f"현재 사용 API 키: {'있음 (마지막 5자리: ' + current_key.last_five + ')' if current_key else '없음'}")
        report.append(f"Google 로그인 상태: {'로그인됨' if self.auth_manager.is_google_logged_in() else '로그아웃'}")
        report.append("")
        
        # 검색 상태
        report.append("[검색 상태]")
        report.append(f"검색어: {self.search_input.text() if hasattr(self, 'search_input') else '없음'}")
        report.append(f"수집 수: {self.video_count.currentText() if hasattr(self, 'video_count') else '없음'}")
        report.append(f"기간: {self.time_frame.currentText() if hasattr(self, 'time_frame') else '없음'}")
        report.append(f"검색된 영상 수: {len(self.search_results) if hasattr(self, 'search_results') else 0}개")
        report.append(f"필터된 영상 수: {len([row for row in range(self.table.rowCount()) if not self.table.isRowHidden(row)]) if hasattr(self, 'table') else 0}개")
        report.append("")
        
        # 필터 상태
        report.append("[필터 상태]")
        report.append(f"쇼츠 필터: {'켜짐' if self.shorts_checkbox.isChecked() else '꺼짐'}")
        report.append(f"롱폼 필터: {'켜짐' if self.longform_checkbox.isChecked() else '꺼짐'}")
        report.append(f"CII 필터: {', '.join([x for x in ['Great!!', 'Good', 'Soso'] if getattr(self, f'cii_{x.lower()}'.replace('!!','')).isChecked()])}")
        report.append(f"조회수 필터: {self.view_count.currentText()}")
        report.append("")
        
        # 최근 로그
        report.append("[최근 로그]")
        report.extend(recent_logs)
        report.append("")
        
        # 현재 상태
        report.append("[현재 상태]")
        report.append(f"상태 메시지: {self.status_label.text() if hasattr(self, 'status_label') else '없음'}")
        if hasattr(self, 'progress_bar'):
            report.append(f"진행률: {self.progress_bar.value()}%")
            
        return "\n".join(report)

   

    def contextMenuEvent(self, event):
        # 테이블 위에서 발생한 이벤트인지 확인
        pos = self.table.viewport().mapFromGlobal(event.globalPos())
        item = self.table.itemAt(pos)
        
        if item is not None and (self.table.columnAt(pos.x()) == 15 or self.table.columnAt(pos.x()) == 16):  # 자막 또는 설명 컬럼
            full_text = item.data(Qt.ItemDataRole.UserRole)
            if full_text:
                # 전체 텍스트를 클립보드에 복사
                clipboard = QApplication.clipboard()
                clipboard.setText(full_text)
                
                # 복사 완료 툴팁 표시
                QToolTip.showText(
                    event.globalPos(),
                    "텍스트가 클립보드에 복사되었습니다.",
                    self.table,
                    self.table.visualItemRect(item),
                    1500  # 1.5초 동안 표시
                )

    def collect_single_subtitle(self, video_id):
        try:
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            except (NoTranscriptFound, TranscriptsDisabled) as e:
                print(f"No transcript available for {video_id}")
                return "자막 없음"
                
            # 순서대로 시도 (한국어 > 영어 > 자동생성)
            for lang in ['ko', 'en']:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    text = "\n".join([line['text'] for line in transcript.fetch()])
                    if text.strip():
                        return text
                except Exception as e:
                    logging.error(f"""
            자막 수집 실패:
            영상 ID: {video_id}
            시도한 언어: ko, en
            오류 메시지: {str(e)}
            """)
                    return "자막 없음"
                    
            # 자동 생성 자막 시도
            try:
                transcript = transcript_list.find_generated_transcript(['ko', 'en'])
                text = "\n".join([line['text'] for line in transcript.fetch()])
                if text.strip():
                    return text
            except:
                pass
                
            return "자막 없음"
            
        except Exception as e:
            print(f"Error collecting subtitle for {video_id}: {str(e)}")
            return "자막 없음"

    def process_next_batch(self):
        try:
            # 수집 중단 체크
            if not hasattr(self, 'is_collecting') or not self.is_collecting:
                self.finish_collection()
                return

            if not self.videos_to_collect:
                # 모든 처리가 완료됨
                self.finish_collection()
                return

            # 다음 4개 영상 가져오기
            current_batch = self.videos_to_collect[:4]  # 여기를 수정 (1개에서 4개로)
            self.videos_to_collect = self.videos_to_collect[4:]  # 여기도 수정

            # ThreadPoolExecutor로 병렬 처리
            with ThreadPoolExecutor(max_workers=4) as executor:
                results = list(executor.map(process_subtitle, current_batch))

            # 결과 처리
            for i, transcript_text in results:
                # 결과 저장 및 UI 업데이트
                self.search_results[i]['transcript'] = transcript_text
                
                item = QTableWidgetItem(transcript_text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                if transcript_text != "자막 없음":
                    item.setBackground(QColor("#E3F2FD"))
                else:
                    item.setBackground(QColor("#FFEBEE"))
                    item.setForeground(QColor("#FF5252"))
                
                item.setData(Qt.ItemDataRole.UserRole, transcript_text)
                item.setToolTip(transcript_text)
                
                self.table.setItem(i, 15, item)
                self.collected += 1
                
                # 진행률 업데이트
                progress = int(self.collected / self.total_videos * 100)
                self.progress_bar.setValue(progress)
                self.status_label.setText(f"자막 수집 중... ({self.collected}/{self.total_videos})")

            # 남은 비디오가 있으면 다음 처리 (20ms 딜레이)
            if self.videos_to_collect and self.is_collecting:
                QTimer.singleShot(20, self.process_next_batch)
            else:
                self.finish_collection()

        except Exception as e:
            QMessageBox.warning(self, "오류", f"자막 수집 중 오류가 발생했습니다: {str(e)}")
            self.finish_collection()

        except Exception as e:
            QMessageBox.warning(self, "오류", f"자막 수집 중 오류가 발생했습니다: {str(e)}")
            self.finish_collection()
    
    def collect_subtitles(self):
        if not self.search_results:
            logging.warning("자막 수집 실패: 수집할 검색 결과가 없음")
            QMessageBox.warning(self, "경고", "수집할 검색 결과가 없습니다.")
            return
        
        # 선택된 행 확인
        selected_rows = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)  # N열 체크
            if item and item.background().color() == QColor("#FF5D5D"):
                selected_rows.append(row)

        # 이미 수집 중이면 중단
        if hasattr(self, 'is_collecting') and self.is_collecting:
            self.is_collecting = False
            self.collect_subtitle_btn.setText("자막 수집")
            self.status_label.setText("자막 수집이 중단되었습니다.")
            return

        try:
            # 자막 수집 시작
            self.is_collecting = True
            self.collect_subtitle_btn.setText("수집 중단")
            
            # 프로그레스 바 초기화
            self.progress_bar.show()
            self.progress_bar.setValue(0)
            
            # 자막 수집이 필요한 영상 필터링
            if selected_rows:  # 선택된 행이 있으면
                self.videos_to_collect = [(i, self.search_results[i]['video_url']) 
                                        for i in selected_rows 
                                        if self.search_results[i]['transcript'] == "자막수집"]
            else:  # 없으면 전체 수집
                self.videos_to_collect = [(i, result['video_url']) 
                                        for i, result in enumerate(self.search_results) 
                                        if result['transcript'] == "자막수집"]
            
            self.total_videos = len(self.videos_to_collect)
            if self.total_videos == 0:
                msg = "선택된 " if selected_rows else "모든 "
                QMessageBox.information(self, "안내", f"{msg}영상의 자막이 이미 수집되었습니다.")
                return

            self.collected = 0
            self.current_batch = []
            self.process_next_batch()

        except Exception as e:
            QMessageBox.warning(self, "오류", f"자막 수집 중 오류가 발생했습니다: {str(e)}")
            self.finish_collection()
    
    def finish_collection(self):
        """자막 수집 종료 시 상태 초기화"""
        self.is_collecting = False
        self.collect_subtitle_btn.setEnabled(True)
        self.collect_subtitle_btn.setText("자막 수집")
        self.progress_bar.hide()
        if hasattr(self, 'collected') and hasattr(self, 'total_videos'):
            self.status_label.setText(f"자막 수집 완료 (총 {self.collected}/{self.total_videos}개)")

   
    def handle_cell_click(self, row, column):
        
            def create_copy_function(button, dialog):
                def copy_text(text):
                    QApplication.clipboard().setText(text)
                    button.setText("복사 완료!")
                    timer = QTimer(dialog)
                    timer.setSingleShot(True)
                    timer.timeout.connect(lambda: button.setText("텍스트 복사"))
                    timer.start(1500)
                return copy_text
        
            if column == 0:  # N열을 클릭했을 때
                item = self.table.item(row, column)
                video_url = self.search_results[row]['video_url']
                
                if item.background().color() == QColor("#FF5D5D"):  # 이미 선택된 상태면
                    # 선택 해제: 원래 회색으로
                    item.setBackground(QColor("#f5f5f5"))
                    item.setForeground(QColor("black"))
                    if video_url in self.selected_urls:
                        self.selected_urls.remove(video_url)
                else:  # 선택 안된 상태면
                    # 선택: 버튼과 같은 빨간색으로
                    item.setBackground(QColor("#FF5D5D"))
                    item.setForeground(QColor("white"))
                    if video_url not in self.selected_urls:
                        self.selected_urls.append(video_url)
                        
                
            
            
            if column == 2:  # 채널명 클릭시
                data = self.search_results[row]
                try:
                    # 현재 API 키 가져오기
                    # API 키 또는 구글 로그인 확인
                    current_key = next((k for k in self.api_manager.keys if k.is_current), None)
                    try:
                        if current_key:
                            youtube = build('youtube', 'v3', developerKey=current_key.key)
                        elif self.auth_manager.is_google_logged_in():
                            credentials = self.auth_manager.get_google_credentials()
                            youtube = build('youtube', 'v3', credentials=credentials)
                        else:
                            QMessageBox.warning(self, "경고", "API 키를 추가하거나 구글 로그인을 해주세요.")
                            return
                    except Exception as e:
                        QMessageBox.warning(self, "경고", f"YouTube API 연결 실패: {str(e)}")
                        return
                        
                    # 상태 표시줄 업데이트
                    self.progress_bar.show()
                    self.progress_bar.setValue(0)
                    self.status_label.setText("채널 정보를 가져오는 중...")
                    QApplication.processEvents()
                        
                                      
                    # video_url에서 채널 ID 추출을 위한 영상 ID 가져오기
                    video_id = data['video_url'].split('v=')[1]
                    self.progress_bar.setValue(20)
                    
                    # 영상 정보로 채널 ID 가져오기
                    video_response = youtube.videos().list(
                        part='snippet',
                        id=video_id
                    ).execute()
                    
                    if not video_response['items']:
                        self.progress_bar.hide()
                        QMessageBox.warning(self, "경고", "영상 정보를 찾을 수 없습니다.")
                        return
                        
                    channel_id = video_response['items'][0]['snippet']['channelId']
                    self.progress_bar.setValue(40)

                    # 채널 정보 가져오기
                    channel_response = youtube.channels().list(
                        part='snippet,statistics,contentDetails',
                        id=channel_id
                    ).execute()
                    
                    if not channel_response['items']:
                        self.progress_bar.hide()
                        QMessageBox.warning(self, "경고", "채널 정보를 찾을 수 없습니다.")
                        return
                        
                    channel_info = channel_response['items'][0]
                    self.progress_bar.setValue(60)
                    
                    # 채널의 업로드 재생목록 ID 가져오기
                    playlist_id = channel_info['contentDetails']['relatedPlaylists']['uploads']
                    # TOP3 영상 가져오기
                    videos_response = youtube.playlistItems().list(
                        part='snippet',
                        playlistId=playlist_id,
                        maxResults=50  # 최근 50개 중에서 찾기
                    ).execute()

                    self.progress_bar.setValue(80)

                    # 비디오 ID 목록 생성
                    video_ids = [item['snippet']['resourceId']['videoId'] for item in videos_response['items']]

                    # 비디오 상세 정보 가져오기
                    videos_details = youtube.videos().list(
                        part='statistics',
                        id=','.join(video_ids[:50])
                    ).execute()

                    # 조회수로 정렬하여 TOP3 선택
                    videos_with_stats = []
                    videos_map = {video['id']: video for video in videos_details['items']}

                    for item in videos_response['items']:
                        video_id = item['snippet']['resourceId']['videoId']
                        if video_id in videos_map:
                            video_info = {
                                'snippet': item['snippet'],
                                'statistics': videos_map[video_id]['statistics'],
                                'id': video_id,
                                'url': f"https://www.youtube.com/watch?v={video_id}"  # URL 추가
                            }
                            videos_with_stats.append(video_info)

                    # 조회수 기준으로 정렬하고 상위 3개만 선택
                    videos_with_stats.sort(
                        key=lambda x: int(x['statistics'].get('viewCount', '0')), 
                        reverse=True
                    )
                    top3_videos = videos_with_stats[:3]
                    
                    # 여기에 디버깅 코드 추가
                    print("=== TOP3 Videos Info ===")
                    for i, video in enumerate(top3_videos):
                        print(f"{i+1}위 영상:")
                        print(f"ID: {video['snippet']['resourceId']['videoId']}")
                        print(f"제목: {video['snippet']['title']}")
                        print(f"조회수: {video['statistics']['viewCount']}")
                        print("------------------------")
                    
                    self.progress_bar.hide()
                    self.status_label.setText("")

                    # 비동기로 이미지 다운로드하는 함수
                    async def download_images():
                        async with aiohttp.ClientSession() as session:
                            # 채널 이미지와 TOP3 썸네일 URL 수집
                            image_urls = [channel_info['snippet']['thumbnails']['default']['url']]  # 채널 이미지
                            image_urls.extend([video['snippet']['thumbnails']['high']['url'] for video in top3_videos])  # TOP3 썸네일 화질 향상
                            
                            # 모든 이미지 동시 다운로드
                            tasks = [session.get(url) for url in image_urls]
                            responses = await asyncio.gather(*tasks)
                            
                            # 응답에서 이미지 데이터 추출
                            image_data = []
                            for response in responses:
                                data = await response.read()
                                image_data.append(data)
                                
                            return image_data

                    # 이미지 다운로드 실행
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    image_data = loop.run_until_complete(download_images())
                    loop.close()

                    # 팝업 다이얼로그 생성
                    dialog = QDialog(self)
                    dialog.setWindowTitle("채널 정보")
                    dialog.setFixedWidth(800)
                    dialog.setStyleSheet("""
                        QDialog {
                            background-color: #D2E9E1;
                        }
                        QLabel {
                            color: #1A365D;
                        }
                        QLabel[cssClass="title"] {
                            font-size: 20px;  /* 16px에서 20px로 변경 */
                            font-weight: bold;
                            color: #1A365D;
                            margin-top: 15px;  /* 상단 여백도 조금 늘림 */
                            margin-bottom: 5px;  /* 하단 여백 추가 */
                        }
                        QLabel[cssClass="info"] {
                            font-size: 14px;
                            background-color: #f8f9fa;
                            border: 1px solid #1A365D;
                            border-radius: 5px;
                            padding: 10px;
                            margin: 5px;
                        }
                        QLabel[cssClass="stats"] {
                            font-size: 14px;
                            background-color: #e3f2fd;
                            border: 1px solid #bbdefb;
                            border-radius: 5px;
                            padding: 8px;
                            margin: 3px;
                        }
                        QLabel[cssClass="circle-image"] {
                            border-radius: 50px;
                            background-color: white;
                        }
                        QTextEdit {
                            background-color: #f8f9fa;
                            border: 1px solid #e9ecef;
                            border-radius: 5px;
                            padding: 10px;
                            margin: 5px;
                            color: #333333;
                        }
                    """)
                    layout = QVBoxLayout(dialog)
                    layout.setSpacing(5)
                    
                    # 첫째 줄: 채널 이미지와 정보를 담을 컨테이너
                    top_widget = QWidget()
                    top_layout = QVBoxLayout(top_widget)
                    top_layout.setSpacing(8)
                    top_layout.setContentsMargins(0, 10, 0, 0)
                    top_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    # 채널 이미지 (중앙 정렬)
                    channel_image = QLabel()
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data[0])

                    # 원형 마스크 생성
                    rounded_pixmap = QPixmap(100, 100)
                    rounded_pixmap.fill(Qt.GlobalColor.transparent)
                    painter = QPainter(rounded_pixmap)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    path = QPainterPath()
                    path.addEllipse(0, 0, 100, 100)
                    painter.setClipPath(path)
                    painter.drawPixmap(0, 0, pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
                    painter.end()

                    channel_image.setPixmap(rounded_pixmap)
                    channel_image.setFixedSize(100, 100)
                    channel_image.setProperty('cssClass', 'circle-image')
                    channel_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    def open_channel(event):
                        QDesktopServices.openUrl(QUrl(f"https://www.youtube.com/channel/{channel_id}"))
                    channel_image.mouseReleaseEvent = open_channel
                    channel_image.setCursor(Qt.CursorShape.PointingHandCursor)
                    top_layout.addWidget(channel_image, 0, Qt.AlignmentFlag.AlignCenter)

                    # 채널 이름과 개설일을 담을 컨테이너
                    name_container = QWidget()
                    name_container.setFixedWidth(dialog.width() - 40)  # 다이얼로그 폭에 맞춤
                    name_layout = QHBoxLayout(name_container)
                    name_layout.setContentsMargins(0, 5, 0, 0)
                    name_layout.setSpacing(10)

                    # 채널명 (가운데 정렬)
                    channel_name = QLabel(channel_info['snippet']['title'])
                    channel_name.setProperty('cssClass', 'title')
                    channel_name.setStyleSheet("""
                        font-size: 20px;
                        font-weight: bold;
                        color: #4a9eff;
                    """)
                    channel_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    channel_name.mouseReleaseEvent = open_channel
                    channel_name.setCursor(Qt.CursorShape.PointingHandCursor)

                    # 개설일 (우측 정렬)
                    channel_created = channel_info['snippet']['publishedAt']
                    try:
                        # 마이크로초 부분 제거
                        clean_date = re.sub(r'\.\d+', '', channel_created)
                        created_date = QLabel(f"채널 개설일: {datetime.fromisoformat(clean_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')}")
                    except Exception as e:
                        # 날짜 파싱에 실패하면 raw 데이터 그대로 표시
                        created_date = QLabel(f"채널 개설일: {channel_created[:10]}")
                    created_date.setStyleSheet("""
                        color: #666;
                        font-size: 12px;
                        padding: 5px;
                    """)
                    created_date.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                    # 레이아웃에 위젯 추가
                    name_layout.addStretch(2)  # 왼쪽 여백
                    name_layout.addWidget(channel_name, 4)  # 채널명에 더 많은 공간 할당
                    name_layout.addWidget(created_date, 2)  # 개설일에 적은 공간 할당

                    top_layout.addWidget(name_container)
                    layout.addWidget(top_widget)
                    
                    # 둘째 줄: 구독자, 총 영상, 마지막 업로드
                    stats_widget = QWidget()
                    stats_layout = QHBoxLayout(stats_widget)
                    stats_layout.setSpacing(10)
                    stats_layout.setContentsMargins(0, 0, 0, 0)  # 상하좌우 여백을 0으로
                    
                    subscriber_label = QLabel(f"구독자 수: {int(data['subscriber_count']):,}명")
                    total_videos_label = QLabel(f"총 영상 수: {int(data['total_videos']):,}개")
                    # 최근 업로드 날짜 가져오기 (playlist의 첫 번째 아이템이 가장 최근)
                    latest_video = videos_response['items'][0]['snippet']['publishedAt'] if videos_response['items'] else channel_info['snippet']['publishedAt']
                    try:
                        # 마이크로초 부분 제거
                        clean_date = re.sub(r'\.\d+', '', latest_video)
                        last_upload = QLabel(f"마지막 업로드: {datetime.fromisoformat(clean_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')}")
                    except Exception as e:
                        # 날짜 파싱에 실패하면 raw 데이터 그대로 표시
                        last_upload = QLabel(f"마지막 업로드: {latest_video[:10]}")
                    for label in [subscriber_label, total_videos_label, last_upload]:
                        label.setStyleSheet("font-weight: bold;")
                    
                    for label in [subscriber_label, total_videos_label, last_upload]:
                        label.setProperty('cssClass', 'stats')
                        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        stats_layout.addWidget(label)
                    
                    layout.addWidget(stats_widget)
                    layout.addSpacing(1)
                    layout.setSpacing(1)  # 이 숫자를 조절하면 모든 위젯 사이 간격이 조절됨
                    
                    # 셋째 줄: 조회수 통계
                    views_widget = QWidget()
                    views_layout = QHBoxLayout(views_widget)
                    views_layout.setSpacing(10)
                    views_layout.setContentsMargins(0, 0, 0, 0)  # 상하좌우 여백을 0으로
                    
                    total_views = int(channel_info['statistics']['viewCount'])
                    avg_views = total_views // int(channel_info['statistics']['videoCount'])
                    total_likes = sum(int(video.get('statistics', {}).get('likeCount', 0)) for video in videos_details['items'])
                    avg_likes = total_likes // len(videos_details['items']) if videos_details['items'] else 0

                    total_views_label = QLabel(f"총 조회수: {total_views:,}회")
                    avg_views_label = QLabel(f"평균 조회수: {avg_views:,}회")
                    avg_likes_label = QLabel(f"평균 좋아요: {avg_likes:,}개")
                    for label in [total_views_label, avg_views_label, avg_likes_label]:
                        label.setStyleSheet("font-weight: bold;")
                    
                    
                    for label in [total_views_label, avg_views_label, avg_likes_label]:
                        label.setProperty('cssClass', 'stats')
                        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        views_layout.addWidget(label)
                    
                    layout.addWidget(views_widget)
                    
                    # 넷째 줄: 채널 설명
                    description_label = QLabel("채널 설명")
                    description_label.setProperty('cssClass', 'title')
                    description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    layout.addWidget(description_label)
                    layout.addSpacing(10)

                    # QLabel 대신 QTextEdit 사용 (선택 및 복사 가능)
                    description_text = QTextEdit()
                    description_text.setPlainText(channel_info['snippet']['description'])
                    description_text.setReadOnly(True)
                    description_text.setFixedHeight(100)
                    layout.addWidget(description_text)
                    
                    # Top 3 영상
                    top_videos_label = QLabel("인기 영상 TOP 3")
                    top_videos_label.setProperty('cssClass', 'title')
                    top_videos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    layout.addWidget(top_videos_label)
                    
                    videos_widget = QWidget()
                    videos_layout = QHBoxLayout(videos_widget)
                    videos_layout.setSpacing(25)  # TOP3 영상 간의 간격 늘림
                    
                    for idx, video in enumerate(top3_videos):
                        video_widget = QWidget()
                        video_layout = QVBoxLayout(video_widget)
                        video_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        video_layout.setSpacing(1)  # 내부 요소들 간의 간격 늘림
                        
                        # 썸네일 (medium 품질로 변경)
                        thumbnail = QLabel()
                        thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        thumb_pixmap = QPixmap()
                        thumb_pixmap.loadFromData(image_data[idx + 1])
                        scaled_thumb = thumb_pixmap.scaled(220, 165, Qt.AspectRatioMode.KeepAspectRatio)  # 썸네일 크기 증가
                        thumbnail.setPixmap(scaled_thumb)

                        def make_click_handler(v_url):
                            def handler(event):
                                QDesktopServices.openUrl(QUrl(v_url))
                            return handler

                        video_url = f"https://www.youtube.com/watch?v={video['snippet']['resourceId']['videoId']}"
                        thumbnail.mouseReleaseEvent = make_click_handler(video_url)
                        thumbnail.setCursor(Qt.CursorShape.PointingHandCursor)
                        
                        
                        video_layout.addWidget(thumbnail)
                        
                        # 제목 (드래그 가능한 텍스트)
                        title = QTextEdit()
                        title.setPlainText(video['snippet']['title'])
                        title.setReadOnly(True)
                        title.setStyleSheet("""
                            QTextEdit {
                                font-weight: bold;
                                border: none;
                                background-color: transparent;
                                margin: 0px;
                                padding: 0px;
                            }
                        """)
                        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        title.setFixedHeight(60)
                        title.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                        title.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                        # 텍스트를 수직 가운데 정렬하기 위한 여백 계산
                        document_height = title.document().size().height()
                        if document_height < 80:  # 고정 높이가 80이므로
                            margin = (80 - document_height) / 2
                            title.setStyleSheet(title.styleSheet() + f"margin-top: {margin}px;")
                        video_layout.addWidget(title)
                        
                        # 조회수와 게시일
                        views = int(video['statistics']['viewCount'])
                        published = datetime.fromisoformat(video['snippet']['publishedAt'].replace('Z', '+00:00'))
                        # 통계 정보를 담을 컨테이너
                        stats_container = QWidget()
                        stats_container.setStyleSheet("""
                            QWidget {
                                background-color: #e3f2fd;
                                border: 1px solid #bbdefb;
                                border-radius: 5px;
                                margin: 3px;
                                padding: 5px;
                            }
                        """)
                        stats_container_layout = QVBoxLayout(stats_container)
                        stats_container_layout.setSpacing(2)
                        stats_container_layout.setContentsMargins(5, 5, 5, 5)

                        # 첫 번째 줄: 조회수와 업로드일 (드래그 가능한 텍스트)
                        stats1 = QTextEdit()
                        stats1.setPlainText(f"조회수: {views:,}회  |  {published.strftime('%Y-%m-%d')}")
                        stats1.setReadOnly(True)
                        stats1.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        stats1.setStyleSheet("""
                            QTextEdit {
                                font-weight: bold;
                                border: none;
                                background: transparent;
                                padding: 0px;
                                margin: 0px;
                            }
                        """)
                        stats1.setFixedHeight(25)
                        stats1.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                        stats1.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                        stats_container_layout.addWidget(stats1)

                        # 기여도와 성과도 계산
                        contribution = (views / int(channel_info['statistics']['viewCount']) * 100)
                        performance = (views / int(data['subscriber_count'])) if int(data['subscriber_count']) > 0 else 0

                        contribution_str = "0%" if abs(contribution) < 0.0001 else (
                            f"{contribution:.1f}%" if contribution < 1 
                            else f"{round(contribution)}%"
                        )

                        performance_str = "0배" if abs(performance) < 0.0001 else (
                            f"{performance:.1f}배" if performance < 1 
                            else f"{round(performance)}배"
                        )

                        # 두 번째 줄: 기여도와 성과도 (드래그 가능한 텍스트)
                        stats2 = QTextEdit()
                        stats2.setPlainText(f"기여도: {contribution_str}  |  성과도: {performance_str}")
                        stats2.setReadOnly(True)
                        stats2.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        stats2.setStyleSheet("""
                            QTextEdit {
                                font-weight: bold;
                                border: none;
                                background: transparent;
                                padding: 0px;
                                margin: 0px;
                            }
                        """)
                        stats2.setFixedHeight(25)
                        stats2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                        stats2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                        stats_container_layout.addWidget(stats2)

                        video_layout.addWidget(stats_container)
                        
                        videos_layout.addWidget(video_widget)
                    
                    layout.addWidget(videos_widget)
                    
                    # 하단 버튼 컨테이너 추가
                    button_container = QWidget()
                    button_layout = QHBoxLayout(button_container)
                    button_layout.setContentsMargins(10, 5, 10, 5)

                    # 닫기 버튼
                    close_button = QPushButton("닫기")
                    close_button.setFixedSize(100, 30)
                    close_button.setStyleSheet("""
                        QPushButton {
                            background-color: #4a9eff;
                            color: white;
                            border: none;
                            border-radius: 5px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #3d8ae0;
                        }
                    """)
                    close_button.clicked.connect(dialog.close)

                    button_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)
                    layout.addWidget(button_container)
                    
                    dialog.exec()
                    
                except Exception as e:
                    self.progress_bar.hide()
                    self.status_label.setText("")
                    QMessageBox.warning(self, "오류", f"채널 정보를 가져오는 중 오류가 발생했습니다: {str(e)}")
                
            
    
            if column == 15:  # 자막 컬럼 클릭시
                item = self.table.item(row, column)
                if item:
                    if item.text() == "자막수집":
                        try:
                            # 커서를 대기 중 모양으로 변경
                            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

                            # 현재 행의 비디오 URL에서 ID 추출
                            video_url = self.search_results[row]['video_url']
                            video_id = video_url.split('v=')[1]
                            
                            # 자막 수집 시작을 표시
                            item.setText("수집중...")
                            item.setBackground(QColor("#FFF3E0"))
                            QApplication.processEvents()  # UI 업데이트
                            
                            try:
                                # YouTube 자막 가져오기
                                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                                try:
                                    transcript = transcript_list.find_transcript(['ko'])
                                except:
                                    try:
                                        transcript = transcript_list.find_transcript(['en'])
                                    except:
                                        transcript = transcript_list.find_generated_transcript(['ko', 'en'])
                                
                                # 자막 텍스트 추출 (시간 정보 없이)
                                transcript_text = "\n".join([line['text'] for line in transcript.fetch()])
                                
                            except Exception as e:
                                transcript_text = "자막 없음"
                            
                            # 결과 저장 및 UI 업데이트
                            self.search_results[row]['transcript'] = transcript_text
                            
                            # UI 업데이트
                            item = QTableWidgetItem(transcript_text)
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            
                            if transcript_text != "자막 없음":
                                item.setBackground(QColor("#E3F2FD"))
                            else:
                                item.setBackground(QColor("#FFEBEE"))
                                item.setForeground(QColor("#FF5252"))
                            
                            # 전체 텍스트를 저장하고 툴팁 설정
                            item.setData(Qt.ItemDataRole.UserRole, transcript_text)
                            item.setToolTip(transcript_text)
                            
                            self.table.setItem(row, 15, item)
                            
                        except Exception as e:
                            # 오류 발생시 원래 상태로 복구
                            item.setText("자막수집")
                            QMessageBox.warning(self, "오류", f"자막 수집 중 오류가 발생했습니다: {str(e)}")
                        finally:
                            # 커서를 원래대로 복구
                            QApplication.restoreOverrideCursor()
                    else:
                        try:
                            # 자막 다이얼로그 생성
                            dialog = QDialog(self)
                            dialog.setWindowTitle("자막 내용")
                            dialog.setFixedSize(400, 800)  # 크기 조절
                            dialog.setStyleSheet("""
                                QDialog {
                                    background-color: white;
                                    border-radius: 10px;
                                }
                                QTextEdit {
                                    border: none;
                                    background-color: #f8f9fa;
                                    border-radius: 5px;
                                    padding: 10px;
                                    font-size: 14px;
                                    color: #111111;
                                    line-height: 1.5;
                                }
                                QLabel {
                                    color: #4a9eff;
                                    font-size: 16px;
                                    font-weight: bold;
                                    padding: 10px;
                                }
                                QPushButton {
                                    background-color: #4a9eff;
                                    color: white;
                                    border: none;
                                    padding: 8px 15px;
                                    border-radius: 5px;
                                    font-weight: bold;
                                }
                                QPushButton:hover {
                                    background-color: #3d8ae0;
                                }
                            """)

                            layout = QVBoxLayout(dialog)
                            layout.setContentsMargins(10, 10, 10, 10)  # 여백 축소
                            layout.setSpacing(5)  # 위젯 간 간격 축소

                            # 비디오 제목 표시
                            video_title = QLabel(f"영상 제목: {self.search_results[row]['title']}")
                            video_title.setWordWrap(True)
                            layout.addWidget(video_title)

                            # 구분선 추가
                            line = QFrame()
                            line.setFrameShape(QFrame.Shape.HLine)
                            line.setStyleSheet("background-color: #4a9eff;")
                            layout.addWidget(line)

                            # 자막 내용 표시
                            text_edit = QTextEdit()
                            formatted_text = self.format_transcript_text(item.text())
                            text_edit.setPlainText(formatted_text)
                            text_edit.setReadOnly(True)
                            text_edit.setStyleSheet("""
                                QTextEdit {
                                    border: none;
                                    background-color: #f8f9fa;
                                    border-radius: 5px;
                                    padding: 15px;
                                    font-size: 14px;
                                    color: #333;
                                    line-height: 1.8;
                                    margin: 0;
                                }
                            """)
                            layout.addWidget(text_edit)

                            # 하단 버튼 영역
                            button_container = QWidget()
                            button_layout = QHBoxLayout(button_container)
                            button_layout.setContentsMargins(0, 10, 0, 0)

                            # 복사 버튼
                            copy_button = QPushButton("텍스트 복사")
                            def copy_text():
                                QApplication.clipboard().setText(text_edit.toPlainText())
                                copy_button.setText("복사 완료!")
                                QTimer.singleShot(1500, lambda: copy_button.setText("텍스트 복사"))
                            copy_button.clicked.connect(lambda: create_copy_function(copy_button, dialog)(text_edit.toPlainText()))
                            button_layout.addWidget(copy_button)

                            # 닫기 버튼
                            close_button = QPushButton("닫기")
                            close_button.clicked.connect(dialog.close)
                            button_layout.addWidget(close_button)

                            layout.addWidget(button_container)

                            dialog.exec()

                        except Exception as e:
                            QMessageBox.warning(self, "오류", f"자막 표시 중 오류가 발생했습니다: {str(e)}")
    
            
            
            if column == 16:  # 설명 컬럼 클릭시
                try:
                    dialog = QDialog(self)
                    dialog.setWindowTitle("영상 설명")
                    dialog.setFixedSize(400, 800)
                    dialog.setStyleSheet("""
                        QDialog {
                            background-color: white;
                            border-radius: 10px;
                        }
                        QTextEdit {
                            border: none;
                            background-color: #f8f9fa;
                            border-radius: 5px;
                            padding: 15px;
                            font-size: 14px;
                            color: #111111;
                            line-height: 1.8;
                        }
                        QLabel {
                            color: #4a9eff;
                            font-size: 16px;
                            font-weight: bold;
                            padding: 10px;
                            qproperty-alignment: AlignCenter;
                        }
                        QPushButton {
                            background-color: #4a9eff;
                            color: white;
                            border: none;
                            padding: 8px 15px;
                            border-radius: 5px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #3d8ae0;
                        }
                    """)

                    layout = QVBoxLayout(dialog)
                    layout.setContentsMargins(10, 10, 10, 10)

                    # 비디오 제목 표시
                    video_title = QLabel(f"영상 제목: {self.search_results[row]['title']}")
                    video_title.setWordWrap(True)
                    layout.addWidget(video_title)

                    # 구분선
                    line = QFrame()
                    line.setFrameShape(QFrame.Shape.HLine)
                    line.setStyleSheet("background-color: #4a9eff;")
                    layout.addWidget(line)

                    # 설명 내용
                    text_edit = QTextEdit()
                    description_text = self.search_results[row]['description']
                    description_text = description_text.replace('\n', '<br>')  # 줄바꿈 유지
                    text_edit.setHtml(description_text)  # HTML 형식으로 설정
                    text_edit.setReadOnly(True)
                    text_edit.setMinimumHeight(600)
                    text_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 왼쪽 정렬
                    text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)  # 자동 줄바꿈
                    layout.addWidget(text_edit)

                    # 하단 버튼
                    button_container = QWidget()
                    button_layout = QHBoxLayout(button_container)
                    button_layout.setContentsMargins(0, 10, 0, 0)

                    # 복사 버튼
                    copy_button = QPushButton("텍스트 복사")
                    def copy_text():
                        QApplication.clipboard().setText(text_edit.toPlainText())
                        copy_button.setText("복사 완료!")
                        QTimer.singleShot(1500, lambda: copy_button.setText("텍스트 복사"))
                    copy_button.clicked.connect(lambda: create_copy_function(copy_button, dialog)(text_edit.toPlainText()))
                    button_layout.addWidget(copy_button)

                    # 닫기 버튼
                    close_button = QPushButton("닫기")
                    close_button.clicked.connect(dialog.close)
                    button_layout.addWidget(close_button)

                    layout.addWidget(button_container)

                    dialog.exec()

                except Exception as e:
                    QMessageBox.warning(self, "오류", f"설명 표시 중 오류가 발생했습니다: {str(e)}")
            
            if column == 12:  # 댓글 수 열 클릭시
                try:
                    # API 키 또는 구글 로그인 확인
                    current_key = next((k for k in self.api_manager.keys if k.is_current), None)
                    try:
                        if current_key:
                            youtube = build('youtube', 'v3', developerKey=current_key.key)
                        elif self.auth_manager.is_google_logged_in():
                            # 기존 credentials 사용
                            credentials = self.auth_manager.get_google_credentials()
                            if credentials:
                                youtube = build('youtube', 'v3', credentials=credentials)
                            else:
                                QMessageBox.warning(self, "경고", "구글 인증에 실패했습니다.")
                                return
                        else:
                            QMessageBox.warning(self, "경고", "API 키를 추가하거나 구글 로그인을 해주세요.")
                            return
                            
                        # 비디오 ID 추출
                        video_url = self.search_results[row]['video_url']
                        video_id = video_url.split('v=')[1]
                        
                        # 댓글 다이얼로그 표시
                        from CommentDialog import CommentDialog
                        dialog = CommentDialog(self)
                        dialog.load_comments(youtube, video_id)
                        dialog.exec()
                        
                    except HttpError as e:
                        error_message = str(e)
                        if 'commentsDisabled' in error_message or 'parameter has disabled comments' in error_message:
                            QMessageBox.information(self, "알림", "이 동영상은 댓글이 비활성화되어 있습니다.")  # 원래 메시지로 복구
                        else:
                            QMessageBox.warning(self, "경고", f"YouTube API 연결 실패: {str(e)}")
                        return
                        
                except Exception as e:
                    QMessageBox.warning(self, "오류", f"댓글을 불러오는 중 오류가 발생했습니다: {str(e)}")
        
   
    def eventFilter(self, source, event):
        if source == self.table and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Delete:
                selected_rows = set()
                deleted_urls = []  # 삭제될 URL들 저장
                
                # N열을 확인해서 빨간색 배경인 행 찾기
                for row in range(self.table.rowCount()):
                    item = self.table.item(row, 0)  # N열(0번 열) 아이템 확인
                    if item and item.background().color() == QColor("#FF5D5D"):
                        selected_rows.add(row)
                        # 삭제될 URL 저장
                        if row < len(self.search_results):
                            deleted_urls.append(self.search_results[row]['video_url'])
                
                if selected_rows:
                    # 삭제 전 데이터 백업
                    deleted_data = []
                    for row in sorted(selected_rows):
                        deleted_data.append({
                            'row': row,
                            'data': self.search_results[row]
                        })
                    self.undo_stack.append(deleted_data)
                    
                    # 뒤에서부터 삭제
                    for row in sorted(selected_rows, reverse=True):
                        self.table.removeRow(row)
                        if row < len(self.search_results):
                            self.search_results.pop(row)
                            
                    # URL 목록에서 삭제된 URL 제거
                    self.selected_urls = [url for url in self.selected_urls if url not in deleted_urls]
                    
                    
                    return True
                    
            elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Z:
                if self.undo_stack:
                    deleted_data = self.undo_stack.pop()
                    for data in deleted_data:
                        row = data['row']
                        self.search_results.insert(row, data['data'])
                    self.update_table()
                    return True
        return super().eventFilter(source, event)

    def closeEvent(self, event):
        # 종료할 때 현재 컬럼 상태 저장
        settings = {}
        for i in range(self.table.columnCount()):
            settings[str(i)] = not self.table.isColumnHidden(i)
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"설정 저장 실패: {str(e)}")
        event.accept()

    def load_column_settings(self):
        # 저장된 설정 불러오기
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                for col, visible in settings.items():
                    col = int(col)
                    if col < self.table.columnCount():
                        self.table.setColumnHidden(col, not visible)
        except Exception as e:
            print(f"설정 로드 실패: {str(e)}")

    def show_api_key_dialog(self):
        dialog = APIKeyDialog(self)
        
        # 다이얼로그가 닫힐 때 settings.json 업데이트
        def on_dialog_closed():
            # 현재 활성화된 API 키 가져오기
            if hasattr(self, 'gemini_api_manager'):
                current_key = self.gemini_api_manager.get_current_key()
                if current_key:
                    # 기존 설정 업데이트
                    try:
                        settings = {}
                        if os.path.exists('settings.json'):
                            with open('settings.json', 'r') as f:
                                settings = json.load(f)
                        
                        settings['google_ai_api_key'] = current_key
                        settings['ai_model'] = 'gemini-2.0-pro-exp-02-05'
                        settings['model_version'] = '2.0'
                        
                        with open('settings.json', 'w') as f:
                            json.dump(settings, f, indent=4)
                    except Exception as e:
                        print(f"설정 저장 오류: {str(e)}")
        
        dialog.finished.connect(on_dialog_closed)
        dialog.exec()
    
    # 여기에 새 함수들 추가
    def show_calendar(self, target_input):
        dialog = QDialog(self)
        dialog.setWindowTitle("날짜 선택")
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)

        calendar = QCalendarWidget()
        calendar.setGridVisible(True)
        calendar.setMinimumDate(QDate(2005, 1, 1))
        calendar.setMaximumDate(QDate.currentDate())

        def on_date_selected(date):
            target_input.setText(date.toString("yyyy-MM-dd"))
            dialog.close()

        calendar.clicked.connect(on_date_selected)
        layout.addWidget(calendar)

        # 입력창 아래 위치로 조정
        button_pos = target_input.mapToGlobal(target_input.rect().bottomLeft())
        dialog.move(button_pos.x(), button_pos.y() + 5)
        
        # 화면 경계 체크 및 위치 조정
        screen = QApplication.primaryScreen().geometry()
        dialog_rect = dialog.frameGeometry()
        dialog_rect.moveTopLeft(dialog.pos())
        
        if dialog_rect.right() > screen.right():
            dialog.move(screen.right() - dialog_rect.width(), dialog_rect.y())
        
        if dialog_rect.bottom() > screen.bottom():
            dialog.move(dialog_rect.x(), button_pos.y() - dialog_rect.height() - 5)

        dialog.exec()

    def start_download(self, format_type):
        # 이미 다운로드 중이면 중지
        if self.downloading_type == format_type:
            self.stop_download(format_type)
            return

        # FFmpeg 체크 및 설치
        try:
            ffmpeg_path = os.path.expandvars(r'%LOCALAPPDATA%\Programs\ffmpeg\bin\ffmpeg.exe')
            if not os.path.exists(ffmpeg_path):
                reply = QMessageBox.question(
                    self,
                    'FFmpeg 설치',
                    'YouTube 다운로드를 위해 FFmpeg 설치가 필요합니다.\n설치하시겠습니까?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.status_label.setText("FFmpeg 설치 중...")
                    self.progress_bar.show()
                    self.progress_bar.setValue(0)
                    
                    install_dir = os.path.expandvars(r'%LOCALAPPDATA%\Programs\ffmpeg')
                    os.makedirs(install_dir, exist_ok=True)
                    
                    # FFmpeg 다운로드
                    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
                    response = requests.get(ffmpeg_url, stream=True)
                    response.raise_for_status()
                    
                    temp_dir = tempfile.mkdtemp()
                    zip_path = os.path.join(temp_dir, 'ffmpeg.zip')
                    
                    with open(zip_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    self.progress_bar.setValue(50)
                    self.status_label.setText("FFmpeg 설치 파일 압축 해제 중...")
                    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    self.progress_bar.setValue(80)
                    self.status_label.setText("FFmpeg 설치 완료 중...")
                    
                    ffmpeg_temp_dir = next(d for d in os.listdir(temp_dir) if d.startswith('ffmpeg'))
                    ffmpeg_bin_dir = os.path.join(install_dir, 'bin')
                    os.makedirs(ffmpeg_bin_dir, exist_ok=True)
                    
                    for file in ['ffmpeg.exe', 'ffplay.exe', 'ffprobe.exe']:
                        src = os.path.join(temp_dir, ffmpeg_temp_dir, 'bin', file)
                        dst = os.path.join(ffmpeg_bin_dir, file)
                        shutil.copy2(src, dst)
                    
                    if ffmpeg_bin_dir not in os.environ['PATH']:
                        os.environ['PATH'] = ffmpeg_bin_dir + os.pathsep + os.environ['PATH']
                    
                    shutil.rmtree(temp_dir)
                    
                    self.progress_bar.setValue(100)
                    self.status_label.setText("FFmpeg 설치 완료!")
                    
                else:
                    return
                    
        except Exception as e:
            QMessageBox.critical(self, "오류", f"FFmpeg 설치 중 오류가 발생했습니다: {str(e)}")
            return

        # 선택된 영상 URL 가져오기
        selected_urls = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.background().color() == QColor("#FF5D5D"):
                selected_urls.append(self.search_results[row]['video_url'])
        
        # 선택된 영상이 없으면 필터링된 모든 영상 선택
        if not selected_urls:
            reply = QMessageBox.question(
                self,
                '전체 다운로드',
                '선택된 영상이 없습니다. 현재 표시된 모든 영상을 다운로드하시겠습니까?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                for row in range(self.table.rowCount()):
                    if not self.table.isRowHidden(row):
                        selected_urls.append(self.search_results[row]['video_url'])
            else:
                return
        
        if not selected_urls:
            QMessageBox.warning(self, "알림", "다운로드할 영상이 없습니다.")
            return
        
        # 저장 경로 선택
        save_path = QFileDialog.getExistingDirectory(
            self,
            "저장 위치 선택",
            os.path.join(os.path.expanduser('~'), 'Desktop'),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not save_path:
            return

        # 버튼 상태 업데이트
        self.downloading_type = format_type
        if format_type == 'mp4':
            self.update_download_button_state('mp4')
        else:
            self.update_download_button_state('mp3')

        # 다운로드 시작
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.status_label.setText("다운로드 준비 중...")
        self.download_all(selected_urls, format_type, save_path)
    
    def update_download_button_state(self, format_type):
        """다운로드 버튼 상태 업데이트"""
        for child in self.findChildren(QPushButton):
            if format_type == 'mp4' and child.text() == "📺 MP4 다운":
                child.setText("📺 중지")
                child.setStyleSheet("""
                    QPushButton {
                        background-color: #ff4a4a;
                        color: white;
                        border: none;
                        padding: 5px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #ff6b6b;
                    }
                """)
            elif format_type == 'mp3' and child.text() == "🎵 MP3 다운":
                child.setText("🎵 중지")
                child.setStyleSheet("""
                    QPushButton {
                        background-color: #ff4a4a;
                        color: white;
                        border: none;
                        padding: 5px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #ff6b6b;
                    }
                """)

    def reset_download_buttons(self):
        """다운로드 버튼 초기 상태로 복구"""
        for child in self.findChildren(QPushButton):
            if child.text() in ["📺 중지", "📺 MP4 다운"]:
                child.setText("📺 MP4 다운")
                child.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
            elif child.text() in ["🎵 중지", "🎵 MP3 다운"]:
                child.setText("🎵 MP3 다운")
                child.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)

    def stop_download(self, format_type):
        """다운로드 중지"""
        self.downloading_type = None
        for worker in self.download_workers:
            if hasattr(worker, 'stop'):
                worker.stop()
        self.download_workers.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("다운로드가 취소되었습니다.")
        self.reset_download_buttons()
    
    def download_all(self, urls, format_type, save_path):
        try:
            self.download_workers = []
            completed = 0
            total = len(urls)
            
            def on_download_progress(status, percentage):
                if self.downloading_type:  # 다운로드가 취소되지 않았을 때만 진행률 업데이트
                    current_progress = (completed * 100 + percentage) / total
                    self.progress_bar.setValue(int(current_progress))
                    self.status_label.setText(f"{status} ({completed+1}/{total})")
            
            def on_download_finished(message):
                nonlocal completed
                if self.downloading_type:  # 다운로드가 취소되지 않았을 때만 처리
                    completed += 1
                    if completed == total:
                        QMessageBox.information(self, "완료", f"모든 다운로드가 완료되었습니다. ({total}개)")
                        self.progress_bar.setValue(0)
                        self.status_label.setText("")
                        self.downloading_type = None
                        self.reset_download_buttons()
                        # 다운로드 폴더 열기
                        QDesktopServices.openUrl(QUrl.fromLocalFile(save_path))
            
            def on_download_error(error):
                if self.downloading_type:  # 다운로드가 취소되지 않았을 때만 에러 메시지 표시
                    QMessageBox.warning(self, "오류", f"다운로드 중 오류가 발생했습니다: {error}")
            
            quality = self.quality_combo.currentText()
            for url in urls:
                if not self.downloading_type:  # 다운로드가 취소되었다면 루프 종료
                    break
                worker = DownloadWorker(url, format_type, save_path, quality)
                worker.progress_signal.connect(on_download_progress)
                worker.finished_signal.connect(on_download_finished)
                worker.error_signal.connect(on_download_error)
                self.download_workers.append(worker)
                worker.start()
                
        except Exception as e:
            QMessageBox.critical(self, "오류", f"다운로드 초기화 중 오류가 발생했습니다: {str(e)}")
            self.downloading_type = None
            self.reset_download_buttons()
    
    
    def check_ffmpeg(self):
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True)
            return True
        except FileNotFoundError:
            return False

    def install_ffmpeg(self):
        try:
            self.status_label.setText("FFmpeg 설치 중...")
            self.progress_bar.show()
            self.progress_bar.setValue(10)

            # 설치 경로
            install_dir = os.path.expandvars(r'%LOCALAPPDATA%\Programs\ffmpeg')
            os.makedirs(install_dir, exist_ok=True)
            
            # FFmpeg 다운로드
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            self.status_label.setText("FFmpeg 다운로드 중...")
            self.progress_bar.setValue(30)
            
            response = requests.get(ffmpeg_url, stream=True)
            response.raise_for_status()
            
            # 임시 파일에 저장
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, 'ffmpeg.zip')
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.status_label.setText("FFmpeg 설치 파일 압축 해제 중...")
            self.progress_bar.setValue(60)
            
            # 압축 해제
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # FFmpeg 파일 복사
            self.status_label.setText("FFmpeg 설치 완료 중...")
            self.progress_bar.setValue(80)
            
            ffmpeg_temp_dir = next(d for d in os.listdir(temp_dir) if d.startswith('ffmpeg'))
            ffmpeg_bin_dir = os.path.join(install_dir, 'bin')
            os.makedirs(ffmpeg_bin_dir, exist_ok=True)
            
            for file in ['ffmpeg.exe', 'ffplay.exe', 'ffprobe.exe']:
                src = os.path.join(temp_dir, ffmpeg_temp_dir, 'bin', file)
                dst = os.path.join(ffmpeg_bin_dir, file)
                shutil.copy2(src, dst)
            
            # PATH에 추가
            if ffmpeg_bin_dir not in os.environ['PATH']:
                os.environ['PATH'] = ffmpeg_bin_dir + os.pathsep + os.environ['PATH']
            
            # 임시 파일 정리
            shutil.rmtree(temp_dir)
            
            self.progress_bar.setValue(100)
            self.status_label.setText("FFmpeg 설치 완료!")
            return True
            
        except Exception as e:
            print(f"FFmpeg 설치 실패: {str(e)}")
            return False

    def change_download_path(self):
        new_path = QFileDialog.getExistingDirectory(
            self,
            "다운로드 기본 경로 선택",
            self.download_path,
            QFileDialog.Option.ShowDirsOnly
        )
        if new_path:
            self.download_path = new_path
            QMessageBox.information(self, "알림", f"다운로드 경로가 변경되었습니다:\n{new_path}")
    
    def on_time_frame_changed(self, text):
        if text == "날짜 직접 선택":
            self.date_input_container.show()
        else:
            self.date_input_container.hide()

    def validate_dates(self):
        if self.time_frame.currentText() == "날짜 직접 선택":
            try:
                start = datetime.strptime(self.start_date.text(), "%Y-%m-%d")
                end = datetime.strptime(self.end_date.text(), "%Y-%m-%d")
                if start > end:
                    QMessageBox.warning(self, "날짜 오류", "시작일이 종료일보다 늦을 수 없습니다.")
                    return False
                if end > datetime.now():
                    QMessageBox.warning(self, "날짜 오류", "종료일이 현재 날짜보다 늦을 수 없습니다.")
                    return False
                return True
            except ValueError:
                QMessageBox.warning(self, "날짜 오류", "올바른 날짜 형식을 입력해주세요 (YYYY-MM-DD)")
                return False
        return True

class AIRecommendationDialog(QDialog):
    def __init__(self, results, parent=None):
        super().__init__(parent)
        self.results = results
        self.setWindowTitle("AI 추천 아이디어")
        self.setStyleSheet("QDialog { background-color: #f5f5f5; } QLabel { color: black; }")
        self.setFixedSize(1000, 800)
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        self.setStyleSheet("""
            QDialog, QTextEdit, QScrollArea {
                background-color: white;
            }
            QLabel, QTextEdit {
                color: black;
            }
            QScrollArea {
                border: none;
            }
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(40, 20, 40, 40)

        # 상단 헤더
        header = QLabel("AI 콘텐츠 아이디어 리포트")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            margin-bottom: 20px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollBar:vertical {
                width: 10px;
                background: #f0f0f0;
            }
            QScrollBar::handle:vertical {
                background: #4a9eff;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(30)

        # 본문 텍스트 영역
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: white;
                font-size: 14px;
                line-height: 1.6;
            }
        """)

        # 결과 텍스트 파싱 및 HTML 생성
        html_content = self.parse_results()
        text_edit.setHtml(html_content)
        
        content_layout.addWidget(text_edit)
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # 하단 버튼
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(15)

        copy_button = QPushButton("📋 전체 복사")
        copy_button.clicked.connect(self.copy_all_content)
        
        close_button = QPushButton("닫기")
        close_button.clicked.connect(self.close)

        button_layout.addWidget(copy_button)
        button_layout.addWidget(close_button)
        
        layout.addWidget(button_container, alignment=Qt.AlignmentFlag.AlignCenter)

    def parse_results(self):
        """결과 텍스트를 파싱하고 HTML 형식으로 반환"""
        # 눈이 편안한 색상들
        colors = [
            "#5383EC",  # 편안한 파란색
            "#F06292",  # 부드러운 분홍색 
            "#4CAF50",  # 편안한 녹색
            "#FF9800",  # 부드러운 주황색
            "#7E57C2"   # 편안한 보라색
        ]
        
        raw_text = self.results['ideas'].replace('*', '')
        
        html = """
        <style>
            .section-header {
                color: white;
                font-size: 22px;
                font-weight: bold;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                margin: 30px 0 20px 0;
            }
            
            .trend-header {
                background-color: #4a9eff;
            }
            
            .ideas-header {
                background-color: #ff69b4;
            }
            
            .trend-item {
                background-color: white;
                padding: 15px;
                margin: 15px 0;
                border-radius: 8px;
                border: 1px solid #e3e3e3;
                color: #111111;
            }
            
            .trend-category {
                margin: 20px 0;
                padding: 15px;
                background-color: white;
                border-radius: 10px;
            }

            .trend-title {
                margin-bottom: 15px;
                padding-bottom: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            
            .idea-box {
                background-color: white;
                padding: 20px;
                margin: 25px 0;
                border-radius: 10px;
            }
            
            .idea-item {
                background-color: #f8f8f8;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                color: #111111;
            }

            .point-list {
                margin-top: 10px;
                margin-bottom: 10px;
                padding-left: 20px;
            }

            .point-item {
                margin-bottom: 8px;
                line-height: 1.4;
            }
        </style>
        """
        
        # 트렌드 섹션 파싱
        if "[시청자 트렌드 분석]" in raw_text:
            html += """
            <div class="section-header trend-header">
                📊 시청자 트렌드 분석
            </div>
            """
            
            # 시청자 트렌드 분석 내용 추출
            trend_section = ""
            if "[시청자 트렌드 분석]" in raw_text and "[추천 콘텐츠 아이디어]" in raw_text:
                trend_section = raw_text.split("[시청자 트렌드 분석]")[1].split("[추천 콘텐츠 아이디어]")[0]
            
            # 트렌드 항목 파싱 - 주제와 내용 구분 명확화
            trend_categories = []
            current_items = []
            current_category = None

            lines = trend_section.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 새로운 카테고리 시작 (- 로 시작하는 항목 전)
                if not line.startswith('-') and (':' in line or (current_category and current_items)):
                    # 이전 카테고리가 있으면 저장
                    if current_category and current_items:
                        trend_categories.append((current_category, current_items))
                        current_items = []
                    
                    if ':' in line:
                        current_category = line.split(':', 1)[0].strip()
                    else:
                        current_category = line
                
                # 항목 라인
                elif line.startswith('-'):
                    item_text = line[1:].strip()
                    
                    # 카테고리가 없는 경우 첫 번째 항목을 기반으로 카테고리 생성
                    if not current_category:
                        current_category = "주요 트렌드"
                    
                    current_items.append(item_text)

            # 마지막 카테고리 처리
            if current_category and current_items:
                trend_categories.append((current_category, current_items))

            # 카테고리별 아이콘 정의 - 일관된 이모티콘 사용
            category_icons = {
                "시청자의 주요 질문 또는 요청사항": "❓",
                "시청자가 가장 긍정적으로 반응하는 콘텐츠 특징": "👍",
                "지금 시청자들이 가장 관심 있어하는 주제": "🎯",
            }

            # 기본 카테고리 아이콘 목록 (위에 없는 카테고리에 사용)
            default_icons = ["📊", "💡", "🏆", "📈", "⭐"]

            # 모든 카테고리와 항목 렌더링
            for i, (category, items) in enumerate(trend_categories):
                # 카테고리에 맞는 아이콘 가져오기, 없으면 기본값 사용
                icon = category_icons.get(category, default_icons[i % len(default_icons)])
                
                # 항상 category_color 정의
                category_color = "#4a9eff"  # 파란색 (트렌드 분석용)
                
                # 첫 번째 카테고리인 경우 (시청자 트렌드/주요 트렌드) 헤더를 표시하지 않음
                if i == 0 and category in ["시청자 트렌드", "주요 트렌드"]:
                    html += f"""
                    <div class="trend-items" style="padding: 0 10px;">
                    """
                else:
                    html += f"""
                    <div class="section-header trend-header" style="background-color: {category_color}; margin-top: 25px; margin-bottom: 15px;">
                        {icon} {category}
                    </div>
                    <div class="trend-items" style="padding: 0 10px;">
                    """
                
                # 주제 출력 (삼각형 이모티콘과 함께)
                for item in items:
                    # 모든 항목을 동일한 스타일로 표시 (들여쓰기 일관성 유지)
                    if ":" in item:
                        # 제목과 내용이 있는 경우
                        title_content = item.split(':', 1)
                        title = title_content[0] + ":"
                        content = title_content[1].strip()
                        
                        # 제목 표시
                        html += f"""
                        <div style="background-color: #f0f8ff; margin: 15px 0; padding: 12px 15px; border-radius: 5px; border-left: 4px solid {category_color};">
                            <span style="color: #0066cc; font-size: 15px; font-weight: bold;">▶ {title}</span>
                        </div>
                        """
                        
                        # 내용 표시 (들여쓰기)
                        html += f"""
                        <div style="background-color: white; margin: 5px 0 15px 25px; padding: 10px 15px; border-radius: 5px;">
                            <span style="color: #333333; font-size: 14px;">{content}</span>
                        </div>
                        """
                    else:
                        # 내용만 있는 항목 (똑같이 들여쓰기된 스타일로 표시)
                        html += f"""
                        <div style="background-color: white; margin: 5px 0 15px 25px; padding: 10px 15px; border-radius: 5px;">
                            <span style="color: #333333; font-size: 14px;">{item}</span>
                        </div>
                        """
                
                html += """
                </div>
                </div>
                """
        
        # 아이디어 섹션 파싱
        if "[추천 콘텐츠 아이디어]" in raw_text:
            html += """
            <div class="section-header ideas-header">
                💡 추천 콘텐츠 아이디어
            </div>
            """
            
            # 추천 아이디어 부분 추출
            ideas_section = raw_text.split("[추천 콘텐츠 아이디어]")[1]
            
            # 각 아이디어 식별 (더 정확한 패턴 사용)
            idea_blocks = []
            current_block = []
            
            for line in ideas_section.strip().split('\n'):
                if re.match(r'^아이디어\s*\d+', line.strip()):
                    if current_block:
                        idea_blocks.append(current_block)
                        current_block = []
                    current_block.append(line)
                elif current_block:
                    current_block.append(line)
            
            # 마지막 블록 추가
            if current_block:
                idea_blocks.append(current_block)
            
            # 각 아이디어 블록을 HTML로 변환
            for i, block in enumerate(idea_blocks):
                color = colors[i % len(colors)]
                
                # 아이디어 제목 추출
                title = block[0].strip()
                
                html += f"""
                <div class="idea-box" style="border-left: 3px solid {color};">
                    <div style="font-size: 20px; font-weight: bold; color: {color}; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee;">
                        ✨ {title}
                    </div>
                """
                
                # 섹션 추적 변수
                found_sections = {
                    '제목 예시': False,
                    '핵심 포인트': False,
                    '차별화 요소': False,
                    '목표 시청자': False
                }
                
                # 핵심 포인트 항목 임시 저장
                core_points = []
                
                # 아이디어 내용 분석
                for j, line in enumerate(block[1:]):
                    line_text = line.strip()
                    if not line_text:
                        continue
                    
                    # 각 섹션 인식 및 처리
                    if '제목 예시' in line_text and not found_sections['제목 예시']:
                        # 제목 예시 처리
                        content = line_text.split(':', 1)[1].strip() if ':' in line_text else ""
                        html += f"""
                        <div class="idea-item">
                            📝 <span style="font-weight: bold; color: {color};">제목 예시:</span> {content}
                        </div>
                        """
                        found_sections['제목 예시'] = True
                        
                    elif '핵심 포인트' in line_text and not found_sections['핵심 포인트']:
                        # 핵심 포인트 시작 (여러 항목 수집 시작)
                        found_sections['핵심 포인트'] = True
                        
                        # 다음 줄부터 항목 수집 (다른 섹션 시작되기 전까지)
                        for k in range(j + 1, len(block[1:])):
                            next_line = block[1:][k].strip()
                            # 다른 섹션 시작되면 중단
                            if any(section in next_line for section in ['차별화 요소', '목표 시청자']) and ':' in next_line:
                                break
                            # 항목 추가 (불필요한 마크업 제거)
                            if next_line and next_line.startswith('-') or next_line.startswith('*'):
                                point = next_line[1:].strip()
                                # 이모지나 특수 기호 제거
                                point = re.sub(r'^[📌🎯🔍👥•*]', '', point).strip()
                                # 콜론 제거
                                if point.endswith(':'):
                                    point = point[:-1].strip()
                                core_points.append(point)
                        
                        # 핵심 포인트 항목 렌더링
                        if core_points:
                            html += f"""
                            <div class="idea-item">
                                🎯 <span style="font-weight: bold; color: {color};">핵심 포인트:</span>
                                <ul class="point-list">
                            """
                            
                            for point in core_points:
                                html += f'<li class="point-item">{point}</li>'
                            
                            html += """
                                </ul>
                            </div>
                            """
                        
                    elif '차별화 요소' in line_text and not found_sections['차별화 요소']:
                        # 차별화 요소 처리
                        content = line_text.split(':', 1)[1].strip() if ':' in line_text else ""
                        html += f"""
                        <div class="idea-item">
                            🔍 <span style="font-weight: bold; color: {color};">차별화 요소:</span> {content}
                        </div>
                        """
                        found_sections['차별화 요소'] = True
                        
                    elif '목표 시청자' in line_text and not found_sections['목표 시청자']:
                        # 목표 시청자 처리
                        content = line_text.split(':', 1)[1].strip() if ':' in line_text else ""
                        html += f"""
                        <div class="idea-item">
                            👥 <span style="font-weight: bold; color: {color};">목표 시청자:</span> {content}
                        </div>
                        """
                        found_sections['목표 시청자'] = True
                
                html += "</div>"  # idea-box 종료
        
        return html
    def copy_all_content(self):
        """모든 내용을 클립보드에 복사"""
        try:
            all_content = self.results['ideas']
            QApplication.clipboard().setText(all_content)
            QMessageBox.information(self, "알림", "모든 내용이 클립보드에 복사되었습니다.")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"복사 중 오류가 발생했습니다: {str(e)}")

class ScriptGeneratorDialog(QDialog):
    def __init__(self, videos, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("📝 대본 생성기")
        self.setStyleSheet("QDialog { background-color: #f5f5f5; } QLabel { color: black; }")
        self.setFixedSize(1000, 800)
        
        # 1개의 영상만 선택 (정확도 향상을 위해)
        if videos:
            # 선택된 영상이 있으면 첫 번째 선택된 영상 사용
            self.selected_video = videos[0]
            self.api_key = None
            
            # 임시 UI 표시 (로딩 중)
            layout = QVBoxLayout(self)
            self.loading_label = QLabel("선택한 영상의 자막을 수집하고 있습니다...")
            self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.loading_label.setStyleSheet("font-size: 18px; color: #333; margin: 20px;")
            
            self.progress = QProgressBar()
            self.progress.setRange(0, 100)
            self.progress.setValue(10)
            self.progress.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                    background-color: #f0f0f0;
                }
                QProgressBar::chunk {
                    background-color: #4a9eff;
                    border-radius: 5px;
                }
            """)
            
            layout.addStretch()
            layout.addWidget(self.loading_label)
            layout.addWidget(self.progress)
            layout.addStretch()
            
            # 자막 수집 시작 (딜레이를 줘서 UI가 먼저 표시되도록)
            QTimer.singleShot(100, self.collect_subtitle)
        else:
            QMessageBox.warning(self, "경고", "분석할 영상이 없습니다.")
            self.reject()
    
    def collect_subtitle(self):
        """선택한 영상의 자막 수집"""
        try:
            # API 키 확인
            try:
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.api_key = settings.get('google_ai_api_key')
                    if not self.api_key:
                        raise Exception("API 키가 설정되지 않았습니다.")
            except Exception as e:
                QMessageBox.warning(self, "경고", "Google AI Studio API 키를 설정에서 먼저 입력해주세요.")
                self.reject()
                return
            
            self.progress.setValue(20)
            video_id = self.selected_video['video_url'].split('v=')[1]
            
            # 이미 자막이 있는 경우 건너뛰기
            if self.selected_video.get('transcript') and self.selected_video['transcript'] not in ["자막수집", "자막 없음"]:
                self.init_ui()
                return
            
            self.loading_label.setText("자막을 가져오는 중입니다...")
            
            # YouTube 자막 가져오기
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript = None
                
                try:
                    transcript = transcript_list.find_transcript(['ko'])
                except:
                    try:
                        transcript = transcript_list.find_transcript(['en'])
                    except:
                        try:
                            transcript = transcript_list.find_generated_transcript(['ko', 'en'])
                        except:
                            self.selected_video['transcript'] = "자막 없음"
                            QMessageBox.warning(self, "경고", "이 영상에는 자막이 없습니다.")
                            self.reject()
                            return
                
                self.progress.setValue(50)
                
                # 자막 텍스트 추출 (시간 정보 없이)
                transcript_text = "\n".join([line['text'] for line in transcript.fetch()])
                self.selected_video['transcript'] = transcript_text
                
            except (NoTranscriptFound, TranscriptsDisabled):
                self.selected_video['transcript'] = "자막 없음"
                QMessageBox.warning(self, "경고", "이 영상에는 자막이 제공되지 않습니다.")
                self.reject()
                return
            except Exception as e:
                self.selected_video['transcript'] = "자막 없음"
                QMessageBox.warning(self, "경고", "자막 수집 중 오류가 발생했습니다. 다른 영상을 시도해보세요.")
                self.reject()
                return
            
            # 테이블에도 자막 업데이트
            for row in range(self.parent.table.rowCount()):
                if row < len(self.parent.search_results):
                    if self.parent.search_results[row]['video_url'] == self.selected_video['video_url']:
                        self.parent.search_results[row]['transcript'] = transcript_text
                        
                        # 테이블 UI 업데이트
                        item = QTableWidgetItem(transcript_text[:100] + "...")
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        item.setBackground(QColor("#E3F2FD"))
                        item.setData(Qt.ItemDataRole.UserRole, transcript_text)
                        item.setToolTip(transcript_text)
                        self.parent.table.setItem(row, 15, item)
                        break
            
            self.progress.setValue(70)
            
            # 자막 수집 완료 후 메인 UI 초기화
            self.init_ui()
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"자막 수집 중 오류가 발생했습니다: {str(e)}")
            self.reject()
    
    def init_ui(self):
        """메인 UI 초기화"""
        # 기존 위젯 제거
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            QWidget().setLayout(self.layout())
        
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333;
                font-weight: bold;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: #f9f9f9;
                line-height: 1.5;
            }
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d8ae0;
            }
            QProgressBar {
                border: none;
                border-radius: 5px;
                text-align: center;
                height: 15px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #4a9eff;
                border-radius: 5px;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 15px;
                padding: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #4a9eff;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 상단 제목
        title_label = QLabel("📝 유튜브 대본 생성기")
        title_label.setStyleSheet("""
            font-size: 24px;
            color: #4a9eff;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 선택된 영상 정보
        video_info = QGroupBox("📹 선택된 영상")
        video_layout = QVBoxLayout(video_info)
        
        title = QLabel(f"제목: {self.selected_video['title']}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setWordWrap(True)
        
        channel = QLabel(f"채널: {self.selected_video['channel_title']}")
        channel.setStyleSheet("font-size: 14px; color: #555;")
        
        views = QLabel(f"조회수: {int(self.selected_video['view_count']):,}회")
        views.setStyleSheet("font-size: 14px; color: #555;")
        
        video_layout.addWidget(title)
        video_layout.addWidget(channel)
        video_layout.addWidget(views)
        
        main_layout.addWidget(video_info)
        
        # 탭 위젯 추가
        self.tabs = QTabWidget()  # self를 추가하여 클래스 변수로 만듭니다
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 10px 15px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #4a9eff;
                color: white;
                font-weight: bold;
            }
        """)
        
        # 분석 결과 탭
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        analysis_layout.setSpacing(10)
        
        # 분석 결과를 하나의 텍스트 에디터에 통합
        analysis_label = QLabel("🔍 영상 분석 결과")
        analysis_label.setStyleSheet("font-size: 16px; color: #4a9eff;")
        analysis_layout.addWidget(analysis_label)
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                line-height: 1.6;
                padding: 15px;
                background-color: #f9f9f9;
            }
        """)
        analysis_layout.addWidget(self.analysis_text)
        
        # 대본 생성 탭
        script_tab = QWidget()
        script_layout = QVBoxLayout(script_tab)

        # 상단 컨트롤 컨테이너 (스타일 선택과 프롬프트 입력을 가로로 배치)
        controls_container = QWidget()
        controls_container.setFixedHeight(80)  # 전체 컨테이너 높이 제한
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(10)  # 좌우 간격 설정

        # 1. 대본 스타일 선택 영역 (왼쪽)
        style_group = QGroupBox("대본 스타일 선택")
        style_group.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                margin-top: 8px;
                padding: 4px;
            }
        """)
        style_layout = QVBoxLayout(style_group)  # 라디오 버튼을 세로로 쌓음
        style_layout.setSpacing(2)
        style_layout.setContentsMargins(5, 12, 5, 2)

        # 라디오 버튼 추가
        self.rewrite_radio = QRadioButton("✍️ AI 원본 재구성 (쇼츠 방향성)")
        self.rewrite_radio.setChecked(True)  # 기본값
        self.rewrite_radio.setStyleSheet("""
            QRadioButton {
                font-size: 12px;
                font-weight: bold;
                color: #333;
                padding: 1px;
            }
        """)

        self.structure_radio = QRadioButton("🏆 AI 3단계 구조화 (롱폼 방향성)")
        self.structure_radio.setStyleSheet("""
            QRadioButton {
                font-size: 12px;
                font-weight: bold;
                color: #333;
                padding: 1px;
            }
        """)

        # 툴팁 설정
        self.rewrite_radio.setToolTip("원본 자막의 주제와 구성을 유지하면서 어문저작권 침해 없이 단어와 표현만 바꿉니다")
        self.structure_radio.setToolTip("완전히 새로운 인트로-본론-아웃트로 구조의 대본을 생성합니다")

        style_layout.addWidget(self.rewrite_radio)
        style_layout.addWidget(self.structure_radio)

        # 2. 추가 프롬프트 입력 영역 (오른쪽)
        prompt_container = QGroupBox("추가 프롬프트 (선택사항)")
        prompt_container.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                margin-top: 8px;
                padding: 0px;
            }
        """)
        # 기본 레이아웃 (QGroupBox에는 반드시 필요함)
        prompt_layout = QVBoxLayout(prompt_container)
        prompt_layout.setSpacing(0)
        prompt_layout.setContentsMargins(2, 15, 2, 2)  # 상단 여백만 제목 때문에 약간 유지

        # 추가 프롬프트 입력 필드 - 이제 직접 섹션에 추가
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("새로운 대본 생성해줘")
        self.prompt_input.setStyleSheet("""
            QTextEdit {
                font-size: 12px;
                padding: 4px;
                background-color: #f9f9f9;
                border: none;
                border-radius: 3px;
            }
        """)
        prompt_layout.addWidget(self.prompt_input)

        # 각 영역을 가로 레이아웃에 추가 (비율 조절)
        controls_layout.addWidget(style_group, 1)  # 왼쪽 40%
        controls_layout.addWidget(prompt_container, 2)  # 오른쪽 60%

        # 컨트롤 컨테이너를 메인 레이아웃에 추가
        script_layout.addWidget(controls_container)

        # 각 영역을 가로 레이아웃에 추가 (비율 조절)
        controls_layout.addWidget(style_group, 1)  # 왼쪽 40%
        controls_layout.addWidget(prompt_container, 2)  # 오른쪽 60%

        # 컨트롤 컨테이너를 메인 레이아웃에 추가
        script_layout.addWidget(controls_container)
        
        
        # 생성된 대본 표시 영역
        script_label = QLabel("생성된 대본")
        script_layout.addWidget(script_label)
        
        self.script_output = QTextEdit()
        self.script_output.setReadOnly(True)
        self.script_output.setPlaceholderText("분석 후 대본이 여기에 표시됩니다...")
        script_layout.addWidget(self.script_output)
        
        # 탭 추가
        self.tabs.addTab(analysis_tab, "분석 결과")
        self.tabs.addTab(script_tab, "대본 생성")
        main_layout.addWidget(self.tabs)
        
        # 하단 버튼 영역
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 진행 상태 표시 영역 추가
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(5)
        
        # 상태 텍스트 라벨 추가
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #4a9eff;
            font-weight: bold;
            font-size: 12px;
        """)
        self.status_label.hide()
        progress_layout.addWidget(self.status_label)
        
        # 진행 바 설정
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        progress_layout.addWidget(self.progress_bar)
        
        button_layout.addWidget(progress_container, 1)  # 스트레치 팩터 1을 부여하여 중앙 정렬
        
        button_layout.addStretch()
        
        self.generate_button = QPushButton("대본 생성하기")
        self.generate_button.clicked.connect(self.generate_script)
        button_layout.addWidget(self.generate_button)
        
        self.copy_button = QPushButton("대본 복사")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copy_script)
        button_layout.addWidget(self.copy_button)
        
        close_button = QPushButton("닫기")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        main_layout.addWidget(button_container)
        
        # 자막 분석 자동 시작
        QTimer.singleShot(500, self.analyze_subtitles)
    
    def analyze_subtitles(self):
        """자막 분석"""
        if not self.selected_video.get('transcript') or self.selected_video['transcript'] in ["자막수집", "자막 없음"]:
            QMessageBox.warning(self, "경고", "자막이 없습니다.")
            return
        
        self.status_label.setText("분석 중...")
        self.status_label.show()
        self.progress_bar.show()
        self.progress_bar.setValue(10)
        self.generate_button.setEnabled(False)
        
        # 워커 스레드 생성
        self.worker = ScriptAnalysisWorker([self.selected_video], self.api_key)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.analysis_signal.connect(self.update_analysis)
        self.worker.error_signal.connect(self.handle_error)
        self.worker.start()
    
    def update_progress(self, message, value):
        self.progress_bar.setValue(value)
    
    def update_analysis(self, results):
        # 별표(*) 제거 및 분석 결과 정리
        summary = self.clean_text(results.get('summary', ''), is_summary=True)  # is_summary=True 추가
        structure = self.clean_text(results.get('structure', ''))
        hooking = self.clean_text(results.get('hooking', ''))
        keywords = self.clean_text(results.get('keywords', ''))
        
        # HTML로 통합된 분석 결과 텍스트 생성 (배경색 추가)
        analysis_html = f"""
        <html>
        <head>
            <style>
                .section-title {{
                    font-size: 16px;
                    font-weight: bold;
                    padding: 8px 12px;
                    border-radius: 5px;
                    margin-top: 18px;
                    margin-bottom: 12px;
                    color: white;
                }}
                .section-content {{
                    padding: 12px 15px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    margin-bottom: 18px;
                    line-height: 1.6;
                    color: #111111;
                }}
                .summary-title {{ background-color: #3498db; }}
                .structure-title {{ background-color: #2ecc71; }}
                .hook-title {{ background-color: #e74c3c; }}
                .keywords-title {{ background-color: #9b59b6; }}
                p {{
                    margin: 8px 0;
                    font-size: 14px;
                    color: #111111;
                }}
            </style>
        </head>
        <body>
            <div class="section-title summary-title">📝 요약</div>
            <div class="section-content">{summary}</div>
            
            <div class="section-title structure-title">📊 구성 방식</div>
            <div class="section-content">{structure}</div>
            
            <div class="section-title hook-title">🎣 초반 후킹 방법</div>
            <div class="section-content">{hooking}</div>
            
            <div class="section-title keywords-title">🔑 주요 키워드</div>
            <div class="section-content">{keywords}</div>
        </body>
        </html>
        """
        
        # HTML 텍스트로 설정
        self.analysis_text.setHtml(analysis_html)
        
        # 분석이 완료되면 대본 생성 버튼 활성화
        self.generate_button.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText("분석 완료!")
        QTimer.singleShot(1500, lambda: self.status_label.hide())  # 1.5초 후 상태 텍스트 숨기기
        
        # 분석 결과 저장
        self.analysis_results = results
    
    def clean_text(self, text, is_summary=False):
        """텍스트 정리: 별표 제거, 줄바꿈 정리, 중복 내용 제거, 자연스러운 형식 유지"""
        # 별표 제거
        text = text.replace('*', '').replace('**', '')
        
        # 여러 개의 연속 줄바꿈을 2개로 제한
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        # 불필요한 서술 부분 제거
        remove_phrases = [
            "다음과 같습니다",
            "다음과 같이 분석됩니다",
            "분석한 결과는 다음과 같습니다",
            "자세히 살펴보면",
            "자막을 분석한 결과",
            "다음과 같은 특징이 있습니다",
            "확인할 수 있습니다"
        ]
        
        for phrase in remove_phrases:
            text = text.replace(phrase, "")
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        # 줄 단위로 처리하여 중복 제거
        lines = text.split('\n')
        unique_lines = []
        content_set = set()  # 중복 내용 체크용
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 숫자 글머리 기호 제거하여 내용만 추출 (번호가 있을 경우)
            content = re.sub(r'^[0-9]+\.\s*', '', line)
            
            # 이미 같은 내용이 있는지 확인
            if content not in content_set:
                content_set.add(content)
                unique_lines.append(content)
        
        # 요약 파트인 경우, 문장마다 줄바꿈 추가
        if is_summary:
            processed_lines = []
            for line in unique_lines:
                # 문장 분리 (문장 끝 부호를 포함한 문장 단위로 분리)
                sentences = re.findall(r'[^.!?]+[.!?]', line + '.')  # 줄 끝에 . 추가하여 마지막 문장도 포함
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence and sentence != '.':  # 빈 문장 및 단독 마침표 제외
                        processed_lines.append(sentence)
            unique_lines = processed_lines
        
        # 번호 다시 매기기 (요약이 아닌 경우만)
        if not is_summary:
            processed_lines = []
            for i, content in enumerate(unique_lines, 1):
                # 원래 콜론이 있으면 구조 유지, 없으면 그냥 번호만 추가
                processed_lines.append(f"{i}. {content}")
            unique_lines = processed_lines
        
        # 줄 단위로 HTML 포맷 적용
        html_lines = []
        for line in unique_lines:
            if not line.strip():
                continue
                
            # 숫자로 시작하는 줄에 스타일 적용
            number_match = re.match(r'^([0-9]+)\.\s*(.*)', line)
            if number_match:
                html_lines.append(f'<p style="font-weight: bold; color: black; margin-top: 10px;">{line}</p>')
            # 글머리 기호로 시작하는 줄에 스타일 적용
            elif line.startswith('-'):
                html_lines.append(f'<p style="margin-left: 15px; margin-top: 5px;">{line}</p>')
            else:
                html_lines.append(f'<p>{line}</p>')
        
        return ''.join(html_lines)

    def similarity(self, str1, str2):
        """두 문자열의 유사성 계산 (0~1 사이 값, 1이면 동일)"""
        # 매우 간단한 유사성 검사: 소문자로 변환 후 두 문자열의 공통 단어 비율 확인
        set1 = set(str1.lower().split())
        set2 = set(str2.lower().split())
        
        if not set1 or not set2:
            return 0
        
        # 자카드 유사도 계산
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0
    
    def remove_asterisks(self, text):
        """텍스트에서 별표(*) 제거"""
        return text.replace('*', '').replace('**', '')
    
    def generate_script(self):
        """대본 생성"""
        self.status_label.setText("대본 생성 중...")
        self.status_label.show()
        self.progress_bar.show()
        self.progress_bar.setValue(10)
        self.generate_button.setEnabled(False)
        
        # 추가 프롬프트 가져오기
        additional_prompt = self.prompt_input.toPlainText()
        
        # 선택된 모드 확인
        selected_mode = "rewrite" if self.rewrite_radio.isChecked() else "structure"

        # 워커 스레드 생성
        self.script_worker = ScriptGenerationWorker(self.analysis_results, additional_prompt, self.api_key, selected_mode)
        self.script_worker.progress_signal.connect(self.update_progress)
        self.script_worker.script_signal.connect(self.update_script)
        self.script_worker.error_signal.connect(self.handle_error)
        self.script_worker.start()
    
    def update_script(self, script):
        """대본 결과 표시 및 포맷팅"""
        # 별표(*) 제거
        script = self.remove_asterisks(script)
        
        # 시간 표현 패턴 제거 (예: "0-8초", "30초 간격", "1분 30초 지점" 등)
        script = re.sub(r'\b\d+[-~]?\d*\s*초\b', '', script)
        script = re.sub(r'\b\d+\s*분\s*\d*\s*초?\b', '', script)
        
        # HTML 형식으로 변환하여 가독성 개선
        formatted_script = self.format_script_as_html(script)
        
        # HTML 텍스트로 설정
        self.script_output.setHtml(formatted_script)
        self.generate_button.setEnabled(True)
        self.copy_button.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText("대본 생성 완료!")
        QTimer.singleShot(1500, lambda: self.status_label.hide())  # 1.5초 후 상태 텍스트 숨기기
        
        # 대본 생성 탭으로 자동 전환
        self.tabs.setCurrentIndex(1)  # 대본 생성 탭 인덱스는 1
    
    def format_script_as_html(self, script):
        """대본을 HTML 형식으로 변환하여 가독성 향상 - 더 깔끔한 디자인"""
        
        # 제목 먼저 추출
        title = ""
        title_match = re.search(r'제목\s*:\s*(.+?)[\n\r]', script)
        if title_match:
            title = title_match.group(1).strip()
            # 제목 줄 제거
            script = re.sub(r'제목\s*:\s*.+?[\n\r]', '', script, 1)
        
        # 섹션을 분리하기 위한 정규 표현식
        sections = re.split(r'\[([^\]]+)\]', script)
        
        # 결과 HTML
        html_parts = []
        
        # 제목이 있으면 추가 (깔끔한 스타일)
        if title:
            html_parts.append(f'<h2 style="color:#4a9eff; margin:10px 0 20px 0; font-size:22px; font-weight:bold; text-align:left;">제목 : {title}</h2>')
        
        # 스타일 정의 - 가독성 높은 왼쪽 정렬 스타일로 변경
        styles = """
        <style>
            body {
                font-family: 'Noto Sans KR', sans-serif;
                line-height: 1.5;
                color: #333;
                background-color: #fff;
                padding: 10px;
            }
            .section-header {
                font-size: 16px;
                font-weight: bold;
                padding: 8px 12px;
                margin: 25px 0 15px 0;
                border-radius: 5px;
                color: white;
                text-align: left;
            }
            .section-content {
                padding: 10px 15px;
                margin: 0 0 15px 0;
                line-height: 1.5;
                font-size: 14px;
                color: #333;
                text-align: left;
            }
            .intro-header { background-color: #3498db; }
            .main-header { background-color: #2ecc71; }
            .outro-header { background-color: #e74c3c; }
            .default-header { background-color: #9b59b6; }
            
            .action { color: #FF5733; }
            .question { color: #9b59b6; font-weight: bold; }
            .subscribe { 
                background-color: #E8F5E9; 
                color: #2E7D32;
                padding: 2px 4px;
                border-radius: 3px;
            }
            p {
                margin: 8px 0;
                text-align: left;
            }
        </style>
        """
        
        # 섹션 별로 처리
        for i in range(0, len(sections)):
            if i % 2 == 0:  # 섹션 내용
                if i > 0:  # 첫 번째가 아닌 경우 (이전 섹션 제목이 있는 경우)
                    content = sections[i].strip()
                    
                    # 액션/감정 표현 스타일링 (소괄호 내용)
                    content = re.sub(r'\(([^)]+)\)', r'<span class="action">(\1)</span>', content)
                    
                    # 질문이나 중요 포인트 강조 (물음표가 포함된 문장)
                    content = re.sub(r'([^.!?]*\?[.!?]*)', r'<span class="question">\1</span>', content)
                    
                    # 구독 유도 멘트 강조
                    keywords = ['구독', '좋아요', '알림 설정', '알림설정', '알림 켜기', '구독하기', '좋아요 버튼']
                    for keyword in keywords:
                        content = re.sub(f'([^.!?]*{keyword}[^.!?]*[.!?])', r'<span class="subscribe">\1</span>', content)
                    
                    # 문장 단위로 줄바꿈 추가 (한 번만 추가하도록 수정)
                    content = re.sub(r'([.!?])\s+', r'\1<br>', content)
                    
                    # 내용을 단락으로 변환
                    paragraphs = content.split('\n\n')
                    formatted_paragraphs = []
                    for para in paragraphs:
                        if para.strip():
                            formatted_paragraphs.append(f"<p>{para.strip()}</p>")
                    
                    section_content = "\n".join(formatted_paragraphs)
                    html_parts.append(f'<div class="section-content">{section_content}</div>')
                    
            else:  # 섹션 제목
                section_title = sections[i].strip()
                header_class = "default-header"
                
                # 섹션 제목에 따라 클래스 결정
                if "인트로" in section_title.lower():
                    header_class = "intro-header"
                elif "본론" in section_title.lower() or "본문" in section_title.lower():
                    header_class = "main-header"
                elif "아웃트로" in section_title.lower() or "결론" in section_title.lower():
                    header_class = "outro-header"
                    
                html_parts.append(f'<div class="section-header {header_class}">{section_title}</div>')
        
        # 시작 부분 처리 (첫 번째 섹션 제목 전)
        if sections[0].strip():
            first_content = sections[0].strip()
            # 줄바꿈 한 번만
            first_content = re.sub(r'([.!?])\s+', r'\1<br>', first_content)
            html_parts.insert(0 if not title else 1, f'<div class="section-content"><p>{first_content}</p></div>')
        
        # 최종 HTML 구성
        complete_html = f"""
        <html>
        <head>
            {styles}
        </head>
        <body>
            {''.join(html_parts)}
        </body>
        </html>
        """
        
        return complete_html
    
    def copy_script(self):
        """대본 복사 - HTML 태그 없이 원본 텍스트만 복사"""
        plain_text = self.script_output.toPlainText()
        QApplication.clipboard().setText(plain_text)
        self.copy_button.setText("복사 완료!")
        QTimer.singleShot(1500, lambda: self.copy_button.setText("대본 복사"))
    
    def handle_error(self, error_message):
        self.progress_bar.hide()
        self.status_label.hide()
        self.generate_button.setEnabled(True)
        QMessageBox.critical(self, "오류", error_message)


class ScriptAnalysisWorker(QThread):
    progress_signal = pyqtSignal(str, int)
    analysis_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, videos, api_key):
        super().__init__()
        self.videos = videos
        self.api_key = api_key
    
    def run(self):
        try:
            import google.generativeai as genai
            
            self.progress_signal.emit("API 연결 중...", 20)
            
            # 여기서부터 수정
            # 현재 활성화된 API 키 가져오기
            parent = QApplication.activeWindow()
            if parent and hasattr(parent, 'gemini_api_manager'):
                gemini_api_manager = parent.gemini_api_manager
                current_key = next((k for k in gemini_api_manager.keys if k.is_current), None)
                
                if current_key and current_key.status == 'active':
                    api_key = current_key.key
                else:
                    # 사용 가능한 다음 키 찾기
                    next_key = gemini_api_manager.get_next_available_key()
                    if next_key:
                        api_key = next_key.key
                    else:
                        # 모든 키가 사용 불가능하면 입력된 키 사용
                        api_key = self.api_key
                    
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')
            else:
                # 기본 API 키 사용
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')
            # 수정 끝
            
            self.progress_signal.emit("영상 분석 중...", 40)
            
            # 자막 데이터 준비
            all_transcripts = []
            for video in self.videos:
                transcript = video.get('transcript', '')
                if transcript and transcript != "자막 없음":
                    all_transcripts.append({
                        'title': video.get('title', ''),
                        'transcript': transcript[:5000]  # 자막이 너무 길 경우 앞부분만 사용
                    })
            
            # 자막이 없는 경우
            if not all_transcripts:
                self.error_signal.emit("분석할 자막이 없습니다.")
                return
            
            self.progress_signal.emit("AI 분석 중...", 60)
            
            # AI 분석 프롬프트
            prompt = f"""당신은 유튜브 영상 자막 분석 및 대본 작성 전문가입니다.
            다음 영상의 자막을 분석하여 아래 4가지 요소를 도출해주세요. 각 섹션을 명확하게 구분하고 중복되지 않게 작성해주세요:

            영상 자막:
            {json.dumps(all_transcripts, ensure_ascii=False, indent=2)}

            분석 요청:
            다음 4개 섹션으로 정확히 구분하여 응답해주세요. 각 섹션 시작에 정확한 마커를 사용해주세요:

            [SUMMARY_START]
            이 영상의 핵심 내용을 3-4문장 이내로 간결하게 요약해주세요.
            [SUMMARY_END]

            [STRUCTURE_START]
            이 영상의 구성을 단계별로 정리해주세요. 도입-본론-결론 구조를 중심으로 최대 4-5개 단계로 간단히 설명해주세요.
            [STRUCTURE_END]

            [HOOK_START]
            이 영상이 시청자의 관심을 끌기 위해 사용한 방법을 3-4가지만 간략히 정리해주세요. 각 방법은 한 문장으로 설명해주세요.
            [HOOK_END]

            [KEYWORDS_START]
            영상에서 자주 언급되는 핵심 키워드 3-5개와 그 의미를 각각 한 문장으로 설명해주세요.
            [KEYWORDS_END]

            중요:
            - 각 섹션은 위의 마커로 정확히 구분해주세요.
            - 마커 외에 섹션 제목(예: "요약:", "구성 방식:")은 추가하지 마세요.
            - 모든 내용은 간결하게 작성해주세요.
            - 불필요한 서술은 제거하고 핵심 정보만 정리해주세요.
            - 별표(*)는 사용하지 마세요.
            """
            
            response = model.generate_content(prompt)
            
            if not response.text:
                self.error_signal.emit("AI가 응답을 생성하지 못했습니다.")
                return
            
            self.progress_signal.emit("분석 결과 처리 중...", 80)
            
            # 응답 텍스트 파싱 (마커 기반)
            text = response.text
            
            # 마커 기반으로 섹션 추출
            def extract_section(start_marker, end_marker):
                pattern = f"{start_marker}(.*?){end_marker}"
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    return match.group(1).strip()
                return ""
            
            summary = extract_section(r"\[SUMMARY_START\]", r"\[SUMMARY_END\]")
            structure = extract_section(r"\[STRUCTURE_START\]", r"\[STRUCTURE_END\]")
            hooking = extract_section(r"\[HOOK_START\]", r"\[HOOK_END\]")
            keywords = extract_section(r"\[KEYWORDS_START\]", r"\[KEYWORDS_END\]")
            
            # 마커 방식으로 추출 실패시 기존 방식 시도
            if not summary or not structure or not hooking or not keywords:
                # 섹션별로 분리 (기존 방식)
                if "요약" in text:
                    parts = re.split(r"구성\s*방식", text, 1)
                    summary = parts[0].split("요약", 1)[1].strip() if len(parts) > 0 else ""
                
                if "구성 방식" in text or "구성방식" in text:
                    pattern = r"(구성\s*방식)(.*?)(초반\s*후킹|주요\s*키워드)"
                    match = re.search(pattern, text, re.DOTALL)
                    if match:
                        structure = match.group(2).strip()
                
                if "초반 후킹" in text or "후킹 방법" in text:
                    pattern = r"(초반\s*후킹|후킹\s*방법)(.*?)(주요\s*키워드)"
                    match = re.search(pattern, text, re.DOTALL)
                    if match:
                        hooking = match.group(2).strip()
                
                if "주요 키워드" in text:
                    parts = text.split("주요 키워드", 1)
                    keywords = parts[1].strip() if len(parts) > 1 else ""
            
            # 섹션 제목과 숫자 제거
            summary = re.sub(r"^[0-9\.]+\s*", "", summary)
            summary = re.sub(r"^요약[:\s]*", "", summary)
            
            structure = re.sub(r"^[0-9\.]+\s*", "", structure)
            structure = re.sub(r"^구성\s*방식[:\s]*", "", structure) 
            
            hooking = re.sub(r"^[0-9\.]+\s*", "", hooking)
            hooking = re.sub(r"^초반\s*후킹[:\s]*", "", hooking)
            hooking = re.sub(r"^후킹\s*방법[:\s]*", "", hooking)
            
            keywords = re.sub(r"^[0-9\.]+\s*", "", keywords)
            keywords = re.sub(r"^주요\s*키워드[:\s]*", "", keywords)
            
            results = {
                'summary': summary,
                'structure': structure,
                'hooking': hooking,
                'keywords': keywords,
                'full_analysis': text,
                'videos': all_transcripts
            }
            
            self.progress_signal.emit("분석 완료!", 100)
            self.analysis_signal.emit(results)
            
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "429" in error_msg:
                self.error_signal.emit(
                    "AI 서비스 일일 사용량이 초과되었습니다 😅\n\n"
                    "다음 방법을 시도해보세요:\n"
                    "1️.내일 다시 시도하기\n"
                    "2.설정에서 다른 API 키 입력하기\n"
                    "🔑 설정 → Google AI Studio API 키 변경"
                )
            elif "invalid" in error_msg or ("key" in error_msg and "error" in error_msg):
                self.error_signal.emit(
                    "API 키가 올바르지 않습니다 ⚠️\n\n"
                    "설정에서 유효한 API 키를 확인해주세요.\n"
                    "🔑 설정 → Google AI Studio API 키 변경"
                )
            else:
                self.error_signal.emit(
                    f"분석 중 문제가 발생했습니다 😕\n\n"
                    f"다시 시도해보시거나, 다른 영상을 선택해주세요.\n"
                    f"⚠️ 오류 상세: {str(e)[:100]}"
                )
    
    
class ScriptGenerationWorker(QThread):
    progress_signal = pyqtSignal(str, int)
    script_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, analysis_results, additional_prompt, api_key, mode="structure"):
        super().__init__()
        self.analysis_results = analysis_results
        self.additional_prompt = additional_prompt
        self.api_key = api_key
        self.mode = mode  # "rewrite" 또는 "structure"
    
    def run(self):
        try:
            import google.generativeai as genai
            
            self.progress_signal.emit("API 연결 중...", 20)
            
            # 여기서부터 수정
            # 현재 활성화된 API 키 가져오기
            parent = QApplication.activeWindow()
            if parent and hasattr(parent, 'gemini_api_manager'):
                gemini_api_manager = parent.gemini_api_manager
                current_key = next((k for k in gemini_api_manager.keys if k.is_current), None)
                
                if current_key and current_key.status == 'active':
                    api_key = current_key.key
                else:
                    # 사용 가능한 다음 키 찾기
                    next_key = gemini_api_manager.get_next_available_key()
                    if next_key:
                        api_key = next_key.key
                    else:
                        # 모든 키가 사용 불가능하면 입력된 키 사용
                        api_key = self.api_key
                    
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')
            else:
                # 기본 API 키 사용
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')
            # 수정 끝
            
            model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')
            
            self.progress_signal.emit("대본 생성 중...", 50)
            
            # 원본 자막 길이 계산
            transcript_text = ""
            for video in self.analysis_results.get('videos', []):
                transcript_text += video.get('transcript', '')
            
            transcript_length = len(transcript_text)
            # 대본 생성을 위한 목표 길이 설정 (원본의 100~120% 사이)
            min_length = int(transcript_length * 1)
            max_length = int(transcript_length * 1.2)
            
            # 대본 생성 프롬프트
            if self.mode == "rewrite":
                prompt = f"""당신은 최고의 유튜브 영상 대본 재작성 전문가입니다. 어문저작권 침해 없이 원본 자막을 새롭게 표현하는 능력이 탁월합니다.

                        다음 분석 결과를 바탕으로 원본 자막의 핵심 내용과 구성을 유지하면서 표현만 완전히 바꾼 대본을 작성해주세요:

                        ===== 분석 결과 =====
                        ▶ 초반 후킹 방법: {self.analysis_results.get('hooking', '')}

                        ▶ 구성 방식: {self.analysis_results.get('structure', '')}

                        ▶ 주요 내용 요약: {self.analysis_results.get('summary', '')}

                        ▶ 핵심 키워드: {self.analysis_results.get('keywords', '')}

                        ▶ 원본 자막 길이: 약 {transcript_length}자

                        ===== 대본 작성 가이드 =====

                        0. 어그로 끄는 제목 생성:
                        - 원본 자막의 내용을 토대로 대본 최상단에 주목을 끌 수 있는 자극적인 제목을 필수적으로 한줄로 포함해주세요
                        - 다음 중 하나의 스타일로 제목을 작성해주세요:
                        * 극단적 반전 유형: (예: 제목 : "이거 왜 샀지...? 반응 보고 후회했습니다")
                        * 자극적&도발 유형: (예: 제목 : "이거 안 사면 당신만 손해! 믿을 수 없는 성능!")
                        * 궁금증 폭발 유형: (예: 제목 : "이 상품, 가격이 미쳤어요... 후기 보면 더 충격적입니다")
                        - 제목 뒤에는 빈 줄을 추가하고 대본 본문을 시작해주세요

                        1. 표절 방지를 위한 리라이팅 원칙:
                        - 원본 자막과 비슷한 길이로 작성하세요 (목표 길이: {min_length}~{max_length}자)
                        - 핵심 주제와 구성은 그대로 유지하세요.
                        - 분석 결과를 파악하여 작성해야합니다. '중요사항 : 초반 후킹, 구성 방식'
                        - 동일한 정보를 전달하고, 원본에서 인사를 하지않는다면 굳이 인사 할 필요 없습니다.
                        - 특히 초반 후킹이 제일 중요하니 최대한 비슷하게 작성해주세요.
                        - 원본의 매력적인 화법과 특징적 표현만 유지
                        - 이모티콘은 절대 사용하지마세요. 이모티콘 사용금지
                        
                        2. 강력한 핵심 후킹 유지:
                        - 원본 자막의 초반 후킹 방식과 유사한 효과를 내되, 다른 단어와 비유로 표현
                        - 핵심 가치 제안은 유지하되 표현 방식만 변경                                              

                        4. 미묘한 개선점 추가:                        
                        - 불필요한 반복이나 군더더기 표현 정리

                        대본 스타일:
                        - 원본과 같은 비격식체/격식체 유지
                        - 감정/액션 지시는 최소한으로만 사용: (진지한 표정으로)
                        - 별표(*) 사용 금지
                        """
            else:  # structure 모드
                prompt = f"""당신은 최고의 유튜브 영상 대본 작성 전문가입니다. 유튜브 알고리즘과 시청자 심리를 완벽히 이해하고 있으며, 시청 유지율을 극대화하는 대본을 작성합니다.

                        다음 분석 결과를 바탕으로 매력적인 유튜브 영상 대본을 작성해주세요:

                        ===== 분석 결과 =====
                        ▶ 초반 후킹 방법: {self.analysis_results.get('hooking', '')}

                        ▶ 구성 방식: {self.analysis_results.get('structure', '')}

                        ▶ 주요 내용 요약: {self.analysis_results.get('summary', '')}

                        ▶ 핵심 키워드: {self.analysis_results.get('keywords', '')}

                        ▶ 원본 자막 길이: 약 {transcript_length}자

                        ===== 대본 작성 가이드 =====

                        0. 어그로 끄는 제목 생성:
                        - 원본 자막의 내용을 토대로 대본 최상단에 주목을 끌 수 있는 자극적인 제목을 필수적으로 한줄로 포함해주세요
                        - 다음 중 하나의 스타일로 제목을 작성해주세요:
                        * 극단적 반전 유형: (예: 제목 : "이거 왜 샀지...? 반응 보고 후회했습니다")
                        * 자극적&도발 유형: (예: 제목 : "이거 안 사면 당신만 손해! 믿을 수 없는 성능!")
                        * 궁금증 폭발 유형: (예: 제목 : "이 상품, 가격이 미쳤어요... 후기 보면 더 충격적입니다")
                        - 제목 뒤에는 빈 줄을 추가하고 대본 본문을 시작해주세요

                        1. 원본 자막의 특성 유지:
                        - 분석한것을 참고하고, 원본 자막과 비슷한 길이로 작성하세요 (목표 길이: {min_length}~{max_length}자)
                        - 원본 자막의 말투와 문체적 특성을 최대한 반영하세요
                        - 분석된 영상의 화자가 사용하는 특징적인 표현이나 단어를 포함하세요
                        - 이모티콘은 절대 사용하지마세요. 이모티콘 사용금지
                        
                        2. 강력한 핵심 후킹:
                        - 시청자가 스크롤을 멈추게 만드는 강력한 첫 문장 (질문/충격적 사실/논쟁적 주장)
                        - 바로 핵심 가치 제안 (이 영상을 통해 얻을 수 있는 명확한 혜택)
                        - 호기심을 자극하는 미스터리나 불완전한 정보 제시

                        3. 시청 유지 전략:
                        - 주기적으로 새로운 정보나 관점 제시 ("그런데 여기서 중요한 점은...")
                        - 중간 지점에 반전/서프라이즈 요소 삽입
                        
                        4. 참여 유도:
                        - 댓글 요청은 구체적으로 ("여러분은 어떤 경험이 있으신가요?")
                        - 좋아요/구독 요청은 자연스럽게 가치와 연결 ("이런 정보가 도움됐다면 좋아요")            

                        5. 내용 구성:
                        - 분석된 구성 방식을 정확히 따르되, 각 섹션을 매끄럽게 연결
                        - 핵심 키워드를 자연스럽게 반복 (최소 3회 언급)
                        - 분석 결과에 언급된 모든 주요 포인트 반드시 포함
                        - 개인적 일화나 사례를 추가해 신뢰성과 공감대 형성

                        # 대본 형식:
                        - [인트로]: 강력한 시작으로 시청자의 관심을 즉시 사로잡으세요
                        - [본론 1/2/3]: 각 섹션별로 명확한 전환과 하위 주제를 구성하세요
                        - [아웃트로]: 핵심 내용 요약 + 다음 영상 암시 + 참여 유도를 포함하세요

                        대본 스타일:
                        - 감정/액션 지시는 최소한으로만 사용하세요(전체 대본에서 3-4회 이하): (진지한 표정으로)
                        - 강조할 부분은 실제 발화를 고려한 자연스러운 표현으로
                        - 전문적이면서도 친근한 대화체 사용
                        - 각 문장은 호흡점을 고려해 간결하게 작성
                        - 별표(*) 사용 금지
                        """
            
            # 추가 프롬프트가 있는 경우
            if self.additional_prompt.strip():
                prompt += f"\n\n추가 요청: {self.additional_prompt}"
            else:
                prompt += "\n\n위 분석 결과를 참고하여 완전히 새로운 대본을 작성해주세요."
            
            response = model.generate_content(prompt)
            
            if not response.text:
                self.error_signal.emit("AI가 대본을 생성하지 못했습니다.")
                return
            
            self.progress_signal.emit("대본 완성!", 100)
            self.script_signal.emit(response.text)
            
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "429" in error_msg:
                self.error_signal.emit(
                    "AI 서비스 일일 사용량이 초과되었습니다 😅\n\n"
                    "다음 방법을 시도해보세요:\n"
                    "1️.내일 다시 시도하기\n"
                    "2️.설정에서 다른 API 키 입력하기\n"
                    "🔑 설정 → Google AI Studio API 키 변경"
                )
            elif "invalid" in error_msg or ("key" in error_msg and "error" in error_msg):
                self.error_signal.emit(
                    "API 키가 올바르지 않습니다 ⚠️\n\n"
                    "설정에서 유효한 API 키를 확인해주세요.\n"
                    "🔑 설정 → Google AI Studio API 키 변경"
                )
            else:
                self.error_signal.emit(
                    f"대본 생성 중 문제가 발생했습니다 😕\n\n"
                    f"다시 시도해보시거나, 다른 영상을 선택해주세요.\n"
                    f"⚠️ 오류 상세: {str(e)[:100]}"
                )

class DownloadWorker(QThread):
    progress_signal = pyqtSignal(str, int)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, url, format_type, download_path, quality="최고화질"):
        super().__init__()
        self.url = url
        self.format_type = format_type
        self.download_path = download_path
        self.quality = quality
        self._is_running = True
    
    def stop(self):
        self._is_running = False
        self.wait()
    
    def get_format(self):
        if self.format_type == 'mp3':
            return 'bestaudio/best'
        
        # 해상도 매핑
        height_map = {
            "⚡ 최고화질": "best",  # 최고화질은 제한 없음
            "🎥 1080p": "1080",
            "📺 720p": "720",
            "📱 480p": "480",
            "💻 360p": "360"
        }
        
        target_height = height_map.get(self.quality, "best")
        
        # h.264 비디오와 호환성 있는 오디오 선택 (단일 형식 문자열)
        if target_height == "best":
            format_str = "bestvideo[vcodec^=avc]+bestaudio/best"
        else:
            format_str = f"bestvideo[height<={target_height}][vcodec^=avc]+bestaudio/best"
        
        print(f"Selected quality: {self.quality}")
        print(f"Using format: {format_str}")
        
        return format_str
    
   
    def run(self):
        if not self._is_running:
            return
                
        try:
            def progress_hook(d):
                if not self._is_running:
                    raise Exception("Download cancelled")
                        
                if d['status'] == 'downloading':
                    total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)
                        
                    if total > 0:
                        percentage = (downloaded / total) * 100
                        if self.format_type == 'mp3':
                            percentage = percentage * 0.5
                        self.progress_signal.emit(f"다운로드 중... {percentage:.1f}%", int(percentage))
                    else:
                        self.progress_signal.emit("다운로드 준비중...", 0)
                            
                elif d['status'] == 'finished':
                    if self.format_type == 'mp4':
                        self.progress_signal.emit("영상 변환 중...", 95)
                    else:
                        self.progress_signal.emit("MP3로 변환 중...", 50)

            # 기본 옵션 설정
            if self.format_type == 'mp3':
                # MP3 다운로드 옵션
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [progress_hook],
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'ffmpeg_location': os.path.expandvars(r'%LOCALAPPDATA%\Programs\ffmpeg\bin\ffmpeg.exe'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }]
                }
            else:
                # MP4 다운로드를 위한 임시 파일 이름 생성
                import uuid
                temp_filename = f"temp_{uuid.uuid4().hex}"
                final_output_template = os.path.join(self.download_path, '%(title)s.%(ext)s')
                temp_output_template = os.path.join(self.download_path, f"{temp_filename}.%(ext)s")

                # 비디오 품질 설정
                height_map = {
                    "⚡ 최고화질": "best",
                    "🎥 1080p": "1080",
                    "📺 720p": "720",
                    "📱 480p": "480",
                    "💻 360p": "360"
                }
                
                target_height = height_map.get(self.quality, "best")
                
                # h.264 포맷 비디오 선택
                if target_height == "best":
                    format_str = "bestvideo[vcodec^=avc]+bestaudio/best"
                else:
                    format_str = f"bestvideo[height<={target_height}][vcodec^=avc]+bestaudio/best"
                    
                ydl_opts = {
                    'format': format_str,
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [progress_hook],
                    'outtmpl': temp_output_template,
                    'ffmpeg_location': os.path.expandvars(r'%LOCALAPPDATA%\Programs\ffmpeg\bin\ffmpeg.exe'),
                    'merge_output_format': 'mp4',
                }

            # 다운로드 시작
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                
                # MP4 형식일 경우 FFmpeg로 직접 변환하여 프리미어 프로와 호환되게 만듦
                if self.format_type == 'mp4' and self._is_running:
                    self.progress_signal.emit("편집툴 호환 형식으로 변환 중...", 98)
                    
                    # 다운로드된 파일 정보 및 경로 가져오기
                    if info and 'entries' in info:
                        # 플레이리스트인 경우
                        downloaded_file = os.path.join(self.download_path, f"{temp_filename}.mp4")
                        title = info['entries'][0].get('title', 'video')
                    else:
                        # 단일 비디오인 경우
                        downloaded_file = os.path.join(self.download_path, f"{temp_filename}.mp4") 
                        title = info.get('title', 'video')
                    
                    # 특수문자 제거하여 안전한 파일명 만들기
                    import re
                    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
                    final_file = os.path.join(self.download_path, f"{safe_title}.mp4")
                    
                    # FFmpeg로 오디오를 AAC로 변환하면서 비디오는 복사
                    ffmpeg_path = os.path.expandvars(r'%LOCALAPPDATA%\Programs\ffmpeg\bin\ffmpeg.exe')
                    import subprocess
                    
                    try:
                        subprocess.run([
                            ffmpeg_path, 
                            '-y',  # 기존 파일 덮어쓰기
                            '-i', downloaded_file,  # 입력 파일
                            '-c:v', 'copy',  # 비디오는 그대로 복사
                            '-c:a', 'aac',  # 오디오는 AAC로 변환
                            '-b:a', '192k',  # 오디오 비트레이트
                            '-movflags', '+faststart',  # 웹 스트리밍 호환성
                            final_file  # 출력 파일
                        ], check=True)
                        
                        # 임시 파일 삭제
                        if os.path.exists(downloaded_file):
                            os.remove(downloaded_file)
                        
                    except subprocess.CalledProcessError as e:
                        raise Exception(f"FFmpeg 처리 중 오류 발생: {str(e)}")
                
                if self._is_running:
                    completion_message = "동영상 다운로드 완료!" if self.format_type == 'mp4' else "음원 다운로드 완료!"
                    self.progress_signal.emit("완료 처리 중...", 100)
                    self.finished_signal.emit(completion_message)
            
        except Exception as e:
            if str(e) != "Download cancelled":
                self.error_signal.emit(str(e))
            
        finally:
            self.finished.emit()
          
    def download_from_url(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "경고", "URL을 입력해주세요.")
            return
            
        # 저장 경로 선택
        save_path = QFileDialog.getExistingDirectory(
            self,
            "저장 위치 선택",
            os.path.join(os.path.expanduser('~'), 'Desktop'),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if save_path:
            try:
                # FFmpeg 체크
                if not os.path.exists(os.path.expandvars(r'%LOCALAPPDATA%\Programs\ffmpeg\bin\ffmpeg.exe')):
                    if not self.install_ffmpeg():
                        return
                
                self.progress_bar.show()
                self.progress_bar.setValue(0)
                self.status_label.setText("다운로드 준비 중...")
                
                quality = self.quality_combo.currentText()
                worker = DownloadWorker(url, 'mp4', save_path, quality)
                worker.progress_signal.connect(lambda s, p: (
                    self.progress_bar.setValue(p),
                    self.status_label.setText(s)
                ))
                worker.finished_signal.connect(lambda: (
                    self.progress_bar.hide(),
                    self.status_label.setText(""),
                    QMessageBox.information(self, "완료", "다운로드가 완료되었습니다."),
                    QDesktopServices.openUrl(QUrl.fromLocalFile(save_path))
                ))
                worker.error_signal.connect(lambda e: (
                    QMessageBox.warning(self, "오류", f"다운로드 중 오류가 발생했습니다: {e}"),
                    self.progress_bar.hide(),
                    self.status_label.setText("")
                ))
                worker.start()
                
            except Exception as e:
                QMessageBox.critical(self, "오류", f"다운로드 초기화 중 오류가 발생했습니다: {str(e)}")
                self.progress_bar.hide()
                self.status_label.setText("")

    
class AIAnalysisWorker(QThread):
    progress_signal = pyqtSignal(str, int)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, api_key, videos):
        super().__init__()
        self.api_key = api_key
        self.videos = videos
        self._is_running = True
        self.youtube_api = None
        
        # YouTube API 초기화
        try:
            parent = QApplication.activeWindow()
            if parent and hasattr(parent, 'api_manager'):
                # API 키 또는 구글 로그인 확인
                current_key = next((k for k in parent.api_manager.keys if k.is_current), None)
                if current_key:
                    self.youtube_api = build('youtube', 'v3', developerKey=current_key.key)
                elif hasattr(parent, 'auth_manager') and parent.auth_manager.is_google_logged_in():
                    credentials = parent.auth_manager.get_google_credentials()
                    if credentials:
                        self.youtube_api = build('youtube', 'v3', credentials=credentials)
        except Exception as e:
            print(f"YouTube API 초기화 오류: {str(e)}")

    def stop(self):
        self._is_running = False
        self.wait()

    def analyze_comments(self, video_id):
        """댓글 분석"""
        if not self.youtube_api:
            print(f"댓글 수집 실패 ({video_id}): YouTube API가 초기화되지 않았습니다.")
            return []
            
        try:
            # 인기 댓글 최대 10개 수집 (댓글 좋아요 순으로 정렬)
            comments_response = self.youtube_api.commentThreads().list(
                part='snippet',
                videoId=video_id,
                order='relevance',
                maxResults=10
            ).execute()

            comments = []
            for item in comments_response.get('items', []):
                try:
                    comment = item['snippet']['topLevelComment']['snippet']
                    # HTML 태그 제거
                    text = re.sub('<[^<]+?>', '', comment['textDisplay'])
                    # 이모지 제거
                    text = text.encode('ascii', 'ignore').decode('ascii')
                    
                    if text.strip():  # 빈 문자열이 아닌 경우만 추가
                        comments.append({
                            'text': text,
                            'likeCount': comment.get('likeCount', 0),
                            'publishedAt': comment['publishedAt']
                        })
                except Exception as e:
                    print(f"댓글 항목 처리 오류: {str(e)}")
                    continue

            print(f"성공적으로 {len(comments)}개의 댓글을 수집했습니다. ({video_id})")
            return comments
        except Exception as e:
            print(f"댓글 수집 오류 ({video_id}): {str(e)}")
            return []

    def analyze_transcript(self, video_id):
        """자막 분석"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = None
            
            # 한국어 -> 영어 -> 자동생성 순으로 시도
            for lang in ['ko', 'en']:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    break
                except:
                    continue
                    
            if not transcript:
                try:
                    transcript = transcript_list.find_generated_transcript(['ko', 'en'])
                except:
                    return "자막 없음"

            return transcript.fetch()
        except Exception as e:
            print(f"자막 수집 오류: {str(e)}")
            return "자막 없음"

    def analyze_content(self, video_data, title, description, comments_data):
        """콘텐츠 종합 분석 - 제목, 설명, 댓글 기반"""
        analysis = {
            'viewer_interests': [],  # 시청자 관심사
            'key_topics': [],      # 주요 주제
            'positive_points': [], # 긍정적 반응
            'negative_points': [], # 부정적 반응
            'viewer_questions_requests': [], # 시청자 질문/요청사항 (이름 변경)
            'key_points': []       # 핵심 포인트
            # 'areas_for_improvement' 항목 제거함
        }

        # 제목과 설명 결합하여 분석
        full_content = f"{title} {description}"
        
        # 자주 등장하는 키워드 추출
        from collections import Counter
        import re
        
        # 한글과 영문 단어 추출 (2글자 이상)
        words = re.findall(r'[가-힣a-zA-Z]{2,}', full_content.lower())
        # 불용어 제거
        stopwords = {'그리고', '그러나', '그래서', '그것은', '이것은', '저것은', 'the', 'and', 'in', 'on', 'at', 'is', 'are', 'am', 'of', 'to', 'for'}
        filtered_words = [word for word in words if word not in stopwords]
        
        # 단어 빈도수 계산
        word_counts = Counter(filtered_words).most_common(10)
        analysis['key_topics'] = [[word, count] for word, count in word_counts]
        
        # 핵심 포인트 직접 생성 (기본값 설정)
        key_points = [
            f"제목 키워드 '{title.split()[0] if title.split() else '주제'}' 중심 콘텐츠",
            "최신 트렌드를 반영한 실용적 접근",
            "시청자 참여를 유도하는 콘텐츠 구성"
        ]
        
        # 1. 제목에서 핵심 키워드 추출해서 추가
        title_keywords = re.findall(r'[가-힣a-zA-Z]{2,}', title.lower())
        if title_keywords:
            title_keywords = [w for w in title_keywords if len(w) > 1 and w not in stopwords]
            if title_keywords:
                key_points[0] = f"제목 키워드 '{title_keywords[0]}' 중심 구성"
        
        # 2. 설명에서 중요 문장 추출 (마침표로 끝나는 짧은 문장 위주)
        desc_sentences = re.findall(r'([^.!?]+[.!?])', description)
        important_sentences = [s.strip() for s in desc_sentences if 10 < len(s) < 100]
        if important_sentences:
            key_points[1] = important_sentences[0]
        
        # 3. 조회수가 높으면 그것도 핵심 포인트로 추가
        if 'view_count' in video_data and int(video_data['view_count']) > 10000:
            key_points[2] = f"높은 조회수({int(video_data['view_count']):,}회)가 증명하는 인기 주제"
        
        analysis['key_points'] = key_points

        # 댓글 분석 (확장된 키워드와 패턴)
        viewer_questions_requests = [
            "콘텐츠의 세부 정보에 대한 추가 설명 요청",
            "비슷한 주제의 후속 영상 제작 요청",
            "실제 적용 방법에 대한 구체적인 예시 요청"
        ]
        
        if comments_data:
            # 질문/요청 관련 키워드 확장
            question_request_words = set(['어떻게', '무엇', '어디서', '언제', '왜', '누가', '얼마나', '어느', '몇', 
                                        '알려주세요', '가르쳐', '부탁', '원해요', '했으면', '바랍니다', '해주세요', 
                                        '필요해요', '원합니다', '알고싶어', '추천', '만들어', '궁금'])
            
            questions_requests = []
            for comment in comments_data:
                text = comment.get('text', '').lower()
                if not text:
                    continue
                
                # 질문/요청 추출
                if '?' in text or any(qr in text for qr in question_request_words):
                    questions_requests.append(text[:100])  # 길이 제한
                
                # 긍정/부정 분류 (유지)
                positive_words = set(['좋아요', '최고', '멋져요', '감사', '훌륭', '대박', '좋은', '좋다', '좋네', '좋고', '짱', '굿', '완벽', '추천', '정확'])
                negative_words = set(['아쉽', '별로', '부족', '싫어', '실망', '아닌', '아니', '안좋', '나쁜', '나쁨', '싫'])
                
                if any(word in text for word in positive_words):
                    analysis['positive_points'].append(text[:100])
                if any(word in text for word in negative_words):
                    analysis['negative_points'].append(text[:100])

            # 질문/요청이 있으면 기본값 대체
            if questions_requests:
                viewer_questions_requests = questions_requests[:3]  # 최대 3개

        analysis['viewer_questions_requests'] = viewer_questions_requests

        # 각 카테고리별로 최대 5개만 유지 (중복 제거)
        for key in ['positive_points', 'negative_points']:
            unique_items = list(set(analysis[key]))[:5]  # 중복 제거하고 최대 5개
            analysis[key] = unique_items

        return analysis
    
    def run(self):
        try:
            import google.generativeai as genai
            import concurrent.futures
            
            # 여기서부터 수정
            # 현재 활성화된 API 키 가져오기
            parent = QApplication.activeWindow()
            if parent and hasattr(parent, 'gemini_api_manager'):
                gemini_api_manager = parent.gemini_api_manager
                current_key = next((k for k in gemini_api_manager.keys if k.is_current), None)
                
                if current_key and current_key.status == 'active':
                    api_key = current_key.key
                else:
                    # 사용 가능한 다음 키 찾기
                    next_key = gemini_api_manager.get_next_available_key()
                    if next_key:
                        api_key = next_key.key
                    else:
                        # 모든 키가 사용 불가능하면 입력된 키 사용
                        api_key = self.api_key
                    
                genai.configure(api_key=api_key)
            else:
                # 기본 API 키 사용
                genai.configure(api_key=self.api_key)
            # 수정 끝
            
            # API 키 유효성 검사를 위한 간단한 테스트
            try:
                model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')
                test_response = model.generate_content("test")
                if not test_response.text:
                    raise Exception("API 응답이 올바르지 않습니다")
            except Exception as e:
                error_msg = str(e).lower()
                if "quota" in error_msg:
                    self.error_signal.emit("Google AI Studio API 할당량이 초과되었습니다.\n설정에서 다른 API 키를 입력하시거나, 내일 다시 시도해주세요.")
                elif "invalid" in error_msg:
                    self.error_signal.emit("유효하지 않은 API 키입니다.\n설정에서 올바른 API 키를 입력해주세요.")
                else:
                    self.error_signal.emit(f"Google AI Studio API 연결 중 오류가 발생했습니다: {str(e)}")
                return

            all_videos_data = []
            total_videos = len(self.videos)

            # 1. 데이터 수집 (30%) - 병렬 처리로 속도 개선
            self.progress_signal.emit("데이터 수집 준비 중...", 5)
            
            # 한 번에 최대 5개 영상 동시 처리 (부하 조절)
            batch_size = 10
            processed = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = []
                
                for video in self.videos:
                    if not self._is_running:
                        return
                    
                    video_id = video['video_url'].split('v=')[1]
                    futures.append(
                        executor.submit(
                            self.collect_video_data, 
                            video_id, 
                            video
                        )
                    )
                
                # 완료된 순서대로 결과 수집
                for future in concurrent.futures.as_completed(futures):
                    if not self._is_running:
                        return
                    
                    processed += 1
                    progress = int((processed / total_videos) * 30)
                    self.progress_signal.emit(f"데이터 수집 중... ({processed}/{total_videos})", progress)
                    
                    # 결과 처리
                    result = future.result()
                    if result:
                        all_videos_data.append(result)

            # 2. AI 분석 (70%)
            self.progress_signal.emit("AI 분석 중...", 30)

            # thumbnail_data와 같은 직렬화 불가능한 데이터 제거
            clean_data = []
            for item in all_videos_data:
                video_copy = dict(item['video'])
                if 'thumbnail_data' in video_copy:
                    del video_copy['thumbnail_data']
                
                clean_item = {
                    'video': video_copy,
                    'analysis': item['analysis']
                }
                clean_data.append(clean_item)

            # AI 프롬프트 생성
            prompt = f"""당신은 유튜브 콘텐츠 전략 전문가입니다.
            다음 데이터를 기반으로 간결하고 구체적인 콘텐츠 아이디어를 제안해주세요:

            === 분석된 데이터 ===
            {json.dumps(clean_data, ensure_ascii=False, indent=2)}

            아래 두 섹션으로만 나누어 분석해주세요. 절대 별표(*) 기호를 사용하지 마세요:

            [시청자 트렌드 분석]
            - 지금 시청자들이 가장 관심 있어하는 주제 (핵심만 간략히)
            - 시청자의 주요 질문 또는 요청사항 (반드시 3개 이상 작성)
            - 시청자가 가장 긍정적으로 반응하는 콘텐츠 특징 (간결하게)

            [추천 콘텐츠 아이디어]
            (총 5개의 아이디어를 제시해주세요. 각 아이디어는 아래 형식으로 모든 항목을 반드시 포함해야 합니다:)

            아이디어 1
            - 제목 예시: (짧고 클릭을 유도하는 매력적인 제목)
            - 핵심 포인트: (3개의 구체적인 핵심 내용, 반드시 포함)
                예시:
                - 시즌별 가장 효과적인 스킨케어 루틴 단계별 설명
                - 다이어트 성공자들의 공통 식습관 3가지 분석
                - 초보자를 위한 카메라 설정 가이드
            - 차별화 요소: (경쟁 콘텐츠와 다른 특별한 점)
            - 목표 시청자: (이 콘텐츠가 특별히 도움이 될 시청자 그룹)

            아이디어 2
            (같은 형식으로 반복)

            ...

            반드시 지켜야 할 규칙:
            1. 시청자 트렌드 분석의 "시청자의 주요 질문 또는 요청사항"은 3개 이상 작성해주세요.
            2. 각 아이디어의 "핵심 포인트"는 정확히 3개씩 작성해주세요.
            3. 모든 항목은 누락 없이 작성해야 합니다.
            4. "핵심 포인트"는 구체적이고 실행 가능한 내용으로 작성해야 합니다. 
             예시:
            - "시즌별 가장 효과적인 스킨케어 루틴 단계별 설명"
            - "다이어트 성공자들의 공통 식습관 3가지 분석"
            - "초보자를 위한 카메라 설정 가이드"
            5. "시청자의 주요 질문 또는 요청사항"은 질문형 또는 요청형 문장으로 작성해주세요. 
             예시:
            - "특정 제품의 실제 사용 후기를 더 자세히 알려주세요"
            - "초보자도 따라할 수 있는 단계별 가이드를 제공해주세요"
            - "다음 영상에서는 더 저렴한 대체품을 소개해주실 수 있나요?"
            """

            response = model.generate_content(prompt)
            if not response.text:
                self.error_signal.emit("AI가 응답을 생성하지 못했습니다.")
                return
                
            self.progress_signal.emit("분석 완료!", 100)
            
            # 최종 결과 반환
            result = {
                'raw_data': all_videos_data,
                'ideas': response.text
            }
            
            self.finished_signal.emit(result)

        except Exception as e:
            print(f"AI 분석 오류: {str(e)}")  # 디버깅용 로그
            
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "exhausted" in error_msg.lower():
                self.error_signal.emit(
                    "AI 서비스 일일 사용량이 초과되었습니다 😅\n\n"
                    "다음 방법을 시도해보세요:\n"
                    "1️.내일 다시 시도하기\n"
                    "2️.설정에서 다른 API 키 입력하기\n"
                    "🔑 설정 → Google AI Studio API 키 변경"
                )
            elif "invalid" in error_msg.lower() and ("key" in error_msg.lower() or "credential" in error_msg.lower()):
                self.error_signal.emit(
                    "API 키가 올바르지 않습니다 ⚠️\n\n"
                    "설정에서 유효한 API 키를 확인해주세요.\n"
                    "🔑 설정 → Google AI Studio API 키 변경"
                )
            else:
                self.error_signal.emit(
                    f"분석 중 오류가 발생했습니다 😕\n\n"
                    f"다시 시도해보시거나, 다른 영상을 선택해주세요.\n"
                    f"⚠️ 오류 상세: {error_msg[:100]}"
                )
            
    def collect_video_data(self, video_id, video):
        """한 영상의 댓글 데이터만 수집 - 자막은 건너뜀"""
        try:
            # 댓글만 수집 (자막 수집 제외)
            comments = self.analyze_comments(video_id)
            
            # 제목과 설명 추출
            title = video.get('title', '')
            description = video.get('description', '')
            
            # 분석 데이터 생성 (자막 대신 제목과 설명 기반)
            video_analysis = self.analyze_content(video, title, description, comments)
            
            return {
                'video': video,
                'analysis': video_analysis
            }
        except Exception as e:
            print(f"영상 데이터 수집 오류 ({video_id}): {str(e)}")
            return None        
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 1순위: 즉시 스플래시 스크린 생성 및 표시
    splash_pix = QPixmap(get_resource_path("images/tubelensint.png"))
    scaled_pix = splash_pix.scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    splash = QSplashScreen(scaled_pix, Qt.WindowType.SplashScreen)
    splash.show()
    app.processEvents()  # 즉시 화면 업데이트 강제
    
    # 앱 아이콘 설정 (낮은 우선순위)
    try:
        app_icon = QIcon(get_resource_path("images/tubelens.ico"))
        app.setWindowIcon(app_icon)
    except Exception as e:
        print(f"아이콘 로딩 오류: {str(e)}")
    
    # 메인 윈도우 생성
    window = YouTubeAnalyzer()
    
    # 인증 관련 다이얼로그는 항상 최상위에 표시
    if not window.auth_manager.is_authenticated():
        def show_auth_dialog():
            key, ok = QInputDialog.getText(
                None,  # 부모를 None으로 설정하여 독립적인 창으로 만듦
                '인증키 입력',
                '프로그램을 사용하려면 인증키가 필요합니다.\n인증키를 입력해주세요:',
                QLineEdit.EchoMode.Normal
            )
            if not ok or not key:
                sys.exit()
            window.validate_and_set_auth_key(key)
        
        QTimer.singleShot(0, show_auth_dialog)  # 즉시 실행되도록 0ms 지연
        
        def on_auth_window_closed():
            if window.auth_manager.is_authenticated():
                window.show()
            splash.finish(window)
            
        window.destroyed.connect(on_auth_window_closed)
    else:
        window.show()
        splash.finish(window)
    
    sys.exit(app.exec())