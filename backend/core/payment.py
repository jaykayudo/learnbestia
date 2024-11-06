from abc import abstractmethod


class BasePayment:
    @abstractmethod
    def initialize_transaction(self, transaction):
        raise NotImplementedError

    @abstractmethod
    def verify_transaction(self, transaction):
        raise NotImplementedError


class FiatPayment(BasePayment):
    pass


class CryptoPayment(BasePayment):
    pass
