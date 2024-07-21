#заточена под великий и могучий русский язык
import service_pb2_grpc
import service_pb2
import grpc.aio
import psycopg2
from concurrent import futures
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
import asyncio

model = SentenceTransformer('cointegrated/rubert-tiny2')
conn_g = psycopg2.connect("dbname=django user=postgres password=zjsjI3Km4b2kK~!E host=psql")
cur_g = conn_g.cursor()
# def get_recommendation(id:int):
#     DF2=pd.DataFrame(columns=["SCORE"],index=df["id"])
#     embeddings =model.encode(df.category+" "+df.main_name)
#     DF2['SCORE'] = linear_kernel(embeddings,embeddings)[id-1]
#     DF2=DF2.drop(id)
#     DF2.sort_values(by="SCORE",ascending=False)
#     return (list(DF2.index))
async def get_recommendations(id:list):
    cur = cur_g
    conn = conn_g
    try:
        cur.execute("SELECT COUNT(*) FROM users_adverstiment")
    except psycopg2.InterfaceError:
        conn = psycopg2.connect("dbname=django user=postgres password=gsxZzlCn9Cu4 host=psql")
        cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users_adverstiment")
    id_count=int(cur.fetchone()[0])
    id_df = pd.read_sql_query(f"SELECT id FROM users_adverstiment WHERE id NOT IN ({','.join(str(i) for i in id)})",conn)
    DF2 = pd.DataFrame(columns=["SCORE"],index=id+list(id_df["id"]))
    DF2["SCORE"]=np.zeros((id_count,),dtype=np.float16)
    for df_with_id in pd.read_sql_query(f"SELECT id,category,main_name FROM users_adverstiment WHERE id IN ({','.join(str(i) for i in id)})",conn,chunksize=10000):
        for df_query in pd.read_sql_query(f"SELECT id,category,main_name FROM users_adverstiment WHERE id NOT IN ({','.join(str(i) for i in id)})",conn,chunksize=10000):
            df=pd.concat([df_with_id,df_query],ignore_index=True)
            embeddings =model.encode(df.category+" "+df.main_name)
            raw_scores = linear_kernel(embeddings,embeddings)
            filtered_score = np.zeros((len(df.index),),dtype=np.float16) #результат без ID из истории
            for i in range(len(df_with_id.index)):
                filtered_score+=raw_scores[i]
            filtered_score/=(len(df_with_id.index)%10000)
            df["SCORE"]=filtered_score
            df=df.set_index("id")
            # DF2=DF2.add(df.drop(columns=["category","main_name"]),fill_value=0)
            for index,val in df.iterrows():
                DF2.loc[index]+=val
    DF2=DF2.drop(id)
    DF2=DF2.dropna()
    DF2=DF2.sort_values(by="SCORE",ascending=False)
    return (list(DF2.index)+id)
async def get_recommendations_by_category(id:list,category:str):
    cur = cur_g
    conn = conn_g
    try:
        cur.execute("SELECT COUNT(*) FROM users_adverstiment WHERE category=%s",(category,))
    except psycopg2.InterfaceError:
        conn = psycopg2.connect("dbname=django user=postgres password=gsxZzlCn9Cu4 host=psql")
        cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users_adverstiment WHERE category=%s",(category,))
    id_count=int(cur.fetchone()[0])
    id_df = pd.read_sql_query(f"SELECT id FROM users_adverstiment WHERE id NOT IN ({','.join(str(i) for i in id)}) AND category=%s",params=[category],con=conn)
    DF2=pd.DataFrame(columns=["SCORE"],index=id+list(id_df["id"]))
    DF2["SCORE"]=np.zeros((id_count,),dtype=np.float16)
    for df_with_id in pd.read_sql_query(f"SELECT id,main_name FROM users_adverstiment WHERE id IN ({','.join(str(i) for i in id)}) AND category=%s",params=[category],con=conn,chunksize=10000):
        for cat_df_without_id in pd.read_sql_query(f"SELECT id,main_name FROM users_adverstiment WHERE id NOT IN ({','.join(str(i) for i in id)}) AND category=%s",params=[category],con=conn,chunksize=10000):
            cat_df=pd.concat([df_with_id,cat_df_without_id],ignore_index=True)
            embeddings =model.encode(cat_df["main_name"].to_numpy())
            raw_scores = linear_kernel(embeddings,embeddings)
            filtered_score = np.zeros((len(cat_df.index),),dtype=np.float16) #результат без ID из истории
            for i in range(len(df_with_id.index)):
                filtered_score+=raw_scores[i]
            filtered_score/=(len(df_with_id.index)%10000)
            cat_df["SCORE"]=filtered_score
            cat_df=cat_df.set_index("id")
            for index,val in cat_df.iterrows():
                DF2.loc[index]+=val
    DF2=DF2.drop(id)
    DF2=DF2.dropna()
    DF2=DF2.sort_values(by="SCORE",ascending=False)
    return (list(DF2.index)+id)
class Recommendation(service_pb2_grpc.RecommendationsServicer):
    async def UpdateRecommendations(self, request, context):
        adv_id = [i for i in request.adv_id]
        rec = await get_recommendations(adv_id)
        return service_pb2.Recommendations_list(id=list(map(int,rec)))
    async def UpdateRecommendationsByCategory(self,request,context):
        adv_id = [i for i in request.adv_id]
        category = request.category
        rec = await get_recommendations_by_category(adv_id,category)
        return service_pb2.Recommendations_list(id=list(map(int,rec)))
async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor())
    service_pb2_grpc.add_RecommendationsServicer_to_server(Recommendation(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    await server.wait_for_termination()
asyncio.run(serve())
