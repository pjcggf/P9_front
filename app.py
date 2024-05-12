"""Page de présentation des résultats"""
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="OC-P9-Recommandation d'articles", page_icon="🤖")

API_CB_URL = 'https://us-west4-p9-reco-contenu.cloudfunctions.net/cb_get_articles_id'
API_CF_URL = 'https://us-west4-p9-reco-contenu.cloudfunctions.net/cf-get-articles-id'

st.markdown("""# Recommandation de contenu
## POC : Conseiller 5 articles à un utilisateur.""")


@st.cache_data
def get_prediction(user, nb, methode_cb='last'):
    """Récupère les articles recommandés"""
    if methode == 'Collaborative Filtering':
        result = requests.get(API_CF_URL,
                                  params={
                                      'user_id': user, 'n': nb},
                                  timeout=300).json()

    else:
        result = requests.get(API_CB_URL,
                                params={'user_id': user,
                                        'nb_results': nb,
                                        'method': methode_cb},
                                timeout=300).json()

    return result


@st.cache_data
def get_user_list(nbusers = 10):
    '''Fonction pour mettre en cache la liste des users'''
    liste_user = requests.get(
        f'https://us-west1-p9-reco-contenu.cloudfunctions.net/get_user_list?nb={nbusers}',
        timeout=100).json()

    return liste_user


nb_users = st.slider("Combien d'utilisateurs souhaitez-vous afficher ?",
        min_value=10, max_value=300, step=10)
user_selected = st.selectbox(
            'Pour quel utilisateurs souhaitez-vous des recommandations',
            get_user_list(nb_users))

nb_res = st.slider("Combien d'articles souhaitez-vous recevoir ?",
                    min_value=1, max_value=10, step=1)

methode = st.radio("Quel type de prédiction souhaitez-vous ?",
                options = ['Collaborative Filtering', 'Content-Based Filtering'],
                captions=["Se base sur les préférences des autres utilisateurs.",
                        "Se base sur les articles déjà consultés par l'utilisateur."]
                )

if methode == 'Content-Based Filtering':
    type_cb = st.radio("Sélectionner le type de prédiction :",
            options=['Dernier article lu', 'Ensemble des articles lus'],
            captions=['Utilise le dernier article lu comme référence.',
                    "Utilise l'ensemble des articles lus par l'utilisateur comme référence."]
            )
try:
    kwargs = {'user': user_selected, 'nb': nb_res, 'methode_cb': type_cb}
except NameError:
    kwargs = {'user': user_selected, 'nb': nb_res}

data = get_prediction(**kwargs)

df = pd.DataFrame([data]).T.sort_values(by=0, ascending=False).reset_index(
).rename({'index': "Id de l'article", 0: "Score de similarité"}, axis=1)
st.dataframe(df)
