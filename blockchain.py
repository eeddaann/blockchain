import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import datetime
import requests
from flask import Flask, jsonify, request, render_template


class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """
        Add a new node to the list of nodes

        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print('{'+last_block+'}')
            print('{'+block+'}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get('http://'+node+'/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain

        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    def get_balance(self, wallet_id):
        balance = 0
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['sender'] == wallet_id:
                    balance -= int(transaction['amount'])
                if transaction['recipient'] == wallet_id:
                    balance += int(transaction['amount'])
        return balance

    def get_user_transactions(self, wallet_id):
        transaction_lst = []
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['sender'] == wallet_id or transaction['recipient'] == wallet_id:
                    transaction_lst.append(transaction)
        return transaction_lst

    def get_user_un_transactions(self, wallet_id):
        transaction_lst = []
        for transaction in self.current_transactions:
            if transaction['sender'] == wallet_id or transaction['recipient'] == wallet_id:
                transaction_lst.append(transaction)
        return transaction_lst

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof

        :param last_proof: Previous Proof
        :param proof: Current Proof
        :return: True if correct, False if not.
        """

        # guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(str(last_proof).encode() + str(proof).encode()).hexdigest()
        print(str(last_proof).encode() + str(proof).encode())
        print(guess_hash)
        # return guess_hash[:4] == "0000"
        return guess_hash[:4] == "0" * 4


# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = "CimCoin_user"  # str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/')
def start():
    return render_template('index.html')


@app.route('/new_transaction', methods=['GET', 'POST'])
def create_transaction():
    if request.method == 'GET':
        user = ""
        if 'wallet_id' in request.cookies:
            user = request.cookies['wallet_id']
        return render_template('new_transaction.html', user=user)
    elif request.method == 'POST':
        sender = request.form['sender']
        recipient = request.form['recipient']
        amount = request.form['amount']
        if blockchain.get_balance(sender) >= int(amount):
            index = blockchain.new_transaction(sender, recipient, amount)
            if request.form['mode'] == 'text':
                response = {
                    'message': "transaction added, you just paid " + str(amount) + " CimCoins to " + recipient,
                }
                return jsonify(response), 200
        else:
            if request.form['mode'] == 'text':
                response = {
                    'message': "transaction failed! you have tried to transfer " + str(
                        amount) + " CimCoins while you have only " + str(blockchain.get_balance(sender)) + " CimCoins.",
                }
                return jsonify(response), 200
            return render_template('transaction_rejected.html', amount=amount, balance=blockchain.get_balance(sender))
        return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        response = app.make_response(render_template('index.html'))
        wallet_id = request.form['wallet_id']
        response.set_cookie('wallet_id', value=wallet_id)
        return response


@app.route('/view_chain', methods=['GET'])
def view_chain():
    return render_template('view_chain.html', length=len(blockchain.chain), chain=blockchain.chain)


@app.route('/my_transactions', methods=['GET'])
def my_transactions():
    if 'wallet_id' in request.cookies:
        user = request.cookies['wallet_id']
    else:
        user = 'guest'
    return render_template('my_transactions.html', transactions=blockchain.get_user_transactions(user),
                           un_transactions=blockchain.get_user_un_transactions(user), user=user,
                           balance=blockchain.get_balance(user))


@app.route('/miner', methods=['GET', 'POST'])
def miner():
    if request.method == 'GET':
        return render_template('miner.html', last_block=blockchain.last_block,
                               last_proof=blockchain.last_block['proof'])
    if request.method == 'POST':
        values = request.form['proof']
        proof = values
        miner = node_identifier
        last_block = blockchain.last_block['proof']
        if blockchain.valid_proof(blockchain.last_block['proof'], proof):
            if 'wallet_id' in request.cookies:
                miner = request.cookies['wallet_id']
                if miner == "":
                    miner = 'guest'
            blockchain.new_transaction(sender="cimcoin_network", recipient=miner, amount=1)  # pay to the miner
            previous_hash = blockchain.hash(last_block)
            block = blockchain.new_block(proof, previous_hash)
            response = {
                'message': "New Block Forged",
                'index': block['index'],
                'transactions': block['transactions'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
            }
            return jsonify(response), 200
        else:
            response = {
                'message': "cannot verify this block!",
                'proof': blockchain.last_block['proof'],
            }
            return jsonify(response), 401


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': 'Transaction will be added to Block '+str(index)}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    print(values)
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


@app.template_filter('strftime')
def _jinja2_filter_datetime(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d  %H:%M:%S')


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
