from typing import Tuple

from payment_system.account import Account, CurrencyReserves
from utils.transaction import Transaction
from utils.currency import Currency
from utils.logger import LOGGER

import queue

class Bank():
    """
    Uma classe para representar um Banco.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do banco.
    currency : Currency
        Moeda corrente das contas bancárias do banco.
    reserves : CurrencyReserves
        Dataclass de contas bancárias contendo as reservas internas do banco.
    operating : bool
        Booleano que indica se o banco está em funcionamento ou não.
    accounts : List[Account]
        Lista contendo as contas bancárias dos clientes do banco.
    transaction_queue : Queue[Transaction]
        Fila FIFO contendo as transações bancárias pendentes que ainda serão processadas.

    Métodos
    -------
    new_account(balance: int = 0, overdraft_limit: int = 0) -> None:
        Cria uma nova conta bancária (Account) no banco.
    new_transfer(origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> None:
        Cria uma nova transação bancária.
    info() -> None:
        Printa informações e estatísticas sobre o funcionamento do banco.
    
    """

    def __init__(self, _id: int, currency: Currency):
        self._id                = _id
        self.currency           = currency
        self.reserves           = CurrencyReserves()
        self.operating          = False
        self.accounts           = []
        self.transaction_queue  = queue.Queue()
        self.lucro              = 0
        self.ncnl               = 0
        self.inter              = 0


    def new_account(self, balance: int = 0, overdraft_limit: int = 0) -> None:
        """
        Esse método deverá criar uma nova conta bancária (Account) no banco com determinado 
        saldo (balance) e limite de cheque especial (overdraft_limit).
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        # Gera _id para a nova Account
        acc_id = len(self.accounts) + 1

        # Cria instância da classe Account
        acc = Account(_id=acc_id, _bank_id=self._id, currency=self.currency, balance=balance, overdraft_limit=overdraft_limit)
  
        # Adiciona a Account criada na lista de contas do banco
        self.accounts.append(acc)

    def new_transfer(origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> None:
        # Implementar
        return

    def info(self) -> None:
        """
        Essa função deverá printar os seguintes dados utilizando o LOGGER fornecido:
        1. Saldo de cada moeda nas reservas internas do banco
        2. Número de transferências nacionais e internacionais realizadas
        3. Número de contas bancárias registradas no banco
        4. Saldo total de todas as contas bancárias (dos clientes) registradas no banco
        5. Lucro do banco: taxas de câmbio acumuladas + juros de cheque especial acumulados
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        LOGGER.info(f"--------------------------------------------------------------------------------------")
        LOGGER.info(f"Estatísticas do Banco Nacional {self._id}:")

        LOGGER.info(f"  1) Saldo de cada moeda nas reservas internas do banco")
        LOGGER.info(f"      USD = {self.reserves.USD.balance}")
        LOGGER.info(f"      EUR = {self.reserves.EUR.balance}")
        LOGGER.info(f"      GBP = {self.reserves.GBP.balance}")
        LOGGER.info(f"      JPY = {self.reserves.JPY.balance}")
        LOGGER.info(f"      CHF = {self.reserves.CHF.balance}")
        LOGGER.info(f"      BRL = {self.reserves.BRL.balance}")

        LOGGER.info(f"  2) Número de transferências nacionais e internacionais realizadas")
        LOGGER.info(f"      Nacionais = {self.ncnl}")
        LOGGER.info(f"      Interacionais = {self.inter}")

        LOGGER.info(f"  3) Número de contas bancárias registradas no banco")
        LOGGER.info(f"      Total de contas = {len(self.accounts)}")
        
        LOGGER.info(f"  4) Saldo total de todas as contas bancárias (dos clientes) registradas no banco")
        total = 0
        for i in range(len(self.accounts)):
            total += self.accounts[i].balance
        LOGGER.info(f"      Saldo das {len(self.accounts)} contas = {total}")

        LOGGER.info(f"  5) Lucro do banco (taxas de câmbio acumuladas + juros de cheque especial acumulados)")
        LOGGER.info(f"      Lucro = {self.lucro}")
        LOGGER.info(f"--------------------------------------------------------------------------------------")