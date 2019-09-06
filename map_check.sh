if [ $# -ne == 1 ]; then
    echo "backupに保存したデイレクトリ名で指定してね〜"
    echo "usage map_check.sh 0904_block_a"
fi

echo 500 > $1_map.txt
./darknet detector map data/config/learning.data data/config/etrobo2019_block.cfg backup/$1/etrobo2019_block_500.weights -gpus 0,1 | grep -v rank >> $1_map.txt
echo 600 >> $1_map.txt
./darknet detector map data/config/learning.data data/config/etrobo2019_block.cfg backup/$1/etrobo2019_block_600.weights -gpus 0,1 | grep -v rank >> $1_map.txt
echo 700 >> $1_map.txt
./darknet detector map data/config/learning.data data/config/etrobo2019_block.cfg backup/$1/etrobo2019_block_700.weights -gpus 0,1 | grep -v rank >> $1_map.txt
echo 800 >> $1_map.txt
./darknet detector map data/config/learning.data data/config/etrobo2019_block.cfg backup/$1/etrobo2019_block_800.weights -gpus 0,1 | grep -v rank >> $1_map.txt
echo 900 >> $1_map.txt
./darknet detector map data/config/learning.data data/config/etrobo2019_block.cfg backup/$1/etrobo2019_block_900.weights -gpus 0,1 | grep -v rank >> $1_map.txt
echo 1000 >> $1_map.txt
./darknet detector map data/config/learning.data data/config/etrobo2019_block.cfg backup/$1/etrobo2019_block_1000.weights -gpus 0,1 | grep -v rank >> $1_map.txt
echo 1100 >> $1_map.txt
./darknet detector map data/config/learning.data data/config/etrobo2019_block.cfg backup/$1/etrobo2019_block_1100.weights -gpus 0,1 | grep -v rank >> $1_map.txt
echo 1200 >> $1_map.txt
./darknet detector map data/config/learning.data data/config/etrobo2019_block.cfg backup/$1/etrobo2019_block_1200.weights -gpus 0,1 | grep -v rank >> $1_map.txt
echo 1300 >> $1_map.txt
./darknet detector map data/config/learning.data data/config/etrobo2019_block.cfg backup/$1/etrobo2019_block_1300.weights -gpus 0,1 | grep -v rank >> $1_map.txt
echo 1400 >> $1_map.txt
./darknet detector map data/config/learning.data data/config/etrobo2019_block.cfg backup/$1/etrobo2019_block_1400.weights -gpus 0,1 | grep -v rank >> $1_map.txt
echo 1500 >> $1_map.txt
./darknet detector map data/config/learning.data data/config/etrobo2019_block.cfg backup/$1/etrobo2019_block_1500.weights -gpus 0,1 | grep -v rank >> $1_map.txt
echo 2000 >> $1_map.txt
./darknet detector map data/config/learning.data data/config/etrobo2019_block.cfg backup/$1/etrobo2019_block_2000.weights -gpus 0,1 | grep -v rank >> $1_map.txt