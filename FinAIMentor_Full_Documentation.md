# FINMENTOR AI - MULTIAGENT FINANCIAL ADVISORY PLATFORM

**Submitted by:**
Roshan Varghese (2448046)
Varun Dsouza (2448059)

**Under the Guidance of:**
Dr. Apash Roy
Associate Professor, Department of Data Science & Statistics

---

## ACKNOWLEDGEMENTS

We would like to express our deepest gratitude to the Almighty for the wisdom, strength, and perseverance granted to us to complete this project successfully.

We are profoundly indebted to our project guide, **Dr. Apash Roy**, Associate Professor, Department of Data Science and Statistics, **Christ (Deemed to be University)**. His expert mentorship, deep technical insights into multi-agent systems, and constant encouragement were pivotal in the successful development of **FinMentor AI**. We thank him for his patience and for providing the critical feedback that shaped this research.

We extend our sincere thanks to **Dr. Saleema J.S.**, former Head of the Department of Data Science and Statistics, for her invaluable guidance and support during the initial conceptualization of this work.

We also express our gratitude to the **Department of Data Science and Statistics** and **Christ (Deemed to be University)** for providing the necessary infrastructure, resources, and a conducive academic environment that facilitated this study. We are thankful for the opportunity to undertake this project and for the institution's commitment to academic excellence.

Finally, we thank our families and peers for their unwavering moral support and encouragement throughout this journey.

**Roshan Varghese (2448046)**
**Varun Dsouza (2448059)**

---

## ABSTRACT

The democratization of capital markets in India has led to a surge in retail participation, yet a significant "financial literacy gap" remains, leaving many investors vulnerable to misinformation and poor decision-making. This project presents **FinMentor AI**, a novel multi-agent financial advisory platform designed to democratize institutional-grade investment guidance. Unlike static chatbots, FinMentor AI utilizes a **Hybrid Neuro-Symbolic Architecture**, combining the reasoning capabilities of Large Language Models (LLMs) via **DSPy** with the deterministic execution of **LangChain** tools. The system features an **Agentic Retrieval-Augmented Generation (RAG)** engine that intelligently retrieves context from real-time market data (Yahoo Finance) and educational repositories (PGVector) to minimize hallucinations. By integrating personalized risk profiling, portfolio optimization, and an interactive educational module, FinMentor AI provides a holistic, transparent, and accessible solution for the modern retail investor.

---


## LIST OF ABBREVIATIONS

| Abbreviation | Full Form |
| :--- | :--- |
| **ACID** | Atomicity, Consistency, Isolation, Durability |
| **AI** | Artificial Intelligence |
| **API** | Application Programming Interface |
| **AUM** | Assets Under Management |
| **CAGR** | Compound Annual Growth Rate |
| **CPU** | Central Processing Unit |
| **DFD** | Data Flow Diagram |
| **DSPy** | Declarative Self-Improving Language Programs |
| **FAQ** | Frequently Asked Questions |
| **FK** | Foreign Key |
| **GenAI** | Generative Artificial Intelligence |
| **HTTP** | Hypertext Transfer Protocol |
| **JSON** | JavaScript Object Notation |
| **JWT** | JSON Web Token |
| **LLM** | Large Language Model |
| **MACD** | Moving Average Convergence Divergence |
| **ML** | Machine Learning |
| **MPT** | Modern Portfolio Theory |
| **MVP** | Minimum Viable Product |
| **NCFE** | National Centre for Financial Education |
| **NIFTY** | National Stock Exchange Fifty |
| **NLP** | Natural Language Processing |
| **ORM** | Object-Relational Mapping |
| **P/E** | Price-to-Earnings Ratio |
| **PDF** | Portable Document Format |
| **PK** | Primary Key |
| **RAG** | Retrieval-Augmented Generation |
| **RAM** | Random Access Memory |
| **ROI** | Return on Investment |
| **RSI** | Relative Strength Index |
| **SEBI** | Securities and Exchange Board of India |
| **SMA** | Simple Moving Average |
| **SPA** | Single Page Application |
| **SQL** | Structured Query Language |
| **SSD** | Solid State Drive |
| **SSE** | Server-Sent Events |
| **UAT** | User Acceptance Testing |
| **UI** | User Interface |
| **UUID** | Universally Unique Identifier |
| **ViT** | Vision Transformer |

---

## CHAPTER 1: INTRODUCTION

### 1.1 INTRODUCTION
The financial landscape has undergone a paradigm shift with the democratization of capital markets. In India, benchmarks like NIFTY-50 have delivered consistent returns (approx. 10% CAGR), attracting a new wave of retail investors. However, this accessibility brings complexity. The simultaneous rise of Generative AI (GenAI) has created a "GenAI gap" in retail investing, where sophisticated investors leverage AI for information processing while the majority lag behind (Blankespoor et al., 2024). FinMentor AI aims to bridge this gap by democratizing access to institutional-grade financial intelligence.

### 1.2 PROBLEM DESCRIPTION
Despite the growth in market participation, financial literacy remains a critical barrier:
*   **Low Literacy Rates**: According to the National Centre for Financial Education (NCFE) 2024 report, only **27% of Indian adults** meet basic financial literacy standards. This lack of knowledge leads to poor investment decisions and susceptibility to scams.
*   **Millennial Deficit**: Only **19% of millennials** possess adequate financial knowledge, despite being the most active demographic in digital trading. This "confidence-competence gap" is a major risk factor.
*   **Advisory Gap**: Traditional financial advisors are cost-prohibitive (₹5,000–₹10,000 per session) for small investors. Wealth management firms typically require a minimum portfolio size (e.g., ₹50 Lakhs), leaving the mass market underserved.
*   **Information Overload**: Beginners are overwhelmed by the sheer volume of unverified financial news, complex jargon, and contradictory signals from "fin-fluencers".

### 1.3 EXISTING SYSTEM
Currently, retail investors in India rely on a fragmented ecosystem for financial decision-making. The existing landscape can be categorized into three main channels:

1.  **Traditional Brokerage Apps (e.g., Zerodha, Groww, Upstox)**:
    *   **Function**: These platforms excel at trade execution and providing raw market data.
    *   **Limitation**: They act merely as gateways. While they provide charts and P/E ratios, they lack the "advisory" layer. They do not tell a user *what* to buy or *why*, leaving the interpretation of complex metrics to the untrained user.
2.  **Human Financial Advisors & Wealth Managers**:
    *   **Function**: Provide personalized, holistic financial planning.
    *   **Limitation**: They are expensive (charging 1-2% of AUM or high flat fees) and inaccessible to investors with smaller portfolios. There is also a potential conflict of interest if advisors earn commissions on products they recommend.
3.  **Social Media & News Aggregators**:
    *   **Function**: Platforms like Twitter, YouTube, and Moneycontrol provide news and opinions.
    *   **Limitation**: This source is plagued by noise and unverified information. "Fin-fluencers" often promote risky assets ("pump and dump" schemes) without accountability.

**Summary of Limitations:**
*   **Lack of Personalization**: Automated platforms do not account for an investor's specific risk tolerance, financial goals, or time horizon.
*   **Information Asymmetry**: Institutional investors have access to sophisticated tools (Bloomberg Terminal), while retail investors rely on delayed or basic data.
*   **No Educational Scaffolding**: Apps assume financial literacy, alienating beginners who don't understand terms like "MACD" or "Beta".

### 1.4 PROPOSED SYSTEM
FinMentor AI proposes a paradigm shift from "Trade Execution" to "Intelligent Advisory". It is a multi-agent system where specialized AI agents collaborate to provide institutional-grade advice to retail investors.

**Key Features & Advantages:**
*   **Hyper-Personalization**: The system builds a psychological risk profile for each user based on a questionnaire and interaction history, tailoring advice to their specific "Financial DNA".
*   **Democratized Intelligence**: By using Large Language Models (LLMs) to synthesize technical analysis, sentiment, and fundamentals, it offers insights previously available only to high-net-worth individuals.
*   **Integrated Education**: The "Concept Explanation Agent" ensures that every piece of advice is an opportunity for the user to learn. If the system recommends a stock based on "low Beta", it explains what Beta is in that context.
*   **24/7 Availability**: Unlike human advisors, the AI agents are available round-the-clock to answer queries, monitor portfolios, and provide reassurance during market volatility.
*   **Multi-Modal Interaction**: Users can interact via text, voice, or by uploading documents (e.g., Annual Reports), making the system accessible and versatile.

### 1.5 PROJECT SCOPE
The project encompasses the end-to-end development of a financial advisory platform:
*   **Web Application**: A responsive React-based frontend providing a chat interface, dashboards, and portfolio visualizations.
*   **Advisory Engine**: A robust Python FastAPI backend orchestrating 13 specialized agents (Risk, Technical, Sentiment, etc.).
*   **Data Integration**: Real-time integration with Yahoo Finance for market data and a vector database for retrieving educational content.
*   **Target Audience**: Young professionals (20-45) entering capital markets who seek guidance but cannot afford professional advisors.

### 1.6 OBJECTIVES
*   **Primary**: To develop an intelligent, multi-agent financial advisory platform that acts as a personalized financial mentor.
*   **Secondary**:
    *   **Context-Aware RAG**: Implement a Retrieval-Augmented Generation engine using PGVector to ensure factual accuracy and reduce hallucinations.
    *   **Real-Time Analytics**: Integrate live stock indicators to provide up-to-the-minute analysis.
    *   **Financial Literacy**: Bridge the knowledge gap by integrating an educational module that simplifies complex financial concepts.

---

## CHAPTER 2: LITERATURE REVIEW

### 2.1 EXISTING FINANCIAL AI SYSTEMS
*   **Robo-Advisors**: Automated platforms like Zerodha Coin or Wealthfront use Modern Portfolio Theory (MPT) to allocate assets. While efficient, they are static and cannot answer "Why?" or handle complex, nuance-based queries.
*   **Chatbots**: Traditional financial chatbots are often rule-based decision trees limited to basic FAQs (e.g., "How to reset password"). They lack the deep context awareness required for advisory.

### 2.2 MULTI-AGENT SYSTEMS IN FINANCE
**Xiao et al. (2024)** introduced **"TradingAgents"**, a framework that simulates a professional trading firm. Their research demonstrated that a collaborative architecture—comprising specialized roles like *Fundamental Analyst*, *Sentiment Analyst*, and *Risk Manager*—outperforms single-agent systems.
*   **Key Finding**: The "debate" mechanism between a Bullish Researcher and a Bearish Researcher significantly reduces bias and improves decision accuracy by **23%** compared to baseline models.
*   **Relevance**: FinMentor AI adopts this hierarchical multi-agent structure, separating "Reasoning" (DSPy agents) from "Execution" (LangChain tools).

### 2.3 RETRIEVAL-AUGMENTED GENERATION (RAG)
Accuracy is paramount in financial advice. **Choi et al. (2025)** published **"FinDER"**, a benchmark dataset for evaluating RAG in finance. They highlighted that generic RAG systems often fail on specific financial queries due to the complexity of documents like 10-K filings.
*   **Key Finding**: Systems that retrieve "evidence chunks" before generating answers show a marked reduction in hallucinations.
*   **Relevance**: Our system implements an **Agentic RAG** pipeline that classifies intent before retrieval, ensuring that an "Educational" query retrieves from the glossary while a "Market" query retrieves from live data.

### 2.4 GENAI ADOPTION
**Blankespoor, Croom, and Grant (2024)** investigated the adoption of GenAI among retail investors. Their study revealed a rapid shift in behavior:
*   **Adoption Rate**: Nearly **47%** of retail investors are already using GenAI tools to process financial information.
*   **The "GenAI Gap"**: There is a risk that AI tools will primarily benefit sophisticated investors, widening the wealth gap.
*   **Relevance**: FinMentor AI is designed specifically to democratize this technology, offering a user-friendly interface that requires no prompt engineering skills.

### 2.5 LLMS AS FINANCIAL FORECASTERS
**Lopez-Lira and Tang (2024)** explored the predictive capabilities of LLMs in **"Can ChatGPT Forecast Stock Price Movements?"**. They found that LLMs, when analyzing headlines, can predict stock market returns more accurately than traditional sentiment analysis methods.
*   **Key Finding**: The "Emergent Ability" of LLMs allows them to understand the nuance of financial news better than simple keyword-based models.
*   **Relevance**: This validates our use of **Google Gemini** for interpreting complex financial news and sentiment, going beyond basic "positive/negative" classification.

---

## CHAPTER 3: SYSTEM ANALYSIS

### 3.1 FUNCTIONAL SPECIFICATIONS
The system is designed to perform the following core functions, broken down by module:

**1. User Management & Profiling**
*   **Registration**: Secure sign-up using email/password with validation.
*   **Risk Profiling**: A dynamic questionnaire to assess the user's risk tolerance (Conservative, Moderate, Aggressive) and investment horizon.
*   **Authentication**: JWT-based session management to ensure secure access to personal financial data.

**2. Intelligent Advisory (Chat)**
*   **Intent Recognition**: The system analyzes user queries to determine intent (e.g., "Analyze stock" vs. "Explain concept").
*   **Multi-Agent Orchestration**: Routes queries to the appropriate agent (e.g., Technical Agent for charts, Fundamental Agent for ratios).
*   **Streaming Responses**: Delivers answers token-by-token to reduce perceived latency.
*   **Contextual Memory**: Remembers previous interactions (up to 10 turns) to maintain a coherent conversation flow.

**3. Real-Time Market Analysis**
*   **Live Data Fetching**: Retrieves real-time prices, volume, and percentage changes from Yahoo Finance.
*   **Technical Indicators**: Calculates SMA, RSI, MACD, and Bollinger Bands on-the-fly.
*   **Visualizations**: Generates data for interactive charts (Line, Candle) on the frontend.

**4. Educational Module (RAG)**
*   **Concept Explanation**: Detects financial jargon in queries and provides simplified definitions.
*   **Document Q&A**: Allows users to upload PDF documents (e.g., Annual Reports) and ask questions based on their content.

### 3.2 BLOCK DIAGRAM

![FinMentor AI System Architecture](system_architecture.png)

The system is organized into three reliable layers, as illustrated in the block diagram above:

**1. Frontend Layer**
*   **React App**: The core user interface accessible via web browsers.
*   **Auth UI**: Handles user registration and secure login.
*   **Chat Interface**: The primary interaction point for querying the AI.
*   **Dashboard**: Visualizes market trends and portfolio performance.

**2. Backend Layer**
*   **FastAPI Server**: The high-performance API gateway handling requests.
*   **Hybrid Orchestrator**: The central logic unit managing the workflow.
    *   **DSPy Agents (Brain)**: Performs high-level reasoning and planning.
    *   **LangChain Executor (Tools)**: Executes specific tasks like fetching data or calculating metrics.

**3. Data Layer**
*   **PostgreSQL DB**: Stores structured user and portfolio data.
*   **PGVector**: Acts as the Knowledge Base for storing document embeddings.
*   **External APIs**: Fetches real-time data from sources like Yahoo Finance.

### 3.3 SYSTEM REQUIREMENTS

#### 3.3.1 Hardware Requirements
*   **Server Side**:
    *   **Processor**: Minimum 4-Core CPU (Recommended: 8-Core for parallel agent execution).
    *   **RAM**: Minimum 16GB (Required for efficient in-memory vector processing and handling concurrent LLM requests).
    *   **Storage**: 50GB SSD (For database and log storage).
*   **Client Side**:
    *   **Device**: Any modern Laptop, Desktop, or Smartphone.
    *   **Browser**: Google Chrome, Mozilla Firefox, Safari, or Microsoft Edge (Latest versions).
    *   **Internet**: Stable broadband connection (Minimum 5 Mbps) for streaming responses.

#### 3.3.2 Software Requirements
*   **Operating System**: Cross-platform compatibility (Windows, Linux, MacOS) for development and deployment.
*   **Backend Framework**: Python 3.10+ with FastAPI (chosen for its async capabilities and performance).
*   **Frontend Framework**: Node.js 18+ with React.js and Vite (for fast build times and reactive UI).
*   **Database**: PostgreSQL 15 with `pgvector` extension (for hybrid relational and vector data storage).
*   **AI Model**: Google Gemini 1.5 Flash (via API) for reasoning and generation.
*   **Libraries**: LangChain, DSPy, SQLAlchemy, Pydantic, yfinance.

### 3.4 FEASIBILITY STUDY
A comprehensive feasibility study was conducted to determine the viability of the project.

#### 3.4.1 Technical Feasibility
*   **Technology Maturity**: The project relies on mature, well-supported technologies. Python and React are industry standards.
*   **AI Capabilities**: Google's Gemini 1.5 Flash API provides a massive context window (1M tokens) and low latency, making it technically feasible to process large financial documents and complex conversation histories without significant lag.
*   **Data Access**: Real-time market data is reliably accessible via the `yfinance` library, and vector storage is efficiently handled by `pgvector`, eliminating the need for complex custom infrastructure.
*   **Conclusion**: The project is technically feasible with high confidence.

#### 3.4.2 Economic Feasibility
*   **Development Costs**: The primary cost driver is the LLM API usage. However, Gemini 1.5 Flash offers a generous free tier for development and a very low-cost paid tier ($0.35/1M tokens), making it highly affordable compared to competitors like GPT-4.
*   **Infrastructure Costs**: Hosting can be managed on platforms like Render or Railway, which offer free tiers for prototypes. The use of open-source libraries avoids expensive licensing fees.
*   **ROI Potential**: For a commercial deployment, a "Freemium" model (basic advice free, advanced portfolio optimization paid) presents a clear path to profitability with low overheads.
*   **Conclusion**: The project is economically viable and cost-effective.

#### 3.4.3 Operational Feasibility
*   **User Adoption**: The chat-based interface mimics popular messaging apps (WhatsApp) and AI tools (ChatGPT), ensuring a near-zero learning curve for users.
*   **Maintenance**: The modular multi-agent architecture allows for easy maintenance. If one agent (e.g., News Agent) fails, the others (e.g., Technical Agent) continue to function, ensuring high system availability.
*   **Scalability**: The stateless nature of the backend allows for easy horizontal scaling to handle increased user loads.

---

## CHAPTER 4: SYSTEM DESIGN

### 4.1 SYSTEM ARCHITECTURE
FinMentor AI utilizes a novel **Hybrid Neuro-Symbolic Architecture** that combines the reasoning capabilities of Large Language Models (LLMs) with the structured execution of traditional code.

#### 4.1.1 The Hybrid Core (DSPy + LangChain)

![Conversational AI Core Architecture](hybrid_core_diagram.png)

Unlike standard chatbots that rely solely on prompt engineering, FinMentor AI separates "Reasoning" from "Execution":

1.  **The Reasoning Layer (DSPy)**:
    *   **Role**: Acts as the "Brain" of the system.
    *   **Function**: Uses **DSPy (Declarative Self-Improving Language Programs)** to define structured "Signatures" for financial tasks. For example, the `FinancialAnalysis` signature explicitly requires the model to output `reasoning`, `analysis`, and `risk_level` separately.
    *   **Advantage**: This ensures that the AI follows a strict logical process (Chain-of-Thought) before generating an answer, significantly reducing hallucinations.

2.  **The Orchestration Layer (LangChain)**:
    *   **Role**: Acts as the "Body" of the system.
    *   **Function**: Manages the execution flow, conversation memory, and tool usage. It receives the user's query, retrieves necessary data (using tools), and passes the context to the DSPy layer for processing.
    *   **Tools**: Integrates with external APIs (Yahoo Finance) and internal calculators (Compound Interest, Portfolio Metrics).

3.  **The Retrieval Layer (Agentic RAG)**:
    *   **Role**: The "Long-term Memory".
    *   **Function**: Uses **PGVector** to store embeddings of financial documents (e.g., 10-K filings, educational articles). Before answering, the system retrieves relevant "evidence chunks" to ground its response in fact.

#### 4.1.2 Backend Micro-Services Architecture
The backend is built on **FastAPI**, employing a modular service-oriented design to ensure scalability and maintainability:
*   **Routers Layer (`backend/routers/`)**: Handles HTTP requests and routing. Specialized routers exist for `auth` (User/Login), `chat` (Inference), `market` (Live Data), and `rag` (Knowledge retrieval).
*   **Service Layer (`backend/services/`)**: Contains the core business logic, separated from the HTTP handling. Key services include:
    *   `AuthService`: Manages JWT token generation and password hashing.
    *   `AgenticRAGService`: Manages the embedding generation and vector search logic.
    *   `MarketService`: Interacts with the Yahoo Finance API to fetch data.
*   **Agent Layer (`backend/agents/`)**: Hosts the AI logic. The `SmartMultiAgentOrchestrator` intelligently routes tasks to specific DSPy modules based on complexity.

#### 4.1.3 Frontend Architecture
The frontend is a **Single Page Application (SPA)** built with **React 18** and **Vite**, designed for high reactivity:
*   **Component-Based Design**: The UI is composed of reusable components (e.g., `StockChart`, `ChatBubble`) found in `frontend/src/components/`, ensuring consistency.
*   **State Management**: Uses React's **Context API** (`AuthContext`) to manage global user state across the application without "prop drilling".
*   **Real-Time Capabilities**: Utilizes **Server-Sent Events (SSE)** for streaming the AI's response token-by-token directly to the chat interface, providing immediate feedback to the user.

#### 4.1.4 Data Persistence Layer
The data layer uses a unified **PostgreSQL** instance to handle two distinct types of data:
1.  **Relational Data**: Traditional tables for `Users`, `Portfolios`, and `Transactions` ensure ACID compliance for financial records.
2.  **Vector Data**: The `pgvector` extension allows storing high-dimensional embeddings (384 dimensions) of text alongside relational data. This eliminates the need for a separate vector database (like Pinecone), simplifying infrastructure and allowing complex joins (e.g., "Find documents similar to this query but only for 'Beginner' level users").

### 4.2 DATA FLOW DIAGRAM (DFD)

![Financial Analysis Engine Flow](data_flow_diagram.png)

The data flow for a typical financial analysis request follows the 6-step process utilized by our "Financial Analysis Engine":

1.  **Agent Request (Input)**: The user's query is received and identified as a financial task.
2.  **Tool Selector (LangChain)**: The system logic selects the appropriate tool (e.g., "Stock Data Fetcher" or "Risk Calculator") required to answer the query.
3.  **Financial Tools**: The selected tool operates within the engine to initiate the data request.
4.  **External APIs**: The system connects to outside sources like **Yahoo Finance** (for market data) or **DuckDuckGo** (for news) to fetch raw information.
5.  **Data Processor (Normalization)**: Raw data is cleaned, normalized, and feature-engineered to ensure consistency.
6.  **Result Formatter (Output)**: The processed insights are summarized, visualizations are prepared, and the final structured response (JSON/Text) is returned to the user.

### 4.3 DATABASE DESIGN
The system uses **PostgreSQL** as a unified database for both relational data and vector embeddings. The schema is designed for scalability and security.

#### 4.3.1 User Management Tables
*   **`users`**: Stores core account information.
    *   `id` (UUID): Unique identifier.
    *   `email`, `password_hash`: Security credentials.
    *   `risk_tolerance`: Stores the user's psychological risk profile (Conservative/Moderate/Aggressive).
    *   `financial_goals`: JSON field storing user objectives (e.g., "Retirement", "Home Buying").

#### 4.3.2 Conversation & Memory Tables
*   **`conversations`**: Represents a chat session.
    *   `topic`: Auto-generated title based on content.
    *   `context`: JSON field storing session-specific memory.
*   **`messages`**: Individual chat exchanges.
    *   `role`: 'user' or 'assistant'.
    *   `content`: The text of the message.
    *   `embedding`: **Vector(384)** column storing the semantic meaning of the message for context retrieval.

#### 4.3.3 Portfolio Management Tables
*   **`portfolios`**: Container for user investments.
    *   `total_value`: Current aggregate value of assets.
    *   `cash_balance`: Available liquid cash.
*   **`holdings`**: Individual stock records.
    *   `symbol`: Stock ticker (e.g., "TATASTEEL").
    *   `quantity`: Number of shares held.
    *   `average_cost`: Buy price for profit/loss calculation.
*   **`transactions`**: Ledger of all buy/sell actions.
    *   `type`: 'BUY' or 'SELL'.
    *   `executed_at`: Timestamp of the trade.

#### 4.3.4 Educational & RAG Tables
*   **`educational_content`**: The Knowledge Base.
    *   `title`, `content`: The educational material.
    *   `embedding`: **Vector(384)** used for RAG retrieval.
    *   `level`: Difficulty level (Beginner/Intermediate/Advanced).
*   **`learning_progress`**: Gamification tracking.
    *   `xp_points`: Experience points earned by learning.
    *   `current_level`: User's proficiency tier.

### 4.4 USER INTERFACE DESIGN
The frontend is built with **React.js** and **Tailwind CSS**, focusing on a "Dark Mode" aesthetic common in financial terminals.
*   **Dashboard**: Provides a high-level view of Portfolio Value and Market Indices.
*   **Chat Interface**: The central hub for interaction, featuring streaming text and markdown support for tables/charts.
*   **Portfolio View**: A detailed table of holdings with live P&L updates.

---

## CHAPTER 5: IMPLEMENTATION

### 5.1 TECHNOLOGY STACK
The implementation of FinMentor AI leverages a modern, scalable technology stack designed for high performance and real-time capabilities.

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Frontend** | React.js | 18.2.0 | User Interface and State Management |
| | Tailwind CSS | 3.3.0 | Utility-first styling for responsive design |
| | Vite | 4.4.0 | Next-generation frontend build tool |
| **Backend** | Python | 3.10+ | Core programming language |
| | FastAPI | 0.100.0 | High-performance async web framework |
| | SQLAlchemy | 2.0.0 | ORM for database interactions |
| **AI & ML** | DSPy | 2.0.0 | Declarative framework for LLM reasoning |
| | LangChain | 0.0.267 | Orchestration of agents and tools |
| | Google Gemini | 1.5 Flash | Large Language Model for generation |
| **Database** | PostgreSQL | 15.0 | Relational database for user data |
| | pgvector | 0.4.0 | Vector similarity search extension |
| **Data** | yfinance | 0.2.28 | Real-time market data fetching |

### 5.2 KEY ALGORITHMS AND LOGIC

#### 5.2.1 Agentic RAG Pipeline (`agentic_rag.py`)
The Retrieval-Augmented Generation (RAG) system is not a simple semantic search. It implements an "Agentic" approach that first understands the *intent* of the user before deciding *where* to look.

1.  **Intent Classification**: The system analyzes the query to classify it into one of several intents:
    *   `HISTORICAL_REFERENCE`: "What did we discuss last time?"
    *   `EDUCATIONAL_QUERY`: "What is a P/E ratio?"
    *   `MARKET_ANALYSIS`: "How is AAPL performing?"
    *   `PORTFOLIO_ADVICE`: "Should I buy more?"
    *   `RISK_ASSESSMENT`: "Is this too risky?"

2.  **Retrieval Planning**: Based on the intent, a retrieval strategy is formed.
    *   *Example*: A `MARKET_ANALYSIS` intent triggers a "Multi-Source" strategy, fetching data from both the "Market" (Yahoo Finance) and "Documents" (Annual Reports).

3.  **Execution**: The system executes the plan, using `pgvector` to find semantically similar chunks in the database.

4.  **Self-Reflection**: For critical queries (like Portfolio Advice), the system performs a self-check to ensure consistency with previous advice and compliance with risk disclosures.

#### 5.2.2 Financial Metrics Calculation (`financial_tools.py`)
FinMentor AI calculates professional-grade portfolio metrics on-the-fly.
*   **Sharpe Ratio**: Measures risk-adjusted return. Calculated as $(R_p - R_f) / \sigma_p$.
*   **Volatility**: Annualized standard deviation of daily returns.
*   **Maximum Drawdown**: The largest peak-to-trough decline in the portfolio's value.

#### 5.2.3 Dynamic Multi-Agent Orchestration
Unlike simple chatbots that use a single prompt, FinMentor AI employs a "Team of Experts" approach. The **Smart Orchestrator** assesses the complexity of every query:
*   **Simple Queries** (e.g., "What is a stock?") are routed to a single Education Agent.
*   **complex Queries** (e.g., "Analyze my tech portfolio risks") trigger a dynamic assembly of agents. The Orchestrator automatically recruits a Market Analyst, a Risk Assessor, and a Portfolio Optimizer, executing them in a dependency-aware graph (e.g., Market Data is fetched *before* Risk Assessment).

#### 5.2.4 Neuro-Symbolic Reasoning (DSPy)
To prevent "hallucinations" common in LLMs, the system uses **Neuro-Symbolic AI** via the DSPy framework. Instead of unstructured text, agents are forced to "think" in structured schemas (Signatures).
*   **Inputs**: Raw context (e.g., 5 years of price data).
*   **Logic**: The LLM must fill specific fields like `support_level`, `resistance_level`, and `trend_direction`.
*   **Output**: A guaranteed, structured JSON object that can be reliably used by other parts of the code.

### 5.3 CODE SNIPPETS

#### 5.3.1 Intent Classification Logic
This snippet from `backend/services/agentic_rag.py` demonstrates how the system classifies user intent based on keyword patterns.

```python
def classify_intent(self, query: str) -> Tuple[QueryIntent, float]:
    """
    Classify the intent of a query - what does the user REALLY want?
    Returns: (intent_type, confidence_score)
    """
    query_lower = query.lower()
    intent_scores = {}

    # Check how well each intent's patterns match the query
    for intent, patterns in self.intent_patterns.items():
        # Count matching patterns (e.g., "should i buy" in query)
        score = sum(1 for pattern in patterns if pattern in query_lower)
        if score > 0:
            intent_scores[intent] = score / len(patterns)

    if intent_scores:
        best_intent = max(intent_scores, key=intent_scores.get)
        return best_intent, intent_scores[best_intent]
    else:
        return QueryIntent.GENERAL_CHAT, 0.5
```

#### 5.3.2 Portfolio Metrics Calculation
This function in `backend/agents/financial_tools.py` calculates the Sharpe Ratio and Volatility, essential for the Risk Agent.

```python
@staticmethod
async def calculate_portfolio_metrics(
    holdings: Dict[str, float],        
    prices: Dict[str, float],          
    historical_data: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """Calculate professional portfolio metrics"""
    try:
        # Calculate total portfolio value
        portfolio_value = sum(holdings[symbol] * prices.get(symbol, 0)
                             for symbol in holdings)

        if historical_data is not None:
            # Calculate daily returns
            returns = historical_data.pct_change().dropna()
            
            # Weighted portfolio returns
            weights = {symbol: (qty * prices.get(symbol, 0)) / portfolio_value
                      for symbol, qty in holdings.items()}
            
            portfolio_returns = sum(weights.get(symbol, 0) * returns[symbol]
                                  for symbol in returns.columns if symbol in weights)

            # Metrics
            annual_return = portfolio_returns.mean() * 252
            volatility = portfolio_returns.std() * np.sqrt(252)
            sharpe_ratio = annual_return / volatility if volatility > 0 else 0
            
            return {
                "portfolio_value": portfolio_value,
                "sharpe_ratio": round(sharpe_ratio, 2),
                "volatility": f"{volatility:.2%}"
            }
    except Exception as e:
        return {"error": str(e)}
```

#### 5.3.3 Streaming Chat Response
The `backend/routers/chat.py` endpoint handles the real-time streaming of the AI's response to the frontend.

```python
@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Streaming Generator
    async def response_generator():
        async for chunk_str in hybrid_system.stream_query(
            query=request.message,
            user_profile=user_profile
        ):
            yield chunk_str
            
    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream"
    )
```

#### 5.3.4 Neuro-Symbolic Logic (DSPy Signature)
This snippet from `backend/agents/specialized_signatures.py` shows how we enforce structured reasoning output from the LLM, reducing hallucinations.

```python
class MarketTechnicalAnalysis(dspy.Signature):
    """Technical analysis of stocks and market trends"""
    
    # Inputs (Context)
    symbol = dspy.InputField(desc="stock symbol or market index")
    timeframe = dspy.InputField(desc="analysis timeframe (1d, 1w, 1m)")
    price_data = dspy.InputField(desc="historical price data")

    # Outputs (Structured Thinking)
    trend = dspy.OutputField(desc="bullish/bearish/neutral")
    support_levels = dspy.OutputField(desc="key support price levels")
    resistance_levels = dspy.OutputField(desc="key resistance price levels")
    recommendation = dspy.OutputField(desc="buy/hold/sell recommendation")
    confidence = dspy.OutputField(desc="confidence score 0-100")
```

#### 5.3.5 Multi-Agent Orchestration Logic
This logic from `backend/agents/smart_orchestrator.py` dynamically selects the "Dream Team" of agents based on query complexity.

```python
def select_agents(self, query: str, intent: QueryIntent, complexity: QueryComplexity) -> List[AgentType]:
    """Select the right team of agents for this query"""
    
    # Start with primary agents
    selected_agents = list(intent_to_agents.get(intent, [AgentType.EDUCATION]))
    
    # Scale up team based on complexity
    if complexity == QueryComplexity.COMPLEX:
        if AgentType.PORTFOLIO_OPTIMIZER in selected_agents:
            # Add Behavioral Analysis to check for bias
            selected_agents.append(AgentType.BEHAVIORAL_ANALYSIS)
    
    elif complexity == QueryComplexity.CRITICAL:
        # Full team for critical decisions
        selected_agents.extend([
            AgentType.RISK_ASSESSMENT,
            AgentType.BEHAVIORAL_ANALYSIS,
            AgentType.TAX_ADVISOR
        ])
    
    # Ensure dependencies are met (e.g., Risk Agent needs Market Data)
    return self._expand_with_dependencies(selected_agents)
```

### 5.4 FRONTEND IMPLEMENTATION
The frontend is implemented as a Single Page Application (SPA) using React. It communicates with the backend via RESTful APIs.
*   **State Management**: Uses React Hooks (`useState`, `useEffect`) to manage chat history and portfolio data.
*   **Real-time Updates**: The chat interface uses `fetch` with `ReadableStream` to display the AI's response character-by-character, mimicking a human typing speed.
*   **Charting**: Uses `recharts` or similar libraries to render interactive financial charts based on the data received from the backend.

### 5.5 KEY INTERFACE COMPONENTS
The FinMentor AI frontend is composed of four primary interface modules:

#### 5.5.1 The Dashboard
Serves as the central hub for market intelligence, providing a real-time **Market Overview**. It displays live updates of major indices (such as NIFTY 50) and tracks current market trends to keep the user informed.
![User Dashboard - Component Visualization](dashboard_view.png)

#### 5.5.2 Intelligent Chat Interface
The core interaction layer where the "Multi-Agent" system presents its reasoning.
![Chat Interface - Component Visualization](chat_interface_main.png)

#### 5.5.3 User Profile Management
A personalized view for managing risk tolerance, financial goals, and education settings.
![User Profile - Component Visualization](user_profile_page.png)

#### 5.5.4 Interactive RAG Viewer
Displays the internal reasoning process and retrieved context for transparency.

*Figure 5.5.4a: The Agent analyzing the query and selecting tools.*
![RAG Reasoning - Step 1](rag_reasoning_step1.png)

*Figure 5.5.4b: The final output with "Thought Process" expanded.*
![RAG Result - Step 2](rag_result_step2.png)

---

## CHAPTER 6: TESTING

### 6.1 TESTING STRATEGY
The testing phase ensured the reliability, accuracy, and performance of the FinMentor AI system. A multi-layered testing approach was adopted:

1.  **Unit Testing**: Focused on individual components, such as specific DSPy signatures and utility functions (e.g., `calculate_portfolio_metrics`).
2.  **Integration Testing**: Verified the interaction between modules, specifically the RAG pipeline (Retrieval -> Generation) and the connection between LangChain tools and external APIs (Yahoo Finance).
3.  **System Testing**: Validated the end-to-end user workflows, from registration to receiving complex portfolio advice.
4.  **User Acceptance Testing (UAT)**: Simulating real-world scenarios to ensure the advice is helpful and the interface is intuitive.

### 6.2 TEST CASES AND RESULTS

#### 6.2.1 Authentication Module
| Test Case ID | Test Description | Input Data | Expected Outcome | Actual Result | Status |
|--------------|------------------|------------|------------------|---------------|--------|
| TC-AUTH-01 | User Registration | Valid Email, Password | User created, Token generated | User created, Token generated | **Pass** |
| TC-AUTH-02 | Duplicate Email | Existing Email | Error: "Email already exists" | Error: "Email already exists" | **Pass** |
| TC-AUTH-03 | Login Validation | Invalid Password | Error: "Invalid credentials" | Error: "Invalid credentials" | **Pass** |

#### 6.2.2 Financial Advisory Module
| Test Case ID | Test Description | Input Data | Expected Outcome | Actual Result | Status |
|--------------|------------------|------------|------------------|---------------|--------|
| TC-ADV-01 | Stock Price Check | "Price of AAPL" | Current price displayed | Price: $150.25 (Live) | **Pass** |
| TC-ADV-02 | Concept Explanation | "What is Beta?" | Simplified definition provided | Explanation of Beta volatility | **Pass** |
| TC-ADV-03 | Portfolio Analysis | "Analyze my portfolio" | Risk & Return metrics shown | Sharpe Ratio & Volatility shown | **Pass** |

#### 6.2.3 RAG Pipeline
| Test Case ID | Test Description | Input Data | Expected Outcome | Actual Result | Status |
|--------------|------------------|------------|------------------|---------------|--------|
| TC-RAG-01 | Context Retrieval | "What did we discuss?" | Summary of last chat | "We discussed Tata Motors..." | **Pass** |
| TC-RAG-02 | Document Q&A | Upload PDF + Query | Answer based on PDF content | Answer cites PDF page 5 | **Pass** |

### 6.3 PERFORMANCE TESTING
*   **Response Latency**: Average response time for simple queries is <2 seconds. Complex RAG queries take ~4-5 seconds.
*   **Concurrency**: The system successfully handled 50 concurrent users without degradation, thanks to FastAPI's async architecture.

---

## CHAPTER 7: CONCLUSION

### 7.1 SUMMARY
FinMentor AI successfully demonstrates a MVP for a multi-agent financial advisor. By combining the reasoning power of LLMs with the accuracy of RAG and real-time data, it offers a superior alternative to static chatbots. The system effectively educates users while providing personalized, data-driven investment advice, bridging the gap between institutional-grade intelligence and retail investors.

### 7.2 SYSTEM LIMITATIONS
While the system achieves its primary objectives, it operates within certain constraints:
*   **Dependency on External APIs**: The system relies on Yahoo Finance for market data and Google Gemini for reasoning. Any downtime or rate-limiting from these providers directly impacts system availability.
*   **Data Latency**: The free tier of the Yahoo Finance API provides data with a slight delay (typically 15 minutes), which may not be suitable for high-frequency trading.
*   **LLM Hallucinations**: Although the Agentic RAG pipeline significantly reduces errors, Large Language Models can still occasionally generate plausible but incorrect information ("hallucinations"), necessitating user verification.
*   **Regulatory Compliance**: FinMentor AI is an educational tool and not a SEBI-registered investment advisor. It does not carry legal liability for financial losses incurred by users.
*   **Internet Dependency**: As a cloud-native application relying on real-time streaming, a stable internet connection is mandatory for operation.

### 7.3 FUTURE SCOPE
The project lays a strong foundation for future enhancements:
*   **Multi-Modal Agents**: Integration of Vision Transformers (ViT) to analyze stock chart images and identify patterns like "Head and Shoulders".
*   **Tax-Loss Harvesting**: Automated suggestions for selling losing assets to offset capital gains tax.
*   **Mobile Application**: Developing a native React Native app for better accessibility on smartphones.
*   **Blockchain Integration**: Using a private blockchain to create an immutable audit trail of all financial advice given by the AI.
*   **Advanced Optimization**: Implementing Black-Litterman models to incorporate user views into portfolio construction.

---

## REFERENCES

[1] Y. Xiao et al., "TradingAgents: Multi-agents LLM financial trading framework," *arXiv preprint arXiv:2412.20138*, 2024. [Online]. Available: https://arxiv.org/abs/2412.20138

[2] E. Choi et al., "FinDER: Financial dataset for question answering and evaluating RAG," *arXiv preprint arXiv:2504.15800*, 2025. [Online]. Available: https://arxiv.org/abs/2504.15800

[3] A. Lopez-Lira and Y. Tang, "Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models," *SSRN Electronic Journal*, 2024. [Online]. Available: https://ssrn.com/abstract=4412788

[4] E. Blankespoor, S. Croom, and J. Grant, "Generative AI and Investor Processing of Financial Information," *SSRN Electronic Journal*, 2024. [Online]. Available: https://ssrn.com/abstract=4644342

[5] National Centre for Financial Education (NCFE), *Financial Literacy and Inclusion in India: Final Report*, NCFE, 2024. [Online]. Available: https://www.ncfe.org.in

[6] O. Khattab et al., "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines," in *arXiv preprint arXiv:2310.03714*, 2023. [Online]. Available: https://arxiv.org/abs/2310.03714

[7] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in *Advances in Neural Information Processing Systems (NeurIPS)*, 2020. [Online]. Available: https://arxiv.org/abs/2005.11401

[8] H. Markowitz, "Portfolio Selection," *The Journal of Finance*, vol. 7, no. 1, pp. 77-91, 1952. [Online]. Available: https://www.jstor.org/stable/2975974

---

## APPENDIX A: DEPLOYMENT GUIDE

### A.1 Local Network (LAN) Access
To demonstrate the project within a local network (e.g., inside a lab or classroom):

1.  **Find Local IP**: Run `ipconfig` (Windows) or `ifconfig` (Mac/Linux) to find the IPv4 Address (e.g., `192.168.1.5`).
2.  **Run Backend**: Execute `uvicorn main:app --host 0.0.0.0 --port 8000 --reload` to listen on all interfaces.
3.  **Run Frontend**: Execute `npm run dev -- --host` to expose the React app.
4.  **Access**: Other devices can access the app via `http://<YOUR_IP>:5173`.

### A.2 Internet Access (ngrok)
To demonstrate the project remotely:

1.  **Install ngrok**: Download from [ngrok.com](https://ngrok.com/).
2.  **Start Tunnel**: Run `ngrok http 8000` in a terminal.
3.  **Share URL**: Use the generated public URL (e.g., `https://xyz.ngrok-free.app`) to access the backend from anywhere.
