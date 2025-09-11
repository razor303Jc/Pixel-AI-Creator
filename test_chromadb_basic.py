"""
Simple ChromaDB connectivity test.
"""

import chromadb
import sys
import os


def test_chromadb_basic():
    """Test basic ChromaDB connection."""

    print("🧪 Testing ChromaDB Basic Connection")
    print("=" * 50)

    # Test 1: Basic connection
    print("1. Testing ChromaDB connection...")
    try:
        client = chromadb.HttpClient(host="localhost", port=8003)
        print("   ✅ ChromaDB client created successfully")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

    # Test 2: List collections
    print("\n2. Testing collection listing...")
    try:
        collections = client.list_collections()
        print(f"   ✅ Found {len(collections)} collections")
        for col in collections:
            print(f"      - {col.name}")
    except Exception as e:
        print(f"   ❌ Collection listing failed: {e}")
        return False

    # Test 3: Create test collection
    print("\n3. Testing collection creation...")
    try:
        test_collection_name = "test_pixel_collection"

        # Try to delete if exists
        try:
            client.delete_collection(name=test_collection_name)
            print("   ℹ️  Cleaned up existing test collection")
        except:
            pass

        # Create new collection
        collection = client.create_collection(name=test_collection_name)
        print(f"   ✅ Created collection: {collection.name}")

        # Test adding some data
        collection.add(
            documents=["This is a test document", "This is another test"],
            ids=["doc1", "doc2"],
            metadatas=[{"source": "test"}, {"source": "test"}],
        )
        print("   ✅ Added test documents to collection")

        # Test counting
        count = collection.count()
        print(f"   ✅ Collection contains {count} documents")

        # Clean up
        client.delete_collection(name=test_collection_name)
        print("   ✅ Cleaned up test collection")

    except Exception as e:
        print(f"   ❌ Collection operations failed: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 ChromaDB Basic Test Complete!")
    print("\nChromaDB is working correctly and ready for integration!")

    return True


if __name__ == "__main__":
    success = test_chromadb_basic()

    if success:
        print("\n✅ ChromaDB is ready for the Pixel-AI-Creator integration!")
        exit(0)
    else:
        print("\n❌ ChromaDB test failed. Please check the setup.")
        exit(1)
