# ============================================
# BASIC TESTS - Cricket Analytics
# ============================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config_loads():
    """Test config file loads correctly"""
    import config
    assert hasattr(config, 'DATA_FOLDER'), "DATA_FOLDER missing from config"
    assert hasattr(config, 'MIN_MATCHES'), "MIN_MATCHES missing from config"
    assert hasattr(config, 'RETIRED_PLAYERS'), "RETIRED_PLAYERS missing"
    assert hasattr(config, 'ALL_SEASONS'), "ALL_SEASONS missing from config"
    assert config.MIN_MATCHES > 0, "MIN_MATCHES must be positive"
    assert len(config.ALL_SEASONS) > 0, "ALL_SEASONS cannot be empty"
    assert len(config.RETIRED_PLAYERS) > 0, "RETIRED_PLAYERS cannot be empty"
    print("✅ Config test passed!")

def test_seasons_are_valid():
    """Test all seasons are valid years"""
    import config
    for season in config.ALL_SEASONS:
        assert season.isdigit(), f"Season {season} is not a valid year"
        assert 2008 <= int(season) <= 2025, f"Season {season} out of range"
    print("✅ Seasons test passed!")

def test_retired_players_are_strings():
    """Test retired players list contains strings"""
    import config
    for player in config.RETIRED_PLAYERS:
        assert isinstance(player, str), f"{player} is not a string"
        assert len(player) > 0, "Empty player name found"
    print("✅ Retired players test passed!")

def test_data_folder_exists():
    """Test data folder path is set"""
    import config
    assert config.DATA_FOLDER == "data/raw", "DATA_FOLDER path incorrect"
    print("✅ Data folder test passed!")

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 RUNNING CRICKET ANALYTICS TESTS")
    print("=" * 50)
    test_config_loads()
    test_seasons_are_valid()
    test_retired_players_are_strings()
    test_data_folder_exists()
    print("\n✅ ALL TESTS PASSED!")