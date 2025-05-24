from crewai import Agent, Task, Crew, Process
from tools.db_tools import insert_products_tool, insert_affiliate_stores_tool
from tools.product_scraper_tool import scrape_store_products
from utils.MyLLM import MyLLM


class ProductDiscoveryCrew:

    def run_full_discovery(self, inputs: dict):
        # Definindo agentes
        db_agent = Agent(
            role="Database Inserter",
            goal="Insert validated affiliate stores and products into the system",
            backstory="You specialize in structured data persistence and work with schemas for affiliate marketing.",
            verbose=True,
            tools=[insert_affiliate_stores_tool, insert_products_tool ],
            llm=MyLLM.GTP4o_mini
        )

        analyst = Agent(
            role="Product Trend Analyst",
            goal="Discover the most searched products in the {nicho} niche during {periodo}",
            backstory="You analyze trending product data from the web to surface the most desired items in specific markets.",
            verbose=True,
            llm=MyLLM.GTP4o_mini
        )

        scraper = Agent(
            role="E-commerce Scraper",
            goal="Scrape products related to trending searches from approved affiliate stores",
            backstory="You use automated tools to fetch product details from e-commerce websites based on search queries.",
            tools=[scrape_store_products],
            verbose=True,
            llm=MyLLM.GTP4o_mini
        )

        # Definindo tarefas
        insert_stores_task = Task(
            description="Insert the curated affiliate stores using the AffiliateStoreCreate schema.",
            expected_output="Confirmation of store insertion with database IDs.",
            agent=db_agent
        )

        find_trending_products_task = Task(
            description="Analyze recent trends and identify the top 5 most searched products within the {nicho} niche during {periodo}.",
            expected_output="A list of product names with highest search interest.",
            agent=analyst
        )

        scrape_products_task = Task(
            description="Use the trending product names to scrape up to 100 relevant items from each store in the database.",
            expected_output="Dictionary with store names as keys and up to 100 products per store in ProductCreate format.",
            agent=scraper
        )

        insert_products_task = Task(
            description="Insert the scraped product data into the database using the ProductCreate schema.",
            expected_output="Confirmation of how many products were inserted per store.",
            agent=db_agent
        )

        # Criando e executando a Crew
        crew = Crew(
            agents=[db_agent, analyst, scraper],
            tasks=[
                insert_stores_task,
                find_trending_products_task,
                scrape_products_task,
                insert_products_task
            ],
            process=Process.sequential,
            verbose=True
        )

        return crew.kickoff(inputs=inputs)
