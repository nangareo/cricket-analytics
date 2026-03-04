# ============================================
# IPL TEAM COLORS AND 2025 ROSTERS
# Updated for IPL 2025 - RCB Champions!
# ============================================

IPL_TEAMS = {
    "Mumbai Indians": {
        "color": "#004BA0",
        "secondary": "#D1AB3E",
        "short": "MI",
        "emoji": "🔵"
    },
    "Chennai Super Kings": {
        "color": "#F9CD05",
        "secondary": "#0081E9",
        "short": "CSK",
        "emoji": "🟡"
    },
    "Royal Challengers Bengaluru": {
        "color": "#EC1C24",
        "secondary": "#000000",
        "short": "RCB",
        "emoji": "🔴"
    },
    "Kolkata Knight Riders": {
        "color": "#3A225D",
        "secondary": "#B3A123",
        "short": "KKR",
        "emoji": "🟣"
    },
    "Delhi Capitals": {
        "color": "#0078BC",
        "secondary": "#EF1C25",
        "short": "DC",
        "emoji": "🔵"
    },
    "Sunrisers Hyderabad": {
        "color": "#F7A721",
        "secondary": "#E8452C",
        "short": "SRH",
        "emoji": "🟠"
    },
    "Rajasthan Royals": {
        "color": "#E73560",
        "secondary": "#2D3E8E",
        "short": "RR",
        "emoji": "🩷"
    },
    "Punjab Kings": {
        "color": "#ED1B24",
        "secondary": "#A7A9AC",
        "short": "PBKS",
        "emoji": "🔴"
    },
    "Lucknow Super Giants": {
        "color": "#A72056",
        "secondary": "#FFCC00",
        "short": "LSG",
        "emoji": "🩵"
    },
    "Gujarat Titans": {
        "color": "#1C4F9C",
        "secondary": "#00B4CC",
        "short": "GT",
        "emoji": "🔵"
    },
}

# ============================================
# IPL 2025 PLAYER → TEAM MAPPING
# Fully updated post mega-auction 2025
# ============================================
PLAYER_TEAMS = {

    # ---- CHENNAI SUPER KINGS ----
    "MS Dhoni":           "Chennai Super Kings",   # Still plays! Captain 2025
    "RA Jadeja":          "Chennai Super Kings",   # Retained
    "RD Gaikwad":         "Chennai Super Kings",   # Retained
    "Shivam Dube":        "Chennai Super Kings",   # Retained
    "Devon Conway":       "Chennai Super Kings",
    "R Ashwin":           "Chennai Super Kings",
    "Rachin Ravindra":    "Chennai Super Kings",
    "Matheesha Pathirana":"Chennai Super Kings",
    "Sam Curran":         "Chennai Super Kings",
    "Khaleel Ahmed":      "Chennai Super Kings",

    # ---- MUMBAI INDIANS ----
    "RG Sharma":          "Mumbai Indians",        # Retained, captain
    "JJ Bumrah":          "Mumbai Indians",        # Retained
    "HH Pandya":          "Mumbai Indians",        # Retained
    "Suryakumar Yadav":   "Mumbai Indians",        # MVP 2025
    "Ishan Kishan":       "Mumbai Indians",
    "Tilak Varma":        "Mumbai Indians",        # Retained
    "Naman Dhir":         "Mumbai Indians",
    "Trent Boult":        "Mumbai Indians",
    "RM Patidar":         "Mumbai Indians",

    # ---- ROYAL CHALLENGERS BENGALURU ----
    # 🏆 IPL 2025 Champions!
    "V Kohli":            "Royal Challengers Bengaluru",  # Retained
    "Rajat Patidar":      "Royal Challengers Bengaluru",  # Captain 2025
    "C Green":            "Royal Challengers Bengaluru",  # Retained
    "Yash Dayal":         "Royal Challengers Bengaluru",  # Retained
    "Liam Livingstone":   "Royal Challengers Bengaluru",
    "Krunal Pandya":      "Royal Challengers Bengaluru",
    "Josh Hazlewood":     "Royal Challengers Bengaluru",
    "Bhuvneshwar Kumar":  "Royal Challengers Bengaluru",
    "Devdutt Padikkal":   "Royal Challengers Bengaluru",
    "Tim David":          "Royal Challengers Bengaluru",
    "Lungi Ngidi":        "Royal Challengers Bengaluru",

    # ---- KOLKATA KNIGHT RIDERS ----
    "SP Narine":          "Kolkata Knight Riders",  # Retained
    "AD Russell":         "Kolkata Knight Riders",  # Retained
    "AM Rahane":          "Kolkata Knight Riders",  # Captain
    "V Iyer":             "Kolkata Knight Riders",  # Retained
    "Q de Kock":          "Kolkata Knight Riders",
    "A Nortje":           "Kolkata Knight Riders",
    "V Chakravarthy":     "Kolkata Knight Riders",  # Retained
    "Moeen Ali":          "Kolkata Knight Riders",
    "R Powell":           "Kolkata Knight Riders",

    # ---- DELHI CAPITALS ----
    "Axar Patel":         "Delhi Capitals",         # Retained, Captain
    "Kuldeep Yadav":      "Delhi Capitals",         # Retained
    "KL Rahul":           "Delhi Capitals",         # Moved from LSG
    "Tristan Stubbs":     "Delhi Capitals",         # Retained
    "Jake Fraser-McGurk": "Delhi Capitals",         # Retained
    "Mitchell Starc":     "Delhi Capitals",
    "Faf du Plessis":     "Delhi Capitals",
    "T Natarajan":        "Delhi Capitals",
    "Mukesh Kumar":       "Delhi Capitals",
    "Karun Nair":         "Delhi Capitals",

    # ---- SUNRISERS HYDERABAD ----
    "HE van der Dussen":  "Sunrisers Hyderabad",
    "PA Patel":           "Sunrisers Hyderabad",
    "Ishan Kishan":       "Sunrisers Hyderabad",
    "Travis Head":        "Sunrisers Hyderabad",    # Retained
    "Heinrich Klaasen":   "Sunrisers Hyderabad",   # Retained
    "Pat Cummins":        "Sunrisers Hyderabad",   # Retained, Captain
    "Mohammed Shami":     "Sunrisers Hyderabad",
    "Abhishek Sharma":    "Sunrisers Hyderabad",   # Retained

    # ---- RAJASTHAN ROYALS ----
    "YS Chahal":          "Rajasthan Royals",
    "Sanju Samson":       "Rajasthan Royals",      # Retained, Captain
    "Shimron Hetmyer":    "Rajasthan Royals",      # Retained
    "Dhruv Jurel":        "Rajasthan Royals",      # Retained
    "Riyan Parag":        "Rajasthan Royals",      # Retained
    "Wanindu Hasaranga":  "Rajasthan Royals",
    "Jofra Archer":       "Rajasthan Royals",

    # ---- PUNJAB KINGS ----
    "Shreyas Iyer":       "Punjab Kings",          # Big buy ₹26.75cr
    "Shashank Singh":     "Punjab Kings",          # Retained
    "Arshdeep Singh":     "Punjab Kings",          # Retained
    "Marcus Stoinis":     "Punjab Kings",
    "Glenn Maxwell":      "Punjab Kings",
    "Yuzvendra Chahal":   "Punjab Kings",

    # ---- LUCKNOW SUPER GIANTS ----
    "RR Pant":            "Lucknow Super Giants",  # ₹27cr record buy
    "Nicholas Pooran":    "Lucknow Super Giants",  # Retained
    "Ravi Bishnoi":       "Lucknow Super Giants",  # Retained
    "Mohsin Khan":        "Lucknow Super Giants",  # Retained
    "David Miller":       "Lucknow Super Giants",
    "Mayank Yadav":       "Lucknow Super Giants",  # Retained

    # ---- GUJARAT TITANS ----
    "Shubman Gill":       "Gujarat Titans",        # Retained, Captain
    "Sai Sudharsan":      "Gujarat Titans",        # Retained, Top scorer 2025
    "Rashid Khan":        "Gujarat Titans",        # Retained
    "Mohammed Siraj":     "Gujarat Titans",
    "Jos Buttler":        "Gujarat Titans",
    "Prasidh Krishna":    "Gujarat Titans",        # Top wicket taker 2025
    "Washington Sundar":  "Gujarat Titans",
}

# ============================================
# RETIRED / NO LONGER IN IPL 2025
# ============================================
IPL_RETIRED_2025 = [
    "SR Tendulkar", "SC Ganguly", "RT Ponting",
    "KC Sangakkara", "CH Gayle", "SR Watson",
    "G Gambhir", "V Sehwag", "BB McCullum",
    "MEK Hussey", "DR Smith", "AC Gilchrist",
    "SL Malinga", "Z Khan", "RP Singh",
    "DW Steyn", "SW Tait", "B Lee",
    "DE Bollinger", "DP Nannes",
    "Harbhajan Singh", "A Mishra",
    "IK Pathan", "YK Pathan", "AS Raina",
    "DJ Bravo", "DA Warner",
]

def get_team_color(player_name):
    """Get team color for a player"""
    team = PLAYER_TEAMS.get(player_name)
    if team and team in IPL_TEAMS:
        return IPL_TEAMS[team]["color"]
    return "#2ecc71"

def get_team_info(player_name):
    """Get full team info for a player"""
    team = PLAYER_TEAMS.get(player_name)
    if team and team in IPL_TEAMS:
        info = IPL_TEAMS[team].copy()
        info["team_name"] = team
        return info
    return {
        "color":     "#2ecc71",
        "secondary": "#ffffff",
        "short":     "IPL",
        "emoji":     "🏏",
        "team_name": "Unknown"
    }