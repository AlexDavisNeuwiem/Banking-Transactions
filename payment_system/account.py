from dataclasses import dataclass

from utils.currency import Currency
from utils.logger import LOGGER

from threading import RLock

@dataclass
class Account:
    """
    Uma classe para representar uma conta bancária.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id: int
        Identificador da conta bancária.
    _bank_id: int
        Identificador do banco no qual a conta bancária foi criada.
    currency : Currency
        Moeda corrente da conta bancária.
    account_lock: Lock
        Mutex que impede que duas ou mais threads modifiquem o saldo ao mesmo tempo
    balance : int
        Saldo da conta bancária.
    overdraft_limit : int
        Limite de cheque especial da conta bancária.

    Métodos
    -------
    info() -> None:
        Printa informações sobre a conta bancária.
    deposit(amount: int) -> None:
        Adiciona o valor `amount` ao saldo da conta bancária.
    withdraw(amount: int) -> list[bool, int]:
        Remove o valor `amount` do saldo da conta bancária.
    """

    _id: int
    _bank_id: int
    currency: Currency
    account_lock: RLock = RLock()
    balance: int = 0
    overdraft_limit: int = 0

    def info(self) -> None:
        """
        Esse método printa informações gerais sobre a conta bancária.
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        self.account_lock.acquire()

        pretty_balance = f"{format(round(self.balance/100), ',d')}.{self.balance%100:02d} {self.currency.name}"
        pretty_overdraft_limit = f"{format(round(self.overdraft_limit/100), ',d')}.{self.overdraft_limit%100:02d} {self.currency.name}"
        LOGGER.info(f"Account::{{ _id={self._id}, _bank_id={self._bank_id}, balance={pretty_balance}, overdraft_limit={pretty_overdraft_limit} }}")

        self.account_lock.release()


    def deposit(self, amount: int) -> bool:
        """
        Esse método deverá adicionar o valor `amount` passado como argumento ao saldo da conta bancária 
        (`balance`). Lembre-se que esse método pode ser chamado concorrentemente por múltiplos 
        PaymentProcessors, então modifique-o para garantir que não ocorram erros de concorrência!
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES NECESSÁRIAS NESTE MÉTODO !

        self.account_lock.acquire()

        self.balance += amount
        LOGGER.info(f"deposit({amount}) successful!")

        self.account_lock.release()

        return True


    def withdraw(self, amount: int) -> list:
        """
        Esse método deverá retirar o valor `amount` especificado do saldo da conta bancária (`balance`).
        Deverá ser retornado um valor bool indicando se foi possível ou não realizar a retirada.
        Lembre-se que esse método pode ser chamado concorrentemente por múltiplos PaymentProcessors, 
        então modifique-o para garantir que não ocorram erros de concorrência!
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES NECESSÁRIAS NESTE MÉTODO !

        result = [False, 0]

        self.account_lock.acquire()

        if self.balance >= amount:
            self.balance -= amount
            result = [True, 0]
            LOGGER.info(f"withdraw({amount}) successful!")
            self.account_lock.release()
            return result
        else:
            overdrafted_amount = abs(self.balance - amount)
            if self.overdraft_limit >= overdrafted_amount:
                self.balance = self.balance - (amount + 0.05*overdrafted_amount)
                result = [True, overdrafted_amount]
                LOGGER.info(f"withdraw({amount}) successful with overdraft!")
                self.account_lock.release()
                return result
            else:
                result = [False, 0]
                LOGGER.warning(f"withdraw({amount}) failed, no balance!")
                self.account_lock.release()
                return result


@dataclass
class CurrencyReserves:
    """
    Uma classe de dados para armazenar as reservas do banco, que serão usadas
    para câmbio e transferências internacionais.
    OBS: NÃO É PERMITIDO ALTERAR ESSA CLASSE!
    """

    USD: Account = Account(_id=1, _bank_id=0, currency=Currency.USD)
    EUR: Account = Account(_id=2, _bank_id=0, currency=Currency.EUR)
    GBP: Account = Account(_id=3, _bank_id=0, currency=Currency.GBP)
    JPY: Account = Account(_id=4, _bank_id=0, currency=Currency.JPY)
    CHF: Account = Account(_id=5, _bank_id=0, currency=Currency.CHF)
    BRL: Account = Account(_id=6, _bank_id=0, currency=Currency.BRL)
