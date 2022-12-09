from random import randint
import time
from threading import Thread, Semaphore

from globals import *
from payment_system.bank import Bank
from utils.transaction import Transaction
from utils.currency import Currency
from utils.logger import LOGGER

import queue

class TransactionGenerator(Thread):
    """
    Uma classe para gerar e simular clientes de um banco por meio da geracão de transações bancárias.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do gerador de transações.
    bank: Bank
        Banco sob o qual o gerador de transações operará.

    Métodos
    -------
    run():
        ....
    """

    def __init__(self, _id: int, bank: Bank):
        Thread.__init__(self)
        self._id  = _id
        self.bank = bank


    def run(self):
        """
        Esse método deverá gerar transacões aleatórias enquanto o banco (self._bank_id)
        estiver em operação.
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        LOGGER.info(f"Inicializado TransactionGenerator para o Banco Nacional {self.bank._id}!")

        i = 0
        while banks[self.bank._id].operating :
            orig_posit = randint(0, len(banks[self.bank._id].accounts) - 1)
            orig_account = banks[self.bank._id].accounts[orig_posit]._id
            origin = (self.bank._id, orig_account)

            destination_bank = randint(0, 5)
            dest_posit = randint(0, len(banks[destination_bank].accounts) - 1)
            dest_account = banks[destination_bank].accounts[dest_posit]._id
            destination = (destination_bank, dest_account)

            amount = randint(100, 1000000)
            new_transaction = Transaction(i, origin, destination, amount, currency=Currency(destination_bank+1))
            banks[self.bank._id].queue_mutex.acquire()
            banks[self.bank._id].transaction_queue.put(new_transaction)
            banks[self.bank._id].queue_mutex.release()
            banks[self.bank._id].queue_sem.release()
            i += 1
            time.sleep(0.2 * time_unit)

        LOGGER.info(f"O TransactionGenerator {self._id} do banco {self.bank._id} foi finalizado.")

