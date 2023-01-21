import imaplib
from tqdm import tqdm

# specifica i percorsi dei file con le credenziali
username_file = 'username.txt'
password_file = 'password.txt'

sender = input("Inserisci il mittente da cercare: ")

# inizializza il contatore dei messaggi e le liste degli account utilizzati e degli account su cui non è stato possibile effettuare l'accesso
message_counter = 0
accounts = []
failed_accounts = []

# apri i file con le credenziali
with open(username_file, 'r') as uf, open(password_file, 'r') as pf:
    #leggi le righe dei file
    username_lines = uf.readlines()
    password_lines = pf.readlines()

for i in tqdm(range(min(len(username_lines), len(password_lines))), desc="Progress", unit="account"):
    email_address = username_lines[i].strip()
    email_password = password_lines[i].strip()
    try:
        # Connettersi al server IMAP di Libero
        mail = imaplib.IMAP4_SSL("imap.libero.it")
        mail.login(email_address, email_password)
        # Selezionare la cartella Posta in arrivo
        mail.select("inbox")
        # Cercare i messaggi che hanno il mittente specificato
        result, data = mail.search(None, f"FROM {sender}")
        # Recuperare gli identificativi dei messaggi
        messages = data[0].split()
        # Stampa gli identificativi dei messaggi
        if len(messages) > 0:
            message_counter += len(messages)
            accounts.append(email_address)
            print(f"Trovati {len(messages)}messaggi da {sender} per l'account {email_address}")
        else:
            print(f"Nessun messaggio trovato da {sender} per l'account {email_address}")
        # Chiudere la connessione al server IMAP
        mail.close()
        mail.logout()
    except imaplib.IMAP4.error as e:
        if "AUTHENTICATIONFAILED" in str(e):
            print(f"Autenticazione fallita per l'account {email_address}: {e}")
            failed_accounts.append(email_address)
        else:
            print(f"Errore durante la chiusura della connessione per l'account {email_address}: {e}")
            failed_accounts.append(email_address)
    # Elimina la prima riga dai file
    with open(username_file, "w") as file:
        for line in username_lines[i + 1:]:
            file.write(line)
    with open(password_file, "w") as file:
        for line in password_lines[i + 1:]:
            file.write(line)

# Mostra il risultato finale
print("\033[92mTotale messaggi trovati da {sender}: {message_counter}\033[0m")
print("\033[92mAccount utilizzati:\033[0m")
for account in accounts:
    print("\033[92m- " + account + "\033[0m")


# Mostra gli account su cui non è stato possibile effettuare l'accesso
if len(failed_accounts) > 0:
    print("\033[91mAccount su cui non è stato possibile effettuare l'accesso:")
    for account in failed_accounts:
        print("- " + account)
    print("\033[0m")
