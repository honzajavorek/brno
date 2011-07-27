#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Runs database update."""



from drivers import agartha, kafelanka, podzemibrno, poznejbrno, brnonow
from tools import log, notify, slugify
import datetime
import os
import subprocess



active_drivers = (
    agartha,
    kafelanka,
    podzemibrno,
    poznejbrno,
    brnonow,
)



notify('Brno', 'Starting update...')
for driver in active_drivers:
    notify('Brno', 'Starting driver "%s"' % driver.__name__)
    log('driver', driver.__name__)
    driver.run()

notify('Brno', 'Exporting and uploading database...')
filename = '%s/db/%s.sql' % (os.path.dirname(os.path.realpath(__file__)), slugify(datetime.date.today()))
log('dump', filename)
with open(filename, 'w') as f:
    subprocess.Popen(['mysqldump', '-h', 'localhost', '-u', 'dev', '--password=dev', 'brno'], stdout=f).wait()