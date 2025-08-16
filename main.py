#!/usr/bin/env python3

from dotenv import load_dotenv
from src.workflow import StartupWorkflow
from datetime import datetime
import os

load_dotenv()

def validate_environment():
    """Validate that all required environment variables are set"""
    required_vars = [
        'GOOGLE_API_KEY',
        'SERP_API_KEY'
    ]
    
    optional_vars = [
        'POLYGON_API_KEY',
        'REDDIT_CLIENT_ID', 
        'REDDIT_CLIENT_SECRET',
        'TWITTER_BEARER_TOKEN'
    ]
    
    missing_required = [var for var in required_vars if not os.getenv(var)]
    missing_optional = [var for var in optional_vars if not os.getenv(var)]
    
    if missing_required:
        print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        print("Please check your .env file")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing optional environment variables: {', '.join(missing_optional)}")
        print("Some features may not work properly")
    
    return True


def print_startup_analysis(result):
    """Pretty print the startup analysis results"""
    print("\n" + "="*80)
    print(f"STARTUP ANALYSIS RESULTS")
    print("="*80)
    
    if result.startup_idea:
        idea = result.startup_idea
        print(f"\n💡 STARTUP IDEA: {idea.name}")
        print(f"Description: {idea.description or 'Auto-generated from query'}")
        
        if idea.category:
            print(f"Category: {idea.category}")
        
        if idea.business_model:
            print(f"Business Model: {idea.business_model}")
        
        # Market Analysis
        if idea.market_analysis:
            market = idea.market_analysis
            print(f"\n📊 MARKET ANALYSIS:")
            print(f"Market Size: {market.market_size or 'Unknown'}")
            print(f"Growth Rate: {market.growth_rate or 'Unknown'}")
            
            if market.target_audience:
                print(f"Target Audience: {', '.join(market.target_audience)}")
            
            if market.market_trends:
                print(f"Market Trends: {', '.join(market.market_trends)}")
            
            if market.barriers_to_entry:
                print(f"Barriers to Entry: {', '.join(market.barriers_to_entry)}")
        
        # Competitor Analysis
        if idea.competitors:
            print(f"\n🏢 COMPETITOR ANALYSIS:")
            print(f"Found {len(idea.competitors)} main competitors:")
            
            for i, comp in enumerate(idea.competitors[:5], 1):
                print(f"\n{i}. {comp.name}")
                print(f"   Website: {comp.website}")
                print(f"   Business Model: {comp.business_model or 'Unknown'}")
                print(f"   Funding Stage: {comp.funding_stage or 'Unknown'}")
                
                if comp.key_features:
                    print(f"   Key Features: {', '.join(comp.key_features[:3])}")
                
                if comp.strengths:
                    print(f"   Strengths: {', '.join(comp.strengths[:2])}")
        
        # Startup Analysis
        if idea.startup_analysis:
            analysis = idea.startup_analysis
            print(f"\n🎯 VIABILITY ASSESSMENT:")
            print(f"Viability Score: {analysis.viability_score or 'N/A'}/10")
            print(f"Market Opportunity: {analysis.market_opportunity or 'Not assessed'}")
            print(f"Time to Market: {analysis.time_to_market or 'Unknown'}")
            print(f"Risk Assessment: {analysis.risk_assessment or 'Not assessed'}")
            
            if analysis.competitive_advantage:
                print(f"Competitive Advantages: {', '.join(analysis.competitive_advantage)}")
            
            if analysis.potential_challenges:
                print(f"Potential Challenges: {', '.join(analysis.potential_challenges)}")
            
            if analysis.monetization_strategies:
                print(f"Monetization Strategies: {', '.join(analysis.monetization_strategies)}")
    
    # Final Analysis & Recommendations
    if result.final_analysis:
        print(f"\n📋 FINAL RECOMMENDATIONS:")
        print("-" * 50)
        print(result.final_analysis)
    
    if result.recommendations:
        print(f"\n✅ KEY TAKEAWAYS:")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"{i}. {rec}")
    
    print("\n" + "="*80)

async def main():
    if not validate_environment():
        return 
    """Main function to run the startup analysis workflow"""
    print("🚀 STARTUP IDEA ANALYZER")
    print("Powered by AI-driven market research and competitor analysis")
    print("-" * 60)
    
    # Initialize the workflow
    try:
        workflow = StartupWorkflow()
        print("✅ Workflow initialized successfully")
        print("✅ MCP tool servers connected")
    except Exception as e:
        print(f"❌ Error initializing workflow: {e}")
        print("Make sure your API keys are set in the .env file and MCP servers are running")
        return
    
    while True:
        try:
            # Get startup idea from user
            print("\n" + "="*60)
            startup_idea = input("💡 Enter your startup idea (or 'quit' to exit): ").strip()
            
            if startup_idea.lower() in {"quit", "exit", "q"}:
                print("👋 Thanks for using Startup Idea Analyzer!")
                break
            
            if not startup_idea:
                print("❌ Please enter a valid startup idea")
                continue
            
            print(f"\n🔍 Analyzing startup idea: '{startup_idea}'")
            print("This may take a few minutes as we gather market data...")
            print("-" * 60)
            
            # Run the analysis workflow
            result = await workflow.run(startup_idea)
            
            # Display results
            print_startup_analysis(result)
            
            # Ask if user wants to save results
            save_option = input("\n💾 Save results to file? (y/n): ").strip().lower()
            if save_option == 'y':
                filename = f"startup_analysis_{startup_idea.replace(' ', '_')[:30]}.txt"
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Startup Analysis Report\n")
                        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Idea: {startup_idea}\n")
                        f.write("="*80 + "\n\n")
                        
                        if result.final_analysis:
                            f.write("FINAL ANALYSIS:\n")
                            f.write(result.final_analysis)
                            f.write("\n\n")
                        
                        if result.recommendations:
                            f.write("RECOMMENDATIONS:\n")
                            for i, rec in enumerate(result.recommendations, 1):
                                f.write(f"{i}. {rec}\n")
                    
                    print(f"✅ Results saved to: {filename}")
                except Exception as e:
                    print(f"❌ Error saving file: {e}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Analysis interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            print("Please try again with a different startup idea.")


async def run_single_analysis(idea: str):
    """Run analysis for a single idea (useful for API/web integration)"""
    workflow = StartupWorkflow()
    return await workflow.run(idea)


if __name__ == "__main__":
    from datetime import datetime
    import asyncio
    asyncio.run(main())