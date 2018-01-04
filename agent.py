import requests

def transaction(sender, recipient, amount,server="http://0.0.0.0:5000/new_transaction"):
    data = {'sender': sender, 'recipient': recipient , 'amount': amount, 'mode':'text'}
    r = requests.post(server, data=data)
    return r.text

def register_node(src="http://0.0.0.0:5000",dst="http://0.0.0.0:80, http://cimcoin.herokuapp.com/"):
    data = {"nodes": [dst]}
    r1 = requests.post(src+"/nodes/register", json=data)
    r2 = requests.get(src + "/nodes/resolve")

    return r2.text

#print(transaction('tal','edan','3')[16:-4])
print(register_node())