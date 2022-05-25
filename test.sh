spark-submit \
    --master yarn \
    --deploy-mode cluster \
    --num-executors 3 \
    test4.py \
    --output $1 
