# ============================================
# FILTER SELECTOR
# Interactive terminal menu to pick seasons
# Also saves selection for dashboard later
# ============================================

import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

FILTER_CACHE = "data/selected_filter.json"

def save_filter(filter_type, value):
    """Save selected filter so dashboard can read it too"""
    os.makedirs("data", exist_ok=True)
    with open(FILTER_CACHE, 'w') as f:
        json.dump({"filter_type": filter_type, "value": value}, f)
    print(f"\n💾 Filter saved for dashboard use too!")

def load_saved_filter():
    """Load previously saved filter"""
    if os.path.exists(FILTER_CACHE):
        with open(FILTER_CACHE, 'r') as f:
            return json.load(f)
    return None

def show_menu():
    """Show the main filter menu"""
    print("\n" + "=" * 55)
    print("🏏  CRICKET ANALYTICS — FILTER SELECTOR")
    print("=" * 55)

    # Show last used filter
    saved = load_saved_filter()
    if saved:
        print(f"📌 Last used: {saved['filter_type']} → {saved['value']}")

    print("\nHow do you want to filter player data?\n")
    print("  1️⃣   All Time (2008 - 2025)")
    print("  2️⃣   Last 3 Seasons (2023, 2024, 2025)")
    print("  3️⃣   Last 5 Seasons (2021 - 2025)")
    print("  4️⃣   Pick a single IPL Season")
    print("  5️⃣   Pick a custom year range")
    print("  6️⃣   Pick multiple specific seasons")
    print("\n" + "-" * 55)

    choice = input("Enter your choice (1-6): ").strip()
    return choice

def get_single_season():
    """Let user pick one IPL season"""
    print("\n📅 Available IPL Seasons:")
    for i, season in enumerate(config.ALL_SEASONS, 1):
        print(f"  {i:2}. IPL {season}")
    print("-" * 30)
    choice = input("Enter season number: ").strip()
    try:
        idx = int(choice) - 1
        selected = config.ALL_SEASONS[idx]
        return [selected]
    except:
        print("❌ Invalid choice, defaulting to All Time")
        return None

def get_year_range():
    """Let user pick a custom year range"""
    print(f"\n📅 Available years: {config.ALL_SEASONS[0]} - {config.ALL_SEASONS[-1]}")
    print("-" * 30)

    start = input("Enter start year (e.g. 2020): ").strip()
    end   = input("Enter end year   (e.g. 2024): ").strip()

    try:
        start_int = int(start)
        end_int   = int(end)
        if start_int > end_int:
            print("❌ Start year must be before end year!")
            return None
        seasons = [s for s in config.ALL_SEASONS
                   if int(s) >= start_int and int(s) <= end_int]
        if not seasons:
            print("❌ No seasons found in that range!")
            return None
        return seasons
    except:
        print("❌ Invalid years entered, defaulting to All Time")
        return None

def get_multiple_seasons():
    """Let user pick multiple specific seasons"""
    print("\n📅 Available IPL Seasons:")
    for i, season in enumerate(config.ALL_SEASONS, 1):
        print(f"  {i:2}. IPL {season}")
    print("-" * 30)
    print("Enter season numbers separated by commas")
    print("Example: 1,3,5 selects 2008, 2010, 2012")
    print("-" * 30)

    choices = input("Your choices: ").strip()
    try:
        indices = [int(x.strip()) - 1 for x in choices.split(',')]
        selected = [config.ALL_SEASONS[i] for i in indices]
        return selected
    except:
        print("❌ Invalid input, defaulting to All Time")
        return None

def run_filter_selector():
    """Main function - show menu and apply filter"""
    choice = show_menu()

    selected_seasons = None

    if choice == '1':
        # All time
        selected_seasons = None
        label = "All Time (2008-2025)"

    elif choice == '2':
        # Last 3 seasons
        selected_seasons = ["2023", "2024", "2025"]
        label = "Last 3 Seasons (2023-2025)"

    elif choice == '3':
        # Last 5 seasons
        selected_seasons = ["2021", "2022", "2023", "2024", "2025"]
        label = "Last 5 Seasons (2021-2025)"

    elif choice == '4':
        # Single season
        selected_seasons = get_single_season()
        label = f"IPL {selected_seasons[0]}" if selected_seasons else "All Time"

    elif choice == '5':
        # Custom year range
        selected_seasons = get_year_range()
        label = f"Custom Range: {selected_seasons[0]}-{selected_seasons[-1]}" \
                if selected_seasons else "All Time"

    elif choice == '6':
        # Multiple specific seasons
        selected_seasons = get_multiple_seasons()
        label = f"Custom Seasons: {', '.join(selected_seasons)}" \
                if selected_seasons else "All Time"

    else:
        print("❌ Invalid choice, defaulting to All Time")
        selected_seasons = None
        label = "All Time"

    # ---- Confirm selection ----
    print("\n" + "=" * 55)
    print(f"✅ Filter Applied: {label}")
    if selected_seasons:
        print(f"   Seasons included: {', '.join(selected_seasons)}")
    print(f"   Retired players excluded: {len(config.RETIRED_PLAYERS)}")
    print(f"   Minimum matches required: {config.MIN_MATCHES}")
    print("=" * 55)

    # Save for dashboard
    save_filter(
        filter_type = "seasons",
        value       = selected_seasons if selected_seasons else "all"
    )

    return selected_seasons

if __name__ == "__main__":
    run_filter_selector()