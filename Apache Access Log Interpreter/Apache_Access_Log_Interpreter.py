#Build 2.3.0

from datetime import date, datetime, timedelta
from getopt import getopt, GetoptError
from os import listdir
from sys import argv, exit
from time import time

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ''

def walkDirectory(directory, month, year, customer, data):
    for selectedFile in listdir(directory):
        #Only scan access_SSL files in directory with this year and this month
        if selectedFile.startswith('access_SSL_' + year + '-' + month):
            parseFile(directory + '/' + selectedFile, customer, data)
    return customer, data

def parseFile(filePath, customer, data):
    with open(filePath) as logFile:
        print(filePath)
        for logLine in logFile:
            if logLine.endswith('\n'):
                logLine = logLine[:-1]
            tempLine = logLine.split(' ')
            #Only log successful requests with HTTP status 2XX and data is known
            if (tempLine[len(tempLine) - 2][:1] == '2') and (tempLine[len(tempLine) - 1] != '-'):
                tempData = int(tempLine[len(tempLine) - 1])
                #Check if request is from local load balancer or direct
                if  find_between(find_between(logLine, ' \"', '\" '), ' ', ' ')[:5] == 'https':
                    tempCustomer = find_between(find_between(find_between(logLine, ' \"', '\" '), ' ', ' '), 'm/', '/')
                    #Check if REST request
                    if len(find_between(find_between(logLine, ' \"', '\" '), ' ', ' ').split('/')) >= 5:
                        if find_between(find_between(logLine, ' \"', '\" '), ' ', ' ').split('/')[4] == 'rest':
                            tempCustomer += '/rest'
                else:
                    tempCustomer = find_between(find_between(find_between(logLine, ' \"', '\" '), ' ', ' '), '/', '/')
                    #Check if REST request
                    if len(find_between(find_between(logLine, ' \"', '\" '), ' ', ' ').split('/')) >= 3:
                        if find_between(find_between(logLine, ' \"', '\" '), ' ', ' ').split('/')[2] == 'rest':
                            tempCustomer += '/rest'
                #Add customer to list if not detected before
                if tempCustomer not in customer:
                    customer.append(tempCustomer)
                    data.append(tempData)
                else:
                    data[customer.index(tempCustomer)] += tempData
    return customer, data

def main(argv):
    customer = []
    data = []
    inputDirectory = []
    resultsDirectory = ''
    #Get argument input
    try:
        opts, args = getopt(argv, 'i:o:', ['input=','output='])
    except GetoptError:
        print('Apache_Access_Log_Interpreter.py -i <inputdirectories> -o <outputdirectory>')
        exit(1)
    for opt, arg in opts:
        if opt in ('-i', '--input'):
            inputDirectory = arg.split(',')
        elif opt in ('-o', '--output'):
            resultsDirectory = arg
    #Only scan logs from last month
    timeNow = date.today()
    timeFirstDay = timeNow.replace(day = 1)
    timeLastMonth = timeFirstDay - timedelta(days = 1)
    timeStringMonth = timeLastMonth.strftime('%B')
    timeIntMonth = timeLastMonth.strftime('%m')
    timeYear = timeLastMonth.strftime('%Y')
    resultsFile = resultsDirectory + '/AccessLogResults-' + timeStringMonth + '.csv'
    startTime = time()
    for directory in inputDirectory:
        walkDirectory(directory, timeIntMonth, timeYear, customer, data)
    with open(resultsFile, 'w') as currentFile:
        for name in customer:
            currentFile.write('{},{}\n'.format(name, data[customer.index(name)]))
    print('That took {} seconds'.format(time() - startTime))

if __name__ == '__main__':
    exit(int(main(argv[1:]) or 0))