from cb_idcheck.database import database
from cb_idcheck.cb_onfido import cb_onfido
from cb_idcheck.record import record
from pprint import pprint

db=database()
id_api=cb_onfido()

print('Processing considerlist...')
#Loop theoufgh all applicant records in consider list.
for document in db.considerlist.find():
    print('Displaying checks for customer ' + document['_id'] +  ', created ' + document['created_utc'] + ', updated ' + document['updated_utc'])
    n_checks_approved=0
    n_checks_rejected=0
    #Loop through all the checks in the applicant record and request a decision from the user.
    for check in id_api.list_checks(document['_id']):
        b_sure=False
        pprint(check)
        while(b_sure==False):
            approve_for_whitelist=input('Approve check for whitelist? [yes/no/quit]: ')
            prepend=""
            if(approve_for_whitelist == "quit"):
                quit()
            elif(approve_for_whitelist == "yes"):
                prepend="The keys will be added to the whitelist. "
            elif(approve_for_whitelist == 'no'):
                prepend="The keys will NOT be added to the whitelist. "
            else:
                print('Please respond yes/no/quit.')
                continue
            while(sure != 'yes' && sure !='no' && sure != 'quit'):
                sure=input(prepend + ' OK? [yes/no/quit]: ')
                if(sure=='quit'):
                    quit()
                elif(sure=='yes'):
                    b_sure=True
                elif(sure=='no'):
                    b_sure=False
                else:
                    print("Please respond yes/no/quit.")
        
        if(approve_for_whitelist=='yes'):
            customer_record record()
            customer_record.import_from_applicant_check(id_api.find_applicant_check(applicant_id=document['_id'], check_id=check.id))
            db.add_check_to_whitelist(customer_record)
            n_checks_approved=n_checks_approved+1
        else:
            n_checks_rejected=n_checks_rejected+1
        
    print('=========================================================================')
    print('Finished processing checks for applicant ' + document['_id'] + '. Summary:')
    print('-------------------------------------------------------------------------')
    print('Checks approved:' + n_checks_approved)
    print('Checks rejected:' + n_checks_rejected)
    print('-------------------------------------------------------------------------')
    remove_ok=input('Remove applicant record from consider list? [yes/no]: ')
    if(remove_ok == 'yes'):
        db.removeFromID(document['_id'])
        remove_ok=input('Remove applicant record from idcheck vendor database? [yes/no]: ')
        if(remove_ok == 'yes'):
            id_api.destroy_applicant(document['_id'])
            
            
print('...finished processing considerlist.')
        
    
