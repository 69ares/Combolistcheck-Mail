import imaplib
import socket
import random
import shutil
import os


with open("proxy.txt", "r") as file:
    proxy_list = [tuple(proxy.strip().split(":")) for proxy in file.readlines()]


use_proxy = input("Vuoi utilizzare un proxy? (s/n): ").lower() == "s"

if use_proxy:

    proxy_ip, proxy_port = random.choice(proxy_list)


    original_create_connection = socket.create_connection
    def create_connection_with_proxy(*args, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((proxy_ip, int(proxy_port)))
            sock.sendall(f'CONNECT {args[0]}:{args[1]} HTTP/1.1\r\n\r\n'.encode())
            return sock
        except:

            if len(proxy_list) > 1:
                proxy_list.remove((proxy_ip, proxy_port))
                return create_connection_with_proxy(*args, **kwargs)
            else:

                use_proxy = input("Proxy non funzionante. Non ci sono altri proxy disponibili, vuoi proseguire l'accesso ai server IMAP senza proxy? (s/n): ").lower() == "s"
                if use_proxy:
                    socket.create_connection = original_create_connection
                    return original_create_connection(*args, **kwargs)
                else:
                    exit()

    socket.create_connection = create_connection_with_proxy

servers = ["imap.libero.it", "imap.tiscali.it", "imap.gmail.com", "imap.yahoo.com", "imap.outlook.com"]


print("Scegli il server IMAP:")
for i, server in enumerate(servers):
    print(f"{i+1}. {server}")

server_index = int(input("Inserisci l'indice del server: "))
imap_server = servers[server_index - 1]

username_file = 'username.txt'
password_file = 'password.txt'


temp_username_file = "temp_" + username_file
temp_password_file = "temp_" + password_file
shutil.copy(username_file, temp_username_file)
shutil.copy(password_file, temp_password_file)


sender = input("Inserisci il mittente da cercare: ")

message_counter = 0
accounts = []
failed_accounts = []

with open(temp_username_file, 'r') as uf, open(temp_password_file, 'r') as pf:
    username_lines = uf.readlines()
    password_lines = pf.readlines()

for i in range(min(len(username_lines), len(password_lines))):
    email_address = username_lines[i].strip()
    email_password = password_lines[i].strip()
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, email_password)
        mail.select("inbox")
        result, data = mail.search(None, f"FROM {sender}")
        messages = data[0].split()
        if len(messages) > 0:
            message_counter += len(messages)
            accounts.append(email_address)
            print(f"Trovati {len(messages)} messaggi da {sender} per l'account {email_address}")
        else:
            print(f"Nessun messaggio trovato da {sender} per l'account {email_address}")
        mail.close()
        mail.logout()
    except imaplib.IMAP4.error as e:
        if "AUTHENTICATIONFAILED" in str(e):
            print(f"Autenticazione fallita per l'account {email_address}: {e}")
            failed_accounts.append(email_address)
        else:
            print(f"Errore durante la chiusura della connessione per l'account {email_address}: {e}")
            failed_accounts.append(email_address)


with open(temp_username_file, "w") as file:
    for line in username_lines[i + 1:]:
        file.write(line)
with open(temp_password_file, "w") as file:
    for line in password_lines[i + 1:]:
        file.write(line)
os.remove(temp_username_file)
os.remove(temp_password_file)

print(f"Totale messaggi trovati da {sender}: {message_counter}")
print(f"Account con successo: {accounts}")
print(f"Account con fallimenti: {failed_accounts}")

