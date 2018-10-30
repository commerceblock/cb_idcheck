from __future__ import print_function
import sys
from tkinter import *
import tkinter as tk
import time
import datetime
from cb_idcheck import cb_onfido
from pprint import pprint
import csv
import collections
from cb_idcheck.statusbar import statusbar
import argparse
import os

class idcheck:
    def parse_args(self, argv=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('--token', required=False, type=str, help="Webhook token. Default=$CB_IDCHECK_API_TOKEN", default=os.environ.get('CB_IDCHECK_API_TOKEN', 'No key'))
        args = parser.parse_args(argv)
        self.token = args.token

    def __init__(self, master):
        self.master=master
        self.title="CommerceBlock ID check"
        self.keys=[]

    def run(self):
        self.id_api=cb_onfido.cb_onfido()
        # create an instance of the API class                                                                                                                                                     
        self.api_instance=self.id_api.api_instance
        self.applicant=self.id_api.onfido.Applicant()
        self.address=self.id_api.onfido.Address()
        self.check=self.id_api.onfido.CheckCreationRequest(async=True)
        self.check.type='express'
        self.report=self.id_api.onfido.Report()
#        self.report.name='identity'
        self.report.name='document'
        self.check.reports=[self.report]

        frameStatus = Frame(self.master)
        frameStatus.pack(side=BOTTOM, fill=X)
        self.status=statusbar(frameStatus)        

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


        #A entry box for each side of the ID document
        frameIDDoc1 = Frame(self.master)
        frameIDDoc1.pack()
        self.entryIDDoc1 = Entry(frameIDDoc1, width=25)
        self.entryIDDoc1.pack(side=LEFT)
        self.entryIDDoc1.insert(0,"/Users/lawrence/Projects/ocean_idcheck/testPicture.png")
        buttonIDDocFileOpen1 = Button(frameIDDoc1, text='ID document front', command=self.openIDDocFile1)
        buttonIDDocFileOpen1.pack(side=LEFT)

        frameIDDoc2 = Frame(self.master)
        frameIDDoc2.pack()
        self.entryIDDoc2 = Entry(frameIDDoc2, width=25)
        self.entryIDDoc2.pack(side=LEFT)
        self.entryIDDoc2.insert(0,"/Users/lawrence/Projects/ocean_idcheck/testPicture.png")
        buttonIDDocFileOpen2 = Button(frameIDDoc2, text='ID document back', command=self.openIDDocFile2)
        buttonIDDocFileOpen2.pack(side=LEFT)

        frameIDDocType = Frame(self.master)
        frameIDDocType.pack()
        self.listboxIDDocType = Listbox(frameIDDocType, exportselection=0)
        self.listboxIDDocType.delete(0,END)
        size=0
        #1 is both sides are required. 0 otherwise.
        self.docTypeSides={"passport": 0, 
                       "national_identity_card":1, 
                       "driving_licence":1, 
                       "uk_biometric_residence_permit":1, 
                       "tax_id":0, 
                       "voter_id":1
                       }
        self.docTypes=list(self.docTypeSides.keys())
        
        for item in self.docTypes:
            self.listboxIDDocType.insert(END,item)
            size=size+1
        self.listboxIDDocType.selection_set(0)
        self.listboxIDDocType.config(height=size)
        self.listboxIDDocType.pack(side=LEFT)
        labelIDDocType = Label(frameIDDocType, text='ID document type')
        labelIDDocType.pack(side=LEFT)

#        framePhoto = Frame(self.master)
#        framePhoto.pack()
#        self.entryPhoto = Entry(framePhoto, width=25)
#        self.entryPhoto.pack(side=LEFT)
#        self.entryPhoto.insert(0,"/Users/lawrence/Projects/ocean_idcheck/testPicture.png")
#        buttonPhotoFileOpen = Button(framePhoto, text='Photo', command=self.openPhotoFile)
#        buttonPhotoFileOpen.pack(side=LEFT)
        
        labelAddress = Label(self.master, text='Address')
        labelAddress.pack()
        frameBuildingNo = Frame(self.master)
        frameBuildingNo.pack()
        self.entryBuildingNo = Entry(frameBuildingNo)
        self.entryBuildingNo.pack(side=LEFT)
        self.entryBuildingNo.insert(0,"10")
        labelBuildingNo = Label(frameBuildingNo, text='Building number')
        labelBuildingNo.pack(side=LEFT)
        frameStreet = Frame(self.master)
        frameStreet.pack()
        self.entryStreet = Entry(frameStreet)
        self.entryStreet.pack(side=LEFT)
        self.entryStreet.insert(0,"Main Street")
        labelStreet = Label(frameStreet, text='Street')
        labelStreet.pack(side=LEFT)
        frameTown = Frame(self.master)
        frameTown.pack()
        self.entryTown = Entry(frameTown)
        self.entryTown.pack(side=LEFT)
        self.entryTown.insert(0,"London")
        labelTown = Label(frameTown, text='Town')
        labelTown.pack(side=LEFT)
        framePostcode = Frame(self.master)
        framePostcode.pack()
        self.entryPostcode = Entry(framePostcode)
        self.entryPostcode.pack(side=LEFT)
        self.entryPostcode.delete(0,END)
        self.entryPostcode.insert(0,"SW4 6EH")
        labelPostcode = Label(framePostcode, text='Postcode')
        labelPostcode.pack(side=LEFT)
        frameCountry = Frame(self.master)
        frameCountry.pack()
        self.entryCountry = Entry(frameCountry)
        self.entryCountry.pack(side=LEFT)
        self.entryCountry.delete(0,END)
        self.entryCountry.insert(0,"GBR")
        labelCountry = Label(frameCountry, text='Country')
        labelCountry.pack(side=LEFT)

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
        buttonSubmit = Button(frameSubmit, text='Submit', command=self.submit)
        buttonSubmit.pack(side=RIGHT)


    def fillApplicant(self):
        self.applicant.first_name = self.entryFirstName.get()
        self.applicant.last_name = self.entryLastName.get()
        self.applicant.dob=datetime.date(int(self.entryYear.get()), int(self.entryMonth.get()), int(self.entryDay.get()))
        self.applicant.country='GBR' #This is the jurisdiction where the ID check takes place, not the applicant's home country.
            
    def fillAddress(self):
        self.address.building_number=self.entryBuildingNo.get()
        self.address.street=self.entryStreet.get()
        self.address.town=self.entryTown.get()
        self.address.postcode=self.entryPostcode.get()
        self.address.country=self.entryCountry.get()
        self.applicant.addresses=[self.address]

    def fillIDDocument(self):
        print(self.listboxIDDocType.curselection()[0])
        self.idDocType=self.docTypes[self.listboxIDDocType.curselection()[0]]
        self.idDoc2Sided=(self.docTypeSides[self.idDocType] == 1)
        self.idDocSide1File=self.entryIDDoc1.get()
        self.idDocSide2File=self.entryIDDoc2.get()
            
    def uploadIDDocument(self):
        self.status.set("Uploading id document...")
        api_response = []
        api_response.append(self.api_instance.upload_document(self.applicant.id, self.idDocType, side="front", file=self.idDocSide1File))
        if (self.idDoc2Sided==True):
            api_response.append(self.api_instance.upload_document(self.applicant.id, self.idDocType, side="back", file=self.idDocSide2File))
        self.status.set("...id document upload complete.")
        return api_response
                
    def fillKeys(self):
        self.check.tags=self.keys
            
    def submit(self):
        self.status.set("Submitting...")
        self.fillApplicant()
        self.fillAddress()
        self.fillIDDocument()
        self.loadKeys()
        self.fillKeys()
        try:
            api_response = self.api_instance.create_applicant(data=self.applicant)
            self.applicant.id=api_response.id
            api_response=self.uploadIDDocument()
            api_response=self.api_instance.create_check(self.applicant.id, data=self.check)
        except cb_onfido.ApiException as e:
            pprint(e.body)
            self.status.set("Error: " + e.body)

 
    def openIDDocFile1(self):
        openphoto(self, self.entryIDDoc1)
  
    def openIDDocFile2(self):
        openphoto(self, self.entryIDDoc2) 

    def openPhotoFile(self):
        openphoto(self, self.entryPhoto) 

    def openphoto(self, entry):
        fileOpened = filedialog.askopenfilename(initialdir = "/", title = "Select file", filetypes = (("jpg files","*.jpg"),("png files","*.png"),("pdf files","*.pdf")))
        entry.delete(0,END)
        entry.insert(0,fileOpened)

    def openKeyFile(self,entry):
        fileOpened = filedialog.askopenfilename(initialdir = "/", title = "Select key file", filetypes = (("all files","*.*")))
        entry.delete(0,END)
        entry.insert(0,fileOpened)

    def openKeyFile(self):
        openKeyFile(self, self.entryKey)
            
    def loadKeys(self):
        with open(self.entryKeyFile.get(),'rt') as csvfile:
            #                keyReader = csv.reader(csvfile, delimiter=' ')
            myDialect = csv.excel
            myDialect.delimiter=' '
            dictReader = csv.DictReader(filter(lambda row: row[0]!='#', csvfile), fieldnames=['tweaked_address', 'untweaked_public_key'],dialect=myDialect)
            for row in dictReader:
                self.keys = self.keys+[row['tweaked_address'], row['untweaked_public_key']]

if __name__ == "__main__":
    from cb_idcheck import idcheck
    root = tk.Tk()
    idc=idcheck.idcheck(root)
    idc.parse_args()
    root.title(idc.title)
    idc.run()
    root.mainloop()            



    



