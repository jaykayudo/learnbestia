from pathlib import Path
from brownie import Payment, Certificate, Learnbestia
from scripts.helpers import get_account, generate_contract_data

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


BASE_DIR = Path(__file__).resolve().parent.parent.parent

BACKEND_CONTRACT_DIR = BASE_DIR / "backend/contracts"


def deploy():
    """
    Steps for Deployment:
    - get account
    - deploy payment contract
    - deploy certificate
    """
    account = get_account()
    print("Deploying Payment contract")
    payment_contract = Payment.deploy(account.address, {"from": account})
    print(f"{GREEN}Deployed Payment contract at {payment_contract.address}{RESET}")

    print("Deploying Certificate Contract")
    certificate_contract = Certificate.deploy(
        account.address, "CERT", "CERT007", {"from": account}
    )
    print(
        f"{GREEN}Deployed Certificate Contract at {certificate_contract.address}{RESET}"
    )

    print("Deploying Learnbestia Token Contract")
    learnbestia_token_contract = Learnbestia.deploy({"from": account})
    print(
        f"{GREEN}Deployed Learnbestia Token Contract at {learnbestia_token_contract.address}{RESET}"
    )

    data = {
        "certificate": certificate_contract,
        "learnbestia": learnbestia_token_contract,
        "payment": payment_contract,
    }

    generate_contract_data(data, str(BACKEND_CONTRACT_DIR / "data.json"))

    return data


def main():
    deploy()
