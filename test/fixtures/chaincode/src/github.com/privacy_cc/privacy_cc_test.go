package main

import (
	"fmt"

	"testing"

	"github.com/hyperledger/fabric/core/chaincode/shim"
)

func TestFunc(t *testing.T) {
	cc := new(PrivacyChaincode)                // 创建Chaincode对象
	stub := shim.NewMockStub("privacy_cc", cc) // 创建MockStub对象
	// 调用Init接口，将a的值设为90
	stub.MockInit("1", [][]byte{[]byte("init"), []byte("90")})
	// 调用get接口查询a的值
	res := stub.MockInvoke("1", [][]byte{[]byte("add"), []byte(`{
		"identifier": "client1_to_rsu1_epoch1",
		"data": {
			"enc_vectors": "enc_vectors1",
			"dec_aes_key": "dec_aes_key",
			"loss_slice": "loss_slice"
		}
	}`)})
	fmt.Println("The value of a is ", string(res.Payload))
	// 查询a的值
	res = stub.MockInvoke("1", [][]byte{[]byte("query"), []byte("client1_to_rsu1_epoch1")})
	fmt.Println("The value of a is ", string(res.Payload))

	// 更新client1_to_rsu1_epoch1的值
	stub.MockInvoke("1", [][]byte{[]byte("update"), []byte(`{
		"identifier": "client1_to_rsu1_epoch1",
		"data": {
			"enc_vectors": "enc_vectors1_update",
			"dec_aes_key": "dec_aes_key_update",
			"loss_slice": "loss_slice_update"
		}
	}`)})

	// 再次查询a的值
	res = stub.MockInvoke("1", [][]byte{[]byte("query"), []byte("client1_to_rsu1_epoch1")})
	fmt.Println("The new value of a is ", string(res.Payload))
}
