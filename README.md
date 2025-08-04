graph_utils: 
- add new method to use symbol for display instead of long address
- add seperate interface for console and streamlit frontend

graph_structure：
- 修改build_graph_from_edge_lists()保存symbol信息到边属性中
= 现在图的边包含from_symbol和to_symbol属性

algorithms + risk_evaluator:
- add config as default, eliminate magic numbers
- delete unused function
- enhance readability

检查单位问题：
- 修改了price_impact_pct在算法中的应用
- gas fee: lamports→SOL

bellman-ford算法存在的问题