import requests

def buy_drink(user,price):
    if '@' in user:
        user,server = user.split('@')
        if server == '':
            server = "http://0.0.0.0:5000"
    else:
        server = "http://cimcoin.herokuapp.com"
    return transaction(user,'CimBar',price,server=server)


def transaction(sender, recipient, amount,server="http://0.0.0.0:5000"):
    data = {'sender': sender, 'recipient': recipient , 'amount': amount, 'mode':'text'}
    r = requests.post(server+'/new_transaction', data=data)
    return r.text[16:-4]

#buy_drink('edan','0')

def register_node(src="http://127.0.0.1:5000",dst="https://cimcoin.herokuapp.com"):
    data = {"nodes": [dst]}
    r1 = requests.post(src+"/nodes/register", json=data)
    r2 = requests.get(src + "/nodes/resolve")

    return r1.text,r2.text

#print(buy_drink('edan','0'))
print(register_node())
print(register_node(dst="http://127.0.0.1:5000",src="https://cimcoin.herokuapp.com"))