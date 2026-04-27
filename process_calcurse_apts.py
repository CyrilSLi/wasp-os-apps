from os import environ, path
from datetime import datetime
base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def base64_encode(num, padding=1):
    if num == 0:
        return base64_chars[0] * padding
    result = ""
    while num > 0:
        result = base64_chars[num % 64] + result
        num //= 64
    return result.rjust(padding, base64_chars[0])
assert base64_encode(64) == base64_chars[1] + base64_chars[0]

days = {}
min_day, max_day = 9999 * 366, 0
apt_names = []

with open(environ["HOME"] + "/.local/share/calcurse/apts") as f:
    for line in f:
        if line[11] != "@":
            continue # Skip full-day events

        day = datetime.strptime(line[:10], "%m/%d/%Y").timetuple()
        day_key = day[0] * 366 + day[7] - 1 # tm_yday is 1-indexed
        if day_key < min_day:
            min_day = day_key
        if day_key > max_day:
            max_day = day_key

        day_apts = days.setdefault(day_key, [])
        truncated_name = line.split("|", 1)[1].strip().replace("\n", " ").replace("\r\n", " ")[:20].ljust(20)
        if truncated_name not in apt_names:
            apt_names.append(truncated_name)
            if len(apt_names) > 64 ** 4 // (24 * 60): # 11650
                raise ValueError("Too many unique appointment names")

        day_apts.append(base64_encode((
            apt_names.index(truncated_name) * (24 * 60) +
            int(line[13:15]) * 60 +
            int(line[16:18])
        ), padding=4))
        days[day_key] = day_apts

with open(path.join(path.dirname(__file__), "apts_data"), "w") as f:
    f.write("".join(base64_encode(i, padding=4) for i in (min_day, max_day, len(apt_names))))
    f.write("".join(apt_names))
    days_list = []
    index = 12 + 20 * len(apt_names) + 4 * (max_day - min_day + 2) # One more for ending index of last day
    for day in range(min_day, max_day + 1):
        day_apts = days.get(day, [])
        f.write(base64_encode(index, padding=4))
        index += len(day_apts) * 4
        days_list.extend(day_apts)
    f.write(base64_encode(index, padding=4)) # Ending index of last day
    f.write("".join(days_list))



# Testing

import base64
base64_decode = lambda s: int.from_bytes(base64.b64decode(s.encode()), "big")

with open(path.join(path.dirname(__file__), "apts_data")) as f:
    min_day = base64_decode(f.read(4))
    max_day = base64_decode(f.read(4))
    num_names = base64_decode(f.read(4))
    print("Min day:", datetime.strptime(f"{min_day//366}-{(min_day%366)}", "%Y-%j"))
    print("Max day:", datetime.strptime(f"{max_day//366}-{(max_day%366)}", "%Y-%j"))
    print("Num names:", num_names)
    while True:
        day = input("Day (YYYYMMDD): ")
        day = datetime.strptime(day, "%Y%m%d").timetuple()
        day_key = day[0] * 366 + day[7] - 1 # tm_yday is 1-indexed
        f.seek(12 + 20 * num_names + 4 * (day_key - min_day))
        day_index = base64_decode(f.read(4))
        next_index = base64_decode(f.read(4))
        f.seek(day_index)
        for i in range((next_index - day_index) // 4):
            apt_data = base64_decode(f.read(4))
            ptr = f.tell()
            f.seek(12 + apt_data // (24 * 60) * 20)
            apt_name = f.read(20).rstrip()
            f.seek(ptr)
            hour = apt_data % (24 * 60) // 60
            minute = apt_data % 60
            print(f"{hour:02}:{minute:02} - {apt_name}")
