"""
JSON exporter class
"""

from prometheus_exporter import Exporter
from .ups_metric import UPSMetric
from hid_ups import HIDUPS
from zenlib.util import handle_plural


class HIDUPSExporter(Exporter):
    """
    Exporter for HID USB UPS devices
    """
    def __init__(self, *args, **kwargs):
        kwargs['port'] = kwargs.pop('port', 9808)
        super().__init__(*args, **kwargs)
        self.ups_list = []
        for dev in HIDUPS.get_UPSs(logger=self.logger, _log_bump=10):
            dev.start()
            self.ups_list.append(dev)
        self.generate_metrics(self.ups_list)

    @handle_plural
    def generate_metrics(self, ups):
        for param in ups.PARAMS:
            self.metrics.append(UPSMetric(param, ups=ups, labels=self.labels, logger=self.logger, _log_init=False))

    def read_config(self):
        try:
            super().read_config()
        except FileNotFoundError:
            # Config file not needed here
            self.logger.debug('No config file found.')
            self.config = {}
