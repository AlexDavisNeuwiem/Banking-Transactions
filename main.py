import argparse, time, sys
from logging import INFO, DEBUG
from random import randint

from globals import *
from payment_system.bank import Bank
from payment_system.payment_processor import PaymentProcessor
from payment_system.transaction_generator import TransactionGenerator
from utils.currency import Currency
from utils.logger import CH, LOGGER


if __name__ == "__main__":
    # Verificação de compatibilidade da versão do python:
    if sys.version_info < (3, 5):
        sys.stdout.write('Utilize o Python 3.5 ou mais recente para desenvolver este trabalho.\n')
        sys.exit(1)

    # Captura de argumentos da linha de comando:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time_unit", "-u", help="Valor da unidade de tempo de simulação")
    parser.add_argument("--total_time", "-t", help="Tempo total de simulação")
    parser.add_argument("--debug", "-d", help="Printar logs em nível DEBUG")
    args = parser.parse_args()
    if args.time_unit:
        time_unit = float(args.time_unit)
    if args.total_time:
        total_time = int(args.total_time)
    if args.debug:
        debug = True

    # Configura logger
    if debug:
        LOGGER.setLevel(DEBUG)
        CH.setLevel(DEBUG)
    else:
        LOGGER.setLevel(INFO)
        CH.setLevel(INFO)

    # Printa argumentos capturados da simulação
    LOGGER.info(f"Iniciando simulação com os seguintes parâmetros:\n\ttotal_time = {total_time}\n\tdebug = {debug}\n")
    time.sleep(3)

    # Inicializa variável `tempo`:
    t = 0
    
    # Cria os Bancos Nacionais e popula a lista global `banks`:
    for i, currency in enumerate(Currency):
        
        # Cria Banco Nacional
        bank = Bank(_id=i, currency=currency)
        
        # Deposita valores aleatórios nas contas internas (reserves) do banco
        bank.reserves.BRL.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.CHF.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.EUR.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.GBP.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.JPY.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.USD.deposit(randint(100_000_000, 10_000_000_000))
        
        # Adiciona banco na lista global de bancos
        banks.append(bank)

    # Cria m contas em cada banco
    m = 50
    for i, bank in enumerate(banks):
        for j in range(m):
            new_balance = randint(100, 1000000)
            new_over_lim = randint(100, 1000000)
            bank.new_account(new_balance, new_over_lim)

    # Inicializa gerador de transações e processadores de pagamentos para os Bancos Nacionais:
    n = 10
    TransGens = []
    PayProcs = []

    for i, bank in enumerate(banks):
        # Inicializa um TransactionGenerator thread por banco:
        tg = TransactionGenerator(_id=i, bank=bank)
        TransGens.append(tg)
        # Inicializa um PaymentProcessor thread por banco.
        for j in range(n):
            pp = PaymentProcessor(_id=(n*i+j), bank=bank)
            PayProcs.append(pp)

    for i, bank in enumerate(banks):
        # Inicializa um TransactionGenerator thread por banco:
        TransGens[i].start()
        # Inicializa um PaymentProcessor thread por banco.
        # Sua solução completa deverá funcionar corretamente com múltiplos PaymentProcessor threads para cada banco.
        for j in range(n):
            PayProcs[n*i+j].start()

    # Enquanto o tempo total de simuação não for atingido:
    while t < total_time:
        dt = randint(0, 3)
        time.sleep(dt * time_unit)
        t += dt

    # Finaliza todas as threads
    for i, bank in enumerate(banks):
        # Finalizando os TransactionGenerators
        TransGens[i].join()
        # Finalizando os PaymentProcessors
        for j in range(n):
            PayProcs[n*i+j].join()

    for i, bank in enumerate(banks):
        bank.operating = False

    # Termina simulação. Após esse print somente dados devem ser printados no console.
    LOGGER.info(f"A simulação chegou ao fim!\n")

    for i, bank in enumerate(banks):
        bank.info()
