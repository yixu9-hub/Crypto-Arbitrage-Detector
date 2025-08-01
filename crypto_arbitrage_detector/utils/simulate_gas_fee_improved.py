import requests
import json
import time
from typing import Optional, Dict, Any
from crypto_arbitrage_detector.configs.request_config import jupiter_swap_api, solana_rpc_api

def fetch_swap_transaction(
    quote_response: Dict[str, Any], 
    user_pubkey: str = jupiter_swap_api["user_pubkey"],
    timeout: int = 30,
    max_retries: int = 3
) -> str:
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
    headers = jupiter_swap_api["headers"].copy()
    headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
    
    payload = {
        "userPublicKey": user_pubkey,
        "quoteResponse": quote_response,
        "prioritizationFeeLamports": None,
        "dynamicComputeUnitLimit": True,
        "asLegacyTransaction": False  # 使用最新的交易格式
    }

    last_exception = None
    
    for attempt in range(max_retries):
        try:
            print(f"[DEBUG] 尝试获取交换交易 (attempt {attempt + 1}/{max_retries})...")
            
            res = requests.post(
                url, 
                headers=headers, 
                json=payload,
                timeout=timeout
            )
            
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
            
        except requests.exceptions.RequestException as e:
            last_exception = Exception(f"Request error: {str(e)}")
            print(f"[WARN] 请求错误 (attempt {attempt + 1}): {e}")
            
        except Exception as e:
            last_exception = e
            print(f"[WARN] 其他错误 (attempt {attempt + 1}): {e}")
        
        # 如果不是最后一次尝试，等待一下再重试
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 指数退避：2, 4, 8 秒
            print(f"[INFO] 等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    
    # 所有重试都失败了
    raise Exception(f"Failed to get swap transaction after {max_retries} attempts: {last_exception}")


def simulate_gas_fee(
    base64_tx: str, 
    unit_price_lamport: float = solana_rpc_api["compute unit price"], 
    base_fee: int = solana_rpc_api["base_fee"],
    timeout: int = 30,
    max_retries: int = 3
) -> int:
    """    
    Simulate gas fee for a transaction using Solana RPC.
    
    Args:
        base64_tx (str): The base64 encoded transaction to simulate.
        unit_price_lamport (float): The price of compute units in lamports.
        base_fee (int): The base fee in lamports.
        timeout (int): Request timeout in seconds. Default: 30
        max_retries (int): Maximum number of retries on failure. Default: 3
        
    Returns:
        int: The total fee in lamports for the simulated transaction.
        
    Raises:
        Exception: If the simulation fails after all retries.
    """
    url = solana_rpc_api["base_url"]
    headers = solana_rpc_api["headers"].copy()
    
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "simulateTransaction",
        "params": [
            base64_tx,
            {
                "sigVerify": False,
                "replaceRecentBlockhash": True,
                "encoding": "base64",
                "commitment": "processed"  # 使用更快的确认级别
            }
        ]
    }

    last_exception = None
    
    for attempt in range(max_retries):
        try:
            print(f"[DEBUG] 尝试模拟交易 gas 费用 (attempt {attempt + 1}/{max_retries})...")
            
            res = requests.post(
                url, 
                headers=headers, 
                json=body,
                timeout=timeout
            )
            
            # 检查HTTP状态码
            if res.status_code != 200:
                raise Exception(f"HTTP {res.status_code}: {res.text}")
            
            result = res.json()
            
            # 检查RPC错误
            if "error" in result:
                raise Exception(f"RPC Error: {result['error']}")
            
            # 提取计算单元消耗
            try:
                units = result["result"]["value"]["unitsConsumed"]
                total_fee = base_fee + int(units * unit_price_lamport)
                
                print(f"[DEBUG] Gas 费用模拟成功:")
                print(f"  - 基础费用: {base_fee} lamports")
                print(f"  - 消耗单元: {units}")
                print(f"  - 单元价格: {unit_price_lamport} lamports")
                print(f"  - 总费用: {total_fee} lamports")
                
                return total_fee
                
            except KeyError as e:
                raise Exception(f"Missing field in simulation result: {e}")
            except (TypeError, ValueError) as e:
                raise Exception(f"Invalid data in simulation result: {e}")
                
        except requests.exceptions.Timeout:
            last_exception = Exception(f"Request timeout after {timeout} seconds")
            print(f"[WARN] 请求超时 (attempt {attempt + 1})")
            
        except requests.exceptions.ConnectionError as e:
            last_exception = Exception(f"Connection error: {str(e)}")
            print(f"[WARN] 连接错误 (attempt {attempt + 1}): {e}")
            
        except requests.exceptions.RequestException as e:
            last_exception = Exception(f"Request error: {str(e)}")
            print(f"[WARN] 请求错误 (attempt {attempt + 1}): {e}")
            
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
    
    # 所有重试都失败了
    raise Exception(f"Failed to simulate gas fee after {max_retries} attempts: {last_exception}")


def get_gas_fee_estimate(quote_response: Dict[str, Any]) -> int:
    """
    便捷函数：获取 gas 费用估算，包含完整的错误处理
    
    Args:
        quote_response: Jupiter API 返回的报价数据
        
    Returns:
        int: Gas 费用 (lamports)
    """
    try:
        # 尝试真实模拟
        swap_tx = fetch_swap_transaction(quote_response)
        gas_fee = simulate_gas_fee(swap_tx)
        return gas_fee
        
    except Exception as e:
        print(f"[ERROR] Gas 费用模拟失败: {e}")
        
        # 使用基于路由复杂度的估算
        try:
            route_plan = quote_response.get("routePlan", [])
            base_fee = solana_rpc_api["base_fee"]
            
            if not route_plan:
                estimated_units = 10000  # 简单交换
            else:
                hop_count = len(route_plan)
                estimated_units = 5000 + (hop_count * 8000)  # 基于跳数估算
            
            unit_price = solana_rpc_api["compute unit price"]
            estimated_fee = base_fee + int(estimated_units * unit_price)
            
            print(f"[INFO] 使用离线估算的 Gas 费用: {estimated_fee} lamports")
            return estimated_fee
            
        except Exception as e2:
            print(f"[ERROR] 离线估算也失败: {e2}")
            default_fee = solana_rpc_api["base_fee"]
            print(f"[INFO] 使用默认 Gas 费用: {default_fee} lamports")
            return default_fee


# 测试函数
if __name__ == "__main__":
    print("🧪 测试改进版本的 gas 费用模拟...")
    
    # 模拟测试数据
    test_quote = {
        "inputMint": "So11111111111111111111111111111111111111112",
        "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "inAmount": "1000000000",
        "outAmount": "191000000",
        "routePlan": []
    }
    
    # 测试便捷函数
    try:
        gas_fee = get_gas_fee_estimate(test_quote)
        print(f"✅ 最终 Gas 费用: {gas_fee} lamports")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
