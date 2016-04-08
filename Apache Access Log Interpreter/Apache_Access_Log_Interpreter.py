#Build 2.7.2

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
        if selectedFile.startswith('access_SSL_' + year + '-' + month): #Scan last months files
            parseFile(directory + '/' + selectedFile, customer, data)
    return customer, data

def parseFile(filePath, customer, data):
    with open(filePath) as logFile:
        print(filePath)
        for logLine in logFile:
            if logLine.endswith('\n'): #Remove trailing n
                logLine = logLine[:-1]
            tempLine = logLine.split(' ')
            tempLineLen = len(tempLine)
            try:
                tempData = int(tempLine[tempLineLen - 1])
                if (tempLine[tempLineLen - 2][:1] == '2'): #Check for successful requests
                    tempFindBetween = find_between(find_between(logLine, ' \"', '\" '), ' ', ' ')
                    if  tempFindBetween[:5] == 'https': #Proxy Server requests
                        tempCustomer = find_between(tempFindBetween, 'm/', '/')
                        arrayID = 4
                    else: #Regular requests
                        tempCustomer = find_between(tempFindBetween, '/', '/')
                        arrayID = 2
                    tempArray = tempFindBetween.split('/')
                    try:
                        if tempArray[arrayID] == 'rest': #Categorise REST requests seperatly
                            tempCustomer += '/rest'
                    except IndexError:
                        pass
                else: #Unsuccessful requests are logged as errors
                    tempCustomer = 'ERROR'
                if tempCustomer == '': #Define blank as ROOT directory
                    tempCustomer = 'ROOT'
                if tempCustomer not in customer:  #Add customer to list if not detected before
                    customer.append(tempCustomer)
                    data.append(tempData)
                else: #Add data to customer if found
                    data[customer.index(tempCustomer)] += tempData
            except ValueError:
                pass
    return customer, data

def main(argv):
    customer = []
    data = []
    inputDirectory = []
    resultsDirectory = ''
    try: #Get argument input
        opts, args = getopt(argv, 'i:o:', ['input=','output='])
    except GetoptError:
        print('Apache_Access_Log_Interpreter.py -i <inputdirectories> -o <outputdirectory>')
        exit(1)
    for opt, arg in opts:
        if opt in ('-i', '--input'): #Input folders
            inputDirectory = arg.split(',')
        elif opt in ('-o', '--output'): #Output file
            resultsDirectory = arg
    #Only scan logs from last month
    timeLastMonth = date.today().replace(day = 1) - timedelta(days = 1)
    timeStringMonth = timeLastMonth.strftime('%B')
    timeIntMonth = timeLastMonth.strftime('%m')
    timeYear = timeLastMonth.strftime('%Y')
    resultsFile = resultsDirectory + '/AccessLogResults-' + timeStringMonth + '.csv'
    startTime = time()
    for directory in inputDirectory:
        walkDirectory(directory, timeIntMonth, timeYear, customer, data)
    with open(resultsFile, 'w') as currentFile:
        totalData = 0
        for name in customer:
            totalData += data[customer.index(name)]
            currentFile.write('{},{}\n'.format(name, data[customer.index(name)]))
        currentFile.write('{},{}\n'.format('TOTAL', totalData))
    print('That took {} seconds'.format(time() - startTime))

if __name__ == '__main__':
    exit(int(main(argv[1:]) or 0))