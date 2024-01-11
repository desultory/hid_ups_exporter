#!/usr/bin/env python3

from signal import signal

from hid_ups_exporter import HIDUPSExporter
from zenlib.util import init_logger, init_argparser, process_args


def main():
    argparser = init_argparser(prog=__package__, description='HID based UPS exporter for Prometheus.')
    logger = init_logger(__package__)

    argparser.add_argument('-p', '--port', type=int, nargs='?', help='Port to listen on.')
    argparser.add_argument('-a', '--address', type=str, nargs='?', help='Address to listen on.')
    args = process_args(argparser, logger=logger)

    kwargs = {'logger': logger}

    if args.port:
        kwargs['port'] = args.port
    if args.address:
        kwargs['ip'] = args.address

    exporter = HIDUPSExporter(**kwargs)

    def handle_shutdown_signal(sig, frame):
        logger.info(f"Received signal: {sig}. Shutting down...")
        for dev in exporter.ups_list:
            dev.loop_thread.loop.clear()
        if hasattr(exporter, '__is_shut_down') and not exporter.__is_shut_down.is_set():
            exporter.shutdown()
        exit(0)

    # Handle SIGINT, SIGTERM, SIGQUIT, SIGABRT
    for sig in [2, 15, 3, 6]:
        signal(sig, handle_shutdown_signal)

    exporter.serve_forever()


if __name__ == '__main__':
    main()
