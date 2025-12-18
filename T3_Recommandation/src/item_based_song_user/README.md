# Test des recommandations Item-Based Song User

## Procédure de test

1. **Générer un utilisateur de test**
   Lancez le script de création d'utilisateur :
   ```bash
   python T3_Recommandation/src/item_based_song_user/create_test_user.py
   ```

2. **Récupérer l'UUID**
   Copiez l'UUID affiché dans la sortie du terminal.

3. **Lancer la recommandation**
   Utilisez l'UUID comme argument pour l'un des scripts de recommandation suivants :

   - `item_based_mk1.py`
   - `item_based_mk2.py`
   - `item_based_mk3.py`
   - `item_based_mk4.py`

   **Exemple de commande :**
   ```bash
   python T3_Recommandation/src/item_based_song_user/item_based/item_based_mk4.py <VOTRE_UUID>
   ```
