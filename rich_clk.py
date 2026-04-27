import fonts, icons, wasp

class RichClkApp():
    NAME = "RichClk"
    ICON = icons.clock

    WDAY = "MonTueWedThuFriSatSun"
    MONTH = "JanFebMarAprMayJunJulAugSepOctNovDec"

    def foreground(self):
        wasp.system.bar.clock = True
        self._now = (-1, -1, -1, -1, -1, -1, -1)
        wasp.watch.drawable.fill()
        self._draw()
        wasp.system.request_tick(1000)

    def sleep(self):
        return True

    def tick(self, ticks):
        wasp.system.keep_awake()
        self._draw()

    def wake(self):
        self._draw()

    def _draw(self):
        draw = wasp.watch.drawable
        draw.set_color(65535)
        now = wasp.watch.rtc.get_localtime()

        if now[6] != self._now[6]: # Day (also full redraw)
            draw.set_font(fonts.sans24)
            draw.string(
                self.WDAY[now[6]*3:(now[6]+1)*3] + " " +
                self.MONTH[(now[1]-1)*3:now[1]*3] + " " +
                str(now[2]) + " " + str(now[0]), 0, 44
            )
            draw.string("Battery:", 0, 100)
            draw.string("Free RAM:", 0, 128)
            draw.string("Uptime:", 0, 156)
            draw.string("Steps:", 0, 184)
            draw.string("# Apps:", 0, 212)
            draw.string(str(sum(1 for i in dir(__import__("apps")) if not i.startswith("_"))), 140, 212)

        if now[4] != self._now[4]: # Hour & Minute
            draw.set_font(fonts.sans36)
            draw.string("{:02}:{:02}:".format(now[3], now[4]), 0, 0)

        if now[5] % 5 == 0 or self._now[5] == -1: # Every 5 seconds (refresh data)
            mem_free = str(wasp.gc.mem_free())
            draw.set_font(fonts.sans24)
            draw.string("{:.3f}V".format(wasp.watch.battery.voltage_mv() / 1000), 140, 100)
            draw.string(mem_free, 140, 128)
            draw.string("{:.1f}h".format(wasp.watch.time.ticks_ms() / 3600000), 140, 156)
            draw.string(str(wasp.watch.accel.steps), 140, 184)
            wasp.gc.collect()

        if now[5] != self._now[5]: # Second
            draw.set_font(fonts.sans36)
            draw.string("{:02}".format(now[5]), 158, 0)
            draw.set_font(fonts.sans24)

        self._now = now