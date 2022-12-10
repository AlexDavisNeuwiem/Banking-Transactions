from threading import Lock

# Lista de Bancos Nacionais
banks = []

# Printar Logs de DEBUG no console?
debug = False

# Variável que armazena a quantidade de Payment_Processors criados
total_processors = 0

# Tempo total de simulação
total_time = 50

# Unidade de tempo (quanto menor, mais rápida a simulação)
time_unit = 1  # 0.1 = 100ms
