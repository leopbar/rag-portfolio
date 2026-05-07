#!/usr/bin/env python3
"""
Automated RAG System Tester

Usage:
    python scripts/test_rag_system.py --queries-file ../test_queries.json
    python scripts/test_rag_system.py --query "O que é divisão do trabalho?"
    python scripts/test_rag_system.py --interactive
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from argparse import ArgumentParser

import httpx


class RAGTester:
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.client = httpx.AsyncClient()
        self.results = []

    async def test_query(self, query_id: str, question: str) -> dict:
        """Test a single query against the RAG system."""
        print(f"\n📝 Testing {query_id}: {question[:60]}...")

        try:
            # Call backend /chat endpoint
            response = await self.client.post(
                f"{self.backend_url}/chat",
                json={"query": question},
                timeout=30.0,
            )

            if response.status_code != 200:
                return {
                    "query_id": query_id,
                    "question": question,
                    "status": "FAILED",
                    "error": f"HTTP {response.status_code}",
                    "response": None,
                    "sources": None,
                }

            # Parse streaming SSE response
            full_response = ""
            sources = []

            for line in response.text.split("\n"):
                if line.startswith("data:"):
                    data = line[5:].strip()
                    if data.startswith("[SOURCES]"):
                        # Parse sources JSON
                        try:
                            sources_json = data.replace("[SOURCES]", "").strip()
                            sources = json.loads(sources_json)
                        except json.JSONDecodeError:
                            pass
                    else:
                        # Accumulate response tokens
                        full_response += data

            return {
                "query_id": query_id,
                "question": question,
                "status": "SUCCESS",
                "response": full_response[:500],  # First 500 chars
                "sources": sources,
                "num_sources": len(sources) if sources else 0,
            }

        except Exception as e:
            return {
                "query_id": query_id,
                "question": question,
                "status": "ERROR",
                "error": str(e),
                "response": None,
                "sources": None,
            }

    async def test_suite(self, queries_file: str) -> list:
        """Test all queries from a JSON suite."""
        queries_path = Path(queries_file)
        if not queries_path.exists():
            print(f"❌ File not found: {queries_file}")
            return []

        with open(queries_path) as f:
            suite = json.load(f)

        all_queries = []
        categories = suite.get("evaluation_suite", {}).get("categories", {})

        print(f"\n🚀 Starting RAG System Test Suite")
        print(f"📊 Backend URL: {self.backend_url}")
        print(f"⏰ Started at: {datetime.now().isoformat()}")

        for category_name, category_data in categories.items():
            queries = category_data.get("queries", [])
            print(f"\n📂 Category: {category_name} ({len(queries)} queries)")

            for query_data in queries:
                result = await self.test_query(
                    query_data["id"],
                    query_data["question"],
                )
                self.results.append({**result, "category": category_name})
                all_queries.append(result)

                # Print status inline
                status_emoji = "✅" if result["status"] == "SUCCESS" else "❌"
                print(f"  {status_emoji} {result['query_id']}: {result['status']}")
                if result.get("num_sources"):
                    print(f"     Sources found: {result['num_sources']}")

        return all_queries

    def generate_report(self, output_file: str = "test_results.json") -> None:
        """Generate a JSON report of test results."""
        total = len(self.results)
        successes = sum(1 for r in self.results if r["status"] == "SUCCESS")
        hallucinations = sum(1 for r in self.results if r.get("should_hallucinate") == False)

        report = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_queries": total,
                "successful": successes,
                "success_rate": f"{100 * successes / total:.1f}%" if total > 0 else "N/A",
            },
            "results": self.results,
            "summary_by_category": self._summarize_by_category(),
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📊 Report saved to: {output_file}")

    def _summarize_by_category(self) -> dict:
        """Summarize results by category."""
        summary = {}
        for result in self.results:
            category = result.get("category", "unknown")
            if category not in summary:
                summary[category] = {"total": 0, "success": 0, "sources_avg": 0}

            summary[category]["total"] += 1
            if result["status"] == "SUCCESS":
                summary[category]["success"] += 1
            if result.get("num_sources"):
                summary[category]["sources_avg"] = (
                    summary[category].get("sources_avg", 0) + result["num_sources"]
                ) / 2

        return summary

    def print_summary(self) -> None:
        """Print test summary to console."""
        total = len(self.results)
        successes = sum(1 for r in self.results if r["status"] == "SUCCESS")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")

        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Queries:  {total}")
        print(f"Successful:     {successes} ✅ ({100*successes/total:.1f}%)")
        print(f"Errors:         {errors} ❌")
        print(f"Completed at:   {datetime.now().isoformat()}")
        print("=" * 60)

        # Category breakdown
        summary = self._summarize_by_category()
        print("\nBy Category:")
        for category, stats in summary.items():
            rate = 100 * stats["success"] / stats["total"]
            print(f"  {category}: {stats['success']}/{stats['total']} ({rate:.0f}%)")

        print("\n💾 Full report: test_results.json")

    async def close(self):
        """Clean up HTTP client."""
        await self.client.aclose()


async def main():
    parser = ArgumentParser(description="Test RAG system")
    parser.add_argument(
        "--queries-file",
        help="Path to test_queries.json",
    )
    parser.add_argument(
        "--query",
        help="Test a single query",
    )
    parser.add_argument(
        "--backend-url",
        default="http://localhost:8000",
        help="Backend URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--output",
        default="test_results.json",
        help="Output report file (default: test_results.json)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode (ask user for queries)",
    )

    args = parser.parse_args()
    tester = RAGTester(backend_url=args.backend_url)

    try:
        if args.query:
            # Single query mode
            result = await tester.test_query("MANUAL", args.query)
            tester.results.append(result)
            print(f"\n✅ Response:\n{result['response'][:300]}")
            if result.get("sources"):
                print(f"\nSources: {len(result['sources'])} found")

        elif args.queries_file:
            # Suite mode
            await tester.test_suite(args.queries_file)
            tester.generate_report(args.output)
            tester.print_summary()

        elif args.interactive:
            # Interactive mode
            print("🎯 Interactive Mode - Press Ctrl+C to exit\n")
            while True:
                query = input("Enter query: ").strip()
                if not query:
                    continue
                result = await tester.test_query("INTERACTIVE", query)
                print(f"\n✅ Response (first 300 chars):\n{result['response'][:300]}")
                if result.get("sources"):
                    print(f"\n📚 Sources ({len(result['sources'])} found):")
                    for src in result["sources"][:3]:
                        print(f"  - {src.get('book', '?')} {src.get('chapter', '?')}")
                print()

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
