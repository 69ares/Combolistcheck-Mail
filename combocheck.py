import imaplib
from tqdm import tqdm

servers = ["imap.libero.it", "imap.gmail.com", "imap.yahoo.com", "imap.outlook.com"]

# chiedere all'utente di scegliere il server IMAP
print("Scegli il server IMAP:")
for i, server in enumerate(servers):
    print(f"{i+1}. {server}")

server_index = int(input("Inserisci l'indice del server: "))
imap_server = servers[server_index - 1]

username_file = 'username.txt'
password_file = 'password.txt'

# chiedere all'utente il mittente da cercare
sender = input("Inserisci il mittente da cercare: ")

message_counter = 0
accounts = []
failed_accounts = []

with open(username_file, 'r') as uf, open(password_file, 'r') as pf:
    username_lines = uf.readlines()
    password_lines = pf.readlines()

for i in tqdm(range(min(len(username_lines), len(password_lines))), desc="Progress", unit="account"):
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
    with open(username_file, "w") as file:
        for line in username_lines[i + 1:]:
            file.write(line)
    with open(password_file, "w") as file:
        for line in password_lines[i + 1:]:
            file.write(line)

print("\033[92mTotale messaggi trovati da {sender}: {message_counter}\033[0m")
print("\033[92mAccount utilizzati:\033[0m")
for account in accounts:
    print("\033[92m- " + account + "\033[0m")

if len(failed_accounts) > 0:
    print("\033[91mAccount su cui non è stato possibile effettuare l'accesso:")
    for account in failed_accounts:
        print("- " + account)
    print("\033[0m")
