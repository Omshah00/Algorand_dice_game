from pyteal import *

def approval_program():
    stake_key = Bytes("STAKE")

    on_creation = Seq([
        App.globalPut(stake_key, Int(100000)),  # 0.1 ALGO
        Return(Int(1))
    ])

    on_roll = Seq([
        Assert(Txn.application_args.length() == Int(1)),
        Assert(Txn.application_args[0] == Bytes("roll")),
        Assert(Txn.application_call().amount() >= App.globalGet(stake_key)),

        # Pseudo-random dice roll
        dice_roll := (Global.latest_timestamp() % Int(6)) + Int(1),
        If(dice_roll >= Int(4)).Then(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: Txn.sender(),
                TxnField.amount: App.globalGet(stake_key) * Int(2),
                TxnField.fee: Int(0),
            }),
            InnerTxnBuilder.Submit()
        ),
        Approve()
    ])

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp, on_roll]
    )
    return program

def clear_state_program():
    return Approve()

if __name__ == "__main__":
    with open("approval.teal", "w") as f:
        f.write(compileTeal(approval_program(), mode=Mode.Application, version=6))

    with open("clear.teal", "w") as f:
        f.write(compileTeal(clear_state_program(), mode=Mode.Application, version=6))
