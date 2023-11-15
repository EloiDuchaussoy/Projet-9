import streamlit as st
import requests
import pandas as pd
import pickle
import json

st.title("My Content POC App")

with open ("df_rel.pickle", 'rb') as f:
    df_rel = pickle.load(f)

user = st.number_input(
    "Select a user:",
    min_value = df_rel.user_id.min(),
    max_value = df_rel.user_id.max(),
    value = None,
)

article = st.selectbox(
    "Select an article read by this user:",
    df_rel.loc[df_rel.user_id == user].click_article_id
)

st.write('User selected:', user)
st.write("Article selected: ", article)

if 'flow' not in st.session_state:
    st.session_state.flow = "Please select a user and an article"

if st.button(
    "Show recommandations",
    type = "primary"
    ):
    if article is not None:
        st.session_state.flow = "Fetching similar articles..."
        st.write(st.session_state.flow)
        r = requests.post(url = "https://ocp9edazfunc.azurewebsites.net/api/httptrigger",
                            data = json.dumps({"article": f"{article}"})
                         )
        rjson = r.json()
        ortho = rjson["orthogonal"]
        st.session_state.flow = f"In the mean time, would you like to discover article {ortho}"
        st.write(st.session_state.flow)
        cb_df = pd.DataFrame(columns= ["article", "score"], index=range(5))
        for i in range(5):
            cb_df.iloc[i, 0] = rjson["similar"+str(i+1)]
            cb_df.iloc[i, 1] = rjson["score"+str(i+1)]
        best_cb_score = cb_df.score.max()
        cb_df.score = cb_df.score/best_cb_score


        st.session_state.flow = "Fetching articles read by similar users..."
        st.write(st.session_state.flow)
        r = requests.post(url = "https://ocp9edazfunc.azurewebsites.net/api/httptrigger1",
                            data = json.dumps({"article": f"{article}",
                                               "user": f"{user}"}))
        rjson = r.json()
        ub_df = pd.DataFrame(columns= ["article", "score"], index=range(5))
        for i in range(5):
            ub_df.iloc[i, 0] = rjson["id"+str(i)]
            ub_df.iloc[i, 1] = rjson["sc"+str(i)]
        best_ub_score = ub_df.score.max()
        ub_df.score = ub_df.score/best_ub_score
        st.write(cb_df.head(2))
        st.write(ub_df.head(3))


    else:
        st.write(st.session_state.flow)

    