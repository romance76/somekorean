import re
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def normalize_for_comparison(s: str) -> str:
    s = re.sub(r'[^\w\s]', '', s.lower())
    s = re.sub(r'\s+', ' ', s).strip()
    # Remove common suffixes
    for suffix in [' inc', ' llc', ' corp', ' restaurant', ' korean']:
        s = s.removesuffix(suffix)
    return s

def deduplicate(businesses: list) -> list:
    seen = []
    unique = []
    for biz in businesses:
        name = normalize_for_comparison(biz.get('name_en', ''))
        addr = normalize_for_comparison(biz.get('address', ''))
        is_dup = False
        for s_name, s_addr in seen:
            if similarity(name, s_name) > 0.85 and similarity(addr, s_addr) > 0.7:
                is_dup = True
                break
        if not is_dup and name:
            seen.append((name, addr))
            unique.append(biz)
    return unique

def deduplicate_against_existing(new_biz: list, existing: list) -> list:
    """Filter out businesses already in the existing list"""
    existing_keys = set()
    for b in existing:
        key = normalize_for_comparison(b.get('name_en', '')) + '|' + normalize_for_comparison(b.get('address', ''))
        existing_keys.add(key)
    result = []
    for b in new_biz:
        key = normalize_for_comparison(b.get('name_en', '')) + '|' + normalize_for_comparison(b.get('address', ''))
        if key not in existing_keys:
            result.append(b)
    return result
