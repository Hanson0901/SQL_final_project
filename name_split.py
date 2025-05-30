def name_split(name):
    parts = name.strip().split()
    if not parts:
        return "", ""
    # 如果第一個是全大寫
    if parts[0].isupper():
        name1 = " ".join(parts[1:]) if len(parts) > 1 else ""
        name2 = parts[0]
        return name1, name2
    # 找到第一個全大寫的單字（非第一個）
    for i in range(1, len(parts)):
        if parts[i].isupper():
            name1 = " ".join(parts[:i])
            name2 = " ".join(parts[i:])
            return name1, name2
    # 沒有全大寫的，第一個為name1，其餘為name2
    name1 = parts[0]
    name2 = " ".join(parts[1:]) if len(parts) > 1 else ""
    return name1, name2

def is_first_upper(name):
    parts = name.strip().split()
    if not parts:
        return False
    return parts[0].isupper()

# 範例
full_name = ["KOK Jing Hong"]
for name in full_name:
    name1, name2 = name_split(name)
    first_upper = is_first_upper(name)
    print("name1:", name1)
    print("name2:", name2)
    print("first_upper:", first_upper)