spark-submit \
    --master yarn \
    --deploy-mode cluster \
    --num-executors 3 \
    test.py \
    --output $1 
