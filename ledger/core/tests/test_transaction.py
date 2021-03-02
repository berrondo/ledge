from decimal import Decimal

from ledger.core.models import (
    Transaction as T,
    Ledger,
    Schema,
)
from ..calculations import Percentual

from .utils import conta


def test_venda():
    # accounts:
    cash_in = conta('cash_in')
    cash_out = conta('cash_out')

    # defining the Transaction Schema:
    Venda = T('Venda',
        d_from=cash_in,
        c_to=cash_out
    )

    # checking registered Transaction Schemas:
    assert Schema.objects.all().count() == 1

    # using the Transaction Schema:
    Venda(100).save()

    # checking transactions in the ledger
    transactions = Ledger.objects.all()
    assert transactions.count() == 1
    assert transactions[0].amount == Decimal(100)

    # checking account balances:
    assert cash_in.balance() == Decimal(-100)
    assert cash_out.balance() == Decimal(100)


def test_venda_com_desconto():
    # accounts:
    cash_in = conta('cash_in')
    cash_out = conta('cash_out')
    conta_desconto = conta('conta_desconto')

    # defining the Transaction Schema:
    VendaComDesconto10 = T('VendaComDesconto10',
        d_from=cash_in,
        c_to=cash_out)(
        T('Desconto',
            amount=10,
            c_to=conta_desconto)
    )

    # checking registered Transaction Schemas:
    assert Schema.objects.all().count() == 2

    # using the Transaction Schema:
    VendaComDesconto10(100).save()

    # checking transactions in the ledger
    transactions = Ledger.objects.all()
    assert transactions.count() == 2
    assert transactions[0].amount == Decimal(100)
    assert transactions[1].amount == Decimal(10)

    # checking account balances:
    assert cash_in.balance() == Decimal(-100)
    assert cash_out.balance() == Decimal(90)
    assert conta_desconto.balance() == Decimal(10)


def test_venda_com_imposto():
    # accounts:
    cash_in = conta('cash_in')
    cash_out = conta('cash_out')
    conta_imposto = conta('conta_imposto')

    # defining the Transaction Schema:
    VendaComImpostoPercentual = T('VendaComImpostoPercentual',
        d_from=cash_in,
        c_to=cash_out)(
        T('ImpostoPercentual',
            amount=Percentual(10),
            c_to=conta_imposto)
    )

    # checking registered Transaction Schemas:
    assert Schema.objects.all().count() == 2

    # using the Transaction Schema:
    VendaComImpostoPercentual(100).save()

    # checking transactions in the ledger
    transactions = Ledger.objects.all()
    assert transactions.count() == 2
    assert transactions[0].amount == Decimal(100)
    assert transactions[1].amount == Decimal(10)

    assert transactions[1].c_to == conta_imposto

    # checking account balances:
    assert cash_in.balance() == Decimal(-100)
    assert cash_out.balance() == Decimal(90)
    assert conta_imposto.balance() == Decimal(10)


def test_venda_com_imposc_tocom_comissao_com_imposto():
    # accounts:
    cash_in = conta('cash_in')
    cash_out = conta('cash_out')
    conta_comissao = conta('conta_comissao')
    conta_imposto = conta('conta_imposto')

    # defining the Transaction Schema:
    VendaComImpostoEComissao = T('VendaComImpostoEComissao',
        d_from=cash_in,
        c_to=cash_out)(
        T('ComissaoPercentual',
            amount=Percentual(10),
            c_to=conta_comissao)(
            T('ImpostoPercentual',
                amount=Percentual(10),
                c_to=conta_imposto)
            ),
        T('ImpostoPercentual',
            amount=Percentual(10),
            c_to=conta_imposto)
    )

    # checking registered Transaction Schemas:
    assert Schema.objects.all().count() == 3

    # using the Transaction Schema:
    VendaComImpostoEComissao(100).save()

    # checking transactions in the ledger
    transactions = Ledger.objects.all()
    assert transactions.count() == 4
    assert transactions[0].amount == Decimal(100)
    assert transactions[1].amount == Decimal(10)
    assert transactions[2].amount == Decimal(1)
    assert transactions[3].amount == Decimal(10)

    # checking account balances:
    assert cash_in.balance() == Decimal(-100)
    assert cash_out.balance() == Decimal(80)
    assert conta_comissao.balance() == Decimal(9)
    assert conta_imposto.balance() == Decimal(11)


# some proposals for Transaction Schema definition:

# Venda = Transacao(
#     'Venda',
#     d_from=conta1,
#     c_to=conta2
# )(
#     Imposto(
#         percentual=10,
#         c_to=conta3
#     )
# )


# class Venda(Transacao):
#     d_from = conta1
#     c_to = conta2
#
#     transactions = (
#         Imposto(
#             percentual=10,
#             c_to=conta3
#         ),
#     )


# class Venda(Transacao):
#     d_from = conta1
#     c_to = conta2
#
#     class Imposto:
#         percentual = 10
#         c_to = conta3
#
#         class Discount:
#             percentual = 1
