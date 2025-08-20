#!/usr/bin/env python3
"""
Test script for the Quran RAG system.
Run this before starting the Telegram bot to ensure everything works correctly.
"""

import json
import os
from dotenv import load_dotenv
from minsearch import AppendableIndex
from openai import OpenAI

def test_rag_system():
    """Test the RAG system components"""
    print("🧪 Testing Quran RAG System...")
    
    # Test 1: Load data
    print("\n1️⃣ Testing data loading...")
    try:
        with open("quran_with_tafsir.json", "r", encoding="utf-8") as f:
            documents = json.load(f)
        print(f"✅ Successfully loaded {len(documents)} documents")
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return False
    
    # Test 2: Initialize search index
    print("\n2️⃣ Testing search index...")
    try:
        index = AppendableIndex(
            text_fields=["question", "text", "section"],
            keyword_fields=["surah_number", "surah_name", "surah_translation", "ayah_number", "reference", "text", "language", "tafsir_text", "tafsir_source"]
        )
        index.fit(documents)
        print("✅ Search index initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize search index: {e}")
        return False
    
    # Test 3: Test search functionality
    print("\n3️⃣ Testing search functionality...")
    try:
        test_query = "patience"
        results = index.search(
            query=test_query,
            boost_dict={'question': 3.0, 'section': 0.5},
            num_results=3,
            output_ids=True
        )
        print(f"✅ Search returned {len(results)} results for query: '{test_query}'")
        if results:
            print(f"   First result: {results[0].get('surah_name', 'N/A')} {results[0].get('reference', 'N/A')}")
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False
    
    # Test 4: Test OpenAI connection
    print("\n4️⃣ Testing OpenAI connection...")
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("   Please create a .env file with your OpenAI API key")
        return False
    
    try:
        client = OpenAI(api_key=api_key)
        # Test with a simple prompt
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{"role": "user", "content": "Say 'Hello' in one word."}],
            max_tokens=10
        )
        print("✅ OpenAI API connection successful")
        print(f"   Test response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False
    
    # Test 5: Test full RAG pipeline
    print("\n5️⃣ Testing full RAG pipeline...")
    try:
        # Build a simple prompt
        prompt_template = """
Answer this question about the Quran in one sentence: {question}

Use this context: {context}
"""
        
        context = ""
        for doc in results[:2]:  # Use first 2 results
            context += f"{doc.get('surah_name', '')} {doc.get('reference', '')}: {doc.get('text', '')[:100]}...\n"
        
        prompt = prompt_template.format(question=test_query, context=context)
        
        # Get LLM response
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        
        answer = response.choices[0].message.content
        print("✅ Full RAG pipeline successful")
        print(f"   Question: '{test_query}'")
        print(f"   Answer: {answer}")
        
    except Exception as e:
        print(f"❌ Full RAG pipeline failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Your RAG system is ready to use.")
    return True

def main():
    """Main function"""
    print("=" * 50)
    print("🧪 Quran RAG System Test Suite")
    print("=" * 50)
    
    success = test_rag_system()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! You can now run the Telegram bot.")
        print("   Run: python quran_bot.py")
    else:
        print("❌ Some tests failed. Please fix the issues before running the bot.")
    print("=" * 50)

if __name__ == "__main__":
    main()
