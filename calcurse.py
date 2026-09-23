import fonts, icons, wasp
from binascii import a2b_base64

class CalcurseApp():
    NAME = "Calcurse"
    ICON = icons.app

    time = wasp.watch.time
    WDAY = "MonTueWedThuFriSatSun"
    MONTH = "JanFebMarAprMayJunJulAugSepOctNovDec"

    def __init__(self):
        self.f = open("apts_data", "rb")
        self.min_day = self.read_b64()
        self.max_day = self.read_b64()
        self.num_names = self.read_b64()

    def read_b64(self):
        return int.from_bytes(a2b_base64(self.f.read(4)), "big")

    def seek_day(self):
        self.f.seek(12 + 20 * self.num_names + 4 * (self.day - self.min_day))
        self.curr_index, self.next_index = self.read_b64(), self.read_b64()
        self.index = self.curr_index

    def read_apt(self):
        apt_data = self.read_b64()
        ptr = self.f.tell()
        self.f.seek(12 + apt_data // (24 * 60) * 20)
        apt_name = self.f.read(20).decode().rstrip()
        self.f.seek(ptr)
        # name, hour, minute
        return apt_name, apt_data % 1440 // 60, apt_data % 60

    def foreground(self):
        wasp.system.bar.clock = True
        wasp.system.request_event(wasp.EventMask.SWIPE_UPDOWN | wasp.EventMask.SWIPE_LEFTRIGHT)

        now = wasp.watch.rtc.get_localtime()
        self.day = now[0] * 366 + now[7] - 1 # tm_yday is 1-indexed
        if self.day < self.min_day or self.day > self.max_day:
            return
        self.seek_day()

        self.f.seek(self.index)
        self.f.read(4) # Look ahead to the apt following the index
        now_minute = now[3] * 60 + now[4]
        while self.next_index >= self.index + 12:
            _, hour, minute = self.read_apt()
            if hour * 60 + minute >= now_minute:
                break
            self.index += 4

        self._draw()

    def sleep(self):
        return True

    def wake(self):
        self._draw()

    def tick(self, ticks):
        self._draw()

    def swipe(self, event):
        if event[0] == wasp.EventType.UP:
            # Two apts per page plus one more to scroll to on the next page
            if self.next_index >= self.index + 12:
                self.index += 4
            elif self.day < self.max_day:
                self.day += 1
                self.seek_day()
        elif event[0] == wasp.EventType.DOWN:
            if self.curr_index <= self.index - 4:
                self.index -= 4
            elif self.day > self.min_day:
                self.day -= 1
                self.seek_day()
        elif event[0] == wasp.EventType.LEFT:
            if self.day < self.max_day:
                self.day += 1
                self.seek_day()
        elif event[0] == wasp.EventType.RIGHT:
            wasp.system.navigate(wasp.EventType.HOME)
            return # Emulate system default behaviour
        self._draw()

    def _draw(self):
        draw = wasp.watch.drawable
        draw.fill()
        draw.set_color(65535)
        draw.set_font(fonts.sans24)
        now = wasp.watch.rtc.get_localtime()

        draw.string(
            self.WDAY[now[6]*3:(now[6]+1)*3] + " " +
            self.MONTH[(now[1]-1)*3:now[1]*3] +
            " {:02} {:02}:{:02}".format(now[2], now[3], now[4]), 0, 0
        )
        day_date = self.time.localtime(self.time.mktime((self.day // 366, 1, 1, 0, 0, 0, 0, 0)) + (self.day % 366) * 86400)
        day_string = (
            self.WDAY[day_date[6]*3:(day_date[6]+1)*3] + " " +
            self.MONTH[(day_date[1]-1)*3:day_date[1]*3] +
            " {:02} ".format(day_date[2])
        )

        self.f.seek(self.index)
        if self.index == self.next_index:
            draw.string(day_string, 0, 50)
            draw.string("No items", 0, 78)
        else:
            for i in range(min(2, (self.next_index - self.index) // 4)):
                height = 50 + i * 106

                apt_name, hour, minute = self.read_apt()
                draw.string(day_string + "{:02}:{:02}".format(hour, minute), 0, height)

                chunks = draw.wrap(apt_name, 240)
                for j in range(1, min(len(chunks), 3)):
                    draw.string(apt_name[chunks[j-1]:chunks[j]], 0, height + 28 * j)

        wasp.gc.collect()