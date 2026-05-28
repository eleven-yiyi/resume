"""
Seed script: import job descriptions into DB.
Run: python scripts/import_jds.py

Generates embeddings locally and inserts all JDs.
"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from services.llama import embed

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://boss:boss123@localhost:5432/bossjob")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# ── JD data ────────────────────────────────────────────────────────────────────
# work_arrangement: "onsite" | "hybrid" | "remote"
# job_type:         "full-time" | "part-time" | "contract" | "internship"
# currency:         "USD" | "EUR" | "GBP" | ...
# highlights:       3–5 short bullet strings shown on the match card
# tags:             skill/domain keywords used for embedding quality
JDS = [
    # ── Software Engineering ───────────────────────────────────────────────────
    {
        "title": "Senior Software Engineer, Backend",
        "company": "Stripe",
        "location": "San Francisco, CA",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 180000, "salary_max": 240000, "currency": "USD",
        "description": (
            "Stripe is looking for a Senior Software Engineer to join our Payments Infrastructure team. "
            "You will design and build the core systems that process hundreds of billions of dollars in payments each year. "
            "Responsibilities include architecting high-availability distributed services in Ruby and Go, "
            "leading technical design reviews, mentoring junior engineers, and partnering closely with product and design "
            "to ship features that millions of businesses rely on. You will own entire feature areas end-to-end, "
            "from database schema design to API contracts to monitoring and alerting. "
            "We value simplicity, reliability, and clear thinking. Our systems need to work every time, at scale, forever."
        ),
        "highlights": [
            "Own distributed payment infrastructure processing $1T+ annually",
            "Lead technical design for cross-team projects",
            "Hybrid work — SF HQ with flexible remote days",
            "Top-of-market compensation + equity",
        ],
        "tags": ["backend", "distributed systems", "Ruby", "Go", "payments", "API design", "PostgreSQL", "Kafka"],
    },
    {
        "title": "Staff Frontend Engineer",
        "company": "Figma",
        "location": "New York, NY",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 200000, "salary_max": 270000, "currency": "USD",
        "description": (
            "Figma is hiring a Staff Frontend Engineer to push the boundaries of what's possible in a browser-based creative tool. "
            "You'll work on Figma's core editor — a highly optimized WebGL and Canvas rendering engine used by millions of designers. "
            "Your responsibilities include leading architecture decisions for our React/TypeScript frontend, "
            "improving rendering performance, driving platform-wide code quality initiatives, and collaborating with design systems teams. "
            "You'll be a technical leader setting direction across multiple product areas and mentoring a team of senior engineers. "
            "We care deeply about craft, performance, and shipping things that feel magical."
        ),
        "highlights": [
            "Core editor team — WebGL rendering at 60fps in the browser",
            "Staff-level technical leadership across frontend org",
            "Cutting-edge TypeScript/React at massive scale",
            "Generous equity + $10K/yr learning budget",
        ],
        "tags": ["frontend", "TypeScript", "React", "WebGL", "Canvas", "performance", "design tools", "staff engineer"],
    },
    {
        "title": "Software Engineer II, Full-Stack",
        "company": "Notion",
        "location": "Remote — US",
        "work_arrangement": "remote",
        "job_type": "full-time",
        "salary_min": 140000, "salary_max": 185000, "currency": "USD",
        "description": (
            "Notion is building the connected workspace for modern teams, and we're looking for a full-stack engineer "
            "to join one of our product squads. You'll work across our React frontend and Node.js/TypeScript backend, "
            "shipping features that shape how millions of people organize their work and knowledge. "
            "Day-to-day you'll scope and implement user-facing features, improve our real-time sync architecture, "
            "write thoughtful code reviews, and participate in on-call rotations. "
            "We're a product-minded engineering team — you'll sit alongside designers and PMs and have direct influence "
            "over what gets built and how. Fully remote within the US with annual team offsites."
        ),
        "highlights": [
            "Full-stack across React + Node.js/TypeScript",
            "Fully remote within the US",
            "Direct product influence in a small cross-functional team",
            "Competitive salary + meaningful equity in a $10B company",
        ],
        "tags": ["full-stack", "React", "Node.js", "TypeScript", "real-time sync", "PostgreSQL", "remote", "SaaS"],
    },
    {
        "title": "iOS Engineer",
        "company": "Duolingo",
        "location": "Pittsburgh, PA",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 130000, "salary_max": 175000, "currency": "USD",
        "description": (
            "Duolingo's iOS team is responsible for the app used by 80 million daily active learners worldwide. "
            "As an iOS Engineer you'll own features in Swift/SwiftUI, collaborate with our animation and design teams "
            "to create delightful learning experiences, optimize app performance and startup time, "
            "and contribute to our shared component library. "
            "You'll work in a highly iterative environment — we A/B test aggressively and ship frequently. "
            "Strong opinions about user experience and attention to detail are a must. "
            "Experience with complex animations, accessibility, or EdTech is a plus."
        ),
        "highlights": [
            "Build features for 80M daily active learners",
            "Swift/SwiftUI with heavy animation focus",
            "High-velocity A/B testing culture",
            "Pittsburgh HQ with relocation assistance available",
        ],
        "tags": ["iOS", "Swift", "SwiftUI", "mobile", "animations", "UIKit", "A/B testing", "EdTech"],
    },
    {
        "title": "Android Engineer",
        "company": "Spotify",
        "location": "London, UK",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 80000, "salary_max": 115000, "currency": "GBP",
        "description": (
            "Spotify is looking for an Android Engineer to join the Home & Discovery team in London. "
            "You'll build and maintain the personalised home feed that surfaces music, podcasts, and audiobooks "
            "to over 600 million users. Your work involves Kotlin, Jetpack Compose, clean architecture, "
            "and close collaboration with our machine learning teams to integrate recommendation signals. "
            "We practise continuous delivery on Android and you'll be involved in the full release pipeline. "
            "Our engineering culture is autonomous and trust-based — squads own their roadmaps end-to-end."
        ),
        "highlights": [
            "Home & Discovery team — 600M+ user impact",
            "Kotlin + Jetpack Compose, modern Android stack",
            "London office with flexible hybrid schedule",
            "Spotify Premium, learning allowance, equity",
        ],
        "tags": ["Android", "Kotlin", "Jetpack Compose", "mobile", "recommendation systems", "CI/CD", "music tech"],
    },
    {
        "title": "Platform Engineer (DevOps)",
        "company": "Cloudflare",
        "location": "Austin, TX",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 150000, "salary_max": 195000, "currency": "USD",
        "description": (
            "Cloudflare's Developer Platform team is hiring a Platform Engineer to build and operate the infrastructure "
            "that powers Workers, Pages, and R2 — products used by millions of developers. "
            "You'll work on Kubernetes-based orchestration, build internal developer tooling, design CI/CD pipelines, "
            "and drive reliability improvements across our global edge network of 300+ PoPs. "
            "You're comfortable writing Go or Rust when scripts aren't enough, have strong opinions about observability, "
            "and thrive in high-ownership environments. On-call is part of the role with rotation shared across the team."
        ),
        "highlights": [
            "Operate infrastructure at Cloudflare's global edge scale",
            "Kubernetes, Go, Terraform on real distributed systems",
            "Austin HQ, hybrid — no coast bias",
            "Significant equity upside at a public tech company",
        ],
        "tags": ["DevOps", "Kubernetes", "Go", "Terraform", "CI/CD", "platform engineering", "reliability", "edge computing"],
    },
    # ── Data / ML ──────────────────────────────────────────────────────────────
    {
        "title": "Senior Data Engineer",
        "company": "Airbnb",
        "location": "San Francisco, CA",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 170000, "salary_max": 220000, "currency": "USD",
        "description": (
            "Airbnb's Data Engineering team builds the pipelines and infrastructure that power our data-driven culture. "
            "As a Senior Data Engineer you'll design and maintain large-scale batch and streaming pipelines on Apache Spark and Flink, "
            "build reusable data models in dbt, partner with Data Science and Analytics Engineering teams, "
            "and ensure data quality across critical business domains like pricing and trust & safety. "
            "You'll have meaningful ownership: you'll architect pipelines from scratch, drive standards across the team, "
            "and participate in quarterly roadmap planning. Python and SQL fluency is required; "
            "experience with Airflow orchestration and Hive/Iceberg table formats is strongly preferred."
        ),
        "highlights": [
            "Design pipelines for Airbnb's core marketplace data",
            "Spark, Flink, Airflow, dbt at petabyte scale",
            "Hybrid — SF HQ + remote flexibility",
            "Top compensation + annual travel credits",
        ],
        "tags": ["data engineering", "Spark", "Flink", "dbt", "Airflow", "Python", "SQL", "Iceberg", "streaming"],
    },
    {
        "title": "Machine Learning Engineer",
        "company": "OpenAI",
        "location": "San Francisco, CA",
        "work_arrangement": "onsite",
        "job_type": "full-time",
        "salary_min": 200000, "salary_max": 370000, "currency": "USD",
        "description": (
            "OpenAI is seeking an ML Engineer to work on the systems and infrastructure that train and serve our frontier models. "
            "You'll write high-performance distributed training code in Python/CUDA, optimize memory and throughput on GPU clusters, "
            "build evaluation harnesses, and work directly with researchers to accelerate their iteration velocity. "
            "This is a deeply technical role — you need strong fundamentals in ML (backprop, transformers, RLHF), "
            "proficiency in PyTorch, and comfort debugging in multi-node GPU environments. "
            "You'll shape how the world's most capable AI systems are built."
        ),
        "highlights": [
            "Train and serve frontier LLMs at global scale",
            "Deep PyTorch + CUDA systems work",
            "Onsite in SF — fast-paced research-engineering collaboration",
            "Industry-leading total compensation",
        ],
        "tags": ["machine learning", "LLM", "PyTorch", "CUDA", "distributed training", "GPU", "transformers", "RLHF"],
    },
    {
        "title": "Data Scientist, Growth",
        "company": "HubSpot",
        "location": "Remote — US/EU",
        "work_arrangement": "remote",
        "job_type": "full-time",
        "salary_min": 120000, "salary_max": 160000, "currency": "USD",
        "description": (
            "HubSpot's Growth Data Science team partners with product and marketing to drive acquisition and retention. "
            "As a Data Scientist you'll own end-to-end analysis of product funnels, design and analyse A/B experiments, "
            "build predictive models for churn and upsell, and present findings to senior leadership. "
            "You'll work in SQL and Python (pandas, scikit-learn, statsmodels), use our internal experimentation platform, "
            "and contribute to a culture of data-driven decision-making. "
            "A strong statistical background and the ability to communicate results clearly to non-technical stakeholders are essential."
        ),
        "highlights": [
            "Own growth analytics for a $2B ARR SaaS product",
            "Python, SQL, A/B experimentation at scale",
            "Fully remote across US and EU time zones",
            "Generous parental leave + flexible PTO",
        ],
        "tags": ["data science", "growth", "A/B testing", "Python", "SQL", "churn prediction", "statistics", "SaaS"],
    },
    {
        "title": "MLOps Engineer",
        "company": "Zalando",
        "location": "Berlin, Germany",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 75000, "salary_max": 105000, "currency": "EUR",
        "description": (
            "Zalando's AI Platform team is building the ML infrastructure that enables 200+ data scientists and ML engineers "
            "to build, train, and deploy models at scale. As an MLOps Engineer you'll own our model serving platform (KServe/Seldon), "
            "build feature stores and model registries, design MLflow-based experiment tracking workflows, "
            "and create tooling that reduces time-to-production for ML teams. "
            "Experience with Kubernetes, Python, and modern ML tooling is required. "
            "Knowledge of recommendation systems or NLP is a plus. "
            "We offer a relocation package and English-first working environment in Berlin."
        ),
        "highlights": [
            "Build ML platform serving 200+ data scientists",
            "Kubernetes, MLflow, KServe, feature stores",
            "Berlin HQ — English-first, relocation supported",
            "30 days paid leave, annual fashion budget",
        ],
        "tags": ["MLOps", "Kubernetes", "MLflow", "Python", "model serving", "feature store", "KServe", "Berlin"],
    },
    # ── Product ────────────────────────────────────────────────────────────────
    {
        "title": "Senior Product Manager, Core Product",
        "company": "Linear",
        "location": "Remote — Worldwide",
        "work_arrangement": "remote",
        "job_type": "full-time",
        "salary_min": 160000, "salary_max": 200000, "currency": "USD",
        "description": (
            "Linear builds software for high-performance teams and we're looking for a Senior Product Manager "
            "to own the roadmap for our core issue tracking and project management features. "
            "You'll work directly with founders and engineering leads to define product strategy, "
            "conduct user research with our power users, write detailed specs, and drive launches. "
            "We're a small team that moves fast — you'll have wide scope and direct impact. "
            "The ideal candidate has shipped B2B SaaS products, has a strong intuition for developer tools, "
            "writes clearly, and can engage deeply with technical implementation details."
        ),
        "highlights": [
            "Own core product roadmap at a beloved developer tool",
            "Work directly with founders — wide scope, fast cycles",
            "Fully remote, async-first culture",
            "Top-quartile comp + equity at a fast-growing Series C",
        ],
        "tags": ["product management", "B2B SaaS", "developer tools", "roadmap", "user research", "remote", "PM"],
    },
    {
        "title": "Product Manager, Payments",
        "company": "Adyen",
        "location": "Amsterdam, Netherlands",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 85000, "salary_max": 120000, "currency": "EUR",
        "description": (
            "Adyen is a global payments platform powering companies like Uber, Spotify, and McDonald's. "
            "We're hiring a Product Manager to own our acquiring product for the European market. "
            "You'll work with engineering, legal, and merchant success to define the feature roadmap, "
            "navigate card scheme rules and regulatory requirements, analyse payment success rates, "
            "and build products that improve conversion for enterprise merchants. "
            "A background in payments, fintech, or financial services is strongly preferred. "
            "Dutch language is not required — we work in English."
        ),
        "highlights": [
            "Own acquiring product for enterprise merchants across Europe",
            "Deep fintech domain — card schemes, authorisation optimisation",
            "Amsterdam HQ in a flat, international organisation",
            "Profit-sharing scheme + excellent benefits",
        ],
        "tags": ["product management", "payments", "fintech", "acquiring", "B2B", "Amsterdam", "Europe"],
    },
    # ── Design ─────────────────────────────────────────────────────────────────
    {
        "title": "Senior Product Designer",
        "company": "Webflow",
        "location": "Remote — US",
        "work_arrangement": "remote",
        "job_type": "full-time",
        "salary_min": 145000, "salary_max": 185000, "currency": "USD",
        "description": (
            "Webflow is building the future of the web, and we're looking for a Senior Product Designer "
            "to join the Designer Experience team. You'll own end-to-end design for our visual CSS editor and responsive design tooling — "
            "features used by hundreds of thousands of professional designers. "
            "Responsibilities include leading discovery, running usability research, shipping high-fidelity prototypes in Figma, "
            "and collaborating daily with engineering and PM. "
            "You have a strong systems thinking mindset, can articulate design rationale clearly, "
            "and care about the details that make complex tools feel simple."
        ),
        "highlights": [
            "Design core visual editor used by 300K+ professional designers",
            "End-to-end ownership from research to shipped pixels",
            "Fully remote with quarterly in-person design sprints",
            "Figma-heavy workflow, strong design system culture",
        ],
        "tags": ["product design", "UX", "Figma", "design systems", "web", "SaaS", "visual editor", "remote"],
    },
    {
        "title": "UX Researcher",
        "company": "Spotify",
        "location": "Stockholm, Sweden",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 620000, "salary_max": 820000, "currency": "SEK",
        "description": (
            "Spotify's UX Research team is looking for a researcher to partner with the Podcast & Video product squad. "
            "You'll plan and execute qualitative and quantitative research — user interviews, diary studies, surveys, "
            "and usability tests — to inform product strategy and design decisions. "
            "You'll synthesise insights into clear narratives, present to leadership, "
            "and embed research thinking into the product development lifecycle. "
            "Experience with both qual and quant methods is required. "
            "A background in entertainment, social, or content platforms is a plus."
        ),
        "highlights": [
            "Drive research for Spotify's podcasts & video product",
            "Mixed-methods — qual interviews to quant surveys",
            "Stockholm HQ with hybrid flexibility",
            "Spotify Premium, 30 days leave, parental benefits",
        ],
        "tags": ["UX research", "user interviews", "usability testing", "qualitative", "quantitative", "product strategy", "Stockholm"],
    },
    # ── Marketing ──────────────────────────────────────────────────────────────
    {
        "title": "Growth Marketing Manager",
        "company": "Canva",
        "location": "Austin, TX",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 100000, "salary_max": 135000, "currency": "USD",
        "description": (
            "Canva is on a mission to make design accessible to everyone. We're hiring a Growth Marketing Manager "
            "to own paid acquisition channels for the US market. "
            "You'll manage a multi-million dollar budget across Google, Meta, LinkedIn, and programmatic channels, "
            "run creative testing at scale, build attribution models, and work with the data team on LTV optimisation. "
            "You're equal parts analytical and creative — you can pull your own SQL queries in the morning "
            "and brief a creative agency in the afternoon. "
            "Experience scaling SaaS or consumer subscription products is strongly preferred."
        ),
        "highlights": [
            "Own $MM+ paid acquisition budget across US market",
            "Creative testing, attribution, LTV modelling",
            "Austin office, hybrid — strong team culture",
            "Competitive base + equity in a $26B company",
        ],
        "tags": ["growth marketing", "paid acquisition", "Google Ads", "Meta Ads", "SaaS", "LTV", "attribution", "Austin"],
    },
    {
        "title": "Content Marketing Lead",
        "company": "Notion",
        "location": "New York, NY",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 110000, "salary_max": 145000, "currency": "USD",
        "description": (
            "Notion is looking for a Content Marketing Lead to build and execute our editorial content strategy. "
            "You'll own the Notion blog, create long-form guides and case studies, "
            "develop content that ranks for high-intent search queries, "
            "and collaborate with design to produce visual content for social. "
            "You'll manage a small team of writers and freelancers and work closely with SEO, product marketing, and community. "
            "The ideal candidate is an exceptional writer with deep B2B SaaS intuition, "
            "comfort with SEO tools (Ahrefs, SEMrush), and experience growing organic traffic at a product-led growth company."
        ),
        "highlights": [
            "Own editorial strategy — blog, guides, case studies",
            "Product-led growth context, strong SEO focus",
            "NYC HQ, hybrid — collaborative creative environment",
            "Equity + comprehensive health/dental/vision",
        ],
        "tags": ["content marketing", "SEO", "editorial", "B2B SaaS", "copywriting", "Ahrefs", "PLG", "New York"],
    },
    {
        "title": "Senior SEO Manager",
        "company": "Semrush",
        "location": "Remote — US",
        "work_arrangement": "remote",
        "job_type": "full-time",
        "salary_min": 95000, "salary_max": 130000, "currency": "USD",
        "description": (
            "Semrush is hiring a Senior SEO Manager to own organic search strategy for our core marketing website. "
            "You'll conduct technical audits, build content briefs, manage internal linking architecture, "
            "analyse crawl data in Screaming Frog, and report on SEO KPIs to leadership. "
            "You'll work closely with content, web development, and international teams "
            "to execute on-page and off-page strategies. "
            "Deep understanding of Google's ranking signals, E-E-A-T, and Core Web Vitals is required. "
            "Experience working on large-scale (100K+ page) websites is a strong plus."
        ),
        "highlights": [
            "Own organic search for a global SaaS marketing website",
            "Technical + content SEO ownership end-to-end",
            "Fully remote with flexible hours",
            "Use Semrush's own toolset — deep data access",
        ],
        "tags": ["SEO", "technical SEO", "content strategy", "Screaming Frog", "Core Web Vitals", "SaaS marketing", "remote"],
    },
    # ── Finance ────────────────────────────────────────────────────────────────
    {
        "title": "Financial Analyst, FP&A",
        "company": "Snowflake",
        "location": "San Mateo, CA",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 95000, "salary_max": 125000, "currency": "USD",
        "description": (
            "Snowflake's FP&A team is looking for a Financial Analyst to support the GTM finance function. "
            "You'll build and maintain financial models for sales productivity and pipeline forecasting, "
            "own monthly close processes, prepare board-level reporting packages, "
            "and partner with Revenue Operations and Sales leadership on budget management. "
            "Advanced Excel/Google Sheets and Workday Adaptive Planning experience is required. "
            "SQL proficiency to pull data from Snowflake (of course) is a must. "
            "CPA or CFA progress is a plus. This role offers a clear path to Sr. Analyst or Manager."
        ),
        "highlights": [
            "GTM finance for a $17B public data cloud company",
            "Board-level reporting and pipeline forecasting",
            "San Mateo HQ, hybrid schedule",
            "ESPP, 401(k) match, strong promotion cadence",
        ],
        "tags": ["FP&A", "financial modelling", "Excel", "SQL", "Workday", "SaaS metrics", "GTM finance", "forecasting"],
    },
    {
        "title": "Corporate Controller",
        "company": "Revolut",
        "location": "London, UK",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 90000, "salary_max": 130000, "currency": "GBP",
        "description": (
            "Revolut is looking for a Corporate Controller to own the group consolidated financial statements "
            "and lead a team of accountants across multiple legal entities. "
            "You'll manage the monthly close calendar, ensure IFRS compliance, liaise with external auditors, "
            "and implement accounting policies for new financial products. "
            "ACA/ACCA qualification is required, with at least 3 years post-qualification experience. "
            "Experience in fintech, banking, or financial services with multi-entity consolidation is strongly preferred. "
            "You'll report directly to the CFO and have significant visibility across the business."
        ),
        "highlights": [
            "Own group consolidation for a 40M+ customer neobank",
            "IFRS, multi-entity, direct CFO reporting line",
            "London HQ, hybrid — fast-paced scale-up",
            "Top fintech pay + RSUs",
        ],
        "tags": ["accounting", "controller", "IFRS", "consolidation", "fintech", "ACA", "ACCA", "audit", "London"],
    },
    # ── Sales ──────────────────────────────────────────────────────────────────
    {
        "title": "Enterprise Account Executive",
        "company": "Datadog",
        "location": "New York, NY",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 120000, "salary_max": 160000, "currency": "USD",
        "description": (
            "Datadog is hiring an Enterprise Account Executive to drive new logo and expansion revenue "
            "within a named accounts territory of Fortune 500 companies. "
            "You'll run a full sales cycle from prospecting to close, navigate complex multi-stakeholder deals, "
            "work with our Solutions Engineering team on technical evaluations, "
            "and forecast accurately in Salesforce. "
            "OTE is $240K–$320K (50/50 split). "
            "5+ years of enterprise software sales with quota attainment track record is required. "
            "Experience selling to engineering, DevOps, or security personas is a strong plus."
        ),
        "highlights": [
            "Fortune 500 territory — new logo + expansion",
            "$240K–$320K OTE, 50/50 split",
            "Sell observability to engineering & DevOps buyers",
            "NYC office with strong peer community",
        ],
        "tags": ["enterprise sales", "SaaS", "account executive", "Salesforce", "B2B", "cloud", "DevOps", "New York"],
    },
    {
        "title": "Sales Development Representative",
        "company": "HubSpot",
        "location": "Dublin, Ireland",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 38000, "salary_max": 48000, "currency": "EUR",
        "description": (
            "HubSpot's Dublin EMEA hub is looking for driven Sales Development Representatives "
            "to join the inbound and outbound SDR team. "
            "You'll qualify inbound leads from marketing, run targeted outbound sequences to ICP prospects, "
            "book discovery calls for Account Executives, and maintain clean Salesforce records. "
            "We invest heavily in SDR development — structured 90-day ramp, dedicated enablement team, "
            "and a clear path to AE promotion typically within 12–18 months. "
            "No prior SaaS sales experience required, but curiosity, resilience, and excellent communication are a must."
        ),
        "highlights": [
            "EMEA SDR team in HubSpot's Dublin hub",
            "Structured ramp + AE promotion path in 12–18 months",
            "Inbound + outbound mix, Salesforce + Outreach",
            "Great culture — ranked #1 Best Place to Work multiple years",
        ],
        "tags": ["SDR", "sales development", "SaaS", "Salesforce", "outbound", "EMEA", "Dublin", "entry level sales"],
    },
    # ── Operations / HR ────────────────────────────────────────────────────────
    {
        "title": "People Operations Manager",
        "company": "Loom",
        "location": "Remote — US",
        "work_arrangement": "remote",
        "job_type": "full-time",
        "salary_min": 100000, "salary_max": 130000, "currency": "USD",
        "description": (
            "Loom (now part of Atlassian) is looking for a People Operations Manager "
            "to run the employee lifecycle from onboarding to offboarding for our distributed team. "
            "You'll own HRIS administration (Workday), manage benefits and leave programmes, "
            "ensure compliance across US states and international locations, "
            "run engagement surveys and implement follow-on action plans, "
            "and partner with finance on headcount planning. "
            "Experience managing People Ops at a company scaling from 100 to 500 employees is ideal. "
            "You're detail-oriented, discreet, and genuinely care about employee experience."
        ),
        "highlights": [
            "Own full employee lifecycle for a fully distributed team",
            "Workday HRIS, benefits, compliance across US + international",
            "Fully remote — async-first, strong documentation culture",
            "Atlassian parent company benefits + equity",
        ],
        "tags": ["HR", "people operations", "HRIS", "Workday", "benefits", "compliance", "remote", "employee experience"],
    },
    {
        "title": "Technical Recruiter",
        "company": "Stripe",
        "location": "Dublin, Ireland",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 55000, "salary_max": 80000, "currency": "EUR",
        "description": (
            "Stripe's EMEA Talent team is hiring a Technical Recruiter to own full-cycle hiring "
            "for software engineering roles across our Dublin and Remote EMEA workforce. "
            "You'll partner with engineering hiring managers to define role requirements, "
            "source passively through LinkedIn Recruiter and GitHub, manage candidates through Greenhouse ATS, "
            "run structured interviews, and close offers competitively. "
            "We care deeply about hiring quality and inclusive processes. "
            "2+ years of technical recruiting in a fast-paced tech company is required."
        ),
        "highlights": [
            "Full-cycle technical recruiting for engineering roles",
            "Greenhouse ATS, LinkedIn Recruiter sourcing",
            "Dublin HQ — EMEA scope",
            "Stripe RSUs, generous parental leave, learning budget",
        ],
        "tags": ["recruiting", "technical recruiting", "talent acquisition", "Greenhouse", "LinkedIn Recruiter", "engineering hiring", "Dublin"],
    },
    {
        "title": "Strategy & Operations Lead",
        "company": "Uber",
        "location": "Chicago, IL",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 125000, "salary_max": 160000, "currency": "USD",
        "description": (
            "Uber's Rides Strategy & Operations team is hiring a Lead to own market performance "
            "for the Midwest region. You'll analyse supply-demand dynamics, design and run pricing experiments, "
            "lead driver incentive programmes, and partner with product and marketing on local initiatives. "
            "You'll present insights and recommendations to senior leadership weekly. "
            "Strong SQL and data visualisation skills (Tableau/Looker) are required. "
            "MBA or equivalent analytical work experience is preferred. "
            "This is a high-visibility, generalist strategy role with a path to Director."
        ),
        "highlights": [
            "Own Midwest market strategy for Uber Rides",
            "Pricing experiments, driver incentives, supply-demand analytics",
            "Chicago HQ, hybrid — direct leadership exposure",
            "RSUs, 401(k) match, Uber credits",
        ],
        "tags": ["strategy", "operations", "marketplace", "SQL", "Tableau", "pricing", "Uber", "Chicago"],
    },
    # ── Customer Success / Support ─────────────────────────────────────────────
    {
        "title": "Customer Success Manager, Mid-Market",
        "company": "Zendesk",
        "location": "San Francisco, CA",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 85000, "salary_max": 115000, "currency": "USD",
        "description": (
            "Zendesk is looking for a Customer Success Manager to own a portfolio of 40–60 mid-market accounts. "
            "You'll drive adoption, conduct regular business reviews, identify expansion opportunities, "
            "and manage renewals with a ~$3M ARR book of business. "
            "You'll be the customer's internal advocate — working with product, support, and professional services "
            "to resolve issues and unlock value. "
            "2+ years in B2B SaaS CSM with Gainsight experience preferred. "
            "Strong commercial instincts and empathy in equal measure."
        ),
        "highlights": [
            "$3M ARR portfolio — adoption, renewal, and expansion",
            "Gainsight-powered CS motion",
            "SF HQ, hybrid schedule",
            "Variable comp on top of base, strong equity programme",
        ],
        "tags": ["customer success", "CSM", "SaaS", "Gainsight", "renewal", "expansion", "mid-market", "B2B"],
    },
    # ── Security / Infrastructure ──────────────────────────────────────────────
    {
        "title": "Security Engineer, AppSec",
        "company": "GitHub",
        "location": "Remote — US",
        "work_arrangement": "remote",
        "job_type": "full-time",
        "salary_min": 165000, "salary_max": 215000, "currency": "USD",
        "description": (
            "GitHub's Application Security team is looking for a Security Engineer to protect the platform "
            "that 100 million developers trust to store their code. "
            "You'll conduct threat modelling and security design reviews for new product features, "
            "run bug bounty triage and response, build SAST/DAST tooling into CI pipelines, "
            "and respond to critical security incidents. "
            "You'll also mentor product engineers on secure coding practices. "
            "5+ years of AppSec experience with proficiency in Ruby or Go is required. "
            "Familiarity with Git internals, OAuth, and supply chain security is a strong plus."
        ),
        "highlights": [
            "Secure the platform used by 100M+ developers",
            "Threat modelling, bug bounty, SAST/DAST, incident response",
            "Fully remote — async-first engineering culture",
            "Microsoft parent benefits + GitHub equity",
        ],
        "tags": ["security", "AppSec", "threat modelling", "SAST", "bug bounty", "Ruby", "Go", "supply chain security"],
    },
    {
        "title": "Site Reliability Engineer",
        "company": "Shopify",
        "location": "Remote — Canada/US/EU",
        "work_arrangement": "remote",
        "job_type": "full-time",
        "salary_min": 145000, "salary_max": "190000", "currency": "USD",
        "description": (
            "Shopify's Production Engineering team is hiring an SRE to ensure the reliability of the infrastructure "
            "powering over 2 million merchants and Black Friday peaks of 50K+ orders per minute. "
            "You'll work on incident response, SLO definition and error budget management, "
            "capacity planning, and building automated toil-reduction tooling in Go. "
            "You'll participate in on-call (PagerDuty) and contribute to our blameless post-mortem culture. "
            "Strong Kubernetes, Terraform, and observability stack (Prometheus, Grafana, Jaeger) experience required."
        ),
        "highlights": [
            "Reliability for 2M+ merchants and 50K orders/min peaks",
            "SLOs, error budgets, incident response, on-call",
            "Fully remote across North America and Europe",
            "RSUs, flexible PTO, strong async culture",
        ],
        "tags": ["SRE", "reliability", "Kubernetes", "Terraform", "Prometheus", "Go", "on-call", "incident response"],
    },
    # ── Miscellaneous ──────────────────────────────────────────────────────────
    {
        "title": "Product Marketing Manager",
        "company": "Atlassian",
        "location": "Austin, TX",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 115000, "salary_max": 150000, "currency": "USD",
        "description": (
            "Atlassian is hiring a Product Marketing Manager for Jira Software to own positioning, "
            "messaging, and go-to-market for our core project tracking product. "
            "You'll craft the narrative for major feature launches, build competitive intelligence programmes, "
            "develop sales enablement materials, and run analyst relations for Gartner and Forrester evaluations. "
            "A deep understanding of developer and engineering personas is critical. "
            "3+ years of B2B SaaS PMM experience required. "
            "Experience marketing to technical buyers in DevOps or agile tooling is a strong plus."
        ),
        "highlights": [
            "Own positioning and GTM for Jira Software",
            "Launches, competitive intel, sales enablement, analyst relations",
            "Austin HQ, hybrid — Atlassian's fastest-growing office",
            "RSUs + ESPP in a $50B+ public company",
        ],
        "tags": ["product marketing", "PMM", "Jira", "B2B SaaS", "GTM", "competitive intelligence", "developer tools", "Austin"],
    },
    {
        "title": "Engineering Manager, Data Platform",
        "company": "Databricks",
        "location": "Amsterdam, Netherlands",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 120000, "salary_max": 165000, "currency": "EUR",
        "description": (
            "Databricks is looking for an Engineering Manager to lead a team of 6–8 engineers "
            "building the Data Ingestion services on the Databricks Lakehouse Platform. "
            "You'll own hiring, career development, sprint planning, architecture reviews, "
            "and delivery of a technical roadmap that processes exabytes of data. "
            "You'll stay close to the code — this is not a pure management role — "
            "and you'll collaborate across the EMEA and US engineering organisations. "
            "Prior EM experience managing distributed systems or data infrastructure teams is required. "
            "Strong Java or Scala background preferred."
        ),
        "highlights": [
            "Lead 6–8 engineers on Lakehouse data ingestion at exabyte scale",
            "Hands-on EM role — architecture and people development",
            "Amsterdam HQ, hybrid — EMEA + US collaboration",
            "Top EM pay + meaningful equity",
        ],
        "tags": ["engineering manager", "data platform", "Scala", "Java", "Spark", "distributed systems", "Amsterdam", "team lead"],
    },
    {
        "title": "Quantitative Analyst",
        "company": "Jane Street",
        "location": "London, UK",
        "work_arrangement": "onsite",
        "job_type": "full-time",
        "salary_min": 120000, "salary_max": 200000, "currency": "GBP",
        "description": (
            "Jane Street is a quantitative trading firm that uses cutting-edge research and technology "
            "to trade in markets around the world. We're looking for Quantitative Analysts "
            "to develop systematic trading strategies, build statistical models for price prediction, "
            "analyse large tick-data sets, and collaborate with technologists to implement strategies in production. "
            "Exceptional mathematical and statistical skills are essential. "
            "A PhD or strong master's in Mathematics, Statistics, Physics, or Computer Science is preferred. "
            "Programming ability in Python, R, or OCaml is required. No prior finance experience necessary."
        ),
        "highlights": [
            "Systematic trading strategy research and implementation",
            "Tick-data analysis, statistical modelling",
            "Onsite in London — highly collaborative quant community",
            "Industry-leading compensation with no ceiling on upside",
        ],
        "tags": ["quantitative analyst", "trading", "statistics", "Python", "OCaml", "financial modelling", "London", "quant finance"],
    },
    {
        "title": "Technical Program Manager",
        "company": "Meta",
        "location": "Menlo Park, CA",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 170000, "salary_max": 230000, "currency": "USD",
        "description": (
            "Meta is hiring a Technical Program Manager to drive cross-functional delivery of the Reality Labs "
            "mixed reality software platform. You'll coordinate engineering teams across hardware, OS, and applications, "
            "own the programme roadmap and dependency tracking, run weekly program reviews with VP-level stakeholders, "
            "and unblock teams by resolving technical and organisational ambiguities. "
            "5+ years of TPM experience on complex hardware/software programmes is required. "
            "Experience with embedded systems, XR, or consumer electronics programmes is a strong plus."
        ),
        "highlights": [
            "Drive Reality Labs mixed reality platform delivery",
            "VP-level stakeholder management across hardware and software",
            "Menlo Park HQ, hybrid",
            "Top Meta RSU package + comprehensive benefits",
        ],
        "tags": ["TPM", "technical program manager", "Reality Labs", "XR", "cross-functional", "hardware", "programme management"],
    },
    {
        "title": "Founding Engineer (Full-Stack)",
        "company": "Runway Financial",
        "location": "New York, NY",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 160000, "salary_max": 210000, "currency": "USD",
        "description": (
            "Runway Financial is a fast-growing Series B startup building the operating system for financial planning. "
            "As a Founding Engineer you'll be one of the first 10 engineers and will have outsized impact "
            "on product, architecture, and culture. "
            "You'll build full-stack features in React + Python/FastAPI, design our data model for complex financial scenarios, "
            "and establish engineering best practices. "
            "We're looking for someone with 5+ years experience who has shipped products end-to-end, "
            "is comfortable with ambiguity, and wants to be more than just a code contributor."
        ),
        "highlights": [
            "Founding engineer — shape product, architecture, and culture",
            "React + Python/FastAPI + PostgreSQL stack",
            "NYC office, hybrid — Series B with clear PMF",
            "Significant early-stage equity",
        ],
        "tags": ["full-stack", "founding engineer", "React", "FastAPI", "Python", "PostgreSQL", "startup", "fintech", "Series B"],
    },
]

# Validate: salary_max should be int not str
for jd in JDS:
    if isinstance(jd.get("salary_max"), str):
        jd["salary_max"] = int(jd["salary_max"])


async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    print(f"Importing {len(JDS)} JDs...")

    async with engine.begin() as conn:
        for i, jd in enumerate(JDS):
            embed_text = f"{jd['title']} {jd['company']} {jd['description']} {' '.join(jd['tags'])}"
            vector = embed(embed_text)

            import json
            await conn.execute(
                text("""
                    INSERT INTO job_descriptions
                        (title, company, location, work_arrangement, job_type,
                         salary_min, salary_max, currency, description,
                         highlights, tags, embedding)
                    VALUES
                        (:title, :company, :location, :wa, :jt,
                         :smin, :smax, :currency, :desc,
                         :highlights, :tags, :embedding)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "title":     jd["title"],
                    "company":   jd["company"],
                    "location":  jd["location"],
                    "wa":        jd["work_arrangement"],
                    "jt":        jd["job_type"],
                    "smin":      jd["salary_min"],
                    "smax":      jd["salary_max"],
                    "currency":  jd["currency"],
                    "desc":      jd["description"],
                    "highlights": json.dumps(jd["highlights"]),
                    "tags":      json.dumps(jd["tags"]),
                    "embedding": str(vector),
                }
            )
            print(f"  [{i+1}/{len(JDS)}] {jd['title']} @ {jd['company']}")

    print("Done.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
