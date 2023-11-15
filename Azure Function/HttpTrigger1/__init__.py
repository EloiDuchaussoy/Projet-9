import json
import io
import pickle
import scipy
from scipy.sparse import csr_array
import implicit
from implicit.als import AlternatingLeastSquares
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient



app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

#@app.route(route="HttpExample")
def HttpExemple1(article: func.HttpRequest, ) -> func.HttpResponse:
    #logging.info('Python HTTP trigger function processed a request.')
    
    art = article.params.get('article')
    user = article.params.get('user')
    #art = article
    if not art:
        try:
            req_body = article.get_json()
        except ValueError:
            pass
        else:
            art = req_body.get('article')
            user = req_body.get('user')
    user = int(user)
    art = int(art)
    try:
        account_url = "https://ocp9edblob.blob.core.windows.net"
        default_credential = DefaultAzureCredential()
    except Exception as e:
        return func.HttpResponse(f"Hello1\n{e}")
    
    try:
        blob_service_client = BlobServiceClient(account_url, credential=default_credential)
    except Exception as e:
        return func.HttpResponse(f"Hello2\n{e}")    
    

    try:
        container_client = blob_service_client.get_container_client(container= "dfrel")
        downloader = container_client.download_blob("df_rel.csv")
        stream = io.BytesIO()
        numbytes = downloader.readinto(stream)
    except Exception as e:
        return func.HttpResponse(f"Hello3\n{e}") 

    stream.seek(0)
    try: 
        df_rel = pd.read_csv(stream, index_col='Unnamed: 0')
    except EOFError:
        print("eof error")
    # res = df_rel.head(5).to_json(orient="index", indent= 4)
        
    # return func.HttpResponse(res) 


    print("restricting search...")
    epoch_ms = 6*60*60*1000
    pd.to_datetime(df_rel.click_timestamp, unit='ms')
    timestamp_df = df_rel.loc[
        (df_rel.user_id == user) &  
        (df_rel.click_article_id == art)
        ]

    timestamp = timestamp_df.click_timestamp.values[0]
    
    df_rel_epoch = df_rel.loc[(df_rel.click_timestamp <= timestamp) &
                        (df_rel.click_timestamp >= timestamp - epoch_ms)]


    print("seraching similar users...")
    users_read =[]
    index_query = []
    i=1
    articles_read = df_rel_epoch.loc[df_rel_epoch["user_id"] == user].click_article_id.values.tolist()
    for arti in articles_read:
        users_read += df_rel_epoch.loc[df_rel["click_article_id"] == arti].user_id.values.tolist()
    users_read = list(set(users_read))
    for u in users_read:
        print("Processing user ", i, " of ", len(users_read))
        i+=1
        index_query += df_rel_epoch.loc[df_rel["user_id"] == u].index.tolist()
    index_query = list(set(index_query))

    df_rel_red = df_rel.iloc[index_query]
    presdf = pd.DataFrame()
    sdf = presdf.astype(dtype=pd.SparseDtype("int", 0))
    index = df_rel_red.user_id.unique()
    columns = df_rel_red.click_article_id.unique()

    print("creating sparse matrix...")
    sdf.index = index
    for col in columns:
        sdf.insert(loc = 0, column = col, value = 0)
    sdfdefrag = sdf.copy()
    for clk in df_rel_red.index:
        sdfdefrag.loc[df_rel.iloc[clk]["user_id"], df_rel.iloc[clk]["click_article_id"]] +=1

    print("running model...")
    model = AlternatingLeastSquares(factors=64, regularization = 0.05, alpha = 2.0)
    model.fit(scipy.sparse.csr_matrix(sdfdefrag))
    ids, scores = model.recommend(
        userid = sdfdefrag.index.get_loc(user), 
        user_items= scipy.sparse.csr_matrix(sdfdefrag.loc[user].values*sdfdefrag.loc[user].reset_index().index), 
        N=5, 
        filter_already_liked_items=True)
    ids = sdfdefrag.iloc[ids].index.values
    return func.HttpResponse(json.dumps({'id0':int(ids[0]),
                                         'id1':int(ids[1]),
                                         'id2':int(ids[2]),
                                         'id3':int(ids[3]),
                                         'id4':int(ids[4]),
                                         'sc0':float(scores[0]),
                                         'sc1':float(scores[1]),
                                         'sc2':float(scores[2]),
                                         'sc3':float(scores[3]),
                                         'sc4':float(scores[4]),}))



def main(req: func.HttpRequest) -> func.HttpResponse:
    return HttpExemple1(req)


if __name__=="__main__":
    main("666")