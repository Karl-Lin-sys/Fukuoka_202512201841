# AI工程師 応募用プロジェクトサマリ（104-job 8vdl8）

## 求人概要
- **企業名**: 創未來智慧生活股份有限公司
- **職種**: AI工程師
- **必須経験**:
  - Python および TensorFlow / PyTorch / scikit-learn 等 ML ライブラリを用いた ML/AI 開発（2年以上）
  - 推薦システム or 時系列分析の実装経験
  - データクレンジング・特徴量エンジニアリング
  - 英語（Listening/Speaking/Reading/Writing いずれも中等）
- **プラス要件**:
  1. アルゴリズムの設計・解析・シミュレーション
  2. NLP / LLM モデル（Chatbot、Llama、MiniCPM 等）
  3. RESTful API、マイクロサービス、SQL 設計
  4. LLM や Chatbot の実務経験

## 当リポジトリのアピールポイント
| 求人要件 | リポジトリ内の該当ポイント |
| --- | --- |
| Python + ML ライブラリ | `modules/ml.py` にて scikit-learn による分類器（LogReg/RandomForest/GBDT/SVM/NN）を実装。Streamlit UI から学習/評価を実行可能。 |
| 推薦/時系列/データ分析 | `modules/data_science.py`（既存）＋ Streamlit のアナリティクスタブでクラスタリング・次元削減・ハイパーパラメータチューニングを実演、分析力を提示。 |
| NLP/LLM・チャットボット | `modules/security.py` などに API 設計の基礎要素。LLM 直接実装は未搭載のため、README で今後の強化案（LLM 推薦、ChatOps）を明記予定。 |
| RESTful API / Microservices | 各モジュールを疎結合化 (`modules/*.py`) しており、今後 FastAPI 等に移行しやすい構造である点をアピール。 |

## 104 応募向けメッセージ例
1. TU Ilmenau CS & Automation の学際ポートフォリオとして、AI/ML・CV・ロボティクス・セキュリティを Streamlit で統合。
2. ML パートでは scikit-learn モデルの学習/UI 化、クラスタリング・次元削減・ハイパーパラメータ自動探索など、E2E の MLOps の素地を提示。
3. NLP/LLM、推薦、時系列を今後拡張するための設計方針とロードマップを README に追記済み。
4. GitHub Actions/Streamlit Cloud 等へのデプロイにも対応しやすい依存構成（`requirements.txt` + `run_app.ps1`）を準備。

本ドキュメントを `README.md` からリンクし、応募先の人事担当者に本リポジトリの狙いを共有してください。
