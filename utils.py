import datetime
import json
import hashlib
from typing import TypedDict, Optional
import tabulate
from colorama import Fore, Style

#Raw Data

user1 = {
	'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
	'balance': 6931.00
}

user2 = {
	'address': '18h23j0dye2e082y3dfhd383h03hof323w',
	'balance': 00.00
}


#Classes 

class Transaction(TypedDict):
	amount: float
	senderAddress: str
	receiverAddress: str
	note: Optional[str]
	timestamp: str
	fee: float

class Wallet:
	def __init__(self, initial_balances=None):
		self.balances = {}
		if initial_balances:
			for balance_info in initial_balances:
				self.balances[balance_info['address']] = round(balance_info['balance'], 8)

	def getBalance(self, address):
		return round(self.balances.get(address, 0) or 0, 8)

	def hasEnoughBalance(self, address, amount):
		return self.getBalance(address) >= round(amount, 8)

	def updateBalance(self, address, amount):
		current_balance = self.getBalance(address)
		self.balances[address] = round(current_balance + amount, 8)


	def process_transaction(self, transaction):
		sender_address = transaction['senderAddress']
		receiver_address = transaction['receiverAddress']
		amount = transaction['amount']
		fee = transaction['fee']
		
		# check if the sender has enough balance (including fee)
		if not self.hasEnoughBalance(sender_address, amount + fee):
			return False
			
		# update the balances
		self.updateBalance(sender_address, -(amount + fee))
		self.updateBalance(receiver_address, amount)
		
		return True
	

	def check_double_spending(self, transactions):
		spent_amounts = {}
		initial_balances = {}
		
		# save the initial balances
		for tx in transactions:
			# save the initial balance of the sender
			if tx['senderAddress'] not in initial_balances:
				initial_balances[tx['senderAddress']] = self.getBalance(tx['senderAddress'])
		
		# check for double spending
		for tx in transactions:
			# get the sender address, amount and fee
			sender_address = tx['senderAddress']
			amount = tx['amount']
			fee = tx['fee']
			
			# get the current spent amount
			current_spent = spent_amounts.get(sender_address, 0)
			# get the total spent amount
			total_spent = current_spent + amount + fee
			# get the initial balance of the sender
			initial_balance = initial_balances.get(sender_address, 0)
			
			# check if the total spent would exceed the initial balance
			if total_spent > initial_balance:
				return True  # double spending detected
			
			# save the total spent amount
			spent_amounts[sender_address] = total_spent
		
		return False

class Block:
	def __init__(self, timestamp, transactions):
		self.index = 0
		self.timestamp = timestamp
		self.transactions = transactions
		self.prev_hash = '0'
		self.nonce = 0
		self.fee = 0
		self.hash = self.calculateHash()

	def calculateHash(self):
		return hashlib.sha256(
			str(self.index).encode() +
			self.prev_hash.encode() +
			str(self.timestamp).encode() +
			json.dumps(self.transactions).encode() +
			str(self.nonce).encode() + 
			str(self.fee).encode()
		).hexdigest()
	

	def mine_block(self, difficulty: int):
		# calculate the target hash
		target = '0' * difficulty  # e.g. "0000" if difficulty is 4
		# mine the block
		while self.hash[:difficulty] != target:
			self.nonce += 1
			self.hash = self.calculateHash()  # update the hash until a valid one is found
		
class Blockchain:
	def __init__(self, existing_chain, existing_wallet):
		# if the chain is already existing, use it
		if existing_chain:
			self.chain = existing_chain
		else:
			self.chain = [self.create_genesis()]
		
		# initialize the pending transactions
		self.pendingTransactions = []
		
		# if the wallet is not existing, create a new one
		if existing_wallet:
			self.wallet: Wallet = existing_wallet
		else:
			# create a new wallet with the initial balances
			self.wallet: Wallet = Wallet([
				{ "address": user1['address'], "balance": user1['balance'] },
				{ "address": user2['address'], "balance": user2['balance'] }
			])
		
	def create_genesis(self) -> Block:
		genesis_transaction: Transaction = {
			"senderAddress": "genesis",
			"receiverAddress": 'none',
			"amount": 0,
			"fee": 0,
			"timestamp": datetime.datetime.now().isoformat(),
			"note": "Genesis block"
		}
		return Block(datetime.datetime.now(), [genesis_transaction])
	
	def latest_block(self) -> Block:
		return self.chain[-1]
	
	def add_block(self, new_block: Block):
		new_block.index = self.latest_block().index + 1 # set index to the last block index + 1
		new_block.prev_hash = self.latest_block().hash # set the previous hash to the hash of the last block

		# mine the block (difficulty -> 4)
		new_block.mine_block(4)

		self.chain.append(new_block) # add the new block to the chain
	
	def add_transaction(self, transaction: Transaction):
		# check if the sender has enough balance
		if not self.wallet.hasEnoughBalance(transaction['senderAddress'], transaction['amount'] + transaction['fee']):
			raise Exception("Insufficient balance")

		# check for double spending in pending transactions
		if self.wallet.check_double_spending([*self.pendingTransactions, transaction]):
			raise Exception("Double spending detected")

		# process the transaction (update balances)
		if not self.wallet.process_transaction(transaction):
			raise Exception("Transaction processing failed")

		# add the transaction to the pending transactions
		self.pendingTransactions.append(transaction)

		if len(self.pendingTransactions) == 10:
			new_block = Block(datetime.datetime.now(), [*self.pendingTransactions])
			self.add_block(new_block)
			self.pendingTransactions = []  # empty the pending transactions
		
	def mine_pending_transactions(self) -> bool:
		if len(self.pendingTransactions) > 0:
			new_block = Block(datetime.datetime.now(), [*self.pendingTransactions])
			self.add_block(new_block)
			# don't reset the wallet, only the pending transactions
			self.pendingTransactions = []
			return True
		return False

	def get_pending_transactions(self) -> list[Transaction]:
		# return the pending transactions (in format of the Transaction type)
		return [*self.pendingTransactions]

	def check_valid(self) -> bool:
		for i in range(1, len(self.chain)):
			current_block = self.chain[i]
			previous_block = self.chain[i - 1]
		
			# check if the hash is valid
			if current_block.hash != current_block.calculateHash():
				print(f"❌ Invalid hash at block {current_block.index}")
				return False

			# check if the previous hash is valid
			if current_block.prev_hash != previous_block.hash:
				print(f"❌ Invalid previous hash at block {current_block.index}")
				return False

			# check if the number of transactions is valid
			if len(current_block.transactions) > 10:
				print(f"❌ Block {current_block.index} has more than 10 transactions")
				return False

			# check if the block has no transactions
			if len(current_block.transactions) == 0:
				print(f"❌ Block {current_block.index} has no transactions")
				return False

			# check if the addresses are valid
			for tx in current_block.transactions:
				if not tx['senderAddress'] or not tx['receiverAddress']:
					print(f"❌ Invalid addresses in a transaction at block {current_block.index}")

		return True

	def calculate_fee(self, amount: float) -> float:
		# base fee: 0.0010 BTC
		base_fee = 0.0010
		
		# additional fee based on amount: 0.10% of transaction amount
		amount_fee = amount * 0.010
		
		# network load factor: increases fee when pending transactions are high
		network_load_factor = min(1 + (len(self.pendingTransactions) / 10), 2)
		
		return (base_fee + amount_fee) * network_load_factor

	def get_balance(self, address: str) -> float:
		return self.wallet.getBalance(address)
		


#Utility Functions

def calculate_fee(amount: float, blockchain: Blockchain) -> float:
	# base fee: 0.0010 BTC
	base_fee = 0.0010
	
	# additional fee based on amount: 0.10% of transaction amount
	amount_fee = round(amount * 0.010, 8)
	
	# network load factor: increases fee when pending transactions are high
	network_load_factor = min(1 + (len(blockchain.pendingTransactions) / 10), 2)
	
	return round((base_fee + amount_fee) * network_load_factor, 8)

def print_balances(blockchain):
	table = [
		[ f"{Fore.CYAN}User{Style.RESET_ALL}", f"{Fore.CYAN}Balance{Style.RESET_ALL}", f"{Fore.CYAN}Address{Style.RESET_ALL}"],
		[f"{Fore.GREEN}You{Style.RESET_ALL}", f"{Fore.GREEN}{blockchain.get_balance(user1['address'])}{Style.RESET_ALL} BTC", f"{Fore.GREEN}{user1['address']}{Style.RESET_ALL}"],
		[f"{Fore.YELLOW}User 2{Style.RESET_ALL}", f"{Fore.YELLOW}{blockchain.get_balance(user2['address'])}{Style.RESET_ALL} BTC", f"{Fore.YELLOW}{user2['address']}{Style.RESET_ALL}"]
	]
	print(tabulate.tabulate(table, headers="firstrow", tablefmt="grid"))

def create_transaction(blockchain, amount, fee, note):
	blockchain.add_transaction({
		"senderAddress": user1['address'],
		"receiverAddress": user2['address'],
		"amount": amount,
		"fee": fee,
		"timestamp": datetime.datetime.now().isoformat(),
		"note": note
	})

def conditional_input(prompt):
	is_valid = input(prompt)
	if is_valid == 'y':
		return True
	else:
		return False