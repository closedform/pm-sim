import random

# Core hand-written questions
BASE_QUESTIONS = [
    {
        "prompt": "What is the annualization factor for a Sharpe measured on daily returns (252 trading days)?",
        "options": ["sqrt(252)", "252", "12", "sqrt(12)"],
        "answer": 0,
    },
    {
        "prompt": "Which firm pioneered early statistical arbitrage in equities?",
        "options": ["Renaissance Technologies", "Citadel", "Bridgewater", "Millennium"],
        "answer": 0,
    },
    {
        "prompt": "What does CVaR (Conditional VaR) measure?",
        "options": [
            "Expected loss in the tail beyond VaR",
            "Average daily loss",
            "Sharpe ratio threshold",
            "Expected return plus variance",
        ],
        "answer": 0,
    },
    {
        "prompt": "Kelly sizing is used to:",
        "options": [
            "Optimize bet size given edge and odds",
            "Lock leverage at max margin",
            "Equal weight all assets",
            "Minimize volatility at any return",
        ],
        "answer": 0,
    },
    {
        "prompt": "Which signal is most associated with carry trades?",
        "options": ["Yield or funding differential", "Price momentum", "Earnings growth", "Seasonality"],
        "answer": 0,
    },
    {
        "prompt": "What is slippage?",
        "options": [
            "Difference between expected and executed price",
            "Exchange fee rebate",
            "Funding rate",
            "Volatility skew",
        ],
        "answer": 0,
    },
    {
        "prompt": "If daily volatility is 1%, what is the annualized volatility using 252 days?",
        "options": ["~15.9%", "~1%", "~6%", "~31.6%"],
        "answer": 0,
    },
    {
        "prompt": "What is the purpose of a risk model?",
        "options": [
            "Estimate factor exposures and portfolio risk",
            "Guarantee profit",
            "Set exchange fees",
            "Compute tax lots only",
        ],
        "answer": 0,
    },
    {
        "prompt": "Which order type reduces market impact but risks non-fill?",
        "options": ["Limit order", "Market order", "IOC market", "Midpoint sweep"],
        "answer": 0,
    },
    {
        "prompt": "What is the main goal of market making?",
        "options": [
            "Capture bid-ask spread while managing inventory",
            "Predict long-term earnings",
            "Exploit credit cycles",
            "Run concentrated directional bets",
        ],
        "answer": 0,
    },
    {
        "prompt": "Which style bets on mean reversion?",
        "options": ["Pairs trading", "Trend following", "Carry", "Growth investing"],
        "answer": 0,
    },
    {
        "prompt": "What is kurtosis?",
        "options": ["Measure of tail heaviness", "Measure of skew", "Average return", "Drawdown depth"],
        "answer": 0,
    },
    {
        "prompt": "What is the main idea behind ensemble methods?",
        "options": [
            "Combine diverse models to improve robustness",
            "Use a single best model only",
            "Ignore variance",
            "Leverage to the max",
        ],
        "answer": 0,
    },
    {
        "prompt": "What is crowding risk?",
        "options": [
            "Many players in the same trade causing fragility",
            "Broker insolvency",
            "FX basis risk",
            "Dividend withholding risk",
        ],
        "answer": 0,
    },
    {
        "prompt": "Sharpe ratio uses which measure of risk?",
        "options": ["Standard deviation", "CVaR", "Skew", "Turnover"],
        "answer": 0,
    },
    {
        "prompt": "Which data type is most likely to give NLP alpha?",
        "options": ["Corporate filings", "Open-high-low-close", "Dividends", "Splits"],
        "answer": 0,
    },
    {
        "prompt": "What is execution algos’ primary objective?",
        "options": ["Reduce market impact and slippage", "Maximize spread capture only", "Increase fees", "Hold positions"],
        "answer": 0,
    },
    {
        "prompt": "What does a higher information ratio imply?",
        "options": ["Better risk-adjusted active return", "Higher turnover", "Lower drawdown only", "Higher leverage"],
        "answer": 0,
    },
    {
        "prompt": "Why use a stop-loss?",
        "options": ["Limit downside on adverse moves", "Increase fill probability", "Guarantee profit", "Reduce commissions"],
        "answer": 0,
    },
    {
        "prompt": "What is alpha decay?",
        "options": [
            "Signal performance fading over time",
            "Commission reduction",
            "Leverage increase",
            "Turnover jump",
        ],
        "answer": 0,
    },
]


DAILY_DAYS = [252, 250, 260, 240, 220, 300, 365, 200]
WEEKLY_PERIODS = [52, 50, 48, 40, 26, 13]
MONTHLY_PERIODS = [12, 11, 10, 9, 6, 4]

STYLES = [
    ("Trend Following", ["Trend Following", "Value", "Carry", "Event-driven"]),
    ("Mean Reversion", ["Mean Reversion", "Momentum", "Carry", "Merger arb"]),
    ("Stat Arb", ["Stat Arb", "Global Macro", "Commodities CTA", "Vol targeting"]),
    ("Pairs Trading", ["Pairs trading", "Value tilt", "Carry FX", "Growth investing"]),
    ("Carry", ["Carry", "Event-driven", "Deep value", "Momentum short-term"]),
    ("Value", ["Value", "Carry", "Trend following", "Risk parity"]),
    ("Momentum", ["Momentum", "Value", "Carry", "Arbitrage"]),
    ("Seasonality", ["Seasonality", "Risk premium", "Beta harvesting", "Carry"]),
    ("Quality", ["Quality", "Size", "Low vol", "Momentum"]),
    ("Low Volatility", ["Low volatility", "Size", "Growth", "Carry"]),
    ("Size Effect", ["Size", "Value", "Carry", "Sentiment"]),
    ("Event Driven", ["Event-driven", "Carry", "Seasonality", "Momentum"]),
    ("Merger Arbitrage", ["Merger arbitrage", "Carry", "FX spot", "Credit default"]),
    ("Convertible Arb", ["Convertible arbitrage", "Trend following", "Carry", "Pairs"]),
    ("Short Volatility", ["Short volatility", "Carry", "Value", "Growth"]),
    ("Long Volatility", ["Long volatility", "Carry", "Momentum", "Dividend growth"]),
    ("Risk Parity", ["Risk parity", "Equal weight", "Buy-write", "Carry"]),
    ("Global Macro", ["Global macro", "Carry", "Pairs", "Value"]),
    ("CTAs", ["Managed futures", "Carry", "Value", "Event-driven"]),
    ("Market Making", ["Market making", "Trend following", "Value", "Carry"]),
]

RISK_METRICS = [
    ("VaR", ["VaR", "Return", "Alpha", "Notional"]),
    ("CVaR", ["CVaR", "Beta", "Variance", "Coupon"]),
    ("Drawdown", ["Drawdown", "Turnover", "Dividend yield", "Convexity"]),
    ("Skew", ["Skew", "Variance", "Duration", "Paydown"]),
    ("Kurtosis", ["Kurtosis", "Sharpe", "Spread", "Carry"]),
    ("Beta", ["Beta", "Alpha", "Duration", "Skew"]),
    ("Tracking Error", ["Tracking error", "Dividend yield", "Breakeven", "Convexity"]),
    ("Information Ratio", ["Information ratio", "Hit rate", "Duration", "Coupon"]),
    ("Max Drawdown", ["Max drawdown", "Max return", "Convexity", "Gamma"]),
    ("Volatility", ["Volatility", "Carry", "Leverage", "Correlation"]),
    ("Correlation", ["Correlation", "Coupon", "Convexity", "Skew"]),
    ("Turnover", ["Turnover", "Beta", "Skew", "Convexity"]),
    ("Hit Rate", ["Hit rate", "Duration", "Variance", "Sharpe"]),
    ("Win/Loss Ratio", ["Win/loss ratio", "Carry", "Beta", "Spread"]),
    ("Tail Ratio", ["Tail ratio", "Skew", "Spread", "Coupon"]),
]

FACTOR_PROMPTS = [
    ("Value factor", ["Value", "Size", "Momentum", "Low vol"]),
    ("Momentum factor", ["Momentum", "Value", "Carry", "Quality"]),
    ("Quality factor", ["Quality", "Size", "Carry", "Event"]),
    ("Size factor", ["Size", "Value", "Carry", "Growth"]),
    ("Low Vol factor", ["Low vol", "Value", "Carry", "Growth"]),
    ("Investment factor", ["Investment", "Size", "Momentum", "Growth"]),
    ("Profitability factor", ["Profitability", "Value", "Carry", "Beta"]),
    ("Carry factor", ["Carry", "Momentum", "Value", "Skew"]),
    ("Term premium", ["Term premium", "Equity premium", "Illiquidity premium", "Basis"]),
    ("Illiquidity premium", ["Illiquidity premium", "Value", "Momentum", "Carry"]),
    ("Commodity curve carry", ["Backwardation/contango", "Momentum", "Quality", "Size"]),
    ("FX carry", ["Rate differential", "Momentum", "Value", "Volatility selling"]),
    ("Quality minus junk", ["Quality", "Value", "Carry", "Market beta"]),
    ("Defensive factor", ["Low vol", "Size", "Carry", "Term"]),
    ("Growth tilt", ["Growth", "Value", "Carry", "Size"]),
    ("Dividend tilt", ["Dividend yield", "Size", "Term premium", "Illiquidity"]),
    ("Short interest signal", ["Short interest", "Value", "Carry", "Beta"]),
    ("Analyst revisions signal", ["Revisions", "Size", "Carry", "Duration"]),
    ("Earnings surprise signal", ["Earnings surprise", "Carry", "Size", "Value"]),
    ("Seasonal factor", ["Seasonality", "Value", "Carry", "Quality"]),
]

MARKET_MICRO = [
    ("Mid-quote", ["Mid-quote", "Last sale", "Closing auction", "Primary listing"]),
    ("Bid-ask spread", ["Bid-ask spread", "Coupon", "Duration", "Notional"]),
    ("Depth", ["Depth", "Skew", "Carry", "Spread"]),
    ("Latency", ["Latency", "Volatility", "Duration", "Coupon"]),
    ("Impact", ["Market impact", "Volatility", "Carry", "Gamma"]),
    ("Pegged order", ["Pegged order", "Market order", "Stop-loss", "FOK"]),
    ("VWAP", ["VWAP", "TWAP", "Close", "Open"]),
    ("TWAP", ["TWAP", "VWAP", "Close", "Open"]),
    ("IOC", ["Immediate-or-cancel", "Good-til-close", "Stop-limit", "Pegged"]),
    ("Dark pool", ["Dark pool", "Primary market", "OTC bond market", "FX swap line"]),
]

EQUITY_ASSETS = [
    "S&P 500 ETF",
    "Nasdaq 100 ETF",
    "Dow Jones ETF",
    "Russell 2000 ETF",
    "MSCI EAFE ETF",
    "MSCI EM ETF",
    "FTSE 100 ETF",
    "Nikkei 225 ETF",
    "DAX ETF",
    "CAC 40 ETF",
    "Healthcare sector ETF",
    "Tech sector ETF",
    "Utilities sector ETF",
    "Energy sector ETF",
    "Financials sector ETF",
    "Semiconductor ETF",
    "Consumer Staples ETF",
    "Consumer Discretionary ETF",
    "Real Estate ETF",
    "Infrastructure ETF",
    "Equal-Weight S&P 500 ETF",
    "Low Volatility Equity ETF",
    "High Dividend Equity ETF",
    "ESG Equity ETF",
    "Frontier Markets Equity ETF",
]

FIXED_INCOME_ASSETS = [
    "US 10Y Treasury future",
    "US 2Y Treasury note",
    "German Bund future",
    "UK Gilt future",
    "JGB 10Y future",
    "High yield bond ETF",
    "Investment grade bond ETF",
    "EM sovereign bond ETF",
    "TIPS ETF",
    "MBS ETF",
    "Municipal bond ETF",
    "Bank loan ETF",
    "Ultra-short Treasury ETF",
    "Long-duration Treasury ETF",
    "Corporate bond future",
]

COMMODITY_ASSETS = [
    "WTI Crude future",
    "Brent Crude future",
    "Gold future",
    "Silver future",
    "Copper future",
    "Corn future",
    "Wheat future",
    "Soybean future",
    "Natural Gas future",
    "Gasoline RBOB future",
    "Heating Oil future",
    "Palladium future",
    "Platinum future",
    "Coffee future",
    "Cocoa future",
]

CURRENCY_ASSETS = [
    "EUR/USD",
    "USD/JPY",
    "GBP/USD",
    "USD/CHF",
    "AUD/USD",
    "NZD/USD",
    "USD/CAD",
    "USD/CNH",
    "USD/MXN",
    "USD/BRL",
    "EUR/GBP",
    "EUR/JPY",
    "USD/INR",
]

CRYPTO_ASSETS = [
    "BTC/USD",
    "ETH/USD",
    "SOL/USD",
    "MATIC/USD",
    "DOGE/USD",
]

INVESTORS = [
    "Jim Simons",
    "Ray Dalio",
    "Ken Griffin",
    "James Harris Simons",
    "Peter Lynch",
    "Warren Buffett",
    "George Soros",
    "Cliff Asness",
    "David Harding",
    "Stanley Druckenmiller",
    "John Paulson",
    "Ed Thorp",
    "Joel Greenblatt",
    "Bill Ackman",
    "Jeff Yass",
    "Jane Street",
    "Two Sigma",
    "D.E. Shaw",
    "AQR Capital",
    "Bridgewater Associates",
]

ECON_EVENTS = [
    "Fed rate hike",
    "Fed rate cut",
    "ECB policy meeting",
    "Nonfarm payrolls",
    "CPI release",
    "PPI release",
    "GDP release",
    "FOMC minutes",
    "BoJ policy meeting",
    "BOE policy meeting",
    "Flash PMIs",
    "ISM manufacturing",
    "Retail sales report",
    "Housing starts",
    "Jobless claims",
    "Trade balance",
    "Jackson Hole symposium",
    "OPEC meeting",
    "Debt ceiling debate",
    "Budget statement",
]

ORDER_TYPES = [
    "Limit order",
    "Market order",
    "Stop order",
    "Stop-limit order",
    "Immediate-or-cancel",
    "Fill-or-kill",
    "Pegged order",
    "Iceberg order",
    "Midpoint peg",
    "Close auction",
]

STAT_TOPICS = [
    "Central limit theorem",
    "Law of large numbers",
    "Confidence interval",
    "p-value",
    "Type I error",
    "Type II error",
    "Homoscedasticity",
    "Heteroscedasticity",
    "Autocorrelation",
    "Stationarity",
    "Unit root",
    "Cointegration",
    "ADF test",
    "Jarque-Bera test",
    "Shapiro-Wilk test",
]

VOL_TOPICS = [
    "Volatility surface",
    "Implied volatility",
    "Realized volatility",
    "Skew",
    "Term structure",
    "Volatility smile",
    "Vega",
    "Gamma",
    "Delta hedging",
    "Vanna/Charm",
]

INDICES = [
    "S&P 500",
    "Nasdaq 100",
    "Dow Jones Industrial Average",
    "Russell 2000",
    "Euro Stoxx 50",
    "FTSE 100",
    "Nikkei 225",
    "Hang Seng",
    "CSI 300",
    "Sensex",
]


def _annualization_questions():
    questions = []
    for days in DAILY_DAYS:
        questions.append(
            {
                "prompt": f"What is the annualization factor for daily returns with {days} trading days?",
                "options": [f"sqrt({days})", f"{days}", "sqrt(52)", "sqrt(12)"],
                "answer": 0,
            }
        )
    for weeks in WEEKLY_PERIODS:
        questions.append(
            {
                "prompt": f"What is the annualization factor for weekly returns with {weeks} weeks?",
                "options": ["sqrt(52)", f"{weeks}", "sqrt(12)", "sqrt(252)"],
                "answer": 0,
            }
        )
    for months in MONTHLY_PERIODS:
        questions.append(
            {
                "prompt": f"What is the annualization factor for monthly returns over {months} months?",
                "options": ["sqrt(12)", f"{months}", "sqrt(52)", "sqrt(252)"],
                "answer": 0,
            }
        )
    return questions


def _style_questions():
    questions = []
    for prompt, options in STYLES:
        questions.append({"prompt": f"Which style best matches this description: {prompt}?", "options": options, "answer": 0})
    return questions


def _risk_questions():
    questions = []
    for metric, options in RISK_METRICS:
        questions.append({"prompt": f"Which item is a risk metric?", "options": options, "answer": 0})
    return questions


def _factor_questions():
    questions = []
    for factor, options in FACTOR_PROMPTS:
        questions.append({"prompt": f"Which option names the factor described: {factor}?", "options": options, "answer": 0})
    return questions


def _micro_questions():
    questions = []
    for term, options in MARKET_MICRO:
        questions.append({"prompt": f"Which microstructure concept fits: {term}?", "options": options, "answer": 0})
    return questions


def _asset_class_questions():
    questions = []
    for asset in EQUITY_ASSETS:
        questions.append(
            {"prompt": f"What asset class best describes {asset}?", "options": ["Equity", "Fixed Income", "Commodity", "Currency"], "answer": 0}
        )
    for asset in FIXED_INCOME_ASSETS:
        questions.append(
            {"prompt": f"What asset class best describes {asset}?", "options": ["Fixed Income", "Equity", "Commodity", "Currency"], "answer": 0}
        )
    for asset in COMMODITY_ASSETS:
        questions.append(
            {"prompt": f"What asset class best describes {asset}?", "options": ["Commodity", "Equity", "Fixed Income", "Currency"], "answer": 0}
        )
    for asset in CURRENCY_ASSETS:
        questions.append(
            {"prompt": f"What asset class best describes {asset}?", "options": ["Currency", "Equity", "Fixed Income", "Commodity"], "answer": 0}
        )
    for asset in CRYPTO_ASSETS:
        questions.append(
            {"prompt": f"How would you classify {asset}?", "options": ["Digital asset", "Equity", "Fixed Income", "Commodity"], "answer": 0}
        )
    return questions


def _investor_questions():
    questions = []
    for name in INVESTORS:
        questions.append(
            {
                "prompt": f"{name} is best known for:",
                "options": [
                    "Running a major hedge fund or quant shop",
                    "Setting exchange policy",
                    "Operating a central bank",
                    "Regulating markets",
                ],
                "answer": 0,
            }
        )
    return questions


def _econ_event_questions():
    questions = []
    for event in ECON_EVENTS:
        questions.append(
            {
                "prompt": f"What type of release or meeting is '{event}'?",
                "options": [
                    "Macro data/central bank event",
                    "Corporate action",
                    "Order type",
                    "Settlement mechanic",
                ],
                "answer": 0,
            }
        )
    return questions


def _order_type_questions():
    questions = []
    for order in ORDER_TYPES:
        questions.append(
            {
                "prompt": f"{order} is primarily:",
                "options": [
                    "An order type",
                    "A risk metric",
                    "A strategy style",
                    "A macro event",
                ],
                "answer": 0,
            }
        )
    return questions


def _stat_questions():
    questions = []
    for topic in STAT_TOPICS:
        questions.append(
            {
                "prompt": f"{topic} is:",
                "options": [
                    "A statistical concept",
                    "An order type",
                    "A sector ETF",
                    "A commodity spread",
                ],
                "answer": 0,
            }
        )
    return questions


def _vol_questions():
    questions = []
    for topic in VOL_TOPICS:
        questions.append(
            {
                "prompt": f"{topic} refers to:",
                "options": [
                    "Options/volatility concept",
                    "Fixed income coupon feature",
                    "FX benchmark",
                    "Equity sector index",
                ],
                "answer": 0,
            }
        )
    return questions


def _index_questions():
    questions = []
    for idx in INDICES:
        questions.append(
            {
                "prompt": f"{idx} is an example of:",
                "options": [
                    "Equity index",
                    "Commodity future",
                    "Bond future",
                    "FX pair",
                ],
                "answer": 0,
            }
        )
    return questions


def get_trivia_questions():
    """
    Build the trivia bank (>=250 questions).
    """
    questions = []
    questions.extend(BASE_QUESTIONS)
    questions.extend(_annualization_questions())
    questions.extend(_style_questions())
    questions.extend(_risk_questions())
    questions.extend(_factor_questions())
    questions.extend(_micro_questions())
    questions.extend(_asset_class_questions())
    questions.extend(_investor_questions())
    questions.extend(_econ_event_questions())
    questions.extend(_order_type_questions())
    questions.extend(_stat_questions())
    questions.extend(_vol_questions())
    questions.extend(_index_questions())
    # Shuffle to add variety
    random.shuffle(questions)
    return questions
