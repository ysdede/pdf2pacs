# -*- coding: utf-8 -*-

from __future__ import division
import sys

try:
    import os.path
    import datetime as dt
    from datetime import date, datetime, timedelta
    import time
    import pdf2txt3, readTags, dicomtk
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


def process(file):
    origFile = 'rapor/{}'.format(file)
    print ': {}, '.format(origFile)
    fileStamp = getSHA1(origFile)
    tagFile = 'Temp/{}.tags'.format(fileStamp)
    backlogFile = "backlog/{}.pdf".format(fileStamp)

    if not os.path.isfile(backlogFile):
        shutil.copyfile(file, backlogFile)
        print 'Backlog kopyalandı: {}'.format(backlogFile)
    else:
        print 'Dosya Backlogda mevcut: {}'.format(backlogFile)

    pdf2txt3.extTxt(origFile, tagFile)
    pdf2Jpeg(backlogFile, fileStamp)
    error = dicomtk.createDicom(fileStamp, tagFile, DICOM, TAGS_SINGLE)
    if error == "":
        print "Dicom object created"
    else:
        print(error)
    return fileStamp

def delorigfile(file):
    origFile = 'rapor/{}'.format(file)
    if os.path.isfile(origFile):
        try:
            os.remove(origFile)
        except OSError as e:
            print ("Error: %s - %s." % (e.filename, e.strerror))

logDosyaAdi = 'Pdf2Pacs.log'
logging.basicConfig(filename=logDosyaAdi, level=logging.DEBUG)
logging.info('Çalışma Zamanı: %s', dt.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

DICOM, PACS, TAGS_SINGLE = getsettings('Settings.ini')

while True:
    files = next(os.walk('rapor/'))[2]
    if files:
        for file in files:
            if file.endswith('pdf'):
                print('Rapor dosyası bulundu'),
                fileStamp = process(file)
                dicomtk.sendtopacs(fileStamp, PACS, TAGS_SINGLE)
                delorigfile(file)
    else:
        print('Yeni dosya yok')
    sleep(10)
