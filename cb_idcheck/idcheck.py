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
from cb_idcheck import statusbar
from cb_idcheck import cbmagic

class idcheck:
    def __init__(self, master):
        self.title="CommerceBlock ID check"
        keys=[]

        self.id_api=cb_onfido.cb_onfido()

        # create an instance of the API class                                                                                                                                                     
        self.api_instance=self.id_api.api_instance
        self.applicant=self.id_api.onfido.Applicant()
        self.address=self.id_api.onfido.Address()
        self.check=self.id_api.onfido.CheckCreationRequest()
        self.check.type='express'
        self.report=self.id_api.onfido.Report()
        self.report.name='identity'
        self.check.reports=[self.report]

        frameStatus = Frame(master)
        frameStatus.pack(side=BOTTOM, fill=X)
        status=statusbar.statusbar(frameStatus)        

        frameTitle = Frame(master)
        frameTitle.pack()
        listboxTitle =Listbox(frameTitle, selectmode=EXTENDED, exportselection=0, height=1)
        listboxTitle.delete(0,END)
        size=0
        for item in ["Miss", "Mr", "Mrs", "Ms"]:
            listboxTitle.insert(END,item)
            size=size+1
        listboxTitle.selection_set(1)
        listboxTitle.config(height=size)
        listboxTitle.pack(side=LEFT)
        labelTitle = Label(frameTitle, text='Title')
        labelTitle.pack(side=LEFT)

        frameFirstName = Frame(master)
        frameFirstName.pack()
        entryFirstName = Entry(frameFirstName)
        entryFirstName.pack(side=LEFT)
        entryFirstName.insert(0,"John")
        labelFirstName = Label(frameFirstName, text='First name')
        labelFirstName.pack(side=LEFT)

        frameMiddleName = Frame(master)
        frameMiddleName.pack()
        entryMiddleName = Entry(frameMiddleName)
        entryMiddleName.pack(side=LEFT)
        entryMiddleName.insert(0,"Edward")
        labelMiddleName = Label(frameMiddleName, text='Middle name')
        labelMiddleName.pack(side=LEFT)

        frameLastName = Frame(master)
        frameLastName.pack()
        entryLastName = Entry(frameLastName)
        entryLastName.pack(side=LEFT)
        entryLastName.insert(0,"Smith")
        labelLastName = Label(frameLastName, text='Last name')
        labelLastName.pack(side=LEFT)
        
        frameGender = Frame(master)
        frameGender.pack()
        listboxGender = Listbox(frameGender, exportselection=0)
        listboxGender.delete(0,END)
        size=0
        for item in ["male", "female"]:
            listboxGender.insert(END,item)
            size=size+1
        listboxGender.selection_set(0)
        listboxGender.config(height=size)
        listboxGender.pack(side=LEFT)
        labelGender = Label(frameGender, text='Gender')
        labelGender.pack(side=LEFT)

        frameDOB = Frame(master)
        frameDOB.pack()
        entryDay = Entry(frameDOB, width=2)
        entryDay.pack(side=LEFT)
        entryDay.insert(0,24)
        entryMonth = Entry(frameDOB, width=2)
        entryMonth.pack(side=LEFT)
        entryMonth.insert(0,12)
        entryYear = Entry(frameDOB, width=4)
        entryYear.pack(side=LEFT)
        entryYear.insert(0,1975)
        labelDOB = Label(frameDOB, text='Date of birth: DD MM YYYY')
        labelDOB.pack(side=LEFT)

        def openIDDocFile():
            openphoto(self, entryIDDoc) 

        def openPhotoFile():
            openphoto(self, entryPhoto) 

        def openphoto(self, entry):
            fileOpened = filedialog.askopenfilename(initialdir = "/", title = "Select file", filetypes = (("jpg files","*.jpg"),("png files","*.png"),("pdf files","*.pdf")))
            entry.delete(0,END)
            entry.insert(0,fileOpened)

        def openKeyFile(self,entry, keys):
            fileOpened = filedialog.askopenfilename(initialdir = "/", title = "Select key file", filetypes = (("all files","*.*")))
            entry.delete(0,END)
            entry.insert(0,fileOpened)

        def openKeyFile():
            openKeyFile(self, entryKey, keys)
            
        def loadKeys():
            with open(entryKeyFile.get(),'rt') as csvfile:
#                keyReader = csv.reader(csvfile, delimiter=' ')
                myDialect = csv.excel
                myDialect.delimiter=' '
                dictReader = csv.DictReader(filter(lambda row: row[0]!='#', csvfile), fieldnames=['tweaked_address', 'untweaked_public_key'],dialect=myDialect)
                for row in dictReader:
                    self.keys = self.keys+[row['tweaked_address'], row['untweaked_public_key']]
                    
            pprint('*** Keys loaded: ***')
            pprint(self.keys)

        frameIDDoc = Frame(master)
        frameIDDoc.pack()
        entryIDDoc = Entry(frameIDDoc, width=25)
        entryIDDoc.pack(side=LEFT)
        entryIDDoc.insert(0,"/Users/lawrence/Projects/ocean-idcheck/testPicture.png")
        buttonIDDocFileOpen = Button(frameIDDoc, text='ID document', command=openIDDocFile)
        buttonIDDocFileOpen.pack(side=LEFT)
        
        frameIDDocType = Frame(master)
        frameIDDocType.pack()
        listboxIDDocType = Listbox(frameIDDocType, exportselection=0)
        listboxIDDocType.delete(0,END)
        size=0
        for item in ["passport", "national_identity_card", "driving_licence", "uk_biometric_residence_permit", "tax_id", "voter_id"]:
            listboxIDDocType.insert(END,item)
            size=size+1
        listboxIDDocType.selection_set(0)
        listboxIDDocType.config(height=size)
        listboxIDDocType.pack(side=LEFT)
        labelIDDocType = Label(frameIDDocType, text='ID document type')
        labelIDDocType.pack(side=LEFT)

        framePhoto = Frame(master)
        framePhoto.pack()
        entryPhoto = Entry(framePhoto, width=25)
        entryPhoto.pack(side=LEFT)
        entryPhoto.insert(0,"/Users/lawrence/Projects/ocean-idcheck/testPicture.png")
        buttonPhotoFileOpen = Button(framePhoto, text='Photo', command=openPhotoFile)
        buttonPhotoFileOpen.pack(side=LEFT)
        
        labelAddress = Label(master, text='Address')
        labelAddress.pack()
        frameBuildingNo = Frame(master)
        frameBuildingNo.pack()
        entryBuildingNo = Entry(frameBuildingNo)
        entryBuildingNo.pack(side=LEFT)
        entryBuildingNo.insert(0,"10")
        labelBuildingNo = Label(frameBuildingNo, text='Building number')
        labelBuildingNo.pack(side=LEFT)
        frameStreet = Frame(master)
        frameStreet.pack()
        entryStreet = Entry(frameStreet)
        entryStreet.pack(side=LEFT)
        entryStreet.insert(0,"Main Street")
        labelStreet = Label(frameStreet, text='Street')
        labelStreet.pack(side=LEFT)
        frameTown = Frame(master)
        frameTown.pack()
        entryTown = Entry(frameTown)
        entryTown.pack(side=LEFT)
        entryTown.insert(0,"London")
        labelTown = Label(frameTown, text='Town')
        labelTown.pack(side=LEFT)
        framePostcode = Frame(master)
        framePostcode.pack()
        entryPostcode = Entry(framePostcode)
        entryPostcode.pack(side=LEFT)
        entryPostcode.delete(0,END)
        entryPostcode.insert(0,"SW4 6EH")
        labelPostcode = Label(framePostcode, text='Postcode')
        labelPostcode.pack(side=LEFT)
        frameCountry = Frame(master)
        frameCountry.pack()
        entryCountry = Entry(frameCountry)
        entryCountry.pack(side=LEFT)
        entryCountry.delete(0,END)
        entryCountry.insert(0,"GBR")
        labelCountry = Label(frameCountry, text='Country')
        labelCountry.pack(side=LEFT)

        frameKeyFile = Frame(master)
        frameKeyFile.pack()
        entryKeyFile = Entry(frameKeyFile, width=25)
        entryKeyFile.pack(side=LEFT)
        entryKeyFile.insert(0,"/Users/lawrence/Projects/ocean-demo/keys.client")
        buttonKeyFileOpen = Button(frameKeyFile, text='Key file', command=openKeyFile)
        buttonKeyFileOpen.pack(side=LEFT)

        status.pack(side=BOTTOM, fill=X)

        def fillApplicant():
            applicant.first_name = entryFirstName.get()
            applicant.last_name = entryLastName.get()
            applicant.dob=datetime.date(int(entryYear.get()), int(entryMonth.get()), int(entryDay.get()))
            applicant.country='GBR' #This is the jurisdiction where the ID check takes place, not the applicant's home country.
            
        def fillAddress():
            address.building_number=entryBuildingNo.get()
            address.street=entryStreet.get()
            address.town=entryTown.get()
            address.postcode=entryPostcode.get()
            address.country=entryCountry.get()
            applicant.addresses=[address]

        def fillIDDocument():
            pprint('hello')

        def fillKeys():
            check.tags=self.keys
            pprint('*** keys loaded to check: ***')
            pprint(check.tags)
            
        def submit():
            status.set("Submitting...")
            fillApplicant()
            fillAddress()
            loadKeys()
            fillKeys()
            try:
                api_response = api_instance.create_applicant(data=applicant)
                applicant_id=api_response.id
                api_response=api_instance.create_check(applicant_id, data=check)
                pprint(api_response)
            except ApiException as e:
                pprint(e.body)
                status.set("Error.")
        
        frameSubmit = Frame(master)
        frameSubmit.pack(side=BOTTOM, fill=X)
        buttonSubmit = Button(frameSubmit, text='Submit', command=submit)
        buttonSubmit.pack(side=RIGHT)
        
    def run():
        root = tk.Tk()
        app = idcheck(root)
        root.title(app.title)
        root.mainloop()






