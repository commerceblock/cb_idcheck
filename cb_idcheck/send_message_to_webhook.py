# Posting to webhook
def send_message_to_webhook():
    from urllib import request, parse
    import json

    post = {
        "payload": {
            "resource_type": "report",
            "action": "report.completed",
            "object": {
                "id": "12345-23122-32123",
                "status": "completed",
                "completed_at": "2014-05-23 13:50:33 UTC",
                "href": "https://api.onfido.com/v2/checks/12343-11122-09290/reports/12345-23122-32123"
                }
            }
        }
    
    try:
        json_data = json.dumps(post)
        req = request.Request("http://127.0.0.1:5000/",
                              data=json_data.encode('ascii'),
                              headers={'Content-Type': 'application/json'}) 
        resp = request.urlopen(req)
    except Exception as em:
        print("EXCEPTION: " + str(em))
        
send_message_to_webhook()
