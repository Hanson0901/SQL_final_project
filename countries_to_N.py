import re
import pycountry

countries = [country.name for country in pycountry.countries]

def adj_to_country(adj):
    patterns = ['ese', 'ian', 'an', 'ean', 'ic', 'ish']
    suffixes = ['a', 'o']
    for pattern in patterns:
        match = re.match(r'^(.*)(' + pattern + ')$', adj)
        if match:
            stem = match.group(1)
            # 直接比對
            if stem in countries:
                return stem
            # 加上常見尾碼再比對
            for suffix in suffixes:
                candidate = stem + suffix
                if candidate in countries:
                    return candidate
    return None

print(adj_to_country('American'))   # America
print(adj_to_country('Canadian'))   # Canada
print(adj_to_country('Brazilian'))  # Brazil
