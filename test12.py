# -*- coding: utf-8 -*-
"""test12

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XYJ3xv3zNnXHXdqZ2iKMu9DgERqwivfa
"""

#!pip install pyspark

from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext
from pyspark.sql.functions import explode
import argparse

spark = SparkSession \
    .builder \
    .appName("COMP5349 A2") \
    .getOrCreate()

from pyspark import SparkConf, SparkContext

spark_conf = SparkConf()\
        .setAppName("assignment2")
sc=SparkContext.getOrCreate(spark_conf) 


#rating_data = 's3://comp5349-data/week6/ratings.csv'

test_init_df = spark.read.json('test.json',multiLine=True)

count_contract=102

test_init_df.printSchema()







#展平嵌套数据

test_data_df= test_init_df.select((explode("data").alias('data')))
test_data_df.printSchema()


test_paragraphs_df= test_data_df.select('data.title',(explode("data.paragraphs").alias('paragraphs'))).withColumnRenamed("data.title", "title")
test_paragraphs_df.printSchema()

df= test_paragraphs_df.select('title',"paragraphs.context", explode("paragraphs.qas").alias('qas')).withColumnRenamed("paragraphs.context", "context")
df.printSchema()

df2= df.select('title',"context",'qas.question','qas.is_impossible','qas.id','qas.answers')\
       .withColumnRenamed("qas.question", "question")\
       .withColumnRenamed("qas.is_impossible", "is_impossible")\
       .withColumnRenamed("qas.id", "id")\
       .withColumnRenamed("qas.answers", "answers")
df2.printSchema()

print("样本分类********************")

#样本分类
# is_impossible=True
data_ture=df2.where("is_impossible=True").select('title',"context",'id','question','is_impossible')

#is_impossible=False
data_false=df2.where("is_impossible=False")\
                      .select('title',"context",'id','question','is_impossible', explode("answers").alias('answers'))\
                      .select('title',"context",'id','question','is_impossible', 'answers.answer_start','answers.text')



data_ture.count()
data_false.count()

print("长文本分割********************")

#长文本分割

def split_rdd(line):
     
     title,comtext,id,question,is_impossible=line
     length=len(comtext)
     a=(length//2048)+1
     b=[]
     for i in range(a):
          c=[]
          if i*2048+4096<length:
             cc=comtext[i*2048:i*2048+4096]
             c.append(title)
             c.append(cc)
             c.append(i)
             c.append(id)
             c.append(question)
          else:
             cc=comtext[i*2048:length]
             c.append(title)
             c.append(cc)
             c.append(i)
             c.append(id)
             c.append(question)
          b.append(c)
     return b


def split_rdd2(line):
     
     title,context,id,question,is_impossible,answer_start,text=line
     length=len(context)
     a=(length//2048)+1
     length_text=len(text)
     start_index=max(0,(answer_start//2048)-1)
     end_index=(answer_start+length_text)//2048
     b=[]
     for i in range(a):
          c=[]
          if i*2048+4096<length:
             cc=context[i*2048:i*2048+4096]
             c.append(title)
             c.append(cc)
             c.append(i)
             c.append(id)
             c.append(question)
             c.append(start_index)
             c.append(end_index)
             c.append(answer_start)
             c.append(text)
          else:
             cc=context[i*2048:length]
             c.append(title)
             c.append(cc)
             c.append(i)
             c.append(id)
             c.append(question)
             c.append(start_index)
             c.append(end_index)
             c.append(answer_start)
             c.append(text)
          b.append(c)
     return b

# impossible samples
a=data_ture.rdd
impossible_samples=a.flatMap(split_rdd)
impossible_samples.count()

#posivle samples + positive samples
aaa=data_false.rdd
ccc=aaa.flatMap(split_rdd2)

##positive
def positive(line):
     
     title,context,index,id,question,start_index,end_index,answer_start,text=line
     if start_index<=index and index<=end_index:
       return title,context,index,id,question,start_index,end_index,answer_start,text

def positive2(line):
     
     title,context,index,id,question,start_index,end_index,answer_start,text=line
     a=answer_start-index*2048
     b=a+len(text)
     answer_start=max(0,a)
     answer_end=min(b,4096)
     
     return title,context,index,id,question,answer_start,answer_end

positive_samples=ccc.map(positive)\
                    .filter( lambda x: x is not None)\
                    .map(positive2)
positive_samples.count()

# possible negative

def possible_negative(line):
     
     title,context,index,id,question,start_index,end_index,answer_start,text=line
     if start_index>index or index>end_index:
       return title,context,index,id,question

possible_negative_samples=ccc.map(possible_negative)\
                             .filter( lambda x: x is not None)

possible_negative_samples.count()

print("样本平衡********************")

print("positive_samples")

#样本平衡：impossible_samples\positive_samples\possible_negative_samples

# positive_samples

def filter1(line):
  title,context,index,id,question,answer_start,answer_end=line
  return context,question,answer_start,answer_end

final_positive=positive_samples.map(filter1)

final_positive.take(1)

# positive_samples

def filter2(line):
  title,context,index,id,question,start_index,end_index=line
  return id,question

def filter_possible_negative(line):
  aa=[]
  title,context,index,id,question=line
  a=[]
  c=0
  if dict2[id]>0:
     dict2[id]=dict2[id]-1
     a.append(context)
     a.append(question)
     a.append(c)
     a.append(c)
     aa.append(a)
  else:
     return('none')
  return aa

count=positive_samples.map(filter2)\
                      .countByKey().items()

count_rdd=sc.parallelize(count)
dict=count_rdd.collectAsMap()
dict2=dict

final_possible=possible_negative_samples.map(filter_possible_negative)\
                                                    .filter( lambda x: x is not 'none')
final_possible.count()

final_possible.take(1)

#impossible_samples

'''
def remove2(line):
  title,context,index,id,question,start_index,end_index=line
  return question,start_index

def remove3(line):
  question,count=line
  avg=round(count/(count_contract-1))
  return question,avg

avg=positive_samples.map(remove2)\
                    .countByKey().items()

avg_rdd=sc.parallelize(avg)
avg_rdd2=avg_rdd.map(remove3)
dict_avg=avg_rdd2.collectAsMap()
dict_avg2=dict_avg

'''

'''
def filter3(line):
  title,context,index,id,question=line
  return (id,question),(context)

def filter4(line):
   a,b=line
   id,question=a
   count_question= dict_avg2[question]
   return a[1],b[:count_question]


'''

'''
impossible_samples2=impossible_samples.map(filter3)
impossible_samples3=impossible_samples2.groupByKey()\
                                       .mapValues(list)\
                                       .map(filter4)\
                                       .flatMapValues(lambda x:x)

'''

'''
def filter5(line):
  question,content=line
  return content,question,0,0


'''

'''
final_impossible=impossible_samples3.map(filter5)
'''

#final_impossible.take(10)

#final_positive/final_possible/final_impossible合并

final_positive.count()

final_possible.count()

a=final_positive.union(final_possible)

#final_sample=a.union(final_impossible)





final_sample_df=a.toDF()
samples=final_sample_df.withColumnRenamed("_1", "source")\
                       .withColumnRenamed("_2", "question")\
                       .withColumnRenamed("_3", "answer_start")\
                       .withColumnRenamed("_4", "answer_end")\

samples.coalesce(1).write.json("sample.json")



