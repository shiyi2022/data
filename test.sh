spark-submit \
    --master yarn \
    --deploy-mode cluster \
    --num-executors 3 \
    test6.py \
    --output $1 
