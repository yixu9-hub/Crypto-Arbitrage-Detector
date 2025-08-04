'''
Arbitrage test data from real-world crypto exchanges
'''
import math
import sys
import os
import networkx as nx
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crypto_arbitrage_detector.utils.data_structures import EdgePairs


arbitrage_test_edges = [

EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='So11111111111111111111111111111111111111112', in_amount=298507.46268656716, out_amount=301111.0, price_ratio=30.1111, weight=-3.4048938745397233, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=220.09663880597014, gas_fee=5113),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', in_amount=298507.46268656716, out_amount=296600.3166, price_ratio=0.0042, weight=5.472670753692815, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.014104283604135893, total_fee=149.25373134328356, gas_fee=5109),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', in_amount=298507.46268656716, out_amount=300871.2735, price_ratio=1.9089, weight=-0.6465271599247191, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=838.8858925373135, gas_fee=5120),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', in_amount=298507.46268656716, out_amount=301366.39680000005, price_ratio=24.6456, weight=-3.204598385570058, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=145.41783880597015, gas_fee=5119),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', in_amount=298507.46268656716, out_amount=301248.4881, price_ratio=22.9313, weight=-3.132502789549713, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=141.41783880597015, gas_fee=5133),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', in_amount=298507.46268656716, out_amount=306877.14719999995, price_ratio=98.7696, weight=-4.59278986509914, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=117.78349253731344, gas_fee=5119),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', in_amount=298507.46268656716, out_amount=301231.1604, price_ratio=26.6836, weight=-3.2840491444785807, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=145.41783880597015, gas_fee=5141),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', in_amount=298507.46268656716, out_amount=300953.0639, price_ratio=1559.3423, weight=-7.352019408780132, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=571.5806925373134, gas_fee=5119),
EdgePairs(from_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', to_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', in_amount=298507.46268656716, out_amount=301060.252, price_ratio=4.843, weight=-1.577534363421092, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=136.7014925373134, gas_fee=5018),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', in_amount=10000.0, out_amount=10000.0, price_ratio=0.0335, weight=3.396209840151116, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=31.2164, gas_fee=6475),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', in_amount=10000.0, out_amount=10087.36, price_ratio=0.064, weight=2.7488721956224653, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=49.8656, gas_fee=6354),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', in_amount=10000.0, out_amount=10036.742400000001, price_ratio=0.8208, weight=0.197475804565632, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=105.6788, gas_fee=5943),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', in_amount=10000.0, out_amount=10010.394, price_ratio=0.762, weight=0.2718087232954908, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=1.0, gas_fee=5663),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', in_amount=10000.0, out_amount=10281.9951, price_ratio=3.3093, weight=-1.1967366866613087, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=25.0, gas_fee=6481),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', in_amount=10000.0, out_amount=10030.2765, price_ratio=0.8885, weight=0.11822063138743108, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=105.6788, gas_fee=5389),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', in_amount=10000.0, out_amount=10084.25, price_ratio=52.25, weight=-3.9560398908449206, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=43.6492, gas_fee=6492),
EdgePairs(from_token='So11111111111111111111111111111111111111112', to_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', in_amount=10000.0, out_amount=10002.187600000001, price_ratio=0.1609, weight=1.8269722249837996, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=0.0, gas_fee=5262),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', in_amount=70619123.0, out_amount=70062059.70149253, price_ratio=234.7079, weight=-5.458341762281972, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.00017207986310288824, total_fee=63561.0, gas_fee=5118),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='So11111111111111111111111111111111111111112', in_amount=70619123.0, out_amount=70619123.0, price_ratio=7061.9123, weight=-8.862471157832914, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.00025397196668706256, total_fee=7068.0468, gas_fee=5108),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', in_amount=70619123.0, out_amount=70593488.844, price_ratio=447.8856, weight=-6.104537842662942, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0002814730388483144, total_fee=36729.0468, gas_fee=5117),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', in_amount=70619123.0, out_amount=70721825.33880001, price_ratio=5783.5971, weight=-8.662781103736043, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0002539739400482406, total_fee=14131.0468, gas_fee=5117),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', in_amount=70619123.0, out_amount=70682237.2917, price_ratio=5380.3941, weight=-8.59051690326108, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0002805892650744582, total_fee=14130.0468, gas_fee=5131),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', in_amount=70619123.0, out_amount=72010674.905, price_ratio=23176.915, weight=-10.050912019166917, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=41248.695999999996, gas_fee=5119),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', in_amount=70619123.0, out_amount=70686486.67740001, price_ratio=6261.5366, weight=-8.742180897231753, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0003044709067971322, total_fee=7102.0, gas_fee=5139),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', in_amount=70619123.0, out_amount=70620220.647, price_ratio=365907.879, weight=-12.810136883981256, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.00034711254656194447, total_fee=147207.234, gas_fee=5119),
EdgePairs(from_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', to_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', in_amount=70619123.0, out_amount=70638805.6872, price_ratio=1136.3298, weight=-7.035558874048708, slippage_bps=50, platform_fee=0.0, price_impact_pct=2.9776e-05, total_fee=63554.6492, gas_fee=5017),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', in_amount=157615.0, out_amount=156477.6119402985, price_ratio=0.5242, weight=0.645881988092831, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=209.43490000000003, gas_fee=5119),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='So11111111111111111111111111111111111111112', in_amount=157615.0, out_amount=157615.0, price_ratio=15.7615, weight=-2.757570257565601, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.00036151106353028966, total_fee=47.2845, gas_fee=5105),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', in_amount=157615.0, out_amount=155362.0706, price_ratio=0.0022, weight=6.119297918617867, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.014374252925803886, total_fee=865.6558, gas_fee=5114),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', in_amount=157615.0, out_amount=157865.92560000002, price_ratio=12.9102, weight=-2.558017696605323, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.00022407664694012837, total_fee=64.9119, gas_fee=5118),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', in_amount=157615.0, out_amount=157792.4481, price_ratio=12.0113, weight=-2.4858478733647518, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.00012969344264389133, total_fee=93.3665, gas_fee=5134),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', in_amount=157615.0, out_amount=160771.4043, price_ratio=51.7449, weight=-3.946325876564399, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=80.9337, gas_fee=5118),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', in_amount=157615.0, out_amount=157788.6108, price_ratio=13.9772, weight=-2.637427430622687, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.00021932462217995677, total_fee=93.3665, gas_fee=5141),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', in_amount=157615.0, out_amount=157669.3428, price_ratio=816.9396, weight=-6.7055651631185516, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0002690819149090148, total_fee=317.1569, gas_fee=5119),
EdgePairs(from_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', to_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', in_amount=157615.0, out_amount=157722.5008, price_ratio=2.5372, weight=-0.931061110777605, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=88.28450000000001, gas_fee=5017),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', in_amount=12228.000000000002, out_amount=12119.402985074626, price_ratio=0.0406, weight=3.20398721237445, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=7.3368, gas_fee=5110),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='So11111111111111111111111111111111111111112', in_amount=12228.000000000002, out_amount=12228.0, price_ratio=1.2228, weight=-0.20114331103454247, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=130.442, gas_fee=5212),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', in_amount=12228.000000000002, out_amount=12230.923999999999, price_ratio=0.0776, weight=2.556187851792964, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=24.7632, gas_fee=5119),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', in_amount=12228.000000000002, out_amount=12223.978500000001, price_ratio=0.9305, weight=0.07203320289983162, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=32.979600000000005, gas_fee=5228),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', in_amount=12228.000000000002, out_amount=12462.177, price_ratio=4.011, weight=-1.3890405867879159, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=13.6556, gas_fee=5118),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', in_amount=12228.000000000002, out_amount=12240.6627, price_ratio=1.0843, weight=-0.08093461749599924, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=130.442, gas_fee=6000),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', in_amount=12228.000000000002, out_amount=12283.1376, price_ratio=63.6432, weight=-4.153292485046427, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=37.196, gas_fee=6000),
EdgePairs(from_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', to_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', in_amount=12228.000000000002, out_amount=12215.226, price_ratio=0.1965, weight=1.627092847672821, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=1.2228, gas_fee=5500),
EdgePairs(from_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', in_amount=13137.0, out_amount=13044.776119402984, price_ratio=0.0437, weight=3.1304071768805923, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=71.3655, gas_fee=6000),
EdgePairs(from_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', to_token='So11111111111111111111111111111111111111112', in_amount=13137.0, out_amount=13137.0, price_ratio=1.3137, weight=-0.2728475834933254, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=143.32930000000002, gas_fee=6000),
EdgePairs(from_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', in_amount=13137.0, out_amount=13145.091, price_ratio=0.0834, weight=2.484106969617436, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=31.4341, gas_fee=6000),
EdgePairs(from_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', in_amount=13137.0, out_amount=13157.328000000001, price_ratio=1.076, weight=-0.07325046173959274, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=143.32930000000002, gas_fee=6000),
EdgePairs(from_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', to_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', in_amount=13137.0, out_amount=13423.7935, price_ratio=4.3205, weight=-1.463371136299317, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=78.3655, gas_fee=6000),
EdgePairs(from_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', to_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', in_amount=13137.0, out_amount=13149.4272, price_ratio=1.1648, weight=-0.1525493984602845, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=143.32930000000002, gas_fee=6000),
EdgePairs(from_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', to_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', in_amount=13137.0, out_amount=13188.577800000001, price_ratio=68.3346, weight=-4.224416226883864, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=62.5161, gas_fee=6000),
EdgePairs(from_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', to_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', in_amount=13137.0, out_amount=13129.0368, price_ratio=0.2112, weight=1.5549497271500305, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=1.0, gas_fee=5500),
EdgePairs(from_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', in_amount=3106.9999999999995, out_amount=3014.9253731343283, price_ratio=0.0101, weight=4.595219855134923, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.002849030819668322, total_fee=11.321, gas_fee=5500),
EdgePairs(from_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', to_token='So11111111111111111111111111111111111111112', in_amount=3106.9999999999995, out_amount=3107.0, price_ratio=0.3107, weight=1.1689274625831354, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=31.3927, gas_fee=6000),
EdgePairs(from_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', in_amount=3106.9999999999995, out_amount=3057.7309999999998, price_ratio=0.0194, weight=3.9424822129128545, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=23.3107, gas_fee=6000),
EdgePairs(from_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', in_amount=3106.9999999999995, out_amount=3068.0052, price_ratio=0.2509, weight=1.3827008256097604, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=18.3107, gas_fee=6000),
EdgePairs(from_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', to_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', in_amount=3106.9999999999995, out_amount=3067.4895, price_ratio=0.2335, weight=1.454573201873185, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=16.3107, gas_fee=6000),
EdgePairs(from_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', to_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', in_amount=3106.9999999999995, out_amount=3067.2213, price_ratio=0.2717, weight=1.303056762549835, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=35.7425, gas_fee=6000),
EdgePairs(from_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', to_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', in_amount=3106.9999999999995, out_amount=3068.121, price_ratio=15.897, weight=-2.7661304121787347, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=17.0933, gas_fee=6000),
EdgePairs(from_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', to_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', in_amount=3106.9999999999995, out_amount=3077.118, price_ratio=0.0495, weight=3.0057826094074924, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=18.320999999999998, gas_fee=6000),
EdgePairs(from_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', in_amount=11289.0, out_amount=11194.029850746268, price_ratio=0.0375, weight=3.283414346005772, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=18.342000000000002, gas_fee=5500),
EdgePairs(from_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', to_token='So11111111111111111111111111111111111111112', in_amount=11289.0, out_amount=11289.0, price_ratio=1.1289, weight=-0.12124370728536422, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=120.36940000000001, gas_fee=6000),
EdgePairs(from_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', in_amount=11289.0, out_amount=11285.234, price_ratio=0.0716, weight=2.636660205015537, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=25.994500000000002, gas_fee=6000),
EdgePairs(from_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', in_amount=11289.0, out_amount=11296.226400000001, price_ratio=0.9238, weight=0.07925968098563209, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=1.1289, gas_fee=5500),
EdgePairs(from_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', to_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', in_amount=11289.0, out_amount=11288.6241, price_ratio=0.8593, weight=0.15163717466295976, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=1.1289, gas_fee=5000),
EdgePairs(from_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', to_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', in_amount=11289.0, out_amount=11519.8239, price_ratio=3.7077, weight=-1.3104117382816625, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=7.3453, gas_fee=6000),
EdgePairs(from_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', to_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', in_amount=11289.0, out_amount=11336.356800000001, price_ratio=58.7376, weight=-4.073080066917377, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=33.339800000000004, gas_fee=6000),
EdgePairs(from_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', to_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', in_amount=11289.0, out_amount=11282.766, price_ratio=0.1815, weight=1.7064996252772315, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=1.1289, gas_fee=5500),
EdgePairs(from_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', in_amount=193.0, out_amount=179.1044776119403, price_ratio=0.0006, weight=7.418580902748128, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.064238865225568, total_fee=2.2545, gas_fee=5500),
EdgePairs(from_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', to_token='So11111111111111111111111111111111111111112', in_amount=193.0, out_amount=193.0, price_ratio=0.0193, weight=3.947650183071297, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=0.2702, gas_fee=5000),
EdgePairs(from_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', in_amount=193.0, out_amount=189.138, price_ratio=0.0012, weight=6.725433722188183, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.019408678616747648, total_fee=2.2545, gas_fee=5500),
EdgePairs(from_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', in_amount=193.0, out_amount=191.9796, price_ratio=0.0157, weight=4.154094566627875, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0064810564221927, total_fee=0.40530000000000005, gas_fee=5500),
EdgePairs(from_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', to_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', in_amount=193.0, out_amount=193.1139, price_ratio=0.0147, weight=4.219907785197447, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.00040780981215659417, total_fee=0.2702, gas_fee=5500),
EdgePairs(from_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', to_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', in_amount=193.0, out_amount=196.36239999999998, price_ratio=0.0632, weight=2.761450977829325, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0016987151126576464, total_fee=1.2545000000000002, gas_fee=6000),
EdgePairs(from_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', to_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', in_amount=193.0, out_amount=191.913, price_ratio=0.017, weight=4.074541934925921, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.006307666329629187, total_fee=0.40530000000000005, gas_fee=5500),
EdgePairs(from_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', to_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', in_amount=193.0, out_amount=198.9248, price_ratio=0.0032, weight=5.744604469176456, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=3.2545, gas_fee=6000),
EdgePairs(from_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', to_token='27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4', in_amount=62164.0, out_amount=62119.40298507462, price_ratio=0.2081, weight=1.5697365455825483, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=883.8632, gas_fee=6000),
EdgePairs(from_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', to_token='So11111111111111111111111111111111111111112', in_amount=62164.0, out_amount=62164.0, price_ratio=6.2164, weight=-1.8271909610593198, slippage_bps=50, platform_fee=0.0, price_impact_pct=8.56210063603234e-05, total_fee=6.2164, gas_fee=5000),
EdgePairs(from_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', to_token='3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh', in_amount=62164.0, out_amount=56495.2984, price_ratio=0.0008, weight=7.1308988302963465, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.09090909090909091, total_fee=31.082, gas_fee=5000),
EdgePairs(from_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', to_token='4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', in_amount=62164.0, out_amount=62573.155, price_ratio=0.397, weight=0.9238189982949466, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=1044.8632, gas_fee=6000),
EdgePairs(from_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', to_token='J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn', in_amount=62164.0, out_amount=62272.31280000001, price_ratio=5.0926, weight=-1.6277885056466936, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=86.8072, gas_fee=6000),
EdgePairs(from_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', to_token='mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So', in_amount=62164.0, out_amount=62224.7142, price_ratio=4.7366, weight=-1.5553195787464962, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=13.2164, gas_fee=5500),
EdgePairs(from_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', to_token='KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', in_amount=62164.0, out_amount=63538.149999999994, price_ratio=20.45, weight=-3.017982882488811, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=1045.8632, gas_fee=6000),
EdgePairs(from_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', to_token='jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v', in_amount=62164.0, out_amount=62222.7102, price_ratio=5.5118, weight=-1.7068912485828134, slippage_bps=50, platform_fee=0.0, price_impact_pct=3.0842823700424017e-06, total_fee=86.72380000000001, gas_fee=6000),
EdgePairs(from_token='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', to_token='31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', in_amount=62164.0, out_amount=62619.293900000004, price_ratio=324.4523, weight=-5.782138529961761, slippage_bps=50, platform_fee=0.0, price_impact_pct=0.0, total_fee=1265.8632, gas_fee=6000)

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
            in_amount=edge.in_amount,
            weight=edge.weight,
            out_amount=edge.out_amount,
            from_symbol=edge.from_token,
            to_symbol=edge.to_token,
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
