# -*- coding: utf-8 -*-
# Copyright (c) 2013 Peter Rowlands
# All rights reserved.

from __future__ import division, absolute_import

from django.core.management.base import BaseCommand

import sys
import SocketServer

from optparse import make_option

from goonpug.libs.logs import GoonPugParser


log_parsers = {}


class GoonPugLogHandler(SocketServer.DatagramRequestHandler):

    verbose = False

    def handle(self):
        data = self.request[0]
        # Strip the 4-byte header and the first 'R' character
        #
        # There is no documentation for this but I am guessing the 'R' stands
        # for 'Remote'? Either way normal log entires are supposed to start
        # with 'L', but the UDP packets start with 'RL'
        data = data[5:].strip()
        if not self.client_address in log_parsers:
            print u'Got new connection from {}'.format(self.client_address[0])
            parser = GoonPugParser(GoonPugLogHandler.verbose)
            log_parsers[self.client_address] = parser
        log_parsers[self.client_address].parse_line(data)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-p', '--port', dest='port', action='store',
                    default=27500, help='port to listen on'),
        make_option('-s', action='store_true', dest='stdin',
                    help='read log entries from stdin instead of '
                    'listening on a network port'),
    )

    def handle(self, *args, **options):
        if options['verbosity'] > 1:
            verbose = True
        else:
            verbose = False
        if options['stdin']:
            log_parser = GoonPugParser(verbose=verbose)
            self.stdout.write("goonpugd: Reading from STDIN")
            while True:
                try:
                    for line in sys.stdin.readlines():
                        log_parser.parse_line(line)
                except KeyboardInterrupt:
                    sys.exit()
                except EOFError:
                    sys.exit()
        else:
            port = int(options['port'])
            self.stdout.write('goonpugd: Listening for HL log'
                              ' connections on port %d' % port)
            GoonPugLogHandler.verbose = verbose
            server = SocketServer.UDPServer(('0.0.0.0', port),
                                            GoonPugLogHandler)
            server.timeout = 30
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                self.stdout.write('goonpugd: exiting')
                sys.exit()
