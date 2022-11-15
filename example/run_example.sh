# example/run_example.sh

python adonis.py -f example/gzip.wasm --func_hooking adonis_res/gzip_api2trace_function.json -t example/trace_001.txt  -s -o example/

echo "[run_example.sh] example finished"
echo "[run_example.sh] please check the analysis results in result/example/"