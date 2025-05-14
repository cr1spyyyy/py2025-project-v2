import os
import json

from src.fileops.session_manager import SessionManager

def test_save_and_load():
    session = {
        "game_id": "test123",
        "players": [{"id": 1, "name": "Test", "stack": 500}],
        "deck": ["AS", "KH", "QC"],
        "hands": {"1": ["AS", "KH", "QC", "JD", "10S"]},
        "bets": [],
        "current_player": 1,
        "pot": 0,
        "history": []
    }

    sm = SessionManager(data_dir='test_data')
    sm.save_session(session)
    loaded = sm.load_session("test123")

    assert session == loaded
    os.remove('test_data/session_test123.json')
    os.rmdir('test_data')
