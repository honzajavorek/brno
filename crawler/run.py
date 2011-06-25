#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Runs database update."""



from drivers import agartha, kafelanka, lunchtime, podzemibrno, poznejbrno
from tools import log, notify, slugify
import datetime
import os
import subprocess
import sys



active_drivers = (
#    agartha,
#    kafelanka,
#    lunchtime,
    podzemibrno,
#    poznejbrno,
)



notify('Brno', 'Starting update...')
for driver in active_drivers:
    log('driver', driver.__name__)
    driver.run()

notify('Brno', 'Exporting and uploading database...')
filename = '%s/db/%s.sql' % (os.path.dirname(sys.argv[0]), slugify(datetime.date.today()))
log('dump', filename)
with open(filename, 'w') as f:
    subprocess.Popen(['mysqldump', '-h', 'localhost', '-u', 'dev', '--password=dev', 'brno'], stdout=f).wait()