#!/usr/bin/env python3

from hid_ups_exporter import HIDUPSExporter
from prometheus_exporter import DEFAULT_EXPORTER_ARGS
from zenlib.util import get_kwargs


def main():
    arguments = DEFAULT_EXPORTER_ARGS.copy()
    arguments += [{'flags': ['--run-forever'], 'help': 'Run forever, even if failing.', 'action': 'store_true'},
                  {'flags': ['--max-fails'], 'help': 'Maximum number of fails before killing the listener.', 'type': int}]

    kwargs = get_kwargs(package=__package__, description='HID UPS Prometheus Exporter', arguments=arguments)

    exporter = HIDUPSExporter(**kwargs)
    exporter.start()


if __name__ == '__main__':
    main()
