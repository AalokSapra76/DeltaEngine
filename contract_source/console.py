from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich import box


def prompt_choice(prompt, choices):

    while True:

        value = input(prompt).strip().upper()

        if value in choices:
            return value

        print(
            "Enter one of: "
            + ", ".join(choices)
        )


def prompt_expiry():

    while True:

        value = input(
            "Expiry (YYYY-MM-DD) : "
        ).strip()

        try:
            datetime.strptime(
                value,
                "%Y-%m-%d"
            )

            return value

        except ValueError:

            print(
                "Enter expiry as YYYY-MM-DD."
            )


def prompt_number(prompt):

    while True:

        try:

            return float(
                input(prompt).strip()
            )

        except ValueError:

            print(
                "Enter a valid number."
            )


def build_contract_summary(contracts):

    table = Table(
        title="Configured Contracts",
        box=box.ROUNDED
    )

    table.add_column(
        "Instrument",
        style="cyan"
    )

    table.add_column("Expiry")

    table.add_column(
        "Strike",
        justify="right"
    )

    table.add_column(
        "Type",
        justify="center"
    )

    table.add_column(
        "Condition",
        justify="center"
    )

    table.add_column(
        "Threshold",
        justify="right"
    )

    for contract in contracts:

        table.add_row(
            contract["instrument"],
            contract["expiry"],
            f"{contract['strike']:g}",
            contract["option_type"],
            contract["trigger_direction"],
            f"{contract['delta_threshold']:.4f}",
        )

    return table


def configure_contracts():

    contracts = []

    while True:

        print()

        print(
            f"Contract {len(contracts) + 1}"
        )

        print("-" * 20)

        contract = {

            "instrument": prompt_choice(

                "Instrument (NIFTY/BANKNIFTY/FINNIFTY) : ",

                (
                    "NIFTY",
                    "BANKNIFTY",
                    "FINNIFTY"
                )

            ),

            "expiry": prompt_expiry(),

            "strike": prompt_number(
                "Strike : "
            ),

            "option_type": prompt_choice(

                "Option Type (CE/PE) : ",

                (
                    "CE",
                    "PE"
                )

            ),

            "trigger_direction": prompt_choice(

                "Trigger Direction (>/<) : ",

                (
                    ">",
                    "<"
                )

            ),

            "delta_threshold": prompt_number(

                "Delta Threshold : "

            ),

        }

        contracts.append(contract)

        if prompt_choice(

            "Add another contract? (Y/N) : ",

            (
                "Y",
                "N"
            )

        ) == "N":

            break

    print()

    Console().print(

        build_contract_summary(
            contracts
        )

    )

    print()

    if prompt_choice(

        "Start Monitoring? (Y/N) : ",

        (
            "Y",
            "N"
        )

    ) == "N":

        print(
            "Monitoring cancelled."
        )

        raise SystemExit(0)

    return contracts


def get_contracts():

    return configure_contracts()