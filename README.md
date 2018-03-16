# Chat-app
Chat application project in 2BA
L'application doit être lancé via le terminal de commande avec la commande 'py Chat.py'
En se connectant à l'application de Chat, le pseudo va être demandé et grâce à la commande /connect on va se connecter au server en fournissant le pseudo , notre ip et le port choisit. En entrant la commande /chat , le thread est lancé et on peut commencer à discuter en recevant les message des autres.
Ce server va gérer la communication via le protocol TCP en créant un socket server qui recevra les socket client comme requête.
Lorsque le client envoit un message avec /send , le server va le décoder et se charger de l'afficher.
Avec la commande /clients on obtient la liste des pseudos des clients connectés sur le server
Il est également possible de se connecter pour discuter en peer to peer avec la commande /join ou il faudra communiquer l'ip et le port de la machine , après cela de la même manière qu'avec le server , on utilise /chat pour pouvoir recevoir et on peut également envoyer nos message
