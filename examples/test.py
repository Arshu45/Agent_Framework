import requests

CATEGORIES = [
    "smartphones",
    "laptops"
]

BASE_URL = "https://dummyjson.com/products/category"


def test_electronics_api():
    print("Testing DummyJSON Electronics APIs...\n")

    all_products = []

    for category in CATEGORIES:
        url = f"{BASE_URL}/{category}"
        print(f"GET {url}")

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()
            products = data.get("products", [])

            assert isinstance(products, list), "Products is not a list"
            assert len(products) > 0, f"No products returned for category: {category}"

            print(f"✅ {category}: {len(products)} products retrieved\n")
            all_products.extend(products)

        except Exception as e:
            print(f"❌ Failed for category: {category}")
            print(e)
            return

    print(f"🎉 SUCCESS: Retrieved {len(all_products)} total electronic products\n")

    print("Sample products:")
    for p in all_products[:3]:
        print("-" * 50)
        print(f"ID     : {p.get('id')}")
        print(f"Title  : {p.get('title')}")
        print(f"Brand  : {p.get('brand')}")
        print(f"Price  : ${p.get('price')}")
        print(f"Rating : {p.get('rating')}")
        print(f"Category: {p.get('category')}")

    print("\n🎯 Electronics API test passed.")


if __name__ == "__main__":
    test_electronics_api()
