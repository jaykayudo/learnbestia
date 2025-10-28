from brownie import network, accounts, config
from brownie.network.account import Account

LOCAL_ENVIRONMENTS = ["mainnet-fork", "development"]


def get_account(env_account=True) -> Account:
    if network.show_active() in LOCAL_ENVIRONMENTS:
        account = accounts[0]
    else:
        if env_account:
            account = accounts.add(config["wallets"]["from"])
        else:
            account = accounts.load("mainaddress")
    return account
