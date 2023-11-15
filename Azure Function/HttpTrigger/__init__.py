import json
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient



app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

#@app.route(route="HttpExample")
def HttpExemple(article: func.HttpRequest, ) -> func.HttpResponse:
    #logging.info('Python HTTP trigger function processed a request.')
    
    art = article.params.get('article')

    #art = article
    if not art:
        try:
            req_body = article.get_json()
        except ValueError:
            pass
        else:
            art = req_body.get('article')

    
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
        container_client = blob_service_client.get_container_client(container= "pca")
        downloader = container_client.download_blob("PCA.pickle")
        b = downloader.readall()   
    except Exception as e:
        return func.HttpResponse(f"Hello3\n{e}") 
    

    
    try: 
        pca = pickle.loads(b)
    except EOFError:
        print("eof error")
    

    cosine_sim = cosine_similarity(pca, pca[int(art)].reshape(1,-1))
    sim_df = pd.DataFrame(cosine_sim)
    sim_df.rename(columns={0:"sim"}, inplace=True)
    sim_df.insert(1, "ortho", 1-abs(sim_df.sim))
    similar = list(range(5))
    score = list(range(5))
    for i in range(5):
        similar[i] = sim_df.loc[sim_df.sim == sim_df.sort_values(by="sim", ascending=False).iloc[1+i].values[0]].index[0]
        score[i] = sim_df.loc[sim_df.sim == sim_df.sort_values(by="sim", ascending=False).iloc[1+i].values[0]].sim.values[0]
    print(score)
    orthogonal = sim_df.loc[sim_df.ortho == sim_df.ortho.max()].index[0]
    maximum = sim_df.ortho.max()
    return func.HttpResponse(json.dumps({'similar1': int(similar[0]),
                                         'similar2': int(similar[1]),
                                         'similar3': int(similar[2]),
                                         'similar4': int(similar[3]),
                                         'similar5': int(similar[4]),
                                         'score1': float(score[0]),
                                         'score2': float(score[1]),
                                         'score3': float(score[2]),
                                         'score4': float(score[3]),
                                         'score5': float(score[4]),
                                         'orthogonal': int(orthogonal)}))



def main(req: func.HttpRequest) -> func.HttpResponse:
    return HttpExemple(req)


if __name__=="__main__":
    main("666")
