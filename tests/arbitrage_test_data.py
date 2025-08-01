'''
Arbitrage test data from real-world crypto exchanges
'''
from crypto_arbitrage_detector.utils.data_structures import EdgePairs
import math
import sys
import os
import networkx as nx
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


arbitrage_test_edges = [

EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', out_amount=37419528.0,
          price_ratio=0.037419528, weight=3.2855625717913735, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00011292685342811092, total_fee=252000.0, gas_fee=5098),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', out_amount=551231704862.0,
          price_ratio=551.231704862, weight=-6.31215523775135, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0003945750220919289, total_fee=500000.0, gas_fee=5098),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', out_amount=162000.0,
          price_ratio=0.000162, weight=8.72791422273189, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0, total_fee=500000.0, gas_fee=5098),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', out_amount=58205708.0,
          price_ratio=0.058205708, weight=2.8437718534524676, slippage_bps=100, platform_fee=0.0, price_impact_pct=1.56775269602829e-05, total_fee=420000.0, gas_fee=5098),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', out_amount=315135274.0,
          price_ratio=0.315135274, weight=1.154753291070174, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00016721183988297348, total_fee=0.0, gas_fee=5098),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', out_amount=820138220.0,
          price_ratio=0.82013822, weight=0.1982823919530335, slippage_bps=100, platform_fee=0.0, price_impact_pct=9.381604745888405e-06, total_fee=100000.0, gas_fee=5098),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', out_amount=8581625735.0,
          price_ratio=8.581625735, weight=-2.1496233751546074, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0001544979745080652, total_fee=0.0, gas_fee=5098),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', out_amount=4902112.0, price_ratio=0.004902112,
          weight=5.318089146320006, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00021092148257933802, total_fee=1004950.349459376, gas_fee=5098),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', out_amount=744054355.0,
          price_ratio=0.744054355, weight=0.29564118902193715, slippage_bps=100, platform_fee=0.0, price_impact_pct=7.384552437558016e-08, total_fee=100000.0, gas_fee=5098),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='So11111111111111111111111111111111111111112', out_amount=26719852146.0,
          price_ratio=26.719852146, weight=-3.2854068151950515, slippage_bps=100, platform_fee=0.0, price_impact_pct=6.528389217962326e-05, total_fee=4653476.010043068, gas_fee=5123),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', out_amount=14725912618808.0,
          price_ratio=14725.912618808, weight=-9.597363984107444, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0005118947542208568, total_fee=8848738.822802922, gas_fee=6500),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', out_amount=4328324.0, price_ratio=0.004328324,
          weight=5.442574878872092, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0001674861288782816, total_fee=17856388.966220148, gas_fee=5134),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', out_amount=1554842354.0, price_ratio=1.554842354,
          weight=-0.4413741604275827, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0003189773289818325, total_fee=14304784.010043068, gas_fee=5132),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', out_amount=8419777710.0,
          price_ratio=8.41977771, weight=-2.1305834276682134, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00011852760313317848, total_fee=2030708.763096, gas_fee=5134),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', out_amount=21914300000.0,
          price_ratio=21.9143, weight=-3.0871393917681123, slippage_bps=100, platform_fee=0.0, price_impact_pct=2.7924938021560036e-05, total_fee=4114883.950336146, gas_fee=5129),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', out_amount=229082084120.0,
          price_ratio=229.08208412, weight=-5.434080385266706, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0008991119822153381, total_fee=4512765.062188, gas_fee=5128),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', out_amount=130956440.0,
          price_ratio=0.13095644, weight=2.032890530161684, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00047384767352666413, total_fee=30965003.06596168, gas_fee=5133),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', out_amount=19880993843.0,
          price_ratio=19.880993843, weight=-2.98976419208148, slippage_bps=100, platform_fee=0.0, price_impact_pct=4.40766813323176e-05, total_fee=5027578.387182922, gas_fee=5131),
EdgePairs(from_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', to_token='So11111111111111111111111111111111111111112', out_amount=1813939.0,
          price_ratio=0.001813939, weight=6.312254555197493, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0, total_fee=0.0, gas_fee=5120),
EdgePairs(from_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', out_amount=67893.0,
          price_ratio=6.7893e-05, weight=9.597577621497555, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0, total_fee=727.0, gas_fee=5128),
EdgePairs(from_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', to_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', out_amount=294.0,
          price_ratio=2.94e-07, weight=15.039686069607729, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0, total_fee=547.0, gas_fee=5128),
EdgePairs(from_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', out_amount=105585.0,
          price_ratio=0.000105585, weight=9.15599424223607, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0, total_fee=763.0, gas_fee=5127),
EdgePairs(from_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', to_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', out_amount=571953.0,
          price_ratio=0.000571953, weight=7.466453737792605, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0, total_fee=1687.85438, gas_fee=5136),
EdgePairs(from_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', out_amount=1487745.0,
          price_ratio=0.001487745, weight=6.510493728224661, slippage_bps=100, platform_fee=0.0, price_impact_pct=4.8856386798583676e-05, total_fee=368.202982096, gas_fee=5129),
EdgePairs(from_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', to_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', out_amount=15569466.0,
          price_ratio=0.015569466, weight=4.162443590448846, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0, total_fee=0.0, gas_fee=5075),
EdgePairs(from_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', to_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', out_amount=8901.0,
          price_ratio=8.901e-06, weight=11.629346927987479, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0, total_fee=305.0, gas_fee=5969),
EdgePairs(from_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', to_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', out_amount=1349698.0,
          price_ratio=0.001349698, weight=6.607874415260908, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0, total_fee=182.0, gas_fee=5127),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='So11111111111111111111111111111111111111112', out_amount=6157931090968.0,
          price_ratio=6157.931090968, weight=-8.725496138257496, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.002357843602132746, total_fee=11081081755.158442, gas_fee=5127),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', out_amount=230079646146.0,
          price_ratio=230.079646146, weight=-5.43842553657079, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.003973925123217754, total_fee=16330833253.247135, gas_fee=6000),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', out_amount=3277951565789227.0,
          price_ratio=3277951.565789227, weight=-15.002729262639605, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.03666089484743752, total_fee=27124019130.0, gas_fee=5133),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', out_amount=339684304244.0,
          price_ratio=339.684304244, weight=-5.828016669341927, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.05463513202205869, total_fee=22366293709.0, gas_fee=5175),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', out_amount=1874025931616.0,
          price_ratio=1874.025931616, weight=-7.535844300277869, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.03677182538723468, total_fee=22625217448.18244, gas_fee=5175),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', out_amount=5048923829061.0,
          price_ratio=5048.923829061, weight=-8.526930396403463, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0026570517626593364, total_fee=13483105022.0, gas_fee=5133),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', out_amount=47371790585393.0,
          price_ratio=47371.790585393, weight=-10.765782195190582, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.10564509914888709, total_fee=6296701006.0, gas_fee=5134),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', out_amount=30141908247.0,
          price_ratio=30.141908247, weight=-3.405916503967903, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.004136110841878016, total_fee=3739293088.4468346, gas_fee=5075),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', out_amount=4579139558209.0,
          price_ratio=4579.139558209, weight=-8.429266390071886, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.002944913588039597, total_fee=13483105022.0, gas_fee=5132),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='So11111111111111111111111111111111111111112', out_amount=17160854635.0,
          price_ratio=17.160854635, weight=-2.8426308967240717, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0012319763805680617, total_fee=8259862.552918199, gas_fee=6500),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', out_amount=642076457.0,
          price_ratio=0.642076457, weight=0.4430478904827417, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0013311966466034164, total_fee=6644851.010152, gas_fee=5175),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', out_amount=9458334758275.0,
          price_ratio=9458.334758275, weight=-9.154651616770208, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0012664270144838374, total_fee=11515313.786156055, gas_fee=5131),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', out_amount=2779906.0,
          price_ratio=0.002779906, weight=5.885338164800903, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0012547454119331742, total_fee=11086033.15736, gas_fee=7000),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', out_amount=5408063135.0, price_ratio=5.408063135,
          weight=-1.6878910130438198, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0012376911346734692, total_fee=6717444.938324399, gas_fee=7000),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', out_amount=14074315762.0,
          price_ratio=14.074315762, weight=-2.6443515591318136, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.001121629133400209, total_fee=7221919.727394495, gas_fee=5133),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', out_amount=147190438203.0,
          price_ratio=147.190438203, weight=-4.991727246324868, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0015054246735095647, total_fee=7118322.502598, gas_fee=5135),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', out_amount=84110652.0,
          price_ratio=0.084110652, weight=2.47562206128418, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0014749895613691295, total_fee=7029771.399746, gas_fee=5129),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', out_amount=12768394613.0,
          price_ratio=12.768394613, weight=-2.5469729466365014, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0012487579913681753, total_fee=7259318.786156055, gas_fee=5132),
EdgePairs(from_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', to_token='So11111111111111111111111111111111111111112', out_amount=3172876182.0,
          price_ratio=3.172876182, weight=-1.1546384894633657, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00010927797119589385, total_fee=0.0, gas_fee=5120),
EdgePairs(from_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', out_amount=118727517.0,
          price_ratio=0.118727517, weight=2.130924184518989, slippage_bps=100, platform_fee=0.0, price_impact_pct=7.186661472289953e-05, total_fee=1269219.0, gas_fee=6000),
EdgePairs(from_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', to_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', out_amount=1748866050708.0,
          price_ratio=1748.866050708, weight=-7.466722885869604, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00026719392394931234, total_fee=1586353.0, gas_fee=6000),
EdgePairs(from_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', to_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', out_amount=514029.0,
          price_ratio=0.000514029, weight=7.573230873867208, slippage_bps=100, platform_fee=0.0, price_impact_pct=2.134005905511811e-05, total_fee=1586513.0, gas_fee=6000),
EdgePairs(from_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', out_amount=184665445.0,
          price_ratio=0.184665445, weight=1.6892094964483113, slippage_bps=100, platform_fee=0.0, price_impact_pct=3.918450018760418e-05, total_fee=1332537.0, gas_fee=6000),
EdgePairs(from_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', out_amount=2602100000.0,
          price_ratio=2.6021, weight=-0.9563188113272276, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0, total_fee=0.0, gas_fee=5075),
EdgePairs(from_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', to_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', out_amount=27226010498.0,
          price_ratio=27.226010498, weight=-3.304172784677513, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00024092422433138314, total_fee=0.0, gas_fee=5075),
EdgePairs(from_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', to_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', out_amount=15551621.0,
          price_ratio=0.015551621, weight=4.163590401416971, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00048606396828119146, total_fee=1586270.0, gas_fee=5127),
EdgePairs(from_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', to_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', out_amount=2360664323.0,
          price_ratio=2.360664323, weight=-0.858943072222465, slippage_bps=100, platform_fee=0.0, price_impact_pct=1.288210704072586e-05, total_fee=317271.0, gas_fee=5075),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='So11111111111111111111111111111111111111112', out_amount=1219140000.0,
          price_ratio=1.21914, weight=-0.19814569214083982, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0001366423712958265, total_fee=0.0, gas_fee=5075),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', out_amount=45619229.0,
          price_ratio=0.045619229, weight=3.0874259627509546, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00025877516970070167, total_fee=307224.0, gas_fee=5075),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', out_amount=672027486441.0,
          price_ratio=672.027486441, weight=-6.510299242128632, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0002321845140829493, total_fee=609570.0, gas_fee=5075),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', out_amount=197501.0,
          price_ratio=0.000197501, weight=8.529766910344776, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00017591047720763724, total_fee=609570.0, gas_fee=5126),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', out_amount=70960750.0,
          price_ratio=0.07096075, weight=2.6456283717018314, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00015432398270389088, total_fee=512040.0, gas_fee=5075),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', out_amount=384183668.0,
          price_ratio=0.384183668, weight=0.9566345386610573, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0003305017321137448, total_fee=0.0, gas_fee=5075),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', out_amount=10462350937.0,
          price_ratio=10.462350937, weight=-2.3477831883544815, slippage_bps=100, platform_fee=0.0, price_impact_pct=1.7421402085023762e-05, total_fee=0.0, gas_fee=6000),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', out_amount=5976262.0,
          price_ratio=0.005976262, weight=5.119959990077849, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00041238112655343176, total_fee=609570.0, gas_fee=5075),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', out_amount=907106416.0,
          price_ratio=0.907106416, weight=0.09749550829618557, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00013669096752547867, total_fee=121914.0, gas_fee=5126),
EdgePairs(from_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', to_token='So11111111111111111111111111111111111111112', out_amount=116394488.0, price_ratio=0.116394488,
          weight=2.1507700987579232, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0012917737278677276, total_fee=349183.46400000004, gas_fee=5500),
EdgePairs(from_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', out_amount=4355757.0, price_ratio=0.004355757,
          weight=5.436256860591437, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0009903166534317271, total_fee=378517.46400000004, gas_fee=5128),
EdgePairs(from_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', to_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', out_amount=64161393136.0,
          price_ratio=64.161393136, weight=-4.161401676788859, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.000530197438972574, total_fee=407381.46400000004, gas_fee=6000),
EdgePairs(from_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', to_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', out_amount=18856.0, price_ratio=1.8856e-05,
          weight=10.878679392330444, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.001005454555608592, total_fee=407381.46400000004, gas_fee=5075),
EdgePairs(from_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', out_amount=6774884.0, price_ratio=0.006774884,
          weight=4.994533034134169, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.000959708709078964, total_fee=398071.46400000004, gas_fee=5075),
EdgePairs(from_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', to_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', out_amount=36681490.0, price_ratio=0.03668149,
          weight=3.305483010826759, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00026802915848946567, total_fee=408548.46400000004, gas_fee=5075),
EdgePairs(from_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', out_amount=95463329.0, price_ratio=0.095463329,
          weight=2.3490130947671055, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0009139407142061161, total_fee=360822.46400000004, gas_fee=5075),
EdgePairs(from_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', to_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', out_amount=570672.0,
          price_ratio=0.000570672, weight=7.468695944179975, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00015920193817993983, total_fee=23431.0, gas_fee=6000),
EdgePairs(from_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', to_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', out_amount=86607240.0, price_ratio=0.08660724,
          weight=2.446371864136902, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0012524477311245752, total_fee=360823.46400000004, gas_fee=5075),
EdgePairs(from_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', to_token='So11111111111111111111111111111111111111112', out_amount=203927801674.0,
          price_ratio=203.927801674, weight=-5.317766017839356, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0001252286762384524, total_fee=0.0, gas_fee=6500),
EdgePairs(from_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', out_amount=7627053364.0,
          price_ratio=7.627053364, weight=-2.0317015798797957, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0008422079453299291, total_fee=18765607.0, gas_fee=6500),
EdgePairs(from_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', to_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', out_amount=112351354273074.0,
          price_ratio=112351.354273074, weight=-11.629386331595779, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0009212000596313167, total_fee=28549986.0, gas_fee=5175),
EdgePairs(from_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', to_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', out_amount=33024439.0,
          price_ratio=0.033024439, weight=3.410507415848992, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0005438393120973515, total_fee=32635139.0, gas_fee=6500),
EdgePairs(from_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', out_amount=11846412770.0,
          price_ratio=11.84641277, weight=-2.4720251019210195, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.002210015456963533, total_fee=103351463.0, gas_fee=5175),
EdgePairs(from_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', to_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', out_amount=64249775084.0,
          price_ratio=64.249775084, weight=-4.1627782231310695, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00046777240707918035, total_fee=0.0, gas_fee=5075),
EdgePairs(from_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', out_amount=167260573901.0,
          price_ratio=167.260573901, weight=-5.119552919138453, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0, total_fee=15704044.0, gas_fee=7000),
EdgePairs(from_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', to_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', out_amount=1740844965808.0,
          price_ratio=1740.844965808, weight=-7.4621258868703, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.005495903978170183, total_fee=0.0, gas_fee=5075),
EdgePairs(from_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', to_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', out_amount=151741844375.0,
          price_ratio=151.741844375, weight=-5.022180684673281, slippage_bps=100, platform_fee=0.0, price_impact_pct=1.503169861870318e-05, total_fee=15703975.0, gas_fee=7500),
EdgePairs(from_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', to_token='So11111111111111111111111111111111111111112', out_amount=1343806504.0,
          price_ratio=1.343806504, weight=-0.295506261498153, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0001348770406807828, total_fee=0.0, gas_fee=5075),
EdgePairs(from_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', out_amount=50283046.0,
          price_ratio=0.050283046, weight=2.9900873163472177, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00027875623756374126, total_fee=537523.0, gas_fee=5175),
EdgePairs(from_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', to_token='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', out_amount=740746788355.0,
          price_ratio=740.746788355, weight=-6.607658850777722, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00014481126618107776, total_fee=671904.0, gas_fee=6000),
EdgePairs(from_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', to_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', out_amount=217697.0,
          price_ratio=0.000217697, weight=8.43240637025051, slippage_bps=100, platform_fee=0.0, price_impact_pct=9.020066237174899e-05, total_fee=671904.0, gas_fee=6000),
EdgePairs(from_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', out_amount=78215290.0,
          price_ratio=0.07821529, weight=2.5482901262465805, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0001749370922938339, total_fee=698769.6504, gas_fee=6000),
EdgePairs(from_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', to_token='JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', out_amount=423520022.0,
          price_ratio=0.423520022, weight=0.8591544885577485, slippage_bps=100, platform_fee=0.0, price_impact_pct=4.785547327473572e-05, total_fee=134380.6504, gas_fee=6000),
EdgePairs(from_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', out_amount=1102185596.0,
          price_ratio=1.102185596, weight=-0.09729511397296824, slippage_bps=100, platform_fee=0.0, price_impact_pct=6.367206231172652e-05, total_fee=134380.6504, gas_fee=5500),
EdgePairs(from_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', to_token='J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr', out_amount=11531260243.0,
          price_ratio=11.531260243, weight=-2.445061629522249, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.0003960755353855462, total_fee=247254.6504, gas_fee=6000),
EdgePairs(from_token='5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm', to_token='7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', out_amount=6587374.0,
          price_ratio=0.006587374, weight=5.022600492432307, slippage_bps=100, platform_fee=0.0, price_impact_pct=0.00043282760182151514, total_fee=671904.0, gas_fee=5175)
]


def create_test_graph_from_edges(edges: list) -> nx.DiGraph:
    """
    Create a NetworkX DiGraph from EdgePairs data for testing algorithms
    """
    graph = nx.DiGraph()

    # Add all unique tokens as nodes
    tokens = set()
    for edge in edges:
        tokens.add(edge.from_token)
        tokens.add(edge.to_token)

    for token in tokens:
        graph.add_node(token)

    # Add edges with all relevant data
    for edge in edges:
        graph.add_edge(
            edge.from_token,
            edge.to_token,
            weight=edge.weight,
            out_amount=edge.out_amount,
            price_ratio=edge.price_ratio,
            slippage_bps=edge.slippage_bps,
            platform_fee=edge.platform_fee,
            price_impact_pct=edge.price_impact_pct,
            total_fee=edge.total_fee,
            gas_fee=edge.gas_fee
        )

    return graph


def create_test_graph_for_bellman_ford() -> nx.DiGraph:
    """
    Create test graph specifically for Bellman-Ford algorithm testing
    """
    return create_test_graph_from_edges(arbitrage_test_edges)


def create_balanced_test_graph() -> nx.DiGraph:
    """
    Create test graph with no arbitrage opportunities (for negative testing)
    """
    return create_test_graph_from_edges(balanced_test_edges)
