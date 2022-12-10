from typing import Tuple
from threading import Thread, Lock, RLock, Semaphore

from globals import *
from payment_system.account import Account, CurrencyReserves
from utils.transaction import Transaction
from utils.currency import *
from utils.logger import LOGGER

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
    queue_lock: Lock
        Lock que impede que dois ou mais Payment_Processors acessem uma mesma posição da Transaction_Queue ao mesmo tempo
    queue_mutex: Lock
        Lock que impede que dois ou mais Transaction_Generators acessem uma mesma posição da Transaction_Queue ao mesmo tempo
    queue_sem: Semaphore
        Semáforo que impede a espera ocupada dos Payment_Processors
    profit: float
        Float que representa o lucro do banco
    profit_lock: Lock
        Lock que impede que duas ou mais threads alterem a variável profit ao mesmo tempo
    ncnl: int
        Inteiro que representa o total de transações nacionais realizadas
    ncnl_lock: Lock
        Lock que impede que duas ou mais threads alterem a variável ncnl ao mesmo tempo
    inter: int
        Inteiro que representa o total de transações internacionais realizadas
    inter_lock: Lock
        Lock que impede que duas ou mais threads alterem a variável inter ao mesmo tempo

    Métodos
    -------
    new_account(balance: int = 0, overdraft_limit: int = 0) -> None:
        Cria uma nova conta bancária (Account) no banco.
    new_ncnl_transfer(self, origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> bool:
        Realiza as transações nacionais de um dado banco
    new_inter_transfer(self, origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> bool:
        Realiza as transações internacionais de um dado banco
    info() -> None:
        Printa informações e estatísticas sobre o funcionamento do banco.
    
    """

    def __init__(self, _id: int, currency: Currency):
        self._id                = _id
        self.currency           = currency
        self.reserves           = CurrencyReserves()
        self.operating          = True
        self.accounts           = []

        self.transaction_queue  = []
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
        acc_id = len(self.accounts)

        # Cria instância da classe Account
        acc = Account(_id=acc_id, _bank_id=self._id, currency=self.currency, balance=balance, overdraft_limit=overdraft_limit)
  
        # Adiciona a Account criada na lista de contas do banco
        self.accounts.append(acc)

    def new_ncnl_transfer(self, origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> bool:
        result = banks[origin[0]].accounts[origin[1]].withdraw(amount)
        if result[0] == False :
            return False
        banks[origin[0]].profit_lock.acquire()
        banks[origin[0]].profit += 0.05*result[1]
        banks[origin[0]].profit_lock.release()
        banks[destination[0]].accounts[destination[1]].deposit(amount)
        banks[origin[0]].ncnl_lock.acquire()
        banks[origin[0]].ncnl += 1
        banks[origin[0]].ncnl_lock.release()
        return True

    def new_inter_transfer(self, origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> bool:
            # Convertendo as moedas
            exchange_rate = get_exchange_rate(banks[origin[0]].currency, banks[destination[0]].currency)

            # Calculando o valor com taxa de câmbio
            new_amount = amount*exchange_rate + 0.01*amount*exchange_rate

            # Fazendo o Lock na conta origem
            banks[origin[0]].accounts[origin[1]].account_lock.acquire()

            # Verificando se é possível realizar a transferência
            if (banks[origin[0]].accounts[origin[1]].balance + banks[origin[0]].accounts[origin[1]].overdraft_limit) < new_amount :
                banks[origin[0]].accounts[origin[1]].account_lock.release()
                return False

            if banks[destination[0]].currency == 1 :
                # Fazendo o Lock na conta especial
                banks[origin[0]].reserves.USD.account_lock.acquire()
                # Verificando se é possível realizar a transferência
                if (banks[origin[0]].reserves.USD.balance + banks[origin[0]].reserves.USD.overdraft_limit) < amount :
                    banks[origin[0]].reserves.USD.account_lock.release()
                    banks[origin[0]].accounts[origin[1]].account_lock.release()
                    return False
                
            elif banks[destination[0]].currency == 2 :
                # Fazendo o Lock na conta especial
                banks[origin[0]].reserves.EUR.account_lock.acquire()
                # Verificando se é possível realizar a transferência
                if (banks[origin[0]].reserves.EUR.balance + banks[origin[0]].reserves.EUR.overdraft_limit) < amount :
                    banks[origin[0]].reserves.EUR.account_lock.release()
                    banks[origin[0]].accounts[origin[1]].account_lock.release()
                    return False
                
            elif banks[destination[0]].currency == 3 :
                # Fazendo o Lock na conta especial
                banks[origin[0]].reserves.GBP.account_lock.acquire()
                # Verificando se é possível realizar a transferência
                if (banks[origin[0]].reserves.GBP.balance + banks[origin[0]].reserves.GBP.overdraft_limit) < amount :
                    banks[origin[0]].reserves.GBP.account_lock.release()
                    banks[origin[0]].accounts[origin[1]].account_lock.release()
                    return False

            elif banks[destination[0]].currency == 4 :
                # Fazendo o Lock na conta especial
                banks[origin[0]].reserves.JPY.account_lock.acquire()
                # Verificando se é possível realizar a transferência
                if (banks[origin[0]].reserves.JPY.balance + banks[origin[0]].reserves.JPY.overdraft_limit) < amount :
                    banks[origin[0]].reserves.JPY.account_lock.release()
                    banks[origin[0]].accounts[origin[1]].account_lock.release()
                    return False
                
            elif banks[destination[0]].currency == 5 :
                # Fazendo o Lock na conta especial
                banks[origin[0]].reserves.CHF.account_lock.acquire()
                # Verificando se é possível realizar a transferência
                if (banks[origin[0]].reserves.CHF.balance + banks[origin[0]].reserves.CHF.overdraft_limit) < amount :
                    banks[origin[0]].reserves.CHF.account_lock.release()
                    banks[origin[0]].accounts[origin[1]].account_lock.release()
                    return False
                
            else:
                # Fazendo o Lock na conta especial
                banks[origin[0]].reserves.BRL.account_lock.acquire()
                # Verificando se é possível realizar a transferência
                if (banks[origin[0]].reserves.BRL.balance + banks[origin[0]].reserves.BRL.overdraft_limit) < amount :
                    banks[origin[0]].reserves.BRL.account_lock.release()
                    banks[origin[0]].accounts[origin[1]].account_lock.release()
                    return False

            # Retirando o valor com taxa de câmbio da conta origem
            result = banks[origin[0]].accounts[origin[1]].withdraw(new_amount)
            
            # Unlock em todas as contas que fizeram Lock
            banks[origin[0]].accounts[origin[1]].account_lock.release()

            banks[origin[0]].profit_lock.acquire()
            banks[origin[0]].profit += 0.05*result[1]
            banks[origin[0]].profit_lock.release()

            # Depositando o valor com taxa de câmbio na conta especial de moeda origem
            if banks[origin[0]].currency == 1 :
                banks[origin[0]].reserves.USD.deposit(new_amount)
                
            elif banks[origin[0]].currency == 2 :
                banks[origin[0]].reserves.EUR.deposit(new_amount)
                
            elif banks[origin[0]].currency == 3 :
                banks[origin[0]].reserves.GBP.deposit(new_amount)

            elif banks[origin[0]].currency == 4 :
                banks[origin[0]].reserves.JPY.deposit(new_amount)
                
            elif banks[origin[0]].currency == 5 :
                banks[origin[0]].reserves.CHF.deposit(new_amount)
                
            else:
                banks[origin[0]].reserves.BRL.deposit(new_amount)

            # Retirando o valor sem taxa de cãmbio da conta especial de moeda destino
            if banks[destination[0]].currency == 1 :
                result = banks[origin[0]].reserves.USD.withdraw(amount)
                banks[origin[0]].reserves.USD.account_lock.release()
                fixing = 0.05*result[1]
                banks[origin[0]].reserves.USD.deposit(fixing)
                
            elif banks[destination[0]].currency == 2 :
                result = banks[origin[0]].reserves.EUR.withdraw(amount)
                banks[origin[0]].reserves.EUR.account_lock.release()
                fixing = 0.05*result[1]
                banks[origin[0]].reserves.EUR.deposit(fixing)
                
            elif banks[destination[0]].currency == 3 :
                result = banks[origin[0]].reserves.GBP.withdraw(amount)
                banks[origin[0]].reserves.GBP.account_lock.release()
                fixing = 0.05*result[1]
                banks[origin[0]].reserves.GBP.deposit(fixing)

            elif banks[destination[0]].currency == 4 :
                result = banks[origin[0]].reserves.JPY.withdraw(amount)
                banks[origin[0]].reserves.JPY.account_lock.release()
                fixing = 0.05*result[1]
                banks[origin[0]].reserves.JPY.deposit(fixing)
                
            elif banks[destination[0]].currency == 5 :
                result = banks[origin[0]].reserves.CHF.withdraw(amount)
                banks[origin[0]].reserves.CHF.account_lock.release()
                fixing = 0.05*result[1]
                banks[origin[0]].reserves.CHF.deposit(fixing)
                
            else:
                result = banks[origin[0]].reserves.BRL.withdraw(amount)
                banks[origin[0]].reserves.BRL.account_lock.release()
                fixing = 0.05*result[1]
                banks[origin[0]].reserves.BRL.deposit(fixing)
            
            # Depositando o valor sem taxa de câmbio na conta destino
            banks[destination[0]].accounts[destination[1]].deposit(amount)

            banks[origin[0]].inter_lock.acquire()
            banks[origin[0]].inter += 1
            banks[origin[0]].inter_lock.release()

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

        LOGGER.info(f"------------------------------ Estatísticas do Banco Nacional {self._id} ------------------------------")

        LOGGER.info(f"  1) Saldo de cada moeda nas reservas internas do banco:")
        LOGGER.info(f"      USD = {self.reserves.USD.balance}")
        LOGGER.info(f"      EUR = {self.reserves.EUR.balance}")
        LOGGER.info(f"      GBP = {self.reserves.GBP.balance}")
        LOGGER.info(f"      JPY = {self.reserves.JPY.balance}")
        LOGGER.info(f"      CHF = {self.reserves.CHF.balance}")
        LOGGER.info(f"      BRL = {self.reserves.BRL.balance}")

        LOGGER.info(f"  2) Número de transferências nacionais e internacionais realizadas:")
        LOGGER.info(f"      Nacionais = {self.ncnl}")
        LOGGER.info(f"      Interacionais = {self.inter}")

        LOGGER.info(f"  3) Número de contas bancárias registradas no banco:")
        LOGGER.info(f"      Total de contas = {len(self.accounts)}")
        
        LOGGER.info(f"  4) Saldo total de todas as contas bancárias (dos clientes) registradas no banco:")
        total = 0
        for i in range(len(self.accounts)):
            total += self.accounts[i].balance
        LOGGER.info(f"      Saldo das {len(self.accounts)} contas = {total}")

        LOGGER.info(f"  5) Lucro do banco (taxas de câmbio acumuladas + juros de cheque especial acumulados):")
        LOGGER.info(f"      Lucro = {self.profit}")

        LOGGER.info(f"  6) Total de transações não concluídas:")
        LOGGER.info(f"      Transações pendentes = {len(self.transaction_queue)}")

        LOGGER.info(f"----------------------------------------------------------------------------------------------")