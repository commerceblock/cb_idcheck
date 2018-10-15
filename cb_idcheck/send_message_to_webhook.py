# Posting to webhook
def send_message_to_webhook():
    from urllib import request, parse
    import json

#This is the type of post we will expect to retrieve from the webhook when we finally get our sandbox token.
    post = {
        "payload": {
            "resource_type": "check",
            "action": "check.completed",
            "object": {
                "id": "12345-23122-32123",
                "status": "complete",
                "result": "clear",
                "completed_at": "2014-05-23 13:50:33 UTC",
                "href": "https://api.onfido.com/v2/applicants/12343-11122-09290/checks/12345-23122-32123",
#We will store the tweaked addresses and untweaked public keys in tags: [ [<tweaked_addresses], [<public_keys>] ]
                "tags": [ ['112B9rf6z97SNnaySCUpGkGAUAke2t3VAR',
                         '16wUjmEnFhwCJsT8o23EbduZZFe5cYbVs', 
                         '1WRYUBvVLnB6MgpJfTAu733pDp4C8ouna', 
                         '1bWswtS9YBs5972Gpge7ibKeR38MuPNaR', 
                         '1d5xHWZEjhw86gVhzcPdZJo8ZKwVzeCta', 
                         '1oqCChDj1MraMygjaHs6tTEp9bSpsuJNm', 
                         '12AATpUrHDLWXqD6KWrJ2558dbWessW95J',
                         '12FZth9rU895EfcD1y6WnQHik84hypmbYu'],
                [ '035f886272d6ea78bc4e4d3e0c758bc3a9286f5d8486db5038ca3326c324730bfc',
                  '038855e0c7b14757e70635e8551ae191b0e035427ac007baa79861a907288ea745', 
                  '036b82e4684ea4751b6202928bb8d95bfd065d7ee4d083a5e4787fdfbe288f7245', 
                  '022102ba686dc4aa7c97ab8b02c942b51d7979627bf3a32887b0aa14ba284eaa1c', 
                  '02871ed997945a329b7a275ee6d821b88b5c038ab076c989ca84ac088a4d56ca21', 
                  '02a04e0f1c46a76c9b2f15197c670f1e4ef6133f2ff1f22ed414d45280f2f5f2b1',      
                  '03b52de5e54b5f08c895d18b23d0971ff140e753fb7e9cb90fd8c90ad37883d0f6',     
                  '038d04a2d3510344189677b0e777b3c70f3b474465675722ab03f51c3196858ebd'] ]
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
