"""
Common compound words and phrasal verbs organized by root word.
These are idiomatic combinations that may not be detected by morphological analysis.
For now, it is manually listed for pure testing purpose.

Upcoming updates: A database might be used to store and query the compound words.
"""

COMPOUND_PATTERNS = {
    'run': [
        'runway', 'runaway', 'runoff', 'rundown', 'run-up', 'runner-up',
        'run-through', 'running mate', 'home run', 'dry run', 'trial run'
    ],
    'win': [
        'breadwinner', 'win-win', 'winning streak'
    ],
    'break': [
        'breakthrough', 'breakdown', 'breakup', 'breakout', 'breakfast',
        'break-in', 'breakwater', 'spring break', 'commercial break'
    ],
    'take': [
        'takeover', 'takeoff', 'takeout', 'take-home', 'intake', 'uptake',
        'double-take'
    ],
    'make': [
        'makeup', 'makeover', 'makeshift', 'remake', 'peacemaker',
        'troublemaker', 'matchmaker', 'filmmaker', 'lawmaker'
    ],
    'work': [
        'workout', 'workshop', 'workload', 'workstation', 'homework',
        'framework', 'teamwork', 'artwork', 'handiwork', 'metalwork'
    ],
    'over': [
        'overall', 'overcome', 'overflow', 'overlook', 'overseas',
        'overnight', 'overturn', 'overdue', 'overgrown'
    ],
    'under': [
        'understand', 'undergo', 'undercover', 'underground', 'underdog',
        'underway', 'underwear', 'underline', 'underneath'
    ],
    'out': [
        'outcome', 'output', 'outbreak', 'outlet', 'outline', 'outlook',
        'outside', 'outstanding', 'outgoing', 'outright'
    ],
    'up': [
        'update', 'upgrade', 'upload', 'upbeat', 'upcoming', 'upfront',
        'uphill', 'upright', 'upset', 'uptown', 'upward'
    ],
    'down': [
        'download', 'downfall', 'downgrade', 'downhill', 'downplay',
        'downpour', 'downright', 'downside', 'downstream', 'downtown'
    ],
    'back': [
        'backup', 'background', 'backbone', 'backfire', 'backpack',
        'backstage', 'backward', 'comeback', 'feedback', 'flashback'
    ],
    'hand': [
        'handbook', 'handmade', 'handout', 'handwriting', 'handy',
        'firsthand', 'secondhand', 'handshake', 'handiwork'
    ],
    'head': [
        'headline', 'headache', 'headquarters', 'headway', 'heading',
        'overhead', 'forehead', 'masthead', 'arrowhead'
    ],
    'life': [
        'lifetime', 'lifestyle', 'lifeguard', 'lifelike', 'lifeline',
        'wildlife', 'nightlife', 'afterlife', 'half-life'
    ],
    'time': [
        'timeline', 'timeout', 'timekeeper', 'timeless', 'overtime',
        'pastime', 'longtime', 'full-time', 'part-time', 'bedtime'
    ],
    'way': [
        'pathway', 'railway', 'highway', 'subway', 'driveway',
        'doorway', 'halfway', 'waterway', 'walkway', 'airway'
    ],
    'water': [
        'waterfall', 'waterproof', 'watermelon', 'waterfront', 'watercolor',
        'underwater', 'seawater', 'freshwater', 'wastewater'
    ],
    'fire': [
        'fireplace', 'fireworks', 'firewall', 'firefighter', 'fireproof',
        'wildfire', 'campfire', 'bonfire', 'gunfire'
    ],
    'set': [
        'upset', 'offset', 'onset', 'outset', 'sunset', 'mindset',
        'setup', 'setback', 'dataset'
    ],
    'put': [
        'input', 'output', 'putdown', 'throughput'
    ],
    'turn': [
        'turnover', 'turnout', 'turnaround', 'downturn', 'upturn', 'overturn'
    ],
    'cut': [
        'cutoff', 'cutback', 'shortcut', 'haircut', 'clear-cut'
    ],
    'look': [
        'outlook', 'overlook', 'lookout', 'onlooker', 'good-looking'
    ],
    'stand': [
        'understand', 'outstanding', 'standby', 'standpoint', 'grandstand'
    ],
    'hold': [
        'household', 'shareholder', 'foothold', 'stronghold', 'threshold',
        'uphold', 'withhold', 'behold'
    ],
    'land': [
        'landmark', 'landscape', 'mainland', 'homeland', 'wonderland',
        'borderland', 'grassland', 'farmland', 'wasteland'
    ]
}

def get_compound_words(root_word: str) -> list:
    """
    Get compound words for a given root word.
    Returns list of compound words if found, empty list otherwise.
    """
    root_lower = root_word.lower().strip()
    return COMPOUND_PATTERNS.get(root_lower, [])

def get_all_compounds_containing(root_word: str) -> list:
    """
    Get all compound words that contain the root word as a substring.
    This is broader than exact root word matching.
    """
    root_lower = root_word.lower().strip()
    results = []
    
    for compounds in COMPOUND_PATTERNS.values():
        for compound in compounds:
            compound_clean = compound.replace('-', '').replace(' ', '').lower()
            if root_lower in compound_clean and compound not in results:
                results.append(compound)
    
    return results
