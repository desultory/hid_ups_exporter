"""
JSON exporter class
"""

from signal import signal, SIGHUP
from asyncio import sleep

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
        signal(SIGHUP, lambda *args: self.init_devices())

    def init_devices(self):
        self.logger.info("Initializing HID UPS devices.")
        self.close_devices()
        self.ups_list = []
        self.ups_tasks = []
        for dev in HIDUPS.get_UPSs(logger=self.logger, _log_bump=10):
            self.ups_list.append(dev)
            task = dev.mainloop()
            self.ups_tasks.append(task)
            self.app.loop.create_task(task)

    def close_devices(self):
        """ Stop the HID device and its running loop """
        if hasattr(self, 'ups_list'):
            for ups in self.ups_list:
                ups.close()

    async def get_metrics(self, *args, **kwargs):
        self.metrics = await super().get_metrics(*args, **kwargs)
        if not getattr(self, 'ups_list', None):
            self.init_devices()
            await sleep(5)
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
