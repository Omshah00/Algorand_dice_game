from algosdk.v2client import algod
from algosdk.future.transaction import ApplicationCallTxn, StateSchema, OnComplete
from algosdk import account, mnemonic
from algosdk.logic import get_application_address
import json

ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

def deploy_app(creator_mnemonic):
    from pyteal import compileTeal, Mode
    import dice_game

    private_key = mnemonic.to_private_key(creator_mnemonic)
    sender = account.address_from_private_key(private_key)

    approval_teal = compileTeal(dice_game.approval_program(), mode=Mode.Application, version=6)
    clear_teal = compileTeal(dice_game.clear_state_program(), mode=Mode.Application, version=6)

    approval_result = algod_client.compile(approval_teal)
    clear_result = algod_client.compile(clear_teal)

    global_schema = StateSchema(num_uints=1, num_byte_slices=0)
    local_schema = StateSchema(num_uints=0, num_byte_slices=0)

    params = algod_client.suggested_params()
    txn = ApplicationCallTxn(
        sender,
        params,
        OnComplete.NoOpOC,
        approval_result["result"],
        clear_result["result"],
        global_schema,
        local_schema
    )
    signed_txn = txn.sign(private_key)
    txid = algod_client.send_transaction(signed_txn)
    print("Transaction ID:", txid)

    from algosdk.future.transaction import wait_for_confirmation
    response = wait_for_confirmation(algod_client, txid, 4)
    print("Deployed App ID:", response["application-index"])

if __name__ == "__main__":
    creator_mnemonic = input("Enter your Algorand mnemonic: ")
    deploy_app(creator_mnemonic)
