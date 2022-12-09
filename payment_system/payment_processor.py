import time
from threading import Thread, Lock, Semaphore

from globals import *
from payment_system.bank import Bank
from utils.transaction import Transaction, TransactionStatus
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
                LOGGER.info(f"Transaction_queue do Banco {self.bank._id}:")
                
                #for trans in trans_queue :
                #    LOGGER.info(f"  {trans._id}")
                
                banks[self.bank._id].queue_lock.release()
            except Exception as err:
                LOGGER.error(f"Falha em PaymentProcessor.run(): {err}")
            else:
                self.process_transaction(transaction)
        LOGGER.info(f"O PaymentProcessor {self._id} do banco {self.bank._id} foi finalizado.")


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
            result = banks[self.bank._id].new_inter_transfer(transaction.origin, transaction.destination, transaction.amount, transaction.currency)
        else:
            result = banks[self.bank._id].new_ncnl_transfer(transaction.origin, transaction.destination, transaction.amount, transaction.currency)

        # NÃO REMOVA ESSE SLEEP!
        # Ele simula uma latência de processamento para a transação.
        time.sleep(3 * time_unit)

        if result == False :
            transaction.set_status(TransactionStatus.FAILED)
            return transaction.status

        transaction.set_status(TransactionStatus.SUCCESSFUL)
        return transaction.status
