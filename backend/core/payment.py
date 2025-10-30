from abc import abstractmethod

from django.conf import settings

from core.models.user import PaymentMethods, Transaction
from core.blockchain import web3, BlockchainService
from core.utils import get_usd_to_token_equivalent


payment_method_token_dict = {
    PaymentMethods.ERC_USDC: settings.ERC_USDC,
    PaymentMethods.ERC_USDT: settings.ERC_USDT,
    PaymentMethods.BESTIA_COIN: settings.BESTIA_COIN,
    PaymentMethods.DOT: settings.DOT,
}


class BasePayment:
    @abstractmethod
    @classmethod
    def initialize_transaction(self, transaction: Transaction):
        raise NotImplementedError

    @abstractmethod
    @classmethod
    def verify_transaction(self, transaction: Transaction) -> bool:
        raise NotImplementedError


# TODO: Integrate stripe
class FiatPayment(BasePayment):
    @classmethod
    def initialize_transaction(self, transaction):
        pass

    @classmethod
    def verify_transaction(self, transaction) -> bool:
        True


class InternalPayment(BasePayment):
    @classmethod
    def initialize_transaction(self, transaction):
        pass

    @classmethod
    def verify_transaction(self, transaction) -> bool:
        True


class CryptoPayment(BasePayment):
    @classmethod
    def initialize_transaction(self, transaction: Transaction):
        contract = BlockchainService.get_payment_contract()
        token = payment_method_token_dict[transaction.PAYMENT_METHODS]
        amount = get_usd_to_token_equivalent(token, transaction.amount)
        address = settings.ADMIN_ADDRESS
        nonce = web3.eth.get_transaction_count(address)
        transaction = contract.functions.createInvoice(
            transaction.ref, amount, token
        ).build_transaction(
            {
                "from": address,
                "nonce": nonce,
                "gas": 200000,
                "gasPrice": web3.to_wei("10", "gwei"),
            }
        )
        signed_tx = web3.eth.account.sign_transaction(transaction, settings.PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        web3.eth.wait_for_transaction_receipt(tx_hash)

        # get created transaction
        data = contract.functions.getInvoice(transaction.ref).call()

    @classmethod
    def verify_transaction(self, transaction) -> bool:
        contract = BlockchainService.get_payment_contract()
        verification = contract.functions.checkPaymentStatus(transaction.ref).call()
        return verification
