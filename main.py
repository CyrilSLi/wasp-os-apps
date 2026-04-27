import wasp
wasp.system.brightness = 1
wasp.system.schedule()

from rich_clk import RichClkApp
wasp.system.register(RichClkApp())
del RichClkApp
wasp.gc.collect()
from calcurse import CalcurseApp
wasp.system.register(CalcurseApp())
del CalcurseApp
wasp.gc.collect()