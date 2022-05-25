spark-submit \
    --master yarn \
    --deploy-mode cluster \
    --num-executors 3 \
    test2.py \
    --output $1 
