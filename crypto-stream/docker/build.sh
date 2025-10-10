# -- Building the Images

docker build \
  -f flink.Dockerfile \
  -t crypto-stream-flink .

docker build \
  -f zeppelin.Dockerfile \
  -t crypto-stream-zeppelin .

