package shared

import (
	"net/rpc"
	"sync"
)

// One reusable RPC connection per server address. Opening a new TCP connection
// for every message exhausted the OS's ephemeral ports under load (about 940
// transfers on macOS), after which every call failed silently.
var (
	rpcPoolMu sync.Mutex
	rpcPool   = map[string]*rpc.Client{}
)

// GetRPCClient returns the cached connection for addr, dialing it the first time.
// rpc.Client is safe for concurrent use, so callers share it and must not Close it.
func GetRPCClient(addr string) (*rpc.Client, error) {
	rpcPoolMu.Lock()
	defer rpcPoolMu.Unlock()
	if c, ok := rpcPool[addr]; ok {
		return c, nil
	}
	c, err := rpc.Dial("tcp", addr)
	if err != nil {
		return nil, err
	}
	rpcPool[addr] = c
	return c, nil
}
