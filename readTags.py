# -*- coding: utf-8 -*-

from datetime import date, datetime

def readTagFile(file):
    with open(file, 'r') as infile:
        data = infile.read()
    return data.splitlines()

def getProcedure(str, splitter):
    return str[:str.find(splitter)]

def getExamDate(str, splitter):
    examDate = str[len(splitter)+ str.find(splitter):]
    return datetime.strptime(examDate, '%m/%d/%Y %I:%M %p')

def getDicomDateTime(str, splitter):
    examDate_object = getExamDate(str, splitter)
    dicomExamDate = examDate_object.strftime('%Y%m%d')
    dicomExamTime = examDate_object.strftime('%H%M%S')
    return dicomExamDate, dicomExamTime

def getPatSex(str):
    return str[:1]

def getPatName(str):
    name = str.replace(', ', '^')
    return name.replace(' ', '^')

def getPatID(str):
    return str

def getPatAge(str, splitter):
    index = str.find(splitter)
    age = str[:index]
    yearMonthorDays =  str[index+1:index+2]
    dicomAge = '00' + age + yearMonthorDays.upper()
    return dicomAge[-4:] # Dicom standardı gereği dört basamak döndür

