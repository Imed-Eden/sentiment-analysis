1) analyzing.py : inovoque l'API Text Analysis et renvoie un fichier JSON avec les résultats
  
2) ranking.py : créé l'index Cognitive Search sur la base d'un fichier JSON et upload les données dans cet index

⚠️⚠️⚠️ POUR L'INSTANT LES FICHIERS 1 ET 2 N'INTERAGISSENT PAS AVEC LE BLOB, ILS SONT CODÉS POUR ÊTRE UTILISÉS LOCALEMENT (à changer dès que possible)

3) back_end.py : interroge Cognitive Search pour créer les fichiers JSON utilisés par la webapp. Ces fichiers sont placés dans un file storage
  
