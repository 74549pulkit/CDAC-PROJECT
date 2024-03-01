from time import sleep
import pandas as pd
import pyspark
from pyspark.sql import SparkSession,Row
from pyspark.sql.functions import from_json, col, when, udf
from pyspark.sql.types import StructType, StructField, StringType, FloatType
from config.config import config
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
def sentiment_analysis1(comment,row) -> str:
    if comment:
        #openai.api_key = config['openai']['api_key']
        if row == 1:
            client = OpenAI(api_key='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')
        elif row==2:
            client=OpenAI(api_key="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")
        #elif row==2:
        #    client=OpenAI(api_key="")
        else:
            client=OpenAI(api_key="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")
            
        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
            messages= [
                {
                    "role": "system",
                    "content": """
                        You're a machine learning model with a task of classifying comments into POSITIVE, NEGATIVE, NEUTRAL.
                        You are to respond with one word from the option specified above, do not add anything else.
                        Here is the comment:
                        
                        {comment}
                    """.format(comment=comment)
                }
            ]
        )
        return completion.choices[0].message.content
    return "Empty"

'''
text_mining_model=joblib.load(r'/opt/bitnami/spark/jobs/model1.pkl')
def predict_udf(text):
    if text is None:
        return None
    else:
        cv=TfidfVectorizer(max_features = 1000)
        X = cv.fit_transform(text).toarray()
        X = pd.DataFrame(X,columns=cv.get_feature_names_out())

        predictions = text_mining_model.predict(X)
        
        return predictions[0]
'''



def start_streaming(spark):
    topic = 'customer_review_topic'
    while True:
        try:
            stream_df = (spark.readStream.format("socket")
                         .option("host", "0.0.0.0")
                         .option("port", 9998)
                         .load()
                         )

            schema = StructType([
                StructField("review_id", StringType()),
                StructField("user_id", StringType()),
                StructField("business_id", StringType()),
                StructField("stars", FloatType()),
                StructField("useful", FloatType()),
                StructField("funny", FloatType()),
                StructField("cool", FloatType()),
                StructField("date", StringType()),
                StructField("text", StringType()),     
                StructField("row_no", FloatType())       
            ])
            

            stream_df = stream_df.select(from_json(col('value'), schema).alias("data")).select(("data.*"))

#            sentiment_analysis_udf = udf(predict_udf, StringType())


            sentiment_analysis_udf = udf(sentiment_analysis1, StringType())

            stream_df = stream_df.withColumn('feedback',
                                             when(col('text').isNotNull(), sentiment_analysis_udf(col('text'),col('row_no')))
                                             .otherwise(None)
                                             )
            stream_df=stream_df.drop(col('row_no'))
            kafka_df = stream_df.selectExpr("CAST(review_id AS STRING) AS key", "to_json(struct(*)) AS value")

            query = (kafka_df.writeStream
                   .format("kafka")
                   .option("kafka.bootstrap.servers", config['kafka']['bootstrap.servers'])
                   .option("kafka.security.protocol", config['kafka']['security.protocol'])
                   .option('kafka.sasl.mechanism', config['kafka']['sasl.mechanisms'])
                   .option('kafka.sasl.jaas.config',
                           'org.apache.kafka.common.security.plain.PlainLoginModule required username="{username}" '
                           'password="{password}";'.format(
                               username=config['kafka']['sasl.username'],
                               password=config['kafka']['sasl.password']
                           ))
                   .option('checkpointLocation', '/tmp/checkpoint')
                   .option('topic',topic)
                   .start()
                   .awaitTermination()
                )

        except Exception as e:
            print(f'Exception encountered: {e}. Retrying in 10 seconds')
            sleep(10)

if __name__ == "__main__":
    spark_conn = SparkSession.builder.appName("SocketStreamConsumer").getOrCreate()

    start_streaming(spark_conn)
