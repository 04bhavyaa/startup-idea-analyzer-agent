#!/usr/bin/env python3

import asyncio
import os
import praw
import tweepy
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from collections import Counter
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent
import mcp.types as types
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

server = Server("social-trends")

class RedditAPI:
    """Wrapper for Reddit API using PRAW"""
    
    def __init__(self):
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent=os.getenv("REDDIT_USER_AGENT", "StartupAnalyzer/1.0")
            )
            # Test connection
            self.reddit.user.me()
        except Exception as e:
            print(f"Reddit API initialization failed: {e}")
            self.reddit = None
    
    def search_posts(self, query: str, subreddit: str = "all", limit: int = 100, time_filter: str = "month") -> List[Dict]:
        """Search Reddit posts for a given query"""
        if not self.reddit:
            return []
        
        try:
            posts = []
            subreddit_obj = self.reddit.subreddit(subreddit)
            
            # Search posts
            search_results = subreddit_obj.search(query, sort="relevance", time_filter=time_filter, limit=limit)
            
            for post in search_results:
                posts.append({
                    "id": post.id,
                    "title": post.title,
                    "text": post.selftext,
                    "score": post.score,
                    "upvote_ratio": post.upvote_ratio,
                    "num_comments": post.num_comments,
                    "created_utc": post.created_utc,
                    "subreddit": str(post.subreddit),
                    "url": f"https://reddit.com{post.permalink}"
                })
            
            return posts
        except Exception as e:
            print(f"Error searching Reddit posts: {e}")
            return []
    
    def get_subreddit_posts(self, subreddit_name: str, sort: str = "hot", limit: int = 50) -> List[Dict]:
        """Get posts from a specific subreddit"""
        if not self.reddit:
            return []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            if sort == "hot":
                post_list = subreddit.hot(limit=limit)
            elif sort == "new":
                post_list = subreddit.new(limit=limit)
            elif sort == "top":
                post_list = subreddit.top(time_filter="month", limit=limit)
            else:
                post_list = subreddit.hot(limit=limit)
            
            for post in post_list:
                posts.append({
                    "title": post.title,
                    "text": post.selftext,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "created_utc": post.created_utc
                })
            
            return posts
        except Exception as e:
            print(f"Error getting subreddit posts: {e}")
            return []

class TwitterAPI:
    """Wrapper for Twitter API v2 using tweepy"""
    
    def __init__(self):
        try:
            # Twitter API v2 with Bearer Token
            bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
            if bearer_token:
                self.client = tweepy.Client(bearer_token=bearer_token)
                # Test connection
                self.client.get_me()
            else:
                print("Twitter Bearer Token not found")
                self.client = None
        except Exception as e:
            print(f"Twitter API initialization failed: {e}")
            self.client = None
    
    def search_tweets(self, query: str, max_results: int = 100) -> List[Dict]:
        """Search recent tweets for a given query"""
        if not self.client:
            return []
        
        try:
            tweets = []
            
            # Search recent tweets (last 7 days for free tier)
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),  # API limit
                tweet_fields=["created_at", "public_metrics", "context_annotations", "lang"],
                user_fields=["verified", "public_metrics"]
            )
            
            if response.data:
                for tweet in response.data:
                    tweets.append({
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                        "public_metrics": tweet.public_metrics,
                        "lang": tweet.lang if hasattr(tweet, 'lang') else 'en'
                    })
            
            return tweets
        except Exception as e:
            print(f"Error searching tweets: {e}")
            return []

class SentimentAnalyzer:
    """Simple sentiment analysis utility"""
    
    @staticmethod
    def analyze_sentiment(text: str) -> Dict[str, float]:
        """Basic sentiment analysis using keyword matching"""
        positive_words = [
            "good", "great", "excellent", "amazing", "awesome", "love", "like", 
            "best", "fantastic", "wonderful", "perfect", "brilliant", "outstanding",
            "impressive", "innovative", "revolutionary", "helpful", "useful"
        ]
        
        negative_words = [
            "bad", "terrible", "awful", "hate", "horrible", "worst", "sucks",
            "disappointing", "useless", "broken", "failed", "problem", "issue",
            "expensive", "overpriced", "scam", "fake", "poor", "lacking"
        ]
        
        neutral_words = [
            "okay", "average", "normal", "standard", "typical", "decent",
            "fair", "reasonable", "moderate", "acceptable"
        ]
        
        text_lower = text.lower()
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        neu_count = sum(1 for word in neutral_words if word in text_lower)
        
        total = pos_count + neg_count + neu_count
        if total == 0:
            return {"positive": 0.33, "negative": 0.33, "neutral": 0.34}
        
        return {
            "positive": pos_count / total,
            "negative": neg_count / total, 
            "neutral": neu_count / total
        }


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """
    List available tools for social media analysis.
    """
    return [
        Tool(
            name="analyze_trends",
            description="Analyze social media trends and sentiment for a topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic or keyword to analyze"
                    },
                    "platforms": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["reddit", "twitter", "both"]
                        },
                        "description": "Social media platforms to analyze",
                        "default": ["both"]
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Time period for analysis",
                        "enum": ["day", "week", "month", "year"],
                        "default": "month"
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="reddit_analysis",
            description="Deep analysis of Reddit discussions on a topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Reddit"
                    },
                    "subreddits": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific subreddits to search (optional)",
                        "default": ["all"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of posts to analyze",
                        "default": 100,
                        "minimum": 10,
                        "maximum": 500
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="twitter_sentiment",
            description="Analyze Twitter sentiment and engagement for a topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Twitter"
                    },
                    "max_tweets": {
                        "type": "integer",
                        "description": "Maximum number of tweets to analyze",
                        "default": 100,
                        "minimum": 10,
                        "maximum": 100
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Handle tool calls for social media analysis.
    """
    if name == "analyze_trends":
        return await handle_analyze_trends(arguments)
    elif name == "reddit_analysis":
        return await handle_reddit_analysis(arguments)
    elif name == "twitter_sentiment":
        return await handle_twitter_sentiment(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_analyze_trends(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Analyze trends across multiple social media platforms.
    """
    try:
        topic = arguments.get("topic", "")
        platforms = arguments.get("platforms", ["both"])
        time_period = arguments.get("time_period", "month")
        
        analysis_result = f"Social Media Trends Analysis for '{topic}':\n\n"
        
        reddit_api = RedditAPI()
        twitter_api = TwitterAPI()
        sentiment_analyzer = SentimentAnalyzer()
        
        # Reddit Analysis
        if "reddit" in platforms or "both" in platforms:
            if reddit_api.reddit:
                analysis_result += "🔴 Reddit Analysis:\n"
                
                # Search across relevant subreddits
                reddit_posts = reddit_api.search_posts(topic, limit=50, time_filter=time_period)
                
                if reddit_posts:
                    # Analyze sentiment
                    all_text = " ".join([post["title"] + " " + post["text"] for post in reddit_posts])
                    sentiment = sentiment_analyzer.analyze_sentiment(all_text)
                    
                    # Calculate engagement metrics
                    avg_score = sum(post["score"] for post in reddit_posts) / len(reddit_posts)
                    avg_comments = sum(post["num_comments"] for post in reddit_posts) / len(reddit_posts)
                    
                    # Top subreddits
                    subreddits = [post["subreddit"] for post in reddit_posts]
                    top_subreddits = Counter(subreddits).most_common(5)
                    
                    analysis_result += f"- Posts Analyzed: {len(reddit_posts)}\n"
                    analysis_result += f"- Average Score: {avg_score:.1f}\n"
                    analysis_result += f"- Average Comments: {avg_comments:.1f}\n"
                    analysis_result += f"- Sentiment - Positive: {sentiment['positive']:.1%}, Negative: {sentiment['negative']:.1%}, Neutral: {sentiment['neutral']:.1%}\n"
                    analysis_result += f"- Top Subreddits: {', '.join([f'r/{sub}({count})' for sub, count in top_subreddits])}\n\n"
                    
                    # Top discussions
                    top_posts = sorted(reddit_posts, key=lambda x: x["score"], reverse=True)[:3]
                    analysis_result += "Top Discussions:\n"
                    for i, post in enumerate(top_posts, 1):
                        analysis_result += f"{i}. {post['title'][:80]}... (Score: {post['score']}, Comments: {post['num_comments']})\n"
                    analysis_result += "\n"
                else:
                    analysis_result += "- No Reddit posts found for this topic\n\n"
            else:
                analysis_result += "- Reddit API not available\n\n"
        
        # Twitter Analysis
        if "twitter" in platforms or "both" in platforms:
            if twitter_api.client:
                analysis_result += "🐦 Twitter Analysis:\n"
                
                tweets = twitter_api.search_tweets(topic, max_results=100)
                
                if tweets:
                    # Analyze sentiment
                    all_tweets_text = " ".join([tweet["text"] for tweet in tweets])
                    sentiment = sentiment_analyzer.analyze_sentiment(all_tweets_text)
                    
                    # Calculate engagement metrics
                    total_likes = sum(tweet["public_metrics"]["like_count"] for tweet in tweets if tweet["public_metrics"])
                    total_retweets = sum(tweet["public_metrics"]["retweet_count"] for tweet in tweets if tweet["public_metrics"])
                    total_replies = sum(tweet["public_metrics"]["reply_count"] for tweet in tweets if tweet["public_metrics"])
                    
                    avg_engagement = (total_likes + total_retweets + total_replies) / len(tweets) if tweets else 0
                    
                    analysis_result += f"- Tweets Analyzed: {len(tweets)}\n"
                    analysis_result += f"- Total Likes: {total_likes:,}\n"
                    analysis_result += f"- Total Retweets: {total_retweets:,}\n"
                    analysis_result += f"- Average Engagement: {avg_engagement:.1f}\n"
                    analysis_result += f"- Sentiment - Positive: {sentiment['positive']:.1%}, Negative: {sentiment['negative']:.1%}, Neutral: {sentiment['neutral']:.1%}\n\n"
                    
                    # Top tweets
                    top_tweets = sorted(tweets, key=lambda x: x["public_metrics"]["like_count"] if x["public_metrics"] else 0, reverse=True)[:3]
                    analysis_result += "Top Tweets:\n"
                    for i, tweet in enumerate(top_tweets, 1):
                        likes = tweet["public_metrics"]["like_count"] if tweet["public_metrics"] else 0
                        analysis_result += f"{i}. {tweet['text'][:100]}... (Likes: {likes})\n"
                    analysis_result += "\n"
                else:
                    analysis_result += "- No tweets found for this topic\n\n"
            else:
                analysis_result += "- Twitter API not available\n\n"
        
        # Overall Assessment
        analysis_result += "📊 Overall Social Media Assessment:\n"
        analysis_result += f"- Topic: '{topic}' shows {'high' if len(reddit_posts) > 20 or len(tweets) > 50 else 'moderate' if len(reddit_posts) > 5 or len(tweets) > 20 else 'low'} social media activity\n"
        analysis_result += f"- Time Period: {time_period}\n"
        analysis_result += f"- Platforms Analyzed: {', '.join(platforms)}\n"
        
        return [types.TextContent(type="text", text=analysis_result)]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error analyzing social media trends: {str(e)}"
        )]


async def handle_reddit_analysis(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Deep analysis of Reddit discussions on a specific topic.
    """
    try:
        query = arguments.get("query", "")
        subreddits = arguments.get("subreddits", ["all"])
        limit = arguments.get("limit", 100)
        
        reddit_api = RedditAPI()
        sentiment_analyzer = SentimentAnalyzer()
        
        if not reddit_api.reddit:
            return [types.TextContent(
                type="text",
                text="Reddit API not available. Please check your credentials."
            )]
        
        analysis_result = f"Deep Reddit Analysis for '{query}':\n\n"
        
        all_posts = []
        
        # Search in specified subreddits
        for subreddit in subreddits:
            posts = reddit_api.search_posts(query, subreddit=subreddit, limit=limit//len(subreddits))
            all_posts.extend(posts)
        
        if not all_posts:
            return [types.TextContent(
                type="text", 
                text=f"No Reddit posts found for query: {query}"
            )]
        
        # Sentiment Analysis
        all_text = " ".join([post["title"] + " " + post["text"] for post in all_posts])
        sentiment = sentiment_analyzer.analyze_sentiment(all_text)
        
        # Engagement Analysis
        total_score = sum(post["score"] for post in all_posts)
        total_comments = sum(post["num_comments"] for post in all_posts)
        avg_upvote_ratio = sum(post["upvote_ratio"] for post in all_posts) / len(all_posts)
        
        analysis_result += f"📈 Engagement Metrics:\n"
        analysis_result += f"- Total Posts: {len(all_posts)}\n"
        analysis_result += f"- Total Upvotes: {total_score:,}\n"
        analysis_result += f"- Total Comments: {total_comments:,}\n"
        analysis_result += f"- Average Upvote Ratio: {avg_upvote_ratio:.1%}\n"
        analysis_result += f"- Average Score per Post: {total_score/len(all_posts):.1f}\n\n"
        
        # Sentiment Breakdown
        analysis_result += f"😊 Sentiment Analysis:\n"
        analysis_result += f"- Positive: {sentiment['positive']:.1%}\n"
        analysis_result += f"- Negative: {sentiment['negative']:.1%}\n"
        analysis_result += f"- Neutral: {sentiment['neutral']:.1%}\n\n"
        
        # Subreddit Distribution
        subreddit_dist = Counter([post["subreddit"] for post in all_posts])
        analysis_result += f"📍 Subreddit Distribution:\n"
        for subreddit, count in subreddit_dist.most_common(10):
            analysis_result += f"- r/{subreddit}: {count} posts\n"
        analysis_result += "\n"
        
        # Top Posts
        top_posts = sorted(all_posts, key=lambda x: x["score"], reverse=True)[:5]
        analysis_result += f"🔥 Top Posts by Score:\n"
        for i, post in enumerate(top_posts, 1):
            analysis_result += f"{i}. {post['title'][:100]}...\n"
            analysis_result += f"   Score: {post['score']}, Comments: {post['num_comments']}, Subreddit: r/{post['subreddit']}\n\n"
        
        # Common Keywords
        all_titles = " ".join([post["title"] for post in all_posts])
        words = re.findall(r'\b\w+\b', all_titles.lower())
        common_words = Counter([word for word in words if len(word) > 3])
        
        analysis_result += f"🔑 Common Keywords:\n"
        for word, count in common_words.most_common(10):
            analysis_result += f"- {word}: {count} mentions\n"
        
        return [types.TextContent(type="text", text=analysis_result)]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error in Reddit analysis: {str(e)}"
        )]


async def handle_twitter_sentiment(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Analyze Twitter sentiment and engagement for a specific topic.
    """
    try:
        query = arguments.get("query", "")
        max_tweets = arguments.get("max_tweets", 100)
        
        twitter_api = TwitterAPI()
        sentiment_analyzer = SentimentAnalyzer()
        
        if not twitter_api.client:
            return [types.TextContent(
                type="text",
                text="Twitter API not available. Please check your Bearer Token."
            )]
        
        analysis_result = f"Twitter Sentiment Analysis for '{query}':\n\n"
        
        tweets = twitter_api.search_tweets(query, max_results=max_tweets)
        
        if not tweets:
            return [types.TextContent(
                type="text",
                text=f"No tweets found for query: {query}"
            )]
        
        # Sentiment Analysis
        all_tweets_text = " ".join([tweet["text"] for tweet in tweets])
        sentiment = sentiment_analyzer.analyze_sentiment(all_tweets_text)
        
        # Engagement Metrics
        total_likes = sum(tweet["public_metrics"]["like_count"] for tweet in tweets if tweet.get("public_metrics"))
        total_retweets = sum(tweet["public_metrics"]["retweet_count"] for tweet in tweets if tweet.get("public_metrics"))
        total_replies = sum(tweet["public_metrics"]["reply_count"] for tweet in tweets if tweet.get("public_metrics"))
        total_quotes = sum(tweet["public_metrics"]["quote_count"] for tweet in tweets if tweet.get("public_metrics"))
        
        analysis_result += f"📊 Engagement Overview:\n"
        analysis_result += f"- Tweets Analyzed: {len(tweets)}\n"
        analysis_result += f"- Total Likes: {total_likes:,}\n"
        analysis_result += f"- Total Retweets: {total_retweets:,}\n"
        analysis_result += f"- Total Replies: {total_replies:,}\n"
        analysis_result += f"- Total Quotes: {total_quotes:,}\n"
        analysis_result += f"- Average Engagement per Tweet: {(total_likes + total_retweets + total_replies)/len(tweets):.1f}\n\n"
        
        # Sentiment Breakdown
        analysis_result += f"😊 Sentiment Distribution:\n"
        analysis_result += f"- Positive: {sentiment['positive']:.1%}\n"
        analysis_result += f"- Negative: {sentiment['negative']:.1%}\n"
        analysis_result += f"- Neutral: {sentiment['neutral']:.1%}\n\n"
        
        # Language Distribution
        languages = Counter([tweet.get("lang", "unknown") for tweet in tweets])
        analysis_result += f"🌍 Language Distribution:\n"
        for lang, count in languages.most_common(5):
            analysis_result += f"- {lang}: {count} tweets\n"
        analysis_result += "\n"
        
        # Top Performing Tweets
        top_tweets = sorted(tweets, key=lambda x: x.get("public_metrics", {}).get("like_count", 0), reverse=True)[:5]
        analysis_result += f"🔥 Top Performing Tweets:\n"
        for i, tweet in enumerate(top_tweets, 1):
            metrics = tweet.get("public_metrics", {})
            likes = metrics.get("like_count", 0)
            retweets = metrics.get("retweet_count", 0)
            
            analysis_result += f"{i}. {tweet['text'][:120]}...\n"
            analysis_result += f"   Likes: {likes}, Retweets: {retweets}\n\n"
        
        # Engagement Quality Assessment
        high_engagement = sum(1 for tweet in tweets if tweet.get("public_metrics", {}).get("like_count", 0) > 10)
        engagement_rate = high_engagement / len(tweets) if tweets else 0
        
        analysis_result += f"📈 Engagement Quality:\n"
        analysis_result += f"- High Engagement Tweets (>10 likes): {high_engagement}\n"
        analysis_result += f"- Engagement Rate: {engagement_rate:.1%}\n"
        analysis_result += f"- Quality Assessment: {'High' if engagement_rate > 0.3 else 'Medium' if engagement_rate > 0.1 else 'Low'}\n"
        
        return [types.TextContent(type="text", text=analysis_result)]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error in Twitter sentiment analysis: {str(e)}"
        )]


async def main():
    """
    Main function to run the Social Trends MCP server.
    """
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="social-trends",
                server_version="0.1.0", 
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())