from signal import signal, SIGHUP
from asyncio import sleep
from threading import Lock

from prometheus_exporter import Exporter
from .ups_metric import UPSMetric
from hid_ups import HIDUPS


class HIDUPSExporter(Exporter):
    """
    Exporter for HID USB UPS devices
    """
    def __init__(self, run_forever=False, max_fails=5, *args, **kwargs):
        kwargs['listen_port'] = kwargs.pop('listen_port', 9808)
        super().__init__(*args, **kwargs)
        self.run_forever = run_forever
        self.max_fails = max_fails
        self.init_lock = Lock()
        signal(SIGHUP, lambda *args: self.init_devices())

    def init_devices(self):
        self.logger.info("Initializing HID UPS devices.")
        with self.init_lock:
            self.close_devices()
            self.ups_list = []
            for dev in HIDUPS.get_UPSs(run_forever=self.run_forever, max_fails=self.max_fails,
                                       logger=self.logger, _log_bump=10):
                self.ups_list.append(dev)
                self.app.loop.create_task(dev.mainloop())

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
        for ups in self.ups_list.copy():
            if not hasattr(ups, 'ups'):
                self.logger.warning("Removing UPS: %s", ups)
                self.ups_list.remove(ups)
            self.logger.debug("Adding metrics for UPS %s", ups)
            ups_metrics = []
            for param in ups.PARAMS:
                if getattr(ups, param, None) is None:
                    self.logger.warning("%s - missing parameter: %s", ups, param)
                    break
                ups_metrics.append(UPSMetric(param, ups=ups, labels=self.labels,
                                             logger=self.logger, _log_init=False))
            else:
                self.metrics.extend(ups_metrics)
        return self.metrics

    def read_config(self):
        try:
            super().read_config()
            self.max_fails = self.config.get('max_fails', 5)
            self.run_forever = self.config.get('run_forever', False)
        except FileNotFoundError:
            # Config file not needed here
            self.logger.debug('No config file found.')
            self.config = {}
