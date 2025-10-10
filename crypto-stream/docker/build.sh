# -- Building the Images

docker build \
  -f flink.Dockerfile \
  -t crypto-stream-flink .

docker build \
  -f jupyter.Dockerfile \
  -t crypto-stream-jupyter .

