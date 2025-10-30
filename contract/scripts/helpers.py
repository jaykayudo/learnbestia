import json

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


def generate_contract_data(data: dict, json_file_path: str = None) -> dict:
    result = {}
    for name, contract in data.items():
        info = {
            "address": contract.address,
            "abi": contract.abi,
            "bytecode": contract.bytecode,
        }
        result[name] = info

    if json_file_path:
        assert json_file_path.endswith(
            ".json"
        ), "Invalid file path provided (should end with .json)"
        json.dump(result, open(json_file_path, "w"))
        print(f"Contract data saved at {json_file_path}")

    return result
