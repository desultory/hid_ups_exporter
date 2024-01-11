from prometheus_exporter import Metric


class UPSMetric(Metric):
    def __init__(self, name, ups, *args, **kwargs):
        kwargs.update({'help': f'UPS {name}', 'metric_type': 'gauge', 'labels': {'ups_serial': ups.name}})
        super().__init__(name, *args, **kwargs)
        self.ups = ups

    def _value(self):
        return getattr(self.ups, self.name) if hasattr(self, 'ups') else None
