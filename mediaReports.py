'''
// Good luck with this code. Do praise if its good.
// And dont curse if its bad :). 
Author: Vreddhi Bhat
Contact: vbhat@akamai.com
'''

import configparser
import requests, logging, json
from akamai.edgegrid import EdgeGridAuth
import json
import argparse
import os
import timeit
from xlsxwriter.workbook import Workbook
import csv

start = timeit.default_timer()
#Setup logging
if not os.path.exists('logs'):
    os.makedirs('logs')
logFile = os.path.join('logs', 'mediaReport.log')

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
consoleFormatter = logging.Formatter("\n[%(asctime)s]  %(message)s" ,"%H:%M:%S")
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler(logFile, mode='w')
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(consoleFormatter)
rootLogger.addHandler(consoleHandler)
#Set Log Level to DEBUG, INFO, WARNING, ERROR, CRITICAL
rootLogger.setLevel(logging.INFO)

#print('\nDetailed logs are stored in ' + logFile)
#Setup commandline arguments
parser = argparse.ArgumentParser(description='OpenAPI credentials are read from ~/.edgerc')
parser.add_argument("-report",help="Generate media report",action="store_true")
parser.add_argument("-cpcodes",help="Comma seperated list of CPCODES")
parser.add_argument("-dimensions",help="Comma seperated list of dimensions")
parser.add_argument("-metrics",help="Comma seperated list of metrics")
parser.add_argument("-startDate",help="Start Date in format MM/DD/YYYY:HH:MM  (Time is in 24 hr format)")
parser.add_argument("-endDate",help="End Date in format MM/DD/YYYY:HH:MM  (Time is in 24 hr format)")
parser.add_argument("-format",help="Output format. Valid values are xlsx (OR) json")


parser.add_argument("-debug",help="Run the program in debug mode",action="store_true")
args = parser.parse_args()

if args.debug:
    rootLogger.setLevel(logging.DEBUG)

try:
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.expanduser("~"),'.edgerc'))
    client_token = config['default']['client_token']
    client_secret = config['default']['client_secret']
    access_token = config['default']['access_token']
    access_hostname = config['default']['host']
    session = requests.Session()
    session.auth = EdgeGridAuth(
                client_token = client_token,
                client_secret = client_secret,
                access_token = access_token
                )
except (NameError, AttributeError, KeyError):
    rootLogger.info('\nLooks like ' + os.path.join(os.path.expanduser("~"),'.edgerc') + ' is missing or has invalid entries\n')
    exit(-1)

if not args.report:
    rootLogger.info("Use -h to know the options to run program")
    exit()



if args.report:
    if args.cpcodes:
        cpcodes = args.cpcodes
    else:
        print('CPCODE(S) is/are manadatory, Use -h to know more')
        exit(-1)

    if args.dimensions:
        dimensions = args.dimensions
    else:
        print('Dimension(s) is/are manadatory, Use -h to know more')
        exit(-1)

    if args.metrics:
        metrics = args.metrics
    else:
        print('metric(s) is/are manadatory, Use -h to know more')
        exit(-1)

    if args.startDate:
        startDate = args.startDate
    else:
        print('startDate is manadatory, Use -h to know more')
        exit(-1)

    if args.endDate:
        endDate = args.endDate
    else:
        print('endDate is manadatory, Use -h to know more')
        exit(-1)

    if args.format:
        if args.format != 'xlsx' and args.format != 'json':
            print('Wrong value of format, Use -h to know more')
            exit(-1)
        Format = args.format
    else:
        print('format is manadatory, Use -h to know more')
        exit(-1)

    reportUrl = 'https://' + access_hostname + '/media-reports/v1/download-delivery/data?cpcodes=' + cpcodes + \
     '&dimensions=' + dimensions +'&metrics=' + metrics + '&startDate=' + startDate + '&endDate=' + endDate
    reportResponse = session.get(reportUrl)
    #print(json.dumps(reportResponse.json(), indent=4))

    if not os.path.exists('reports'):
        os.makedirs('reports')
    output_file_name = 'DownloadReport' + startDate + '_TO_' + endDate
    output_file_name = output_file_name.replace('/','_').replace(':','_')
    outputFile = os.path.join('reports', output_file_name)

    if Format == 'xlsx':
        xlsxFile = outputFile.replace('.csv', '') + '.xlsx'
        with open(outputFile, 'w') as fileHandler:
            fileHandler.write(
                'Type, name, description, index, aggregate, peak, unit \n')
    elif Format == 'json':
        jsonFile =   outputFile.replace('.csv', '') + '.json'

    if reportResponse.status_code == 200:
        rootLogger.info('Generating Report..')
        for everyColumn in reportResponse.json()['columns']:
            if 'type' in everyColumn:
                Type = everyColumn['type']
            else:
                Type = ' '
            if 'name' in everyColumn:
                name = everyColumn['name'].replace(',','')
            else:
                name = ' '
            if 'description' in everyColumn:
                description = everyColumn['description'].replace(',','')
            else:
                description = ' '
            if 'index' in everyColumn:
                index = everyColumn['index']
            else:
                index = ' '
            if 'aggregate' in everyColumn:
                aggregate = everyColumn['aggregate']
            else:
                aggregate = ' '
            if 'peak' in everyColumn:
                peak = everyColumn['peak']
            else:
                peak = ' '
            if 'unit' in everyColumn and everyColumn['unit'] is not None:
                unit = everyColumn['unit']
            else:
                unit = ' '

            if Format == 'xlsx':
                with open(outputFile, 'a') as fileHandler:
                    fileHandler.write(str(Type) + ', ' + str(name) + ', ' + str(description) + ', ' + str(index) + ', '
                                      + str(aggregate) + ', ' +
                                      str(peak) + ', ' + str(unit) + '\n')
        if Format == 'xlsx':
            # Merge CSV files into XLSX
            workbook = Workbook(os.path.join(xlsxFile))
            worksheet = workbook.add_worksheet('Download Report')
            with open(os.path.join(outputFile), 'rt', encoding='utf8') as f:
                reader = csv.reader(f)
                for r, row in enumerate(reader):
                    for c, col in enumerate(row):
                        worksheet.write(r, c, col)
            workbook.close()
            # Delete the csv file at the end
            os.remove(outputFile)
            rootLogger.info('Report is saved as ' + xlsxFile)
        else:
            #Write in JSON format
            with open(jsonFile, 'w') as fileHandler:
                fileHandler.write(json.dumps(reportResponse.json(), indent=4))
            rootLogger.info('Report is saved as ' + jsonFile)

    else:
        rootLogger.info('Unable to fetch reports. Contact Akamai')



stop = timeit.default_timer()
print('Total time taken: ' + str(stop - start))
