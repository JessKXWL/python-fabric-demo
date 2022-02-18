# python-fabric-demo

The fabric-sdk-py test has been completed

https://github.com/hyperledger/fabric-sdk-py.git

# packages use
```
go version
go1.17.7 linux/amd64

github.com/hyperledger/fabric/common/util@v1.4
github.com/hyperledger/fabric/core/chaincode/shim@v1.4
github.com/hyperledger/fabric/protos/peer@v1.4
```
# Usage
```
git clone https://github.com/JessKXWL/python-fabric-demo.git

cd python-fabric-demo

source /root/fabric-sdk-py/venv/bin/activate

export PYTHONPATH="${PYTHONPATH}:/root/python-fabric-demo"

export HLF_VERSION=1.4.6

python3 -u test/integration/start.py 2>&1 | tee  log.log
```
