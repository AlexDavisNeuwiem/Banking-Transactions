from threading import Lock

# Lista de Bancos Nacionais
banks = []

# Printar Logs de DEBUG no console?
debug = False

# Armazena a quantidade de Payment_Processors que não finalizaram
not_finalized = 0

# Lock que bloqueia acesso à variável "not_finalized"
not_fin_lock = Lock()

# Tempo total de simulação
total_time = 1000

# Unidade de tempo (quanto menor, mais rápida a simulação)
time_unit = 0.1  # 0.1 = 100ms
