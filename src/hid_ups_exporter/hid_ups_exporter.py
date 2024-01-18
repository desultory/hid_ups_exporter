"""
JSON exporter class
"""

from signal import signal, SIGHUP

from prometheus_exporter import Exporter
from .ups_metric import UPSMetric
from hid_ups import HIDUPS


class HIDUPSExporter(Exporter):
    """
    Exporter for HID USB UPS devices
    """
    def __init__(self, *args, **kwargs):
        kwargs['listen_port'] = kwargs.pop('listen_port', 9808)
        super().__init__(*args, **kwargs)
        self.ups_list = []
        signal(SIGHUP, lambda *args: self.init_devices())
        self.init_devices()

    def init_devices(self):
        from asyncio import get_event_loop
        mainloop = get_event_loop()
        for dev in HIDUPS.get_UPSs(logger=self.logger, _log_bump=10):
            self.ups_list.append(dev)
            mainloop.create_task(dev.mainloop())

    async def get_metrics(self, *args, **kwargs):
        self.metrics = []
        for ups in self.ups_list:
            for param in ups.PARAMS:
                self.metrics.append(UPSMetric(param, ups=ups, labels=self.labels, logger=self.logger, _log_init=False))
        return self.metrics

    def read_config(self):
        try:
            super().read_config()
        except FileNotFoundError:
            # Config file not needed here
            self.logger.debug('No config file found.')
            self.config = {}
