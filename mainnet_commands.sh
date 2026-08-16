#!/bin/bash
# Mainnet QTY Commands for Dilithium Wallet Operations

# Note: Remove -regtest flag for mainnet operations
# QTY is running on mainnet at port 8332
# Wallet operations use mainnet blockchain

# Navigate to src directory where qty-cli is located
cd "$(dirname "$0")/src" || exit 1

#1. Create a new wallet
./qty-cli createwallet "dilithium_wallet"

#2. Dump information about the wallet
./qty-cli -rpcwallet="dilithium_wallet" getwalletinfo

#3. Create a new Dilithium address
./qty-cli -rpcwallet="dilithium_wallet" getnewdilithiumaddress

#4. Sign an arbitrary message with Dilithium
# Replace <address> and <message> with actual values
# Example: ./qty-cli -rpcwallet="dilithium_wallet" signmessagewithdilithium "qty1..." "Hello World"
./qty-cli -rpcwallet="dilithium_wallet" signmessagewithdilithium "<address>" "<message>"

#5. Verify the Dilithium signature
# Replace <message>, <address>, and <signature> with actual values
./qty-cli verifydilithiumsignature "<message>" "<address>" "<signature>"

#6. Note: On mainnet, you cannot use generatetoaddress to mine coins
# You need to receive funds from another source or use a mining pool
# For testing on mainnet, you would need real QTY coins sent to your address
echo "Note: On mainnet, you cannot generate blocks with generatetoaddress."
echo "You need to receive real QTY from another source."

#7. See which outputs we can spend?
# First, let's see what type of output we have
./qty-cli -rpcwallet="dilithium_wallet" listunspent

#8. Create a raw transaction
# Create a transaction with proper fee
# Replace <unspent> txid/vout and <address> with actual values
# Example: ./qty-cli createrawtransaction '[{"txid":"abc123...","vout":0}]' '{"qty1...":0.00099}'
./qty-cli createrawtransaction \
  '[{"txid":"<unspent>","vout":0}]' \
  '{"<address>":0.00099}'

#9. Then sign it with Dilithium
# Replace <hex> with the hex from step 8
./qty-cli -rpcwallet="dilithium_wallet" signtransactionwithdilithium <hex>

#10. Broadcast the transaction
# Replace <signed_hex> with the signed transaction hex from step 9
./qty-cli sendrawtransaction <signed_hex>
