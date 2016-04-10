# -*- coding: cp1254 -*-

from __future__ import division
import sys

try:
    import os.path
    import datetime as dt
    from datetime import date, datetime, timedelta
    import time
    import pdf2txt3, readTags
    from time import sleep
    import os, ConfigParser, subprocess
    import shutil, errno
    import subprocess, logging
    import hashlib
except Exception as e:
    print ('Modül yüklenemedi.')
    sys.exit(2)


def getsettings(ayar_dosyasi):
    logging.info('Ayar dosyası: %s', ayar_dosyasi)
    config = ConfigParser.RawConfigParser()
    config.read(ayar_dosyasi)
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
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    # md5 = hashlib.md5()
    sha1 = hashlib.sha1()

    with open(fileName, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            # md5.update(data)
            sha1.update(data)
    return sha1.hexdigest()


def pdf2Jpeg(infile, outfile):
    folder = 'Temp/{}'.format(outfile)
    if not os.path.exists(folder):
        os.mkdir(folder, 0755)
    command = """"Util/ImageMagic/convert.exe" -density 150 {} {}/Page%02d.jpg""".format(infile, folder)
    print (command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()


def createDicom(fileStamp, tagFile, DICOM, PACS, TAGS_SINGLE):
    jpegPath = 'Temp/{}/'.format(fileStamp)
    firstPage = True
    files = next(os.walk(jpegPath))[2]
    if files:
        print('JPEG dosyalar bulundu:')
        for file in files:
            if file.endswith('jpg'):
                print file
                tagData = readTags.readTagFile(tagFile)
                patName = readTags.getPatName(tagData[TAGS_SINGLE['PatName']])
                patID = readTags.getPatID(tagData[TAGS_SINGLE['PatID']])
                patSex = readTags.getPatSex(tagData[TAGS_SINGLE['PatSex']])
                patAge = readTags.getPatAge(tagData[TAGS_SINGLE['PatAge']], ' ')
                procedure = readTags.getProcedure(tagData[TAGS_SINGLE['Procedure']],TAGS_SINGLE['ProcExamSplitter'])
                examDate, examTime = readTags.getDicomDateTime(tagData[TAGS_SINGLE['ExamDate']],TAGS_SINGLE['ProcExamSplitter'])

                img2dcmCommand = \
'Util/dcmtk/bin/img2dcm -i JPEG -l1 --do-checks +i1 +i2 -ll info {}{} {}{}.dcm -k 0010,0010="{}" \
-k 0010,1010="{}" -k 0008,0060="{}" -k 0008,0021="{}" -k 0008,0022="{}" -k 0008,0023="{}" \
-k 0010,0020="{}" -k 0010,0040="{}" -k 0008,0016="{}" -k 0008,0020="{}" -k 0008,0030="{}"  \
-k 0008,1030="{}" -k 0008,103E="{}" -k 0008,0005="{}" -k 0008,0031="{}" -k 0008,0032="{}" \
-k 0008,0033="{}" -k 0008,0070="{}" -k 0008,1090="{}" -k 0008,0080="{}" -k 0008,0081="{}" \
-k 0008,1040="{}" -k 0018,1000="{}" -k 0018,1016="{}" -k 0018,1018="{}" -k 0018,1019="{}"'.format(\
                    jpegPath, file, jpegPath, file, patName, patAge, DICOM['Modality'], examDate, examDate, examDate, patID, patSex, \
                    DICOM['SOPClassUID'], examDate, examTime, procedure, DICOM['SeriesDescription'], DICOM['CharacterSet'], \
                    examTime, examTime, examTime, DICOM['Manufacturer'], DICOM['ManufacturersModelName'], DICOM['InstitutionName'],\
                    DICOM['InstitutionAddress'], DICOM['DepartmentName'], DICOM['DeviceSerialNumber'],\
                    DICOM['SecondaryCaptureDeviceManufacturer'], DICOM['SecondaryCaptureDeviceModel'], \
                    DICOM['SecondaryCaptureDeviceSoftwareVersion'])

                print img2dcmCommand


logDosyaAdi = 'Pdf2Pacs.log'
logging.basicConfig(filename=logDosyaAdi, level=logging.DEBUG)
logging.info('Çalışma Zamanı: %s', dt.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

DICOM, PACS, TAGS_SINGLE = getsettings('Settings.ini')
print DICOM
print '****************'
print PACS
print '****************'
print TAGS_SINGLE

while (True):
    files = next(os.walk('rapor/'))[2]
    if files:
        print('Dosyalar bulundu'),
        for file in files:
            if file.endswith('pdf'):
                origFile = 'rapor/{}'.format(file)
                print ': {}, '.format(origFile)
                fileStamp = getSHA1(origFile)
                tagFile = 'Temp/{}.tags'.format(fileStamp)
                backlogFile = "backlog/{}.pdf".format(fileStamp)

                if not os.path.isfile(backlogFile):
                    shutil.copyfile(file, backlogFile)
                    print 'Backlog kopyalandı: {}'.format(backlogFile)
                else: print 'Dosya Backlogda mevcut: {}'.format(backlogFile)

                pdf2txt3.extTxt(origFile, tagFile)
                pdf2Jpeg(backlogFile, fileStamp)
                createDicom(fileStamp, tagFile,DICOM, PACS, TAGS_SINGLE)


                if os.path.isfile(origFile):
                    try:
                        os.remove(origFile)
                    except OSError, e:
                        print ("Error: %s - %s." % (e.filename, e.strerror))

    else:
        print('Yeni dosya yok')
    sleep(20)
