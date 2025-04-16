from utils import *
from utils import *
import json
import datetime
from colorama import init, Fore, Style

# Initialize colorama
init()

def main():
	# init the blockchain
	blockchain = Blockchain(None, None) 

	# init the blockchain data
	global blockchain_data
	blockchain_data = []

	# print initial balances
	print_balances(blockchain)

	while True:
		choice = input(f'{Fore.CYAN}1. Create transaction\n2. Mine pending transactions\n3. Print blockchain\n4. Exit{Style.RESET_ALL}\n')
		if choice == '1':
			while True:
				try:
					amount = round(float(input(f"{Fore.GREEN}Enter BTC amount: {Style.RESET_ALL}")), 8)
					fee = calculate_fee(amount, blockchain)
					note = conditional_input(f"{Fore.YELLOW}Do you want to add a note? (y/n): {Style.RESET_ALL}")
					if note:
						note = input(f"{Fore.YELLOW}Enter note: {Style.RESET_ALL}")
					else:
						note = ""
					
					create_transaction(blockchain, amount, fee, note)
					print(f"\n{Fore.GREEN}Transaction added to pending transactions.{Style.RESET_ALL}")
					print_balances(blockchain)
					break
						
				except ValueError:
					print(f"{Fore.RED}Please enter a valid number{Style.RESET_ALL}")
				except EOFError:
					print(f"{Fore.RED}No input received{Style.RESET_ALL}")
					break
				except Exception as e:
					print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

		elif choice == '2':
			if len(blockchain.pendingTransactions) == 0:
				print(f"{Fore.YELLOW}No pending transactions to mine.{Style.RESET_ALL}")
			else:
				blockchain.mine_pending_transactions()
				print(f"\n{Fore.GREEN}Pending transactions mined into a new block.{Style.RESET_ALL}")
				print_balances(blockchain)

		elif choice == '3':
			blockchain_data = []
			for block in blockchain.chain:
				block_data = {
					"index": block.index,
					"timestamp": block.timestamp.isoformat() if isinstance(block.timestamp, datetime.datetime) else block.timestamp,
					"transactions": block.transactions,
					"prev_hash": block.prev_hash,
					"hash": block.hash,
					"nonce": block.nonce
				}
				blockchain_data.append(block_data)
			
			# Write to file only once at the end
			with open('blockchain_data.json', 'w') as f:
				json.dump(blockchain_data, f, indent=2)
			print(f"\n{Fore.GREEN}Blockchain saved to blockchain_data.json{Style.RESET_ALL}")

		elif choice == '4':
			break

	

if __name__ == "__main__":
	main()
