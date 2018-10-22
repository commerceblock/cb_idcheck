# Posting to webhook
def send_message_to_webhook():
    from urllib import request, parse
    import json

#This is the type of post we will expect to retrieve from the webhook.
    post='{"payload":{"resource_type":"check","action":"check.completed","object":{"id":"cd210ae4-f487-43da-9f7a-21de0ac43550","status":"complete","completed_at":"2018-10-19 13:03:28 UTC","href":"https://api.onfido.com/v2/applicants/2bc75038-4776-464c-807d-7d7ad21a08ce/checks/cd210ae4-f487-43da-9f7a-21de0ac43550"}}}'
    try:
        json_data = json.dumps(post)
        req = request.Request("http://127.0.0.1:5000/",
                              data=json_data.encode('ascii'),
                              method='POST',
                              headers={'Content-Type': 'application/json',
#                                       'X-Signature' : '84918579430de8e287a654a63c5104dfad9f1cb9'}) 
                                       'X-Signature' : '84918579430de8e287a654a63c5104dfad9f1cb8'}) 
        resp = request.urlopen(req)
    except Exception as em:
        print("EXCEPTION: " + str(em))
        
send_message_to_webhook()
