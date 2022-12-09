from typing import Tuple
from threading import Thread, Lock, RLock, Semaphore

from globals import *
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
    profit: float
        Float que representa o lucro do banco
    ncnl: int
        Inteiro que representa o total de transações nacionais realizadas
    inter: int
        Inteiro que representa o total de transações internacionais realizadas

    Métodos
    -------
    new_account(balance: int = 0, overdraft_limit: int = 0) -> None:
        Cria uma nova conta bancária (Account) no banco.
    new_transfer(origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> bool:
        Cria uma nova transação bancária.
    info() -> None:
        Printa informações e estatísticas sobre o funcionamento do banco.
    
    """

    def __init__(self, _id: int, currency: Currency):
        self._id                = _id
        self.currency           = currency
        self.reserves           = CurrencyReserves()
        self.operating          = True
        self.accounts           = []

        self.transaction_queue  = queue.Queue()
        self.queue_lock         = Lock()
        self.queue_mutex        = Lock()
        self.queue_sem          = Semaphore(0)

        self.profit             = 0
        self.profit_lock        = Lock()

        self.ncnl               = 0
        self.ncnl_lock          = Lock()

        self.inter              = 0
        self.inter_lock         = Lock()

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

    def new_ncnl_transfer(origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> bool:
        result = banks[origin[0]].accounts[origin[1]].withdraw(banks[origin[0]].accounts[origin[1]], amount)
        if result[0] == False :
            return False
        banks[origin[0]].profit_lock.acquire()
        banks[origin[0]].profit += 0.05*result[1]
        banks[origin[0]].profit_lock.release()
        banks[destination[0]].accounts[destination[1]].deposit(banks[destination[0]].accounts[destination[1]], amount)
        banks[origin[0]].ncnl_lock.acquire()
        banks[origin[0]].ncnl += 1
        banks[origin[0]].ncnl_lock.release()
        return True

    def new_inter_transfer(origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> bool:

            """
            - Sou conta BRL e quero transferir 200 USD para uma conta externa
            - Com rate de 1 USD = 5 BRL, tenho que transferir 1000 BRL
            - Primeiro transfiro os 1000 BRLs para o banco BRL (+ taxa de câmbio 0.01*1000)
                - withdraw 1000+10 BRL da conta de origem
                - deposit 1000+10 BRL na conta do banco de origem
                - withdraw 200 USD da conta do banco de origem
                - deposit 200 USD na conta destino
            """

            # Convertendo as moedas
            exchange_rate = banks[origin[0]].currency.get_exchange_rate(banks[origin[0]].currency, banks[destination[0]].currency)

            # Calculando o valor com taxa de câmbio
            new_amount = amount*exchange_rate + 0.01*amount*exchange_rate

            # Fazendo o Lock na conta origem
            banks[origin[0]].accounts[origin[1]].account_lock.acquire()

            # Fazer um if e lock com todas as contas especiais e verificar se tudo funciona certinho

            # Fim do teste

            # Retirando o valor com taxa de câmbio da conta origem
            result = banks[origin[0]].accounts[origin[1]].withdraw(banks[origin[0]].accounts[origin[1]], new_amount)

            banks[origin[0]].profit_lock.acquire()
            banks[origin[0]].profit += 0.05*result[1]
            banks[origin[0]].profit_lock.release()

            # Depositando o valor com taxa de câmbio na conta especial de moeda origem
            if banks[origin[0]].currency == 1 :
                banks[origin[0]].reserves.USD.deposit(banks[origin[0]].reserves.USD, new_amount)
                
            elif banks[origin[0]].currency == 2 :
                banks[origin[0]].reserves.EUR.deposit(banks[origin[0]].reserves.EUR, new_amount)
                
            elif banks[origin[0]].currency == 3 :
                banks[origin[0]].reserves.GBP.deposit(banks[origin[0]].reserves.GBP, new_amount)

            elif banks[origin[0]].currency == 4 :
                banks[origin[0]].reserves.JPY.deposit(banks[origin[0]].reserves.JPY, new_amount)
                
            elif banks[origin[0]].currency == 5 :
                banks[origin[0]].reserves.CHF.deposit(banks[origin[0]].reserves.CHF, new_amount)
                
            else:
                banks[origin[0]].reserves.BRL.deposit(banks[origin[0]].reserves.BRL, new_amount)

            # Retirando o valor sem taxa de cãmbio da conta especial de moeda destino
            if banks[destination[0]].currency == 1 :
                banks[origin[0]].reserves.USD.withdraw(banks[origin[0]].reserves.USD, amount)
                
            elif banks[destination[0]].currency == 2 :
                banks[origin[0]].reserves.EUR.withdraw(banks[origin[0]].reserves.EUR, amount)
                
            elif banks[destination[0]].currency == 3 :
                banks[origin[0]].reserves.GBP.withdraw(banks[origin[0]].reserves.GBP, amount)

            elif banks[destination[0]].currency == 4 :
                banks[origin[0]].reserves.JPY.withdraw(banks[origin[0]].reserves.JPY, amount)
                
            elif banks[destination[0]].currency == 5 :
                banks[origin[0]].reserves.CHF.withdraw(banks[origin[0]].reserves.CHF, amount)
                
            else:
                banks[origin[0]].reserves.BRL.withdraw(banks[origin[0]].reserves.BRL, amount)
            
            # Depositando o valor sem taxa de câmbio na conta destino
            banks[destination[0]].accounts[destination[1]].deposit(banks[destination[0]].accounts[destination[1]], amount)

            banks[origin[0]].inter_lock.acquire()
            banks[origin[0]].inter += 1
            banks[origin[0]].inter_lock.release()

            # Unlock em todas as contas que fizeram Lock
            banks[origin[0]].accounts[origin[1]].account_lock.release()

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
        LOGGER.info(f"      Lucro = {self.profit}")
        LOGGER.info(f"--------------------------------------------------------------------------------------")