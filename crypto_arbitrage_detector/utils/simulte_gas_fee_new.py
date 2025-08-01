import requests
import json
import time
import base64
from crypto_arbitrage_detector.configs.request_config import jupiter_swap_api, solana_rpc_api

def fetch_swap_transaction(quote_response, user_pubkey = jupiter_swap_api["user_pubkey"], timeout=30, max_retries=3):
    """    
    Fetch the swap transaction from Jupiter API based on the quote response.
    Args:
        quote_response (dict): The response from the Jupiter quote API containing swap details.
        user_pubkey (str): The public key of the user initiating the swap.
        timeout (int): Request timeout in seconds. Default: 30
        max_retries (int): Maximum number of retries on failure. Default: 3
    Returns:
        str: The base64 encoded swap transaction data.
    Raises:
        Exception: If the swap transaction cannot be fetched after all retries.
    """
    url = jupiter_swap_api["base_url"]
    headers = jupiter_swap_api["headers"]
    payload = {
        "userPublicKey": user_pubkey,
        "quoteResponse": quote_response,
        "prioritizationFeeLamports": None,
        "dynamicComputeUnitLimit": True
    }

    last_exception = None
    
    for attempt in range(max_retries):
        try:
            print(f"[DEBUG] 尝试获取交换交易 (attempt {attempt + 1}/{max_retries})...")
            
            res = requests.post(url, headers=headers, json=payload, timeout=timeout)
            
            # 检查HTTP状态码
            if res.status_code != 200:
                raise Exception(f"HTTP {res.status_code}: {res.text}")
            
            result = res.json()
            
            # 检查响应结构
            if "error" in result:
                raise Exception(f"API Error: {result['error']}")
            
            tx = result.get("swapTransaction", None)
            if not tx:
                raise Exception(f"Missing swapTransaction in response: {json.dumps(result, indent=2)}")
            
            print(f"[DEBUG] 交换交易获取成功，长度: {len(tx)} 字符")
            return tx
            
        except requests.exceptions.Timeout:
            last_exception = Exception(f"Request timeout after {timeout} seconds")
            print(f"[WARN] 请求超时 (attempt {attempt + 1})")
            
        except requests.exceptions.ConnectionError as e:
            last_exception = Exception(f"Connection error: {str(e)}")
            print(f"[WARN] 连接错误 (attempt {attempt + 1}): {e}")
            
        except Exception as e:
            last_exception = e
            print(f"[WARN] 获取交换交易失败 (attempt {attempt + 1}): {e}")
        
        # 如果不是最后一次尝试，等待一下再重试
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 指数退避：2, 4, 8 秒
            print(f"[INFO] 等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    
    # 所有重试都失败了
    raise Exception(f"Failed to get swap transaction after {max_retries} attempts: {last_exception}")


def estimate_gas_fee_by_complexity(base64_tx: str):
    """
    基于交易复杂度估算gas费用 (当RPC模拟失败时的fallback方法)
    
    Args:
        base64_tx (str): The base64 encoded transaction to analyze.
    
    Returns:
        int: Estimated total gas fee in lamports.
    """
    try:
        # 解码交易以分析其复杂度
        tx_bytes = base64.b64decode(base64_tx)
        
        # 基础费用
        base_fee = solana_rpc_api["base_fee"]
        
        # 根据交易大小估算计算单元
        tx_size = len(tx_bytes)
        
        # 启发式规则估算计算单元
        if tx_size < 500:
            # 简单交易 (直接转账等)
            estimated_units = 2000
        elif tx_size < 1000:
            # 中等复杂度交易 (简单DEX交换)
            estimated_units = 15000
        elif tx_size < 1500:
            # 复杂交易 (多跳交换、DeFi协议)
            estimated_units = 35000
        else:
            # 非常复杂的交易
            estimated_units = 50000
        
        # 分析交易内容以获得更准确的估算
        try:
            # 根据交易复杂度调整
            if len(tx_bytes) > 1200:
                estimated_units += 10000  # Jupiter等复杂协议
                
        except:
            pass
        
        # 计算总费用
        unit_price = solana_rpc_api["compute unit price"]
        compute_fee = int(estimated_units * unit_price)
        total_fee = base_fee + compute_fee
        
        print(f"[DEBUG] 智能估算: {total_fee} lamports (base: {base_fee}, compute: {compute_fee}, units: {estimated_units}, size: {tx_size})")
        
        return total_fee
        
    except Exception as e:
        # 如果连解码都失败了，返回保守估算
        base_fee = solana_rpc_api["base_fee"]
        conservative_estimate = base_fee + 20000  # 保守的计算单元费用
        print(f"[DEBUG] 保守估算: {conservative_estimate} lamports (fallback due to: {e})")
        return conservative_estimate


def simulate_gas_fee(base64_tx: str, unit_price_lamport: float = solana_rpc_api["compute unit price"], base_fee: int = solana_rpc_api["base_fee"], timeout=30, max_retries=3):
    """    
    Simulate gas fee for a transaction using Solana RPC with intelligent fallback.
    Args:
        base64_tx (str): The base64 encoded transaction to simulate.
        unit_price_lamport (float): The price of compute units in lamports.
        base_fee (int): The base fee in lamports.
        timeout (int): Request timeout in seconds. Default: 30
        max_retries (int): Maximum number of retries on failure. Default: 3
    Returns:
        int: The total fee in lamports for the simulated transaction.
    """
    url = solana_rpc_api["base_url"]
    headers = solana_rpc_api["headers"]
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "simulateTransaction",
        "params": [
            base64_tx,
            {
                "sigVerify": False,
                "replaceRecentBlockhash": True,
                "encoding": "base64"
            }
        ]
    }

    last_exception = None
    
    for attempt in range(max_retries):
        try:
            print(f"[DEBUG] 尝试模拟交易 gas 费用 (attempt {attempt + 1}/{max_retries})...")
            
            res = requests.post(url, headers=headers, json=body, timeout=timeout)
            
            # 检查HTTP状态码
            if res.status_code != 200:
                raise Exception(f"HTTP {res.status_code}: {res.text}")
            
            result = res.json()
            
            # 检查RPC错误
            if "error" in result:
                raise Exception(f"RPC Error: {result['error']}")
            
            # 提取计算单元消耗
            try:
                value = result["result"]["value"]
                units = value.get("unitsConsumed", 0)
                err = value.get("err", None)
                
                if err is not None:
                    # 模拟有错误，使用智能估算
                    if err == "AccountNotFound":
                        print(f"[WARN] AccountNotFound错误，使用智能估算")
                    else:
                        print(f"[WARN] 模拟错误 {err}，使用智能估算")
                    return estimate_gas_fee_by_complexity(base64_tx)
                
                if units == 0:
                    # 计算单元为0，可能是模拟问题，使用智能估算
                    print(f"[WARN] 计算单元为0，使用智能估算")
                    return estimate_gas_fee_by_complexity(base64_tx)
                
                # 正常情况：有有效的计算单元消耗
                total_fee = base_fee + int(units * unit_price_lamport)
                print(f"[DEBUG] Gas 费用模拟成功: {total_fee} lamports (base: {base_fee}, units: {units})")
                return total_fee
                
            except KeyError as e:
                print(f"[WARN] RPC响应格式错误: {e}，使用智能估算")
                return estimate_gas_fee_by_complexity(base64_tx)
            except (TypeError, ValueError) as e:
                print(f"[WARN] 数据解析错误: {e}，使用智能估算")
                return estimate_gas_fee_by_complexity(base64_tx)
                
        except requests.exceptions.Timeout:
            last_exception = Exception(f"Request timeout after {timeout} seconds")
            print(f"[WARN] 请求超时 (attempt {attempt + 1})")
            
        except requests.exceptions.ConnectionError as e:
            last_exception = Exception(f"Connection error: {str(e)}")
            print(f"[WARN] 连接错误 (attempt {attempt + 1}): {e}")
            
        except Exception as e:
            last_exception = e
            print(f"[WARN] 模拟错误 (attempt {attempt + 1}): {e}")
            
            # 如果是数据解析错误，打印详细信息
            if "Missing field" in str(e) or "Invalid data" in str(e):
                try:
                    print(f"[DEBUG] 完整响应: {json.dumps(result, indent=2)}")
                except:
                    pass
        
        # 如果不是最后一次尝试，等待一下再重试
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 指数退避
            print(f"[INFO] 等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    
    # 所有RPC尝试都失败，使用智能估算作为最终fallback
    print(f"[WARN] RPC模拟完全失败，使用智能估算 (last error: {last_exception})")
    return estimate_gas_fee_by_complexity(base64_tx)
