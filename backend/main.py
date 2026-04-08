from llm_service import llm_client

if __name__ == "__main__":
    result = llm_client.evaluate_vacancy(
        resume_text="Skills: Python, Django, JavaScript",
        context="Looking for a first remote fulltime job. I have no experience yet",
        vacancy_description="""Тип вакансії
        Повна зайнятість
        &nbsp;
        Місцезнаходження
        Дистанційно
        &nbsp;
        Повний опис вакансії
        AI-native, all-in-one Transportation Management System (TMS) for modern trucking operations. The platform helps carriers, brokers, hybrid operators, private fleets, and enterprise teams manage the full workflow — from dispatch and delivery to invoicing and financial visibility — all in one place.

        The product is already operating at scale: used by 1,000+ companies, processing $1.9B+ in freight volume annually, with a very fast product iteration cycle (hundreds of product updates per year).

        The system is designed to integrate seamlessly with the broader trucking ecosystem, including ELDs, factoring, fuel and toll providers, payroll systems, email, load boards, BI/data tools, and more. It supports 160+ integrations, as well as APIs and webhooks for custom connectivity.

        Work environment: fast-growing startup, high ownership, tight feedback loops, and a strong expectation of end-to-end responsibility — from identifying problems to shipping real outcomes, not just completing tasks.

        The Role

        We need a Senior Backend Engineer who can architect scalable systems, write clean Python code, and move from idea to production fast. You'll have significant autonomy and impact.

        What You'll Do

        Design, build, and maintain backend services and APIs that power our platform
        Own features end-to-end: from system design to deployment to monitoring
        Make architectural decisions that balance speed with scalability
        Write clean, testable, maintainable code with proper documentation
        Collaborate with frontend engineers, product, and other stakeholders
        Participate in code reviews and mentor junior engineers
        Help shape our engineering culture and best practices
        What We're Looking For

        3+ years of backend development experience with Python as your primary language
        Strong experience with web frameworks (FastAPI, Django, Flask)
        Proficiency with databases (PostgreSQL, Redis, etc.) and data modeling
        Experience building and consuming RESTful APIs and/or GraphQL
        Comfortable with cloud platforms (AWS, GCP, or Azure)
        Understanding of system design, scalability, and performance optimization
        Experience with CI/CD, testing, and monitoring tools
        Bonus Points

        Experience with microservices architecture
        Background in distributed systems or data-intensive applications
        Contributions to open source projects
        Previous startup experience
        """,
    )

    print(result)
