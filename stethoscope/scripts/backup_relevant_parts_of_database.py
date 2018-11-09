from pyramid.paster import bootstrap
from stethoscope.models.replication_helper import ReplicationHelper
from stethoscope.models.rssi_reading import RssiReading
from stethoscope.models.training_run import TrainingRun
import os
import ipdb
import subprocess
import sys


def main(filename, dbsession):

    training_runs = TrainingRun.completed(dbsession)
    trun_rhelper = ReplicationHelper(TrainingRun)

    trun_sql = trun_rhelper.insert_bulk(training_runs)


    rssi_reading_ids = TrainingRun.rssi_reading_ids_from_all_completed_training_runs(dbsession)
    rssi_readings = dbsession.query(RssiReading).filter(RssiReading.id.in_(rssi_reading_ids))
    reading_helper = ReplicationHelper(RssiReading)
    reading_sql = reading_helper.insert_bulk(rssi_readings)

    with open(filename, 'w') as f:
        f.write(trun_sql)
        f.write(reading_sql)

    success(filename)




def success(filename):
    print('SUCCESS!')
    print(f'Database backup saved in {filename}')
    print('Note backup does not include schema')


def usage(this_filename):
    print('USAGE')
    print('cd /path/to/stethoscope')
    print(f'env/bin/python {this_filename} <output_file>')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage(sys.argv[0])
        sys.exit()

    filename = sys.argv[1]

    with bootstrap('development.ini') as env:
        request = env['request']
        dbsession = request.dbsession
        request.tm.begin()
        main(filename, dbsession)

