from __future__ import print_function
import sys
import tkinter
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
import time
import datetime
from cb_idcheck import cb_onfido
from pprint import pprint
import csv
import collections
from cb_idcheck.statusbar import statusbar
import argparse
import os
from cb_idcheck.idcheck_config import idcheck_config
from pprint import pprint

class idcheck:
    def parse_args(self, argv=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('--gui', required=False, type=bool, help="Use a data entry graphical user interface? Default=False", default=False)
        parser.add_argument('--token', required=False, type=str, help="Onfido API token. Default=$CB_IDCHECK_API_TOKEN", default=os.environ.get('CB_IDCHECK_API_TOKEN', 'No key'))
        parser.add_argument('--keys', required=False, type=str, help="A file containing a list of the applicant's public keys, as generated by the Commerceblock Ocean wallet.", default=None)
        parser.add_argument('--first_name', required=False, type=str, help="Applicant's first name.", default="")
        parser.add_argument('--last_name', required=False, type=str, help="Applicant's last name. Default=None", default="")
        parser.add_argument('--dob_year', required=False, type=str, help="Applicant's year of birth: YYYY. Default=0001", default="0001")
        parser.add_argument('--dob_month', required=False, type=str, help="Applicant's month of birth: MM. Default=01", default="01")
        parser.add_argument('--dob_day', required=False, type=str, help="Applicant's day of birth: DD. Default=01", default="01")
        parser.add_argument('--idDocType', required=False, type=str, help="ID document type. One of: passport, national_identity_card, driving_licence, uk_biometric_residence_permit, tax_id, voter_id. Default=passport", default="passport")
        parser.add_argument('--idDocSide1', required=False, type=str, help="Side1 of ID document as a path to a file containing a jpg or png formatted image. Default=None", default=None)
        parser.add_argument('--idDocSide2', required=False, type=str, help="Side2 of ID document, if document is 2-sided as a path to a file containing a jpg or png formatted image. Default=None", default=None)
        parser.add_argument('--photo', required=False, type=str, help="Live photo of applicant as a path to a file containing a jpg or png formatted image. Default=None", default=None)

        args = parser.parse_args(argv)
        self.token = args.token
        self.gui = args.gui
        self.setApplicant(args.first_name, args.last_name, args.dob_year, args.dob_month, args.dob_day)
        self.setIDDocument(args.idDocType, args.idDocSide1, args.idDocSide2)
        self.setPhoto(args.photo)
        self.importKeys(args.keys)


    def __init__(self, token=None, master=None):
        self.token=token
        self.master=master
        self.title="CommerceBlock ID check"
        self.keys=[]
        self.progress_value=0
        self.id_api=cb_onfido.cb_onfido()
        # create an instance of the API class                                                                                                                                                     
        self.api_instance=self.id_api.api_instance
        self.applicant=self.id_api.onfido.Applicant()
        self.applicant.country='GBR' #This is the jurisdiction where the ID check takes place, not the applicant's home country.
        self.address=self.id_api.onfido.Address()
        self.cfg=idcheck_config(self.id_api.onfido.CheckCreationRequest(async=True))

        #1 is both sides are required. 0 otherwise.
        self.docTypeSides={"passport": 0, 
                       "national_identity_card":1, 
                       "driving_licence":1, 
                       "uk_biometric_residence_permit":1, 
                       "tax_id":0, 
                       "voter_id":1
                       }
        self.docTypes=list(self.docTypeSides.keys())
        


    def run(self):
        frameStatus = Frame(self.master)
        frameStatus.pack(side=BOTTOM, fill=X)
        self.status=statusbar(frameStatus)        

        frameProgress = Frame(self.master)
        frameProgress.pack(side=BOTTOM, fill=X)
        self.progress=Progressbar(frameProgress, orient='horizontal', mode='indeterminate', value=self.progress_value) 
        self.progress.pack(side=LEFT, fill=BOTH, expand=1)

        frameTitle = Frame(self.master)
        frameTitle.pack()
        self.listboxTitle =Listbox(frameTitle, selectmode=EXTENDED, exportselection=0, height=1)
        self.listboxTitle.delete(0,END)
        size=0
        for item in ["Miss", "Mr", "Mrs", "Ms"]:
            self.listboxTitle.insert(END,item)
            size=size+1
        self.listboxTitle.selection_set(1)
        self.listboxTitle.config(height=size)
        self.listboxTitle.pack(side=LEFT)
        labelTitle = Label(frameTitle, text='Title')
        labelTitle.pack(side=LEFT)

        frameFirstName = Frame(self.master)
        frameFirstName.pack()
        self.entryFirstName = Entry(frameFirstName)
        self.entryFirstName.pack(side=LEFT)
        self.entryFirstName.insert(0,"John")
        labelFirstName = Label(frameFirstName, text='First name')
        labelFirstName.pack(side=LEFT)

        frameMiddleName = Frame(self.master)
        frameMiddleName.pack()
        self.entryMiddleName = Entry(frameMiddleName)
        self.entryMiddleName.pack(side=LEFT)
        self.entryMiddleName.insert(0,"Edward")
        labelMiddleName = Label(frameMiddleName, text='Middle name')
        labelMiddleName.pack(side=LEFT)

        frameLastName = Frame(self.master)
        frameLastName.pack()
        self.entryLastName = Entry(frameLastName)
        self.entryLastName.pack(side=LEFT)
        self.entryLastName.insert(0,"Smith")
        labelLastName = Label(frameLastName, text='Last name')
        labelLastName.pack(side=LEFT)
        
        frameGender = Frame(self.master)
        frameGender.pack()
        self.listboxGender = Listbox(frameGender, exportselection=0)
        self.listboxGender.delete(0,END)
        size=0
        for item in ["male", "female"]:
            self.listboxGender.insert(END,item)
            size=size+1
        self.listboxGender.selection_set(0)
        self.listboxGender.config(height=size)
        self.listboxGender.pack(side=LEFT)
        labelGender = Label(frameGender, text='Gender')
        labelGender.pack(side=LEFT)

        frameDOB = Frame(self.master)
        frameDOB.pack()
        self.entryDay = Entry(frameDOB, width=2)
        self.entryDay.pack(side=LEFT)
        self.entryDay.insert(0,24)
        self.entryMonth = Entry(frameDOB, width=2)
        self.entryMonth.pack(side=LEFT)
        self.entryMonth.insert(0,12)
        self.entryYear = Entry(frameDOB, width=4)
        self.entryYear.pack(side=LEFT)
        self.entryYear.insert(0,1975)
        labelDOB = Label(frameDOB, text='Date of birth: DD MM YYYY')
        labelDOB.pack(side=LEFT)


        #A entry box for each side of the ID documentt
        frameIDDoc1 = Frame(self.master)
        frameIDDoc1.pack()
        self.entryIDDoc1 = Entry(frameIDDoc1, width=25)
        self.entryIDDoc1.pack(side=LEFT)
        self.entryIDDoc1.insert(0,"/Users/lawrence/Projects/ocean_idcheck/ticketFront.jpg")
        buttonIDDocFileOpen1 = Button(frameIDDoc1, text='ID document front', command=self.openIDDocFile1)
        buttonIDDocFileOpen1.pack(side=LEFT)

        frameIDDoc2 = Frame(self.master)
        frameIDDoc2.pack()
        self.entryIDDoc2 = Entry(frameIDDoc2, width=25)
        self.entryIDDoc2.pack(side=LEFT)
        self.entryIDDoc2.insert(0,"/Users/lawrence/Projects/ocean_idcheck/ticketBack.jpg")
        buttonIDDocFileOpen2 = Button(frameIDDoc2, text='ID document back', command=self.openIDDocFile2)
        buttonIDDocFileOpen2.pack(side=LEFT)

        frameIDDocType = Frame(self.master)
        frameIDDocType.pack()
        self.listboxIDDocType = Listbox(frameIDDocType, exportselection=0)
        self.listboxIDDocType.delete(0,END)
        size=0
        for item in self.docTypes:
            self.listboxIDDocType.insert(END,item)
            size=size+1
        self.listboxIDDocType.selection_set(0)
        self.listboxIDDocType.config(height=size)
        self.listboxIDDocType.pack(side=LEFT)
        labelIDDocType = Label(frameIDDocType, text='ID document type')
        labelIDDocType.pack(side=LEFT)

        framePhoto = Frame(self.master)
        framePhoto.pack()
        self.entryPhoto = Entry(framePhoto, width=25)
        self.entryPhoto.pack(side=LEFT)
        self.entryPhoto.insert(0,"/Users/lawrence/Projects/ocean_idcheck/testPicture.png")
        buttonPhotoFileOpen = Button(framePhoto, text='Live photo', command=self.openPhotoFile)
        buttonPhotoFileOpen.pack(side=LEFT)

        
#       labelAddress = Label(self.master, text='Address')
#       labelAddress.pack()
#        frameBuildingNo = Frame(self.master)
#        frameBuildingNo.pack()
#        self.entryBuildingNo = Entry(frameBuildingNo)
#        self.entryBuildingNo.pack(side=LEFT)
#        self.entryBuildingNo.insert(0,"10")
#        labelBuildingNo = Label(frameBuildingNo, text='Building number')
#        labelBuildingNo.packside=LEFT)
#        frameStreet = Frame(self.master)
#        frameStreet.pack()
#        self.entryStreet = Entry(frameStreet)
#        self.entryStreet.pack(side=LEFT)
#        self.entryStreet.insert(0,"Main Street")
#        labelStreet = Label(frameStreet, text='Street')
#        labelStreet.pack(side=LEFT)
#        frameTown = Frame(self.master)
#        frameTown.pack()
#        self.entryTown = Entry(frameTown)
#        self.entryTown.pack(side=LEFT)
#        self.entryTown.insert(0,"London")
#        labelTown = Label(frameTown, text='Town')
#        labelTown.pack(side=LEFT)
#        framePostcode = Frame(self.master)
#        framePostcode.pack()
#        self.entryPostcode = Entry(framePostcode)
#        self.entryPostcode.pack(side=LEFT)
#        self.entryPostcode.delete(0,END)
#        self.entryPostcode.insert(0,"SW4 6EH")
#        labelPostcode = Label(framePostcode, text='Postcode')
#        labelPostcode.pack(side=LEFT)
#        frameCountry = Frame(self.master)
#        frameCountry.pack()
#        self.entryCountry = Entry(frameCountry)
#        self.entryCountry.pack(side=LEFT)
#        self.entryCountry.delete(0,END)
#        self.entryCountry.insert(0,"GBR")
#        labelCountry = Label(frameCountry, text='Country')
#        labelCountry.pack(side=LEFT)

        frameKeyFile = Frame(self.master)
        frameKeyFile.pack()
        self.entryKeyFile = Entry(frameKeyFile, width=25)
        self.entryKeyFile.pack(side=LEFT)
        self.entryKeyFile.insert(0,"/Users/lawrence/Projects/ocean-demo/keys.client")
        buttonKeyFileOpen = Button(frameKeyFile, text='Key file', command=self.openKeyFile)
        buttonKeyFileOpen.pack(side=LEFT)

        self.status.pack(side=BOTTOM, fill=X)

        frameSubmit = Frame(self.master)
        frameSubmit.pack(side=BOTTOM, fill=X)
        buttonSubmit = Button(frameSubmit, text='Submit ID check', command=self.submitFromGUI)
        buttonSubmit.pack(side=RIGHT)

    #Enter applicant data 
    def setApplicant(self, first_name, last_name, dob_year, dob_month, dob_day):
        self.applicant.first_name=first_name
        self.applicant.last_name=last_name
        self.applicant.dob=datetime.date(year=int(dob_year),month=int(dob_month),day=int(dob_day))
                       
    #Fill applicant data from GUI
    def fillApplicant(self):
        self.setApplicant(first_name = self.entryFirstName.get(), 
                       last_name = self.entryLastName.get(), 
                       dob_year=self.entryYear.get(),
                       dob_month=self.entryMonth.get(),
                       dob_day=self.entryDay.get())
#Not using addresses
#    def fillAddress(self):
#        self.address.building_number=self.entryBuildingNo.get()
#        self.address.street=self.entryStreet.get()
#        self.address.town=self.entryTown.get()
#        self.address.postcode=self.entryPostcode.get()
#        self.address.country=self.entryCountry.get()
#        self.applicant.addresses=[self.address]

    def setIDDocument(self, idDocType="passport", idDocSide1File="", idDocSide2File=""):
        self.idDocType=idDocType
        self.idDoc2Sided=(self.docTypeSides[self.idDocType] == 1),
        self.idDocSide1File=idDocSide1File
        self.idDocSide2File=idDocSide2File

    def fillIDDocument(self):
        self.setIDDocument(idDocType=self.docTypes[self.listboxIDDocType.curselection()[0]],
                           idDocSide1File=self.entryIDDoc1.get(),
                           idDocSide2File=self.entryIDDoc2.get())           
            
    def uploadIDDocument(self):
        self.printStatus("Uploading id document...")
        api_response = []
        api_response.append(self.api_instance.upload_document(self.applicant.id, self.idDocType, side="front", file=self.idDocSide1File))
        if (self.idDoc2Sided==True):
            api_response.append(self.api_instance.upload_document(self.applicant.id, self.idDocType, side="back", file=self.idDocSide2File))
        self.printStatus("...id document upload complete.")
        return api_response

    def setPhoto(self, photoFile):
        self.photoFile=photoFile

    def fillPhoto(self):
        self.setPhoto(photoFile=self.entryPhoto.get())

    def uploadPhoto(self):
        self.printStatus("Uploading live photo...")
        api_response = self.api_instance.upload_live_photo(applicant_id=self.applicant.id, file=self.photoFile, advanced_validation=True)
        self.printStatus("...live photo upload complete.")
        return api_response

    def printStatus(self, msg):
        if self.gui is True:
            self.status.set(msg)
        print(msg)

    def openphoto(self, entry):
        fileOpened = filedialog.askopenfilename(initialdir = "/", title = "Select file", filetypes = (("jpg files","*.jpg"),("png files","*.png"),("pdf files","*.pdf")))
        entry.delete(0,END)
        entry.insert(0,fileOpened)

    def openIDDocFile1(self):
        self.openphoto(self.entryIDDoc1)
  
    def openIDDocFile2(self):
        self.openphoto(self.entryIDDoc2) 

    def openPhotoFile(self):
        self.openphoto(self.entryPhoto) 

    def openKeyFile(self,entry=None):
        if(entry==None):
            entry=self.entryKeyFile
        fileOpened = filedialog.askopenfilename(initialdir = "/", title = "Select key file")
        entry.delete(0,END)
        entry.insert(0,fileOpened)

    def fillKeys(self):
        self.importKeys(keyFile=self.entryKeyFile.get())

    def importKeys(self, keyFile):
        if keyFile is None:
            return
        with open(keyFile,'rt') as csvfile:
            #                keyReader = csv.reader(csvfile, delimiter=' ')
            myDialect = csv.excel
            myDialect.delimiter=' '
            dictReader = csv.DictReader(filter(lambda row: row[0]!='#', csvfile), fieldnames=['tweaked_address', 'untweaked_public_key'],dialect=myDialect)
            for row in dictReader:
                self.keys = self.keys+[row['tweaked_address'], row['untweaked_public_key']]
            self.cfg.check.tags=self.keys

    def submitFromGUI(self):
        self.fillDataFromGUI()
        self.submit()

    def fillDataFromGUI(self):
        self.fillApplicant()
#        self.fillAddress()
        self.fillIDDocument()
        self.fillPhoto()
        self.fillKeys()

    def submit(self):
        if self.gui is True:
            self.progress.start()
        self.printStatus("Submitting...")
        try:
            api_response = self.api_instance.create_applicant(data=self.applicant)
            self.applicant.id=api_response.id
            api_response=self.uploadIDDocument()
            api_response=self.uploadPhoto()
            api_response=self.api_instance.create_check(self.applicant.id, data=self.cfg.check)
            self.printStatus("Submission complete.")
            time.sleep(1)
            self.master.quit()
        except cb_onfido.ApiException as e:
            pprint(e.body)
            self.printStatus("Error: " + e.body)
        if self.gui is True:
            self.progress.stop()

    def __str__(self):
        print ("Applicant:")
        pprint(idc.applicant)
        print("Check:")
        pprint(idc.check)

 


if __name__ == "__main__":
    from cb_idcheck import idcheck
    root = tkinter.Tk()
    idc=idcheck.idcheck(master=root)
    idc.parse_args()
    if idc.gui is True:
        root.title(idc.title)
        idc.run()
        root.mainloop()            
    else:
        idc.submit()




    



