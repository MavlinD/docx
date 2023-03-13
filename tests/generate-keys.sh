#!/bin/sh

# https://pyjwt.readthedocs.io/en/latest/algorithms.html
# создаёт файлы ключей, в настройках вид алгоритма выбрать
# authjwt_algorithm: str = "ES256"

key_folder=.
openssl ecparam -name secp256k1 -genkey -noout -out $key_folder/priv-key.pem
openssl ec -in $key_folder/priv-key.pem -pubout > $key_folder/pub-key.pem
