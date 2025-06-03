from algosdk.v2client import algod
from algosdk.future.transaction import ApplicationCreateTxn, StateSchema, OnComplete
from algosdk import account, mnemonic
import json

ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

def deploy_app(creator_mnemonic):
    from pyteal import compileTeal, Mode
    import dice_game

    private_key = mnemonic.to_private_key(creator_mnemonic)
    sender = account.address_from_private_key(private_key)

    # Compile PyTeal to TEAL
    approval_teal = compileTeal(dice_game.approval_program(), mode=Mode.Application, version=6)
    clear_teal = compileTeal(dice_game.clear_state_program(), mode=Mode.Application, version=6)

    # Compile TEAL to bytes using algod
    approval_result = algod_client.compile(approval_teal)
    clear_result = algod_client.compile(clear_teal)
    approval_program = bytes.fromhex(approval_result["result"])
    clear_program = bytes.fromhex(clear_result["result"])

    # Define state schemas
    global_schema = StateSchema(num_uints=1, num_byte_slices=0)
    local_schema = StateSchema(num_uints=0, num_byte_slices=0)

    # Get suggested params
    params = algod_client.suggested_params()

    # Create application creation transaction
    txn = ApplicationCreateTxn(
        sender=sender,
        sp=params,
        on_complete=OnComplete.NoOpOC,
        approval_program=approval_program,
        clear_program=clear_program,
        global_schema=global_schema,
        local_schema=local_schema
    )

    # Sign and send the transaction
    signed_txn = txn.sign(private_key)
    txid = algod_client.send_transaction(signed_txn)
    print("Transaction ID:", txid)

    # Wait for confirmation
    from algosdk.future.transaction import wait_for_confirmation
    response = wait_for_confirmation(algod_client, txid, 4)
    print("Deployed App ID:", response["application-index"])

if __name__ == "__main__":
    creator_mnemonic = input("Enter your Algorand mnemonic: ")
    deploy_app(creator_mnemonic)
