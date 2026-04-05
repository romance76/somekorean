import re

def normalize_phone(phone: str) -> str:
    if not phone: return ''
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return phone.strip()

def normalize_address(addr: str) -> str:
    if not addr: return ''
    addr = re.sub(r'\s+', ' ', addr).strip()
    return addr

def normalize_hours(hours_text: str) -> dict:
    if not hours_text: return {}
    day_map = {
        'mon': 'mon', 'monday': 'mon', '\uc6d4': 'mon',
        'tue': 'tue', 'tuesday': 'tue', '\ud654': 'tue',
        'wed': 'wed', 'wednesday': 'wed', '\uc218': 'wed',
        'thu': 'thu', 'thursday': 'thu', '\ubaa9': 'thu',
        'fri': 'fri', 'friday': 'fri', '\uae08': 'fri',
        'sat': 'sat', 'saturday': 'sat', '\ud1a0': 'sat',
        'sun': 'sun', 'sunday': 'sun', '\uc77c': 'sun',
    }
    return {}

def categorize_korean(name: str, category_hint: str) -> str:
    name_lower = (name + ' ' + category_hint).lower()
    if any(x in name_lower for x in ['restaurant', 'bbq', '\uc2dd\ub2f9', 'grill', 'kitchen', 'bistro', 'eatery']): return '\uc2dd\ub2f9'
    if any(x in name_lower for x in ['grocery', 'market', 'mart', '\ub9c8\ud2b8', 'supermarket', 'h mart', 'hmart']): return '\ub9c8\ud2b8/\uc2dd\ud488\uc810'
    if any(x in name_lower for x in ['hair', 'salon', 'beauty', '\ubbf8\uc6a9', 'spa', 'nail']): return '\ubbf8\uc6a9/\uc2a4\ud30c'
    if any(x in name_lower for x in ['church', '\uad50\ud68c', 'christian', 'presbyterian', 'baptist']): return '\uad50\ud68c'
    if any(x in name_lower for x in ['real estate', 'realty', '\ubd80\ub3d9\uc0b0']): return '\ubd80\ub3d9\uc0b0'
    if any(x in name_lower for x in ['insurance', '\ubcf4\ud5d8']): return '\ubcf4\ud5d8'
    if any(x in name_lower for x in ['doctor', 'medical', 'clinic', 'physician', '\uc758\uc6d0', '\ubcd1\uc6d0']): return '\uc758\ub8cc'
    if any(x in name_lower for x in ['dentist', 'dental', '\uce58\uacfc']): return '\uce58\uacfc'
    if any(x in name_lower for x in ['lawyer', 'attorney', 'law', '\ubcc0\ud638\uc0ac']): return '\ubc95\ub960'
    if any(x in name_lower for x in ['accounting', 'cpa', 'tax', '\ud68c\uacc4', '\uc138\ubb34']): return '\ud68c\uacc4/\uc138\ubb34'
    if any(x in name_lower for x in ['bakery', 'bread', '\ubca0\uc774\ucee4\ub9ac', '\ube75']): return '\ubca0\uc774\ucee4\ub9ac'
    if any(x in name_lower for x in ['cafe', 'coffee', '\uce74\ud398', 'tea', 'boba']): return '\uce74\ud398'
    if any(x in name_lower for x in ['school', 'academy', 'tutor', '\ud559\uc6d0', '\uad50\uc721']): return '\uad50\uc721/\ud559\uc6d0'
    if any(x in name_lower for x in ['auto', 'car', 'mechanic', '\uc790\ub3d9\ucc28', '\uc815\ube44']): return '\uc790\ub3d9\ucc28'
    if any(x in name_lower for x in ['karaoke', 'norebang', '\ub178\ub798\ubc29']): return '\ub178\ub798\ubc29'
    if any(x in name_lower for x in ['taekwondo', 'martial', '\ud0dc\uad8c\ub3c4', '\ub3c4\uc7a5']): return '\ud0dc\uad8c\ub3c4/\ubb34\uc220'
    if any(x in name_lower for x in ['travel', '\uc5ec\ud589\uc0ac']): return '\uc5ec\ud589\uc0ac'
    if any(x in name_lower for x in ['pharmacy', 'drug', '\uc57d\uad6d']): return '\uc57d\uad6d'
    return '\uae30\ud0c0'
