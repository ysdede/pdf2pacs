#!c:\python27\python.exe
import sys
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter

# main
def main(argv):
	# debug option
	debug = 0
	# input option
	password = ''
	pagenos = set()
	maxpages = 0
	# output option
	outfile = None
	outtype = None
	imagewriter = None
	rotation = 0
	layoutmode = 'normal'
	codec = 'utf-8'
	pageno = 1
	scale = 1
	caching = True
	showpageno = True
	#'-d': debug += 1
	laparams = LAParams()
	laparams.line_margin = float(30)
	laparams.word_margin = float(0.1)
	#'-n': laparams = None
	#'-A': laparams.all_texts = True
	#'-V': laparams.detect_vertical = True
	#'-M': laparams.char_margin = float(v)
	#'-F': laparams.boxes_flow = float(v)
	#'-Y': layoutmode = v
	#
	PDFDocument.debug = debug
	PDFParser.debug = debug
	CMapDB.debug = debug
	PDFResourceManager.debug = debug
	PDFPageInterpreter.debug = debug
	PDFDevice.debug = debug
	#
	rsrcmgr = PDFResourceManager(caching=caching)
	
	outtype = 'text'
		
	if outfile:
		outfp = file(outfile, 'w')
	else:
		outfp = sys.stdout
		
	if outtype == 'text':
		device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
							   imagewriter=imagewriter)
	fname = 'SAMPLE/sample.pdf'	   
	
	fp = file(fname, 'rb')
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	for page in PDFPage.get_pages(fp, pagenos,
								  maxpages=maxpages, password=password,
								  caching=caching, check_extractable=True):
		page.rotate = (page.rotate+rotation) % 360
		interpreter.process_page(page)
	fp.close()
	device.close()
	outfp.close()
	return

if __name__ == '__main__': sys.exit(main(sys.argv))
