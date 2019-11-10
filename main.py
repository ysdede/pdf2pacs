# -*- coding: utf-8 -*-

from __future__ import division
import sys

try:
    import os.path
    import datetime as dt
    from datetime import date, datetime, timedelta
    import time
    import pdf2txt3, readTags, dicomtk, colors
    from time import sleep
    import os, ConfigParser, subprocess
    import shutil, errno
    import subprocess, logging
    import hashlib
    import colorama
except Exception as e:
    print ('Import error, run: "pip install -r requirements.txt to install missing dependencies."')
    sys.exit(2)


def getsettings(settingsFile):
    logging.info('Settings file: %s', settingsFile)
    config = ConfigParser.RawConfigParser()
    config.read(settingsFile)
    DICOM, PACS, TAGS_SINGLE = dict(), dict(), dict()
    # TAGS_SINGLE = dict()

    #
    DICOM['Modality'] = config.get('DICOM', 'Modality')
    DICOM['SeriesDescription'] = config.get('DICOM', 'SeriesDescription')
    DICOM['SOPClassUID'] = config.get('DICOM', 'SOPClassUID')
    DICOM['CharacterSet'] = config.get('DICOM', 'CharacterSet')
    DICOM['ConversionType'] = config.get('DICOM', 'ConversionType')
    DICOM['Manufacturer'] = config.get('DICOM', 'Manufacturer')
    DICOM['StationName'] = config.get('DICOM', 'StationName')
    DICOM['ManufacturersModelName'] = config.get('DICOM', 'ManufacturersModelName')
    DICOM['DeviceSerialNumber'] = config.get('DICOM', 'DeviceSerialNumber')
    DICOM['InstitutionName'] = config.get('DICOM', 'InstitutionName')
    DICOM['InstitutionAddress'] = config.get('DICOM', 'InstitutionAddress')
    DICOM['DepartmentName'] = config.get('DICOM', 'DepartmentName')
    DICOM['SecondaryCaptureDeviceManufacturer'] = config.get('DICOM', 'SecondaryCaptureDeviceManufacturer')
    DICOM['SecondaryCaptureDeviceModel'] = config.get('DICOM', 'SecondaryCaptureDeviceModel')
    DICOM['SecondaryCaptureDeviceSoftwareVersion'] = config.get('DICOM', 'SecondaryCaptureDeviceSoftwareVersion')
    #
    PACS['Address'] = config.get('PACS', 'Address')
    PACS['Port'] = config.get('PACS', 'Port')
    PACS['AET'] = config.get('PACS', 'AET')
    PACS['AEC'] = config.get('PACS', 'AEC')
    PACS['ScuParams'] = config.get('PACS', 'ScuParams')
    #
    TAGS_SINGLE['PatSex'] = config.getint('TAGS_SINGLE', 'PatSex')
    TAGS_SINGLE['PatName'] = config.getint('TAGS_SINGLE', 'PatName')
    TAGS_SINGLE['PatID'] = config.getint('TAGS_SINGLE', 'PatID')
    TAGS_SINGLE['PatAge'] = config.getint('TAGS_SINGLE', 'PatAge')
    TAGS_SINGLE['Procedure'] = config.getint('TAGS_SINGLE', 'Procedure')
    TAGS_SINGLE['ExamDate'] = config.getint('TAGS_SINGLE', 'ExamDate')
    TAGS_SINGLE['ExamDateFormat'] = config.get('TAGS_SINGLE', 'ExamDateFormat').strip('"')
    TAGS_SINGLE['ProcExamSplitter'] = config.get('TAGS_SINGLE', 'ProcExamSplitter').strip('"')
    TAGS_SINGLE['PatAgeSplitter'] = config.get('TAGS_SINGLE', 'PatAgeSplitter').strip('"')
    #
    return DICOM, PACS, TAGS_SINGLE


def getSHA1(fileName):
    buffSize = 65536
    sha1 = hashlib.sha1()

    with open(fileName, 'rb') as f:
        while True:
            data = f.read(buffSize)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def pdf2Jpeg(infile, outfile):
    status = -2
    folder = '{}/{}'.format(tempFolder, outfile)
    if not os.path.exists(folder):
        os.mkdir(folder, 0o0755)
    
    command = """gswin32c.exe -dNOPAUSE -sDEVICE=jpeg -r{} -dJPEGQ=95 -dTextAlphaBits=4 -dGraphicsAlphaBits=4 -sOutputFile={}/Page%02d.jpg {} -dBATCH """.format(jpegDensity, folder, infile)
    print (command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    print(error)


def process(file):
    origFile = '{}/{}'.format(captureFolder, file)
    print(origFile)

    fileStamp = getSHA1(origFile)
    tagFile = '{}/{}.tags'.format(tempFolder, fileStamp)
    backlogFile = "{}/{}.pdf".format(backlogFolder, fileStamp)

    if not os.path.isfile(backlogFile):
        shutil.copyfile(file, backlogFile)
        MSG = 'Created backlog file: {}'.format(backlogFile)
        print('%s%s%s' % (colors.OKGREEN, MSG, colors.ENDC))
    else:
        MSG = 'Skipping, file already exits in backlog: {}'.format(backlogFile)
        print('%s%s%s' % (colors.WARNING, MSG, colors.ENDC))

    pdf2txt3.extTxt(origFile, tagFile)
    pdf2Jpeg(backlogFile, fileStamp)
    error = dicomtk.createDicom(tempFolder, fileStamp, tagFile, DICOM, TAGS_SINGLE)
    if error == "":
        MSG = "Dicom object created..."
        print('%s%s%s' % (colors.OKGREEN, MSG, colors.ENDC))
    else:
        print('%s%s%s' % (colors.FAIL, error, colors.ENDC))
    return fileStamp

def delorigfile(file):
    origFile = '{}/{}'.format(captureFolder, file)
    if os.path.isfile(origFile):
        try:
            os.remove(origFile)
        except OSError as e:
            MSG = "Error: %s - %s." % (e.filename, e.strerror)
            print('%s%s%s' % (colors.FAIL, MSG, colors.ENDC))

colorama.init()

root = os.getcwd()

DEBUG = False

print('%s%s%s' % (colors.OKGREEN, root, colors.ENDC))

logDosyaAdi = 'Pdf2Pacs.log'
logging.basicConfig(filename=logDosyaAdi, level=logging.DEBUG)
logging.info('Timestamp: %s', dt.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

captureFolder = 'rapor'
tempFolder = 'Temp'
backlogFolder = 'backlog'
dcmtk = 'Util/dcmtk/bin'
jpegDensity = '150'
print("Root: {}".format(root))
print("Capture folder: /{}".format(captureFolder))


DICOM, PACS, TAGS_SINGLE = getsettings('Settings.ini')

STUDY = dict()

MSG = 'Waiting for incoming data in folder: /%s' % captureFolder
print('%s%s%s' % (colors.HEADER, MSG, colors.ENDC))

while True:
    files = next(os.walk(captureFolder + '/'))[2]
    if DEBUG: print(files)
    if files:
        for file in files:
            if file.endswith('pdf'):
                MSG = 'Found new pdf file...'
                print('%s%s%s' % (colors.BOLD, MSG, colors.ENDC))
                fileStamp = process(file)
                if DEBUG: print('Created filestamp: %s' % fileStamp)
                dicomtk.decompressJpegs(dcmtk, tempFolder, fileStamp)
                dicomtk.sendtopacs(root, dcmtk, tempFolder, fileStamp, PACS, TAGS_SINGLE)
                delorigfile(file)
    else:
        print('.'),
    sleep(5)

