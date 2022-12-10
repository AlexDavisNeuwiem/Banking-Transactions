import time
from threading import Thread, Lock, Semaphore
from typing import Tuple

from globals import *
from payment_system.bank import Bank
from utils.transaction import Transaction, TransactionStatus
from utils.currency import *
from utils.logger import LOGGER

class PaymentProcessor(Thread):
    """
    Uma classe para representar um processador de pagamentos de um banco.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do processador de pagamentos.
    bank: Bank
        Banco sob o qual o processador de pagamentos operará.

    Métodos
    -------
    run():
        Inicia thread to PaymentProcessor
    process_transaction(transaction: Transaction) -> TransactionStatus:
        Processa uma transação bancária.
    new_ncnl_transfer(self, origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> bool:
        Realiza as transações nacionais de um dado banco
    new_inter_transfer(self, origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> bool:
        Realiza as transações internacionais de um dado banco
    """

    def __init__(self, _id: int, bank: Bank):
        Thread.__init__(self)
        self._id  = _id
        self.bank = bank


    def run(self):
        """
        Esse método deve buscar Transactions na fila de transações do banco e processá-las 
        utilizando o método self.process_transaction(self, transaction: Transaction).
        Ele não deve ser finalizado prematuramente (antes do banco realmente fechar).
        """
        # TODO: IMPLEMENTE/MODIFIQUE O CÓDIGO NECESSÁRIO ABAIXO !

        LOGGER.info(f"Inicializado o PaymentProcessor {self._id} do Banco {self.bank._id}!")
        trans_queue = banks[self.bank._id].transaction_queue

        while banks[self.bank._id].operating :
            try:
                banks[self.bank._id].queue_sem.acquire()
                if not(banks[self.bank._id].operating) :
                    break
                banks[self.bank._id].queue_lock.acquire()
                transaction = trans_queue.pop(0)
                LOGGER.info(f"Transaction_queue do Banco {self.bank._id}: {[trans._id for trans in trans_queue]}")
                banks[self.bank._id].queue_lock.release()
            except Exception as err:
                LOGGER.error(f"Falha em PaymentProcessor.run(): {err}")
            else:
                self.process_transaction(transaction)
        LOGGER.info(f"O PaymentProcessor {self._id} do banco {self.bank._id} foi finalizado.")

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

    def process_transaction(self, transaction: Transaction) -> TransactionStatus:
        """
        Esse método deverá processar as transações bancárias do banco ao qual foi designado.
        Caso a transferência seja realizada para um banco diferente (em moeda diferente), a 
        lógica para transações internacionais detalhada no enunciado (README.md) deverá ser
        aplicada.
        Ela deve retornar o status da transacão processada.
        """
        # TODO: IMPLEMENTE/MODIFIQUE O CÓDIGO NECESSÁRIO ABAIXO !

        LOGGER.info(f"PaymentProcessor {self._id} do Banco {self.bank._id} iniciando processamento da Transaction {transaction._id}!")

        result = False

        if transaction.origin[0] != transaction.destination[0] :
            result = self.new_inter_transfer(transaction.origin, transaction.destination, transaction.amount, transaction.currency)
        else:
            result = self.new_ncnl_transfer(transaction.origin, transaction.destination, transaction.amount, transaction.currency)

        # NÃO REMOVA ESSE SLEEP!
        # Ele simula uma latência de processamento para a transação.
        time.sleep(3 * time_unit)

        if result == False :
            transaction.set_status(TransactionStatus.FAILED)
        else:
            transaction.set_status(TransactionStatus.SUCCESSFUL)

        self.bank.total_trans_lock.acquire()
        self.bank.total_trans += 1
        self.bank.total_trans_time += transaction.get_processing_time().total_seconds()
        self.bank.total_trans_lock.release()

        return transaction.status
