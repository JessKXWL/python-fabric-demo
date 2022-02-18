# python-fabric-demo

The fabric-sdk-py test has been completed

https://github.com/hyperledger/fabric-sdk-py.git

# Usage
`
git clone https://github.com/JessKXWL/python-fabric-demo.git

cd python-fabric-demo

source /root/fabric-sdk-py/venv/bin/activate

export PYTHONPATH="${PYTHONPATH}:/root/python-fabric-demo"

export HLF_VERSION=1.4.6

python3 -u test/integration/start.py 2>&1 | tee  log.log
`
