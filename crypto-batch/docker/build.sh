# -- Building the Images

docker build \
  -f jupyter.Dockerfile \
  -t crypto-batch-jupyter .

docker build \
  -f hive.Dockerfile \
  -t crypto-batch-hive-metastore .

docker build \
  -f trino.Dockerfile \
  -t crypto-batch-trino ..
