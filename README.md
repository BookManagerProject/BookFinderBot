# 📚 BookFinderBot 🤖

## Descrizione

BookFinderBot è un un bot Telegram. Gli utenti attraverso di esso potranno cercare comodamente tramite foto o testo i
propri libri e aggiungerli ai preferiti.

## 🚀 Installazione del servizio

### Prerequisiti

- [Python 3.8](https://www.python.org/downloads/release/python-380/) & pip
- [BotFramework Emulator](https://github.com/microsoft/BotFramework-Emulator/releases)
- Microsoft Azure Subscription
- [ODBC Driver for SQL Server 17](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16#version-17)

### Tipi di risorse utilizzate

- Bot di Azure
- Servizio app
- Bing Search
- Language Understanding (LUIS)
- Servizi cognitivi
- Azure SQL

### Deployment risorse in cloud

#### Setup di Base

La creazione di qualsiasi tipo di risorsa nel cloud Azure necessita di una subscription. Accedere al portale Azure
tramite account Microsoft, selezionare la voce Subscriptions > Add e seguire i passaggi indicati. Una volta fatto verrà
mostrata la pagina della subscription appena creata; da qui recarsi al menù Resource Groups e creare un nuovo gruppo di
risorse. Ora si è pronti alla creazione delle risorse necessarie al progetto.
* **

#### Bot di Azure

1. Creazione di un bot di Azure:

    * Accedere al portale di Azure e selezionare "Create a resource".
    * Cerca "Bot Channels Registration" e seleziona "Create".
    * Configurare l'istanza di Bot Channels Registration come richiesto, incluso il nome del bot e l'abbonamento di
      Azure.
    * Selezionare "Create" per creare il bot.

2. Creazione di un bot su Telegram:
    * Aprire Telegram e cercare "@BotFather".
    * Seguire le istruzioni di @BotFather per creare un nuovo bot su Telegram e ricevere il token di accesso per il bot.
    * Collegamento del bot di Telegram al bot di Azure:
    * Nella sezione "Settings" di Bot Channels Registration, selezionare "Telegram" come canale di messaggistica.
    * Inserire il token di accesso del bot di Telegram nella casella "Token di accesso".
    * Inserire il nome utente del bot di Telegram nella casella "Nome utente del bot".

3. Configurazione dell'endpoint di messaggistica tramite il servizio App di Azure:
    * Nella sezione "Settings" di Bot Channels Registration, selezionare "Channels" e quindi "Web Chat".
    * Copiare il valore di "Site URL" per il servizio Web Chat.
    * Accedere al portale di Azure e selezionare il servizio App creato in precedenza per il bot.
    * Nella sezione "Settings", selezionare "Configuration".
    * Aggiungere una nuova variabile di configurazione chiamata "MicrosoftAppId". Il valore di questa variabile è l'ID
      dell'applicazione di Bot di Azure, che può essere trovato nella sezione "Settings" del bot.
    * Aggiungere una nuova variabile di configurazione chiamata "MicrosoftAppPassword". Il valore di questa variabile è
      la password dell'applicazione di Bot di Azure, che può essere trovata nella sezione "Settings" del bot.
    * Nella sezione "Settings", selezionare "Domains".
    * Aggiungere il dominio del servizio App di Azure come endpoint di messaggistica del bot. Ad esempio, se il dominio
      del servizio App di Azure è "mybot.azurewebsites.net", il valore dell'endpoint di messaggistica
      sarà "https://mybot.azurewebsites.net/api/messages".
    * Salvare le modifiche.

* **

### Servizio app

1. Accedere al portale di Azure e selezionare "Create a resource".
2. Cerca "Web App" e seleziona "Create".
3. Configurare l'istanza di Web App come richiesto, inclusi il nome dell'istanza e l'abbonamento di Azure. Scegliere
   Python 3.7 come runtime stack.
4. Selezionare "Create" per creare l'istanza di Web App.
5. Una volta creata l'istanza di Web App, è possibile caricare l'applicazione Python su di essa. È possibile farlo in
   diversi modi, tra cui l'upload diretto dei file o l'utilizzo di GitHub Actions.
6. Per caricare i file direttamente, è possibile utilizzare uno strumento di gestione FTP, come FileZilla, per caricare
   i file dell'applicazione nella cartella corretta dell'istanza di Web App.
7. Per utilizzare GitHub Actions, è necessario configurare il repository dell'applicazione per il rilascio continuo su
   Azure. Ciò può essere fatto seguendo i passaggi descritti nella documentazione di Azure.
8. Una volta caricata l'applicazione Python, è necessario configurare il comando avvia specificando la
   stringa ``gunicorn --bind 0.0.0.0 --worker-class aiohttp.worker.GunicornWebWorker --timeout 600 app:APP" nella sezione "Configurazione" -> "Comando avvia" dell'istanza di Web App``.
9. Infine, per utilizzare l'applicazione Python su Web App, è possibile accedere all'URL pubblico dell'istanza di Web
   App attraverso un browser web o utilizzando un client HTTP. L'applicazione Python dovrebbe essere in grado di gestire
   le richieste HTTP in arrivo e fornire le risposte corrispondenti.

* **

### Bing Search

1. Accedere al portale di Azure e selezionare "Create a resource".
2. Cerca "Bing Search" e seleziona "Create".
3. Configurare l'istanza di Bing Search come richiesto, inclusi il nome dell'istanza e l'abbonamento di Azure.
4. Selezionare "Create" per creare l'istanza di Bing Search.
5. Una volta creato l'istanza di Bing Search, è possibile accedere al servizio attraverso l'API endpoint e iniziare a
   utilizzarlo per effettuare ricerche su Bing.
6. Per utilizzare il servizio Bing Search all'interno di un'applicazione, è necessario generare una chiave di accesso
   per il servizio. Per fare ciò, è necessario accedere al portale di Azure e selezionare l'istanza di Bing Search
   creata in precedenza.
7. Nella sezione "Keys", è possibile generare una chiave di accesso per il servizio Bing Search.
8. Una volta generata la chiave di accesso, è possibile utilizzarla per autenticarsi e accedere alle funzionalità del
   servizio Bing Search all'interno dell'applicazione.
9. Per integrare il servizio Bing Search all'interno di un'applicazione, è possibile utilizzare le librerie client di
   Bing Search per il linguaggio di programmazione utilizzato nell'applicazione. Le librerie client sono disponibili per
   diverse piattaforme, tra cui .NET, Java e Python.
10. Per utilizzare il servizio Bing Search all'interno di un'applicazione web, è possibile utilizzare il servizio come
    API REST. L'API endpoint è disponibile nell'istanza di Bing Search creata in precedenza e richiede l'autenticazione
    tramite la chiave di accesso generata in precedenza.

* **

### Language Understanding (LUIS)

Per LUIS è possibile fare riferimento al file [REDME-LUIS.md](cognitiveModels/README-LUIS.md)
* **

### Servizi cognitivi

1. Accedere al portale di Azure e selezionare "Create a resource".
2. Cerca "Servizi cognitivi" e seleziona "Create".
3. Configurare l'istanza di Servizi cognitivi come richiesto, inclusi il nome dell'istanza e l'abbonamento di Azure.
   Selezionare "Computer Vision" come servizio da utilizzare.
4. Selezionare "Create" per creare l'istanza di Servizi cognitivi.
5. Una volta creata l'istanza di Servizi cognitivi, è possibile utilizzare le API fornite dal servizio per il
   riconoscimento del testo da un'immagine.
6. Per il riconoscimento del testo da un'immagine, è possibile utilizzare l'API OCR (Optical Character Recognition)
   fornita da Computer Vision. Per utilizzare l'API, è necessario inviare un'immagine al servizio attraverso una
   richiesta HTTP.

* **

### Azure SQL

1. Accedere al portale di Azure e selezionare "Create a resource".
2. Cerca "Azure SQL" e seleziona "Create".
3. Configurare l'istanza di Azure SQL come richiesto, inclusi il nome dell'istanza, il tipo di deployment, l'abbonamento
   di Azure e le impostazioni di sicurezza.
4. Selezionare "Create" per creare l'istanza di Azure SQL.
5. Una volta creata l'istanza di Azure SQL, è possibile utilizzarla per archiviare e gestire i dati.
6. Per accedere all'istanza di Azure SQL, è possibile utilizzare uno strumento di gestione del database, come SQL Server
   Management Studio o Azure Data Studio.
7. Utilizzare le credenziali fornite durante la configurazione per effettuare il login all'istanza di Azure SQL.
8. Creare un nuovo database all'interno dell'istanza di Azure SQL, utilizzando uno strumento di gestione del database o
   una query SQL.
9. Creare tabelle e altri oggetti del database all'interno del nuovo database, utilizzando uno strumento di gestione del
   database o una query SQL.
10. Utilizzare l'API di Azure SQL per connettersi al database e interagire con i dati. Per esempio, si può utilizzare
    una libreria per Python come pyodbc o SQLAlchemy.

## Installazione

Il progetto contiene tutto il necessario per il funzionamento

Per utilizzare basta clonare il progetto con git:

```
git clone XX
```

Installare le dipendenze con il seguente comando:

```
pip install -r requirments.txt
```

