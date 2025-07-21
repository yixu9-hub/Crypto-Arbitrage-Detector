# Crypto-Arbitrage-Detector
This project builds an automated system to detect crypto arbitrage opportunities on the Solana blockchain. By modeling token swaps as a weighted, directed graph, we apply graph-based techniques (e.g., Bellman-Ford) to identify negative cycles that represent profitable trading paths.

Crypto-Arbitrage-Detector/Feature/algorithm架构
├── utils/
│   ├── data_structures.py  # 来自Nova, 新增opportunity class
│   ├── get_quote_pair.py   # 来自Nova, fetches trading pair quotes from APIs
│   ├── graph_structure.py  # Builds and manages token swap graph
├── src/
│   ├── bellman_ford_algorithm.py  # Implements Bellman-Ford for negative cycle detection
│   ├── triangle_arbitrage_algorithm.py  # Detects triangle arbitrage opportunities
│   ├── two_hop_arbitrage_algorithm.py  # Implements two-hop arbitrage detection
│   ├── arbitrage_detector_integrated.py  # Interface for 3 algoruthms
│
├── test/
│   ├── mock_data.py  # Provides static test data for development
│   ├── arbitrage_test_data.py  # 测试各种套利方法
└── ├── simple_graph_demo.py  # Demonstrates basic graph operations


>>> Update features:

1. Build a graph structure class based on edge pairs
    by NetworkX, support inserting and updating edges
    -> graph_structure.py

2. Initialize token swap graph, synchronized with data collection module
    -> graph_structure.py

3. Prepare a basic iterative framework
    -> arbitrage_detector_integrated.py

4. Implement opportunity detector
    -> bellman_ford_algorithm.py, triangle_arbitrage_algorithm.py, two_hop_arbitrage_algorithm.py

5. Strategy selector for choosing suitable algorithm based on current conditions
    -> arbitrage_detector_integrated.py


>>> 算法工作流：

已经有的交易图，目前离线模式
       ↓
   ArbitrageDetectorIntergrated
       ↓
┌─────────────┬──────────────┬────────────────┐
│ BellmanFord │  Triangle    │   TwoHop       │
│ Arbitrage   │  Arbitrage   │   Arbitrage    │
└─────────────┴──────────────┴────────────────┘
       ↓
   排序后，输出套利机会

>>> Next step:

1. 引入更大的离线图 + 导入在线图，视图功能优化，增加实时price moniter功能
2. 各种算法性能测算，性能优化
3. 更复杂的风险管理配置文件，检查滑点、实时交易费用等价格影响是否在可接受范围内，计算风险调整后的置信度分数
4. ...