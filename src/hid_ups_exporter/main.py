#!/usr/bin/env python3

from hid_ups_exporter import HIDUPSExporter
from zenlib.util import init_logger, init_argparser, process_args


def main():
    argparser = init_argparser(prog=__package__, description='HID based UPS exporter for Prometheus.')
    logger = init_logger(__package__)

    argparser.add_argument('-p', '--port', type=int, nargs='?', help='Port to listen on.')
    argparser.add_argument('-a', '--address', type=str, nargs='?', help='Address to listen on.')
    argparser.add_argument('--run-forever', action='store_true', help='Run forever, even if failing.')
    argparser.add_argument('--max-fails', type=int, nargs='?', help='Maximum number of fails before killing the listener.')
    args = process_args(argparser, logger=logger)

    kwargs = {'logger': logger, 'run_forever': args.run_forever}

    if args.port:
        kwargs['listen_port'] = args.port
    if args.address:
        kwargs['listen_ip'] = args.address
    if args.max_fails:
        kwargs['max_fails'] = args.max_fails

    exporter = HIDUPSExporter(**kwargs)
    exporter.start()


if __name__ == '__main__':
    main()
