#!/usr/bin/env python
#
# Simple runner of Flask test application.
#

import sys

from testapp import app


if __name__ == '__main__':
    host, port = '0.0.0.0', 4332

    if len(sys.argv) == 2:
        port = sys.argv[1]

        if ':' in port:
            host, port = port.split(':')

        port = int(port)

    app.run(debug=True, host=host, port=port)
