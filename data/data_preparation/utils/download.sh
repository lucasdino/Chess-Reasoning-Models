set -ex

# For test data
mkdir test
cd test
wget https://storage.googleapis.com/searchless_chess/data/test/action_value_data.bag
cd ..

# # For train data
# mkdir train
# cd train
# for idx in $(seq -f "%05g" 0 2147)
# do
#   wget https://storage.googleapis.com/searchless_chess/data/train/action_value-$idx-of-02148_data.bag
# done
# cd ..
