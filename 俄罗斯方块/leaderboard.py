import json
import os
from datetime import datetime
from constants import LEADERBOARD_FILE


class Leaderboard:
    """排行榜管理"""
    def __init__(self):
        self.scores = self.load()

    def load(self):
        """加载排行榜"""
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save(self):
        """保存排行榜"""
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=2)

    def add_score(self, name, score, level, lines):
        """添加分数到排行榜"""
        entry = {
            "name": name if name else "Anonymous",
            "score": score,
            "level": level,
            "lines": lines,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.scores.append(entry)
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:20]
        self.save()

    def get_top(self, count=10):
        """获取前N名"""
        return self.scores[:count]
