#Build 1.1.1

from sys import exit
from tkinter import Tk, messagebox
from tkinter.filedialog import askdirectory, asksaveasfilename
from time import time
from os import listdir

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ''

def customError(type, message):
    messagebox.showerror(type, message)
    exit(0)

def parseFile(filePath, customer, data):
    with open(filePath) as logFile:
        for logLine in logFile:
            try:
                tempCustomer = ''
                temp
                if logLine.endswith('\n'):
                    logLine = logLine[:-1]
                tempLine = logLine.split(' ')
                #Only log successful requests with HTTP status 2XX and data is known
                if (tempLine[len(tempLine) - 2][:1] == '2') and (tempLine[len(tempLine) - 1] != '-'):
                    tempData = int(tempLine[len(tempLine) - 1])
                    #Check if request is from local load balancer or direct
                    if  find_between(find_between(logLine, ' \"', '\" '), ' ', ' ')[:5] == 'https':
                        tempCustomer = find_between(find_between(find_between(logLine, ' \"', '\" '), ' ', ' '), 'm/', '/')
                    else:
                        tempCustomer = find_between(find_between(find_between(logLine, ' \"', '\" '), ' ', ' '), '/', '/')
                    #Add customer to list if not detected before
                if tempCustomer not in customer:
                    customer.append(tempCustomer)
                    data.append(tempData)
                else:
                    data[customer.index(tempCustomer)] += tempData
            except UnboundLocalError:
                print('{} in {}'.format(logLine, logFile))
                customError('UnboundLocalError', 'Could Not Parse File Correctly')
    return customer, data

def main():
    customer = []
    data = []
    fileFormat = [('Comma-Separated Values', '*.csv')]
    #Stop main window opening
    Tk().withdraw()
    selectedDirectory = askdirectory(title = 'Select log file directory', initialdir = '/')
    if selectedDirectory == '':
        customError('FileNotFoundError', 'No Input Directory Provided')
    resultsFile = asksaveasfilename(title = 'Select results as...', initialdir = '/', filetypes = fileFormat, defaultextension = '.csv')
    if resultsFile == '':
        customError('FileNotFoundError', 'No Output File Provided')
    startTime = time()
    for selectedFile in listdir(selectedDirectory):
        #Only scan access_SSL files in directory
        if selectedFile.startswith('access_SSL'):
            parseFile(selectedDirectory + "/" + selectedFile, customer, data)
    with open(resultsFile, 'w') as resultsF:
        for i in customer:
            resultsF.write('{},{}\n'.format(i, data[customer.index(i)]))
        #Debug Runnning Timer
        #resultsF.write('That took {} seconds'.format(time() - startTime))

if __name__ == '__main__':
    exit(int(main() or 0))