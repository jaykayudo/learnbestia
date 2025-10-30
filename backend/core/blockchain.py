import json
from web3 import Web3
from django.conf import settings
from loguru import logger

web3 = Web3(Web3.HTTPProvider(settings.PROVIDER_URL))
assert web3.is_connected()

# Load contract data file
with open(settings.CONTRACT_DIR / "data.json", "r") as file:
    data_file = json.load(file)


class BlockchainService:
    @classmethod
    def get_payment_contract(cls):
        """
        Get the payment contract for payment interaction
        """
        payment_abi = data_file["payment"]["abi"]
        payment_contract_address = data_file["payment"]["address"]

        contract = web3.eth.contract(address=payment_contract_address, abi=payment_abi)
        return contract

    @classmethod
    def get_certficate_nft_contract(cls, certificate_contract_address: str):
        """
        Get the certificate nft contract for certificate interaction
        """
        certificate_abi = data_file["certificate"]["abi"]
        contract = web3.eth.contract(
            address=certificate_contract_address, abi=certificate_abi
        )
        return contract

    @classmethod
    def get_learnbestia_token_contract(cls):
        """
        Get the learnbestia token contract for learnbestia token interaction
        """
        learnbestia_abi = data_file["learnbestia"]["abi"]
        learnbestia_contract_address = data_file["learnbestia"]["address"]

        contract = web3.eth.contract(
            address=learnbestia_contract_address, abi=learnbestia_abi
        )
        return contract

    @classmethod
    def deploy_certicate_nft(cls, name: str, symbol: str):
        admin = settings.ADDRESS
        private_key = settings.PRIVATE_KEY
        certificate_abi = data_file["certificate"]["abi"]
        certificate_bytecode = data_file["certificate"]["bytecode"]

        nonce = web3.eth.get_transaction_count(admin)

        Certificate = web3.eth.contract(
            abi=certificate_abi, bytecode=certificate_bytecode
        )
        transaction = Certificate.constructor(admin, name, symbol).build_transaction(
            {
                "from": admin,
                "nonce": nonce,
                "gas": 2000000,
                "gasPrice": web3.to_wei("10", "gwei"),
            }
        )
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        logger.info(
            f"Deploying certificate nft contract... (tx hash: {web3.to_hex(tx_hash)})"
        )

        # Wait for transaction receipt
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info("Contract deployed at:", tx_receipt.contractAddress)
        return tx_receipt.contractAddress
