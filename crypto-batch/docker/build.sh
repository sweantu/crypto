# -- Building the Images

docker build \
  -f spark.Dockerfile \
  -t crypto-batch-spark .

docker build \
  -f jupyter.Dockerfile \
  -t crypto-batch-jupyter .

docker build \
  -f hive.Dockerfile \
  -t crypto-batch-hive-metastore .

docker build \
  -f trino.Dockerfile \
  -t crypto-batch-trino ..

docker build \
  -f superset.Dockerfile \
  -t crypto-batch-superset .
